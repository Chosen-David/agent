import importlib.util,json,sqlite3,tempfile,io,contextlib,hashlib,re,shutil,subprocess
from pathlib import Path
from unittest.mock import patch
from agent_runtime import project_memory as candidate
from agent_runtime.project_docs import snapshot_project_docs
R=Path('.agent-runs/memory-index-probe-20261016-1406');OUT=R/'reviewer'
spec=importlib.util.spec_from_file_location('agent_runtime._independent_index_baseline',R/'baseline.py');baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline)
assert baseline.MemoryLedger is not candidate.MemoryLedger
assert baseline.main.__globals__ is baseline.__dict__ and candidate.main.__globals__ is candidate.__dict__
assert baseline.main.__globals__['MemoryLedger'] is baseline.MemoryLedger
source=Path('agent_runtime/project_memory.py').read_text();old=(R/'baseline.py').read_text()
assert source.replace('                    CREATE INDEX IF NOT EXISTS memory_dependencies_parent\n                        ON dependencies(parent, child);\n','')==old
TABLES=['entries','dependencies','document_dependencies','events','sqlite_sequence']
def snap(path):
 with sqlite3.connect(path) as db:return {t:db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall() for t in TABLES}
def schema(path):
 with sqlite3.connect(path) as db:return db.execute('SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY name').fetchall()
def index(path):
 with sqlite3.connect(path) as db:return dict(list=db.execute('PRAGMA index_list(dependencies)').fetchall(),info=db.execute('PRAGMA index_info(memory_dependencies_parent)').fetchall(),xinfo=db.execute('PRAGMA index_xinfo(memory_dependencies_parent)').fetchall())
def execute(path,sql):
 with sqlite3.connect(path) as db:db.executescript(sql)
def normalized_sql(s):return re.sub(r'\s+','',s).lower().replace('ifnotexists','')
checks=[]
with tempfile.TemporaryDirectory(dir=OUT) as tmp:
 tmp=Path(tmp);root=tmp/'legacy';root.mkdir();(root/'TASK.md').write_text('## 2026-10-16\n- [ ] [T1] Index fixture\n')
 l=baseline.MemoryLedger(root,create=True);refs=snapshot_project_docs(root)
 for name,deps in [('a',[]),('b',['a']),('c',['a'])]:l.add(name,'claim',name,'synthetic:independent',deps=deps,evidence='verified',document_refs=refs)
 l.correct('b','b2','new b','synthetic','revision',document_refs=refs)
 before=snap(l.path);assert len(before['document_dependencies'])==4
 bytes_before=l.path.read_bytes();schema_before=schema(l.path);read=candidate.MemoryLedger(root)
 assert read.check(['a','b2'])[0]['document_refs']==refs
 assert [x['id'] for x in read.impact('a')]==['b','c'];read.history('a');read.list()
 assert l.path.read_bytes()==bytes_before and schema(l.path)==schema_before
 # Genuine explicit init upgrade: all logical bytes incl nonempty document snapshots exact.
 candidate.MemoryLedger(root,create=True);after=snap(l.path);assert after==before
 idx=index(l.path);named=next(r for r in idx['list'] if r[1]=='memory_dependencies_parent')
 assert named[2:]==(0,'c',0) and any(r[3]=='pk' for r in idx['list'])
 assert idx['info']==[(0,1,'parent'),(1,0,'child')]
 assert idx['xinfo']==[(0,1,'parent',0,'BINARY',1),(1,0,'child',0,'BINARY',1),(2,-1,None,0,'BINARY',0)]
 installed_bytes=l.path.read_bytes();candidate.MemoryLedger(root,create=True);assert snap(l.path)==before and l.path.read_bytes()==installed_bytes
 delta=[r for r in schema(l.path) if r not in schema_before];assert len(delta)==1 and normalized_sql(delta[0][3])==normalized_sql('CREATE INDEX memory_dependencies_parent ON dependencies(parent,child)')
 # Compare real init index attributes and entire schema to diagnostic manual DDL.
 manual=tmp/'manual';manual.mkdir();ml=baseline.MemoryLedger(manual,create=True);execute(ml.path,'CREATE INDEX memory_dependencies_parent ON dependencies(parent,child)')
 fresh=candidate.MemoryLedger(tmp/'fresh',create=True)
 assert index(fresh.path)==index(ml.path)
 normalize_schema=lambda rows:[(a,b,c,normalized_sql(d) if d else None) for a,b,c,d in rows]
 assert normalize_schema(schema(fresh.path))==normalize_schema(schema(ml.path))
 diag=json.loads((R/'raw.json').read_text())['fixtures']['impact_sparse5000']['plans']['1']
 assert normalized_sql(next(r[3] for r in schema(fresh.path) if r[1]=='memory_dependencies_parent'))==normalized_sql(next(r[3] for r in diag['schema'] if r[1]=='memory_dependencies_parent'))
 sql='''WITH RECURSIVE affected(id) AS (SELECT child FROM dependencies WHERE parent=? UNION SELECT d.child FROM dependencies d JOIN affected a ON d.parent=a.id) SELECT id FROM affected ORDER BY id'''
 with sqlite3.connect(l.path) as db:eqp=db.execute('EXPLAIN QUERY PLAN '+sql,('a',)).fetchall()
 assert sum('COVERING INDEX memory_dependencies_parent' in r[3] for r in eqp)==2
 checks.append(dict(case='nonempty_documents_upgrade',logical_state_exact=True,legacy_read_no_migration=True,repeat_idempotent=True,index=idx,schema_delta=delta,diagnostic_schema_equivalent=True,eqp=eqp))
 # Actual public Python add/correct do not install the reverse index on legacy.
 execute(l.path,'DROP INDEX memory_dependencies_parent');read.add('plain','claim','plain','s',evidence='verified');assert index(l.path)['info']==[]
 trigger=[];saved=candidate.MemoryLedger._event;before=snap(l.path)
 def fail(db,eid,action,*args):
  if action=='stale':trigger.append(eid);raise sqlite3.OperationalError('independent installed-index rollback')
  return saved(db,eid,action,*args)
 # Install index again before exercising actual production indexed correction.
 candidate.MemoryLedger(root,create=True);assert snap(l.path)==before
 with patch.object(candidate.MemoryLedger,'_event',side_effect=fail):
  try:read.correct('a','a2','new a','s','correction',document_refs=refs)
  except candidate.MemoryError as e:assert 'independent installed-index rollback' in str(e)
  else:raise AssertionError('postmutation error not triggered')
 assert trigger==['c'] and snap(l.path)==before
 try:read.correct('a','bad','x','s','bad',deps=['c'],document_refs=refs)
 except candidate.MemoryError as e:assert 'invalidated lineage' in str(e)
 else:raise AssertionError('lineage accepted')
 assert snap(l.path)==before
 result=read.correct('a','a2','new a','s','correction',document_refs=refs);assert result['affected']==['b','c']
 assert read.history('b')['entry']['status']=='superseded' and read.history('c')['entry']['status']=='stale'
 assert read.history('a2')['entry']['document_refs']==refs
 # CLI validation failure happens after initialization and retains index only.
 execute(l.path,'DROP INDEX memory_dependencies_parent');before=snap(l.path)
 args=['--root',str(root),'add','--id','a','--kind','claim','--content','duplicate','--source','s']
 stdout=io.StringIO();stderr=io.StringIO()
 with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):status=candidate.main(args)
 assert status==2 and 'immutable' in json.loads(stderr.getvalue())['error'] and stdout.getvalue()==''
 assert snap(l.path)==before and index(l.path)['info']==[(0,1,'parent'),(1,0,'child')]
 checks.append(dict(case='production_api_and_failure',python_add_no_index_install=True,postmutation_rollback=True,lineage_rollback=True,normal_correction_preserves_history_and_document_snapshot=True,failed_cli_add_installs_index_without_rows=True))
 # Same-name wrong indexes intentionally remain; table collision fails without business changes.
 execute(l.path,'DROP INDEX memory_dependencies_parent; CREATE INDEX memory_dependencies_parent ON dependencies(child)');before=snap(l.path);prior=schema(l.path)
 candidate.MemoryLedger(root,create=True);assert snap(l.path)==before and schema(l.path)==prior and index(l.path)['info']==[(0,0,'child')]
 execute(l.path,'DROP INDEX memory_dependencies_parent; CREATE TABLE custom_rows(x TEXT); CREATE INDEX memory_dependencies_parent ON custom_rows(x)');prior=schema(l.path)
 candidate.MemoryLedger(root,create=True);assert snap(l.path)==before and schema(l.path)==prior
 execute(l.path,'DROP INDEX memory_dependencies_parent; CREATE TABLE memory_dependencies_parent(x TEXT)');prior=schema(l.path)
 try:candidate.MemoryLedger(root,create=True)
 except candidate.MemoryError as e:assert 'already a table named memory_dependencies_parent' in str(e)
 else:raise AssertionError('table collision accepted')
 assert snap(l.path)==before and schema(l.path)==prior
 checks.append(dict(case='same_name_boundaries',wrong_column_index_preserved=True,index_on_another_table_preserved=True,table_collision_fails_preserving_business_rows=True))
 # One actual baseline/candidate CLI invocation with isolated modules, stable data comparison.
 expected=[]
 for arm,mod in enumerate([baseline,candidate]):
  rt=tmp/f'cli{arm}';legacy=baseline.MemoryLedger(rt,create=True);legacy.add('a','claim','a','s',evidence='verified')
  out=io.StringIO()
  with contextlib.redirect_stdout(out):status=mod.main(['--root',str(rt),'add','--id','new-entry','--kind','claim','--content','new','--source','synthetic:experiment','--dep','a','--evidence','verified'])
  assert status==0;answer=json.loads(out.getvalue());dbrow=next(x for x in snap(legacy.path)['entries'] if x[0]=='new-entry');assert answer['created_at']==dbrow[-1]
  answer['created_at']='<clock>';expected.append(answer)
 assert expected[0]==expected[1]
 checks.append(dict(case='real_cli_globals',distinct_module_globals=True,stable_output_equal=True,returned_clock_matches_database=True))
report=dict(source_sha256=hashlib.sha256(source.encode()).hexdigest(),baseline_sha256=hashlib.sha256(old.encode()).hexdigest(),only_two_line_ddl_delta=True,checks=checks)
(OUT/'implementation-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'cases':len(checks),'all_passed':True,'source':report['source_sha256']}))
