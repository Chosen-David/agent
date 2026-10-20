import ast,json,subprocess,tempfile
from unittest.mock import patch
from agent_runtime import project_memory as m
source=subprocess.check_output(['git','show','fad3bd48:agent_runtime/project_memory.py'],text=True)
cls=next(x for x in ast.parse(source).body if isinstance(x,ast.ClassDef) and x.name=='MemoryLedger')
fn=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='_context_closure')
ns=dict(vars(m));exec(compile(ast.Module(body=[fn],type_ignores=[]),'base','exec'),ns)
before=ns['_context_closure'];after=m.MemoryLedger._context_closure
cases={'diamond':None,'absent':'DROP TABLE document_dependencies','unknown':None,'empty':None,'duplicate':None,'bad_scope':"UPDATE entries SET scope='broken', status='stale' WHERE id='leaf'",'stale':"UPDATE entries SET status='stale' WHERE id='a'",'bad_binding':"INSERT INTO document_dependencies VALUES('a','broken')",'cycle':"INSERT INTO dependencies VALUES('p','leaf')",'missing_parent':"INSERT INTO dependencies VALUES('p','missing')"}
results=[]
for case,sql in cases.items():
 with tempfile.TemporaryDirectory() as root:
  ledger=m.MemoryLedger(root,create=True)
  for name,deps in [('p',[]),('a',['p']),('b',['p']),('leaf',['a','b'])]:ledger.add(name,'claim',name,'fixture',deps=deps,evidence='verified')
  if sql:
   with ledger._connect(write=True) as db:
    if case=='missing_parent':db.execute('COMMIT');db.execute('PRAGMA foreign_keys=OFF')
    db.execute(sql)
  refs={'unknown':['missing'],'empty':[],'duplicate':['leaf','leaf']}.get(case,['leaf','p'])
  values=[]
  for method in [before,after]:
   try:values.append(('ok',method(ledger,refs)))
   except Exception as e:values.append((type(e).__name__,str(e)))
  assert values[0]==values[1],(case,values)
  results.append({'case':case,'same':True,'result_type':values[0][0]})
print(json.dumps(results,indent=2))
