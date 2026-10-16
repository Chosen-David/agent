import hashlib,json,random,sqlite3,subprocess,tempfile,types
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import patch
import agent_runtime.project_memory as c
OUT=Path('.agent-runs/memory-schema-20261016/reviewer')
b=types.ModuleType('agent_runtime._reviewbaseline'); b.__package__='agent_runtime'
source=subprocess.check_output(['git','show','06ed701:agent_runtime/project_memory.py']); exec(source,b.__dict__)
results=[]
def observe(op):
 try:return {'value':op()}
 except Exception as e:return {'exception':type(e).__name__,'message':str(e)}
def fixture(root, n=4, edges=None):
 ledger=c.MemoryLedger(root,create=True)
 if edges is None:edges=[('n3','n1'),('n3','n2'),('n1','n0'),('n2','n0')]
 with ledger._connect(write=True) as db:
  db.executemany('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',[(f'n{i}','claim','x','source','[]','verified','active','fixed') for i in range(n)])
  db.executemany('INSERT INTO dependencies VALUES(?,?)',edges)
 return ledger
def compare(label,ledger,refs=['n3']):
 before=observe(lambda:b.MemoryLedger(ledger.root).check(refs));after=observe(lambda:ledger.check(refs))
 results.append(dict(label=label,before=before,after=after,equal=before==after))
 return after
with tempfile.TemporaryDirectory(dir=OUT) as tmp:
 root=Path(tmp)
 cases=[('normal',None),('scope_stale',"UPDATE entries SET scope='bad',status='stale' WHERE id='n0'"),('scope_null',"UPDATE entries SET scope='null' WHERE id='n0'"),('document_bad_stale',"INSERT INTO document_dependencies VALUES('n0','bad'); UPDATE entries SET status='stale' WHERE id='n0'"),('document_wrong',"INSERT INTO document_dependencies VALUES('n0','{}')"),('document_json_null',"INSERT INTO document_dependencies VALUES('n0','null')"),('document_json_list',"INSERT INTO document_dependencies VALUES('n0','[]')"),('document_utf8',"INSERT INTO document_dependencies VALUES('n0',CAST(X'FF' AS TEXT))"),('content_utf8',"UPDATE entries SET content=CAST(X'FF' AS TEXT) WHERE id='n0'"),('scope_utf8',"UPDATE entries SET scope=CAST(X'FF' AS TEXT) WHERE id='n0'"),('source_utf8',"UPDATE entries SET source=CAST(X'FF' AS TEXT) WHERE id='n0'"),('legacy','DROP TABLE document_dependencies'),('missing_deps','DROP TABLE dependencies'),('missing_entries','DROP TABLE document_dependencies; DROP TABLE dependencies; DROP TABLE entries'),('missing_doc_column','ALTER TABLE document_dependencies RENAME COLUMN snapshot TO wrong'),('inactive',"UPDATE entries SET status='candidate' WHERE id='n0'"),('priority',"UPDATE entries SET status='stale' WHERE id IN ('n0','n2')"),('cycle',"INSERT INTO dependencies VALUES('n0','n3')")]
 for label,sql in cases:
  ledger=fixture(root/label)
  if sql:
   with ledger._connect(write=True) as db:db.executescript(sql)
  compare(label,ledger)
 ledger=fixture(root/'refs')
 for refs in [[],(),None,'n3',['n3','n3'],['bad!'],['missing'],['n3','n0','n1'],['n0','n3'],[1]]:compare('refs:'+repr(refs),ledger,refs)
 rng=random.Random(8317)
 for j in range(100):
  n=rng.randrange(1,30);edges=[(f'n{i}',f'n{k}') for i in range(n) for k in range(n) if rng.random()<.055]
  ledger=fixture(root/f'random{j}',n,edges)
  with ledger._connect(write=True) as db:
   for i in range(n):
    status=rng.choices(['active','stale','candidate'],[90,7,3])[0]
    db.execute('UPDATE entries SET status=? WHERE id=?',(status,f'n{i}'))
  compare(f'random{j}',ledger,rng.sample([f'n{i}' for i in range(n)],rng.randrange(1,min(n,8)+1)))
 ledger=fixture(root/'deep',1500,[(f'n{i}',f'n{i-1}') for i in range(1,1500)])
 compare('deep1500',ledger,['n1499','n0'])
 # Direct entry points remain uncached and observe DDL between hydration calls.
 for module in [b,c]:
  ledger=fixture(root/('direct'+module.__name__))
  with ledger._connect(write=True) as db:
   first=module.MemoryLedger._get(db,'n0');db.execute('DROP TABLE document_dependencies')
   second=module.MemoryLedger._get(db,'n0');direct=module.MemoryLedger._check(db,['n3'])
   results.append(dict(label='direct:'+module.__name__,pass_=first==second and direct[0]['id']=='n3'))
 # Native cache cardinality / traversal / fail-before-schema observation.
 ledger=fixture(root/'trace');trace=[];orig=c._read_entry
 def read(db,*a,**kw):db.set_trace_callback(trace.append);return orig(db,*a,**kw)
 with patch.object(c,'_read_entry',side_effect=read):ledger.check(['n3','n0'])
 reads=[q.split("'")[1] for q in trace if q.startswith('SELECT * FROM entries WHERE id=')]
 results.append(dict(label='native-trace',reads=reads,schema_count=sum('FROM sqlite_master' in q for q in trace),pass_=reads==['n3','n1','n0','n2'] and sum('FROM sqlite_master' in q for q in trace)==1))
 for kind in ['missing','bad_scope']:
  trace.clear()
  if kind=='bad_scope':
   with ledger._connect(write=True) as db:db.execute("UPDATE entries SET scope='bad' WHERE id='n3'")
  with patch.object(c,'_read_entry',side_effect=read):outcome=observe(lambda:ledger.check(['missing' if kind=='missing' else 'n3']))
  results.append(dict(label='before-schema:'+kind,outcome=outcome,pass_=not any('FROM sqlite_master' in q for q in trace)))
 # All customary dispatch/factory customization routes must be uncached.
 original_connect=sqlite3.connect
 class Connection(sqlite3.Connection):pass
 for mode in ['instance_connect','class_connect','subclass','sqlite_connect','connection_subclass','row_factory','text_factory','no_transaction','class_get','class_check','instance_check','document_validator']:
  ledger=fixture(root/mode);trace=[];original=ledger._connect
  @contextmanager
  def custom(*args,**kwargs):
   if mode=='connection_subclass':
    db=original_connect(ledger.path,factory=Connection);db.row_factory=sqlite3.Row;db.execute('BEGIN')
    try:db.set_trace_callback(trace.append);yield db
    finally:db.close()
   else:
    with original(*args,**kwargs) as db:
     if mode=='row_factory':db.row_factory=lambda cur,row:dict(zip([d[0] for d in cur.description],row)) # SELECT numeric indexing fails equally
     if mode=='text_factory':db.text_factory=bytes
     if mode=='no_transaction':db.commit()
     db.set_trace_callback(trace.append);yield db
  with patch.object(c,'_read_entry',side_effect=read):
   if mode=='instance_connect':ledger._connect=custom;actual=observe(lambda:ledger.check(['n3']))
   elif mode in ['class_connect','connection_subclass','row_factory','text_factory','no_transaction']:
    with patch.object(c.MemoryLedger,'_connect',lambda *a,**kw:custom(**kw)):actual=observe(lambda:ledger.check(['n3']))
   elif mode=='subclass':
    class Sub(c.MemoryLedger):pass
    ledger=Sub(ledger.root);actual=observe(lambda:ledger.check(['n3']))
   elif mode=='sqlite_connect':
    with patch.object(sqlite3,'connect',wraps=original_connect):actual=observe(lambda:ledger.check(['n3']))
   elif mode=='class_get':
    with patch.object(c.MemoryLedger,'_get',wraps=c.MemoryLedger._get):actual=observe(lambda:ledger.check(['n3']))
   elif mode=='class_check':
    with patch.object(c.MemoryLedger,'_check',return_value=['sentinel']):actual=observe(lambda:ledger.check(['n3']))
   elif mode=='instance_check':ledger._check=lambda *a:['sentinel'];actual=observe(lambda:ledger.check(['n3']))
   elif mode=='document_validator':
    with patch.object(c,'check_document_refs',wraps=c.check_document_refs):actual=observe(lambda:ledger.check(['n3']))
  count=sum('FROM sqlite_master' in q for q in trace)
  expected=0 if mode in ['class_check','instance_check'] else 1 if mode in ['row_factory','text_factory'] else 4
  results.append(dict(label='fallback:'+mode,outcome=actual,schema_count=count,pass_=count==expected))
 # Minimal independent repro: mutable sqlite3.Row identity allows factory callback into cached path.
 saved_row=sqlite3.Row
 for module in [b,c]:
  ledger=fixture(root/('row-repro'+module.__name__))
  def factory(cur,values):
   result=saved_row(cur,values)
   if len(values)==8 and result['id']=='n1':cur.connection.execute('DROP TABLE document_dependencies')
   return result
  with patch.object(sqlite3,'Row',factory):outcome=observe(lambda:module.MemoryLedger(ledger.root).check(['n3']))
  results.append(dict(label='mutable-sqlite3.Row:'+module.__name__,outcome=outcome))
report=dict(results=results,differential_cases=sum('equal' in r for r in results),differential_failures=[r for r in results if r.get('equal') is False],property_failures=[r for r in results if r.get('pass_') is False])
(OUT/'correctness.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
