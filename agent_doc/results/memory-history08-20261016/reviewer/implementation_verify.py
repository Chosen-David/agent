import importlib.util,json,sqlite3,tempfile,io,contextlib,hashlib,re
from pathlib import Path
from unittest.mock import patch
from agent_runtime import project_memory as candidate
from agent_runtime.project_docs import snapshot_project_docs
R=Path('.agent-runs/memory-history-20261016-1601');O=R/'reviewer'
spec=importlib.util.spec_from_file_location('agent_runtime._independent_history_baseline',R/'baseline.py');baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline)
assert baseline.MemoryLedger is not candidate.MemoryLedger
assert baseline.main.__globals__ is baseline.__dict__ and candidate.main.__globals__ is candidate.__dict__
assert baseline.main.__globals__['MemoryLedger'] is baseline.MemoryLedger
old=(R/'baseline.py').read_text();source=Path('agent_runtime/project_memory.py').read_text()
assert source.replace('                    CREATE INDEX IF NOT EXISTS memory_events_entry\n                        ON events(entry_id);\n','')==old
TABLES=['entries','dependencies','document_dependencies','events','sqlite_sequence']
def snap(path):
 with sqlite3.connect(path) as db:return {t:db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall() for t in TABLES}
def schema(path):
 with sqlite3.connect(path) as db:return db.execute('SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY name').fetchall()
def idx(path):
 with sqlite3.connect(path) as db:return dict(list=db.execute('PRAGMA index_list(events)').fetchall(),info=db.execute('PRAGMA index_info(memory_events_entry)').fetchall(),xinfo=db.execute('PRAGMA index_xinfo(memory_events_entry)').fetchall())
def sql(path,query):
 with sqlite3.connect(path) as db:db.executescript(query)
def normsql(s):return re.sub(r'\s+','',s).lower().replace('ifnotexists','')
checks=[]
with tempfile.TemporaryDirectory(dir=O) as td:
 root=Path(td)/'legacy';root.mkdir();(root/'TASK.md').write_text('## 2026-10-16\n- [ ] [T1] Exact history\n');refs=snapshot_project_docs(root)
 l=baseline.MemoryLedger(root,create=True)
 for name,deps in [('a',[]),('b',['a']),('c',['a'])]:l.add(name,'claim',name,'fixture',deps=deps,evidence='verified',document_refs=refs)
 l.correct('b','b2','new b','fixture','revision',document_refs=refs)
 with l._connect(write=True) as db:
  db.executemany('INSERT INTO events(sequence,entry_id,action,reason,source,related_id,created_at) VALUES(?,?,?,?,?,?,?)',[(90,'a','fixture90','r90','s90','x90','1900'),(-20,'a','fixture-20','r-20','s-20','x-20','2200'),(0,'a','fixture0','r0','s0','x0','2100')])
 before=snap(l.path);assert len(before['document_dependencies'])==4
 oldhist=l.history('a');assert [e['sequence'] for e in oldhist['events']]==[-20,0,1,90]
 physical=l.path.read_bytes();oldschema=schema(l.path);read=candidate.MemoryLedger(root);assert read.history('a')==oldhist
 read.list();read.impact('a');read.check(['a','b2']);assert l.path.read_bytes()==physical and schema(l.path)==oldschema and idx(l.path)['info']==[]
 candidate.MemoryLedger(root,create=True);assert snap(l.path)==before and read.history('a')==oldhist
 meta=idx(l.path);assert meta['info']==[(0,1,'entry_id')]
 assert meta['xinfo']==[(0,1,'entry_id',0,'BINARY',1),(1,-1,None,0,'BINARY',0)]
 named=next(x for x in meta['list'] if x[1]=='memory_events_entry');assert named[2:]==(0,'c',0)
 physical=l.path.read_bytes();candidate.MemoryLedger(root,create=True);assert l.path.read_bytes()==physical and snap(l.path)==before
 delta=[r for r in schema(l.path) if r not in oldschema];assert len(delta)==1 and normsql(delta[0][3])==normsql('CREATE INDEX memory_events_entry ON events(entry_id)')
 manual=baseline.MemoryLedger(Path(td)/'manual',create=True);sql(manual.path,'CREATE INDEX memory_events_entry ON events(entry_id)');fresh=candidate.MemoryLedger(Path(td)/'fresh',create=True)
 assert idx(manual.path)==idx(fresh.path)
 normschema=lambda rows:[(a,b,c,normsql(d) if d else None) for a,b,c,d in rows]
 assert normschema(schema(manual.path))==normschema(schema(fresh.path))
 diag=json.loads((R/'raw.json').read_text())['fixtures']['history_first50000']['plans']['1']['schema']
 assert normschema(schema(fresh.path))==normschema(diag)
 with sqlite3.connect(l.path) as db:eqp=db.execute('EXPLAIN QUERY PLAN SELECT * FROM events WHERE entry_id=? ORDER BY sequence',('a',)).fetchall()
 assert any('USING INDEX memory_events_entry' in x[3] for x in eqp) and not any('COVERING' in x[3] or 'TEMP B-TREE' in x[3] for x in eqp)
 checks.append(dict(case='actual_schema_upgrade',nonempty_documents_exact=True,old_clocks_and_sequence_exact=True,legacy_reads_no_migration=True,repeat_physical_and_logical_idempotent=True,sequence_negative_gaps_backwards_clock_exact=True,index=meta,diagnostic_entire_schema_equivalent=True,eqp=eqp))
 # Python ordinary writes do not install this index; production indexed correction rollback preserved.
 sql(l.path,'DROP INDEX memory_events_entry');read.add('plain','claim','plain','fixture',evidence='verified');assert idx(l.path)['info']==[]
 candidate.MemoryLedger(root,create=True);before=snap(l.path);orig=candidate.MemoryLedger._event;hits=[]
 def fail(db,eid,action,*args):
  if action=='stale':hits.append(eid);raise sqlite3.OperationalError('independent indexed history rollback')
  return orig(db,eid,action,*args)
 with patch.object(candidate.MemoryLedger,'_event',side_effect=fail):
  try:read.correct('a','a2','new','fixture','reason',document_refs=refs)
  except candidate.MemoryError as e:assert 'independent indexed history rollback' in str(e)
  else:raise AssertionError('write error not triggered')
 assert hits==['c'] and snap(l.path)==before
 try:read.correct('a','bad','bad','fixture','reason',deps=['c'],document_refs=refs)
 except candidate.MemoryError as e:assert 'invalidated lineage' in str(e)
 else:raise AssertionError('invalid lineage accepted')
 assert snap(l.path)==before
 result=read.correct('a','a2','new','fixture','reason',document_refs=refs);assert result['affected']==['b','c']
 assert read.history('b')['entry']['status']=='superseded' and read.history('c')['entry']['status']=='stale'
 assert read.history('a2')['entry']['document_refs']==refs
 checks.append(dict(case='business_rollback',normal_add_no_index_install=True,preinsert_and_postwrite_rollback=True,superseded_protection=True,document_refs_preserved=True))
 # Failed actual CLI still installs the init index but must not change business state.
 sql(l.path,'DROP INDEX memory_events_entry');before=snap(l.path);out=io.StringIO();err=io.StringIO()
 with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):rc=candidate.main(['--root',str(root),'add','--id','a','--kind','claim','--content','duplicate','--source','fixture'])
 assert rc==2 and out.getvalue()=='' and 'immutable' in json.loads(err.getvalue())['error']
 assert snap(l.path)==before and idx(l.path)['info']==[(0,1,'entry_id')]
 sql(l.path,'DROP INDEX memory_events_entry;CREATE INDEX memory_events_entry ON events(action)');prior=schema(l.path);candidate.MemoryLedger(root,create=True);assert schema(l.path)==prior and snap(l.path)==before
 sql(l.path,'DROP INDEX memory_events_entry;CREATE TABLE custom_rows(x);CREATE INDEX memory_events_entry ON custom_rows(x)');prior=schema(l.path);candidate.MemoryLedger(root,create=True);assert schema(l.path)==prior and snap(l.path)==before
 sql(l.path,'DROP INDEX memory_events_entry;CREATE TABLE memory_events_entry(marker TEXT)');prior=schema(l.path)
 try:candidate.MemoryLedger(root,create=True)
 except candidate.MemoryError as e:assert 'already a table named memory_events_entry' in str(e)
 else:raise AssertionError('table collision accepted')
 assert schema(l.path)==prior and snap(l.path)==before
 checks.append(dict(case='cli_and_same_names',failed_add_installs_without_business_mutation=True,wrong_column_index_preserved=True,index_on_other_table_preserved=True,table_collision_preserves_business_state=True))
 # Independent invocation of actual main with separately loaded baseline globals.
 packets=[]
 for arm,mod in enumerate([baseline,candidate]):
  rt=Path(td)/f'cli{arm}';ledger=baseline.MemoryLedger(rt,create=True);ledger.add('a','claim','a','fixture',evidence='verified');output=io.StringIO()
  with contextlib.redirect_stdout(output):rc=mod.main(['--root',str(rt),'add','--id','new-entry','--kind','claim','--content','new','--source','synthetic:experiment','--evidence','verified'])
  assert rc==0;packet=json.loads(output.getvalue());row=next(x for x in snap(ledger.path)['entries'] if x[0]=='new-entry');assert packet['created_at']==row[-1];packet['created_at']='<new-clock>';packets.append(packet)
 assert packets[0]==packets[1]
 checks.append(dict(case='real_cli',independent_module_globals=True,stable_packet_equal=True,returned_clock_matches_db=True))
(O/'implementation-verification.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.encode()).hexdigest(),baseline_sha256=hashlib.sha256(old.encode()).hexdigest(),two_line_ddl_only=True,checks=checks,all_passed=True),indent=2)+'\n')
print(json.dumps(dict(groups=len(checks),all_passed=True)))
