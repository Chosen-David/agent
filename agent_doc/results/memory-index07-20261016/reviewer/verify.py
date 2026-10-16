import json,hashlib,statistics,random,re,math,sqlite3,tempfile,sys,importlib.util,platform,subprocess
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
R=Path('.agent-runs/memory-index-probe-20261016-1406');OUT=R/'reviewer'
spec=importlib.util.spec_from_file_location('reviewed_probe',R/'probe.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
from agent_runtime.project_memory import MemoryLedger,MemoryError
records={'producer':json.loads((R/'raw.json').read_text()),'replica':json.loads((OUT/'raw.json').read_text())};checks=[]
# Independently regenerate full logical inputs, not only fixture node count.
def expected_input(cfg):
 n=cfg['nodes'];s={t:[] for t in p.TABLES}
 for i in range(n):
  s['entries'].append(dict(id=f'n{i:05}',kind='claim',content='x'*128,source='synthetic:seed',scope='[]',evidence='verified',status='active',created_at='2000-01-01T00:00:00.000Z'))
  s['events'].append(dict(sequence=i+1,entry_id=f'n{i:05}',action='created',reason='verified',source='synthetic:seed',related_id=None,created_at='2000-01-01T00:00:00.000Z'))
  if i and ('wide' in cfg or i%16):s['dependencies'].append(dict(child=f'n{i:05}',parent=f'n{0 if "wide" in cfg else i-1:05}'))
 s['sqlite_sequence']=[dict(name='events',seq=n)]
 for t in s:s[t].sort(key=lambda x:json.dumps(x,sort_keys=True))
 return s
for label,d in records.items():
 rng=random.Random(71406)
 assert d['plan_hash']==hashlib.sha256((R/'plan-v2.json').read_bytes()).hexdigest()
 assert d['source_hash']==hashlib.sha256(Path('agent_runtime/project_memory.py').read_bytes()).hexdigest()
 for cfg in p.PLAN['fixtures']:
  fid=cfg['id'];v=d['fixtures'][fid];assert v['input_hash']==p.digest(expected_input(cfg))
  bypair={i:{} for i in range(21)}
  for i in range(-3,21):
   order=[0,1];rng.shuffle(order)
   if i<0:continue
   pair=[x for x in v['samples'] if x['pair']==i]
   assert len(pair)==2 and [x['arm'] for x in pair]==order
   for sample in pair:
    assert sample['order']==order and math.isfinite(sample['wall_ns']) and sample['wall_ns']>0
    bypair[i][sample['arm']]=sample
    raw=sample['timestamps'];n=cfg['nodes']
    expected_events=0 if cfg['op']=='impact' else 1 if cfg['op']=='add' else (512 if 'wide' in cfg else 15)+3
    assert len(raw)==expected_events+(cfg['op']!='impact')
    events=[x[1] for x in raw if x[0]=='events'];assert sorted(events)==list(range(n+1,n+1+expected_events))
    for table,key,field,ts in raw:
     assert field=='created_at' and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z',ts);datetime.fromisoformat(ts.replace('Z','+00:00'))
     assert table=='events' or key==('revision' if cfg['op']=='correct' else 'new-entry')
   assert pair[0]['output_hash']==pair[1]['output_hash'] and pair[0]['state_hash']==pair[1]['state_hash']
  assert len(v['samples'])==42 and len(v['ddl'])==21
  med={str(a):statistics.median(x['wall_ns'] for x in v['samples'] if x['arm']==a) for a in (0,1)}
  reduction=1-med['1']/med['0'];assert med==v['median_ns'] and abs(reduction-v['reduction'])<1e-12
  eqp0=' '.join(row[3] for row in v['plans']['0']['eqp']);eqp1=' '.join(row[3] for row in v['plans']['1']['eqp'])
  assert 'AUTOMATIC COVERING INDEX' in eqp0 and 'SCAN dependencies' in eqp0
  assert eqp1.count('COVERING INDEX memory_dependencies_parent')==2 and 'AUTOMATIC' not in eqp1
  a=v['plans']['0'];b=v['plans']['1'];assert a['pragma']['automatic_index']==b['pragma']['automatic_index']==[[1]]
  extra=[row for row in b['schema'] if row not in a['schema']]
  assert extra==[['index','memory_dependencies_parent','dependencies',p.DDL]]
  assert [row for row in b['schema'] if row not in extra]==a['schema']
  assert b['index_info']==[[0,1,'parent'],[1,0,'child']]
  for ddl in v['ddl']:
   assert ddl['ns']>0 and ddl['bytes_after']>ddl['bytes_before']
   assert ddl['bytes_after']-ddl['bytes_before']==(b['pragma']['page_count'][0][0]-a['pragma']['page_count'][0][0])*4096
  checks.append(dict(record=label,fixture=fid,median_ns=med,reduction=reduction,gate=reduction>=(.20 if 'sparse5000' in fid else -.15),ddl_median_ns=statistics.median(x['ns'] for x in v['ddl']),file_growth=v['ddl'][0]['bytes_after']-v['ddl'][0]['bytes_before'],relative_iqr={str(a):(statistics.quantiles([x['wall_ns'] for x in v['samples'] if x['arm']==a],n=4)[2]-statistics.quantiles([x['wall_ns'] for x in v['samples'] if x['arm']==a],n=4)[0])/med[str(a)] for a in (0,1)}))
assert all(x['gate'] for x in checks)
semantics=[]
with tempfile.TemporaryDirectory(dir=OUT) as temp:
 for arm in (0,1):
  l=MemoryLedger(Path(temp)/str(arm),create=True)
  for name,deps in [('a',[]),('b',['a']),('c',['a'])]:l.add(name,'claim',name,'test',deps=deps,evidence='verified')
  l.correct('b','b2','new b','test','new')
  if arm:
   with sqlite3.connect(l.path) as db:db.execute(p.DDL)
  before=p.snap(l.path)
  try:l.correct('a','bad','bad','test','reason',deps=['c'])
  except MemoryError as e:assert 'invalidated lineage' in str(e)
  else:raise AssertionError('lineage accepted')
  assert p.snap(l.path)==before
  trigger=[];original=MemoryLedger._event
  def fail(db,entry_id,action,*args):
   if action=='stale':trigger.append(entry_id);raise sqlite3.OperationalError('independent injected write')
   return original(db,entry_id,action,*args)
  with patch.object(MemoryLedger,'_event',side_effect=fail):
   try:l.correct('a','a2','new a','test','reason')
   except MemoryError as e:assert 'independent injected write' in str(e)
   else:raise AssertionError('injection not reached')
  assert trigger==['c'] and p.snap(l.path)==before
  result=l.correct('a','a2','new a','test','reason');assert result['affected']==['b','c']
  after=p.snap(l.path);assert result['revision']['created_at']==next(r for r in after['entries'] if r['id']=='a2')['created_at']
  assert {k:l.history(k)['entry']['status'] for k in ['a','a2','b','b2','c']}==dict(a='superseded',a2='active',b='superseded',b2='active',c='stale')
  assert [x['id'] for x in l.impact('a')]==['b','c']
  assert [x['action'] for x in l.history('a')['events']]==['created','corrected']
  assert [x['action'] for x in l.history('c')['events']]==['created','stale']
  semantics.append(dict(arm=arm,lineage_rollback=True,injected_write_rollback=True,active_trigger=trigger,statuses_events_impact=True,returned_clock_matches_db=True))
 # Oracle-independent Python reachability for random cyclic/shared graphs.
 rng=random.Random(91406)
 for case in range(60):
  n=rng.randrange(1,45);edges={(i,j) for i in range(n) for j in range(n) if rng.random()<.07};target=rng.randrange(n)
  expected=set();todo=[target]
  while todo:
   parent=todo.pop()
   for child,dep in edges:
    if dep==parent and child not in expected:expected.add(child);todo.append(child)
  outcomes=[]
  for arm in (0,1):
   l=MemoryLedger(Path(temp)/f'g{case}-{arm}',create=True)
   with l._connect(write=True) as db:
    db.executemany('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',[(str(i),'claim','x','s','[]','verified','active','fixed') for i in range(n)])
    db.executemany('INSERT INTO dependencies VALUES(?,?)',[(str(a),str(b)) for a,b in edges])
    if arm:db.execute(p.DDL)
   actual=l.impact(str(target));assert [r['id'] for r in actual]==sorted(map(str,expected));outcomes.append(actual)
  assert outcomes[0]==outcomes[1]
 # Verify normalizer rejects changes it is forbidden to suppress.
 old=expected_input(p.PLAN['fixtures'][2]);bad=json.loads(json.dumps(old));bad['entries'][0]['created_at']='changed'
 try:p.normalize(bad,old)
 except AssertionError:pass
 else:raise AssertionError('old timestamp normalized')
 bad=json.loads(json.dumps(old));bad['entries'].append(dict(old['entries'][0],id='revision',created_at='invalid'))
 try:p.normalize(bad,old)
 except AssertionError:pass
 else:raise AssertionError('bad new clock normalized')
 # Reproduce the original failed-fixture explanation rather than guessing it.
 l=MemoryLedger(Path(temp)/'original-oracle',create=True)
 l.add('a','claim','a','test',evidence='verified');l.add('b','claim','b','test',deps=['a'],evidence='verified');l.correct('b','b2','new b','test','new')
 trigger=[]
 def record(db,entry_id,action,*args):
  if action=='stale':trigger.append(entry_id)
  return original(db,entry_id,action,*args)
 with patch.object(MemoryLedger,'_event',side_effect=record):l.correct('a','a2','new a','test','reason')
 assert trigger==[] and l.history('b')['entry']['status']=='superseded' and l.history('b2')['entry']['status']=='active'
report=dict(raw_checks=checks,semantics=semantics,random_reference_graphs=60,original_oracle_no_active_descendant_confirmed=True,timestamp_negative_probes=True,source_unmodified=not subprocess.check_output(['git','diff','--','agent_runtime/project_memory.py']),environment=dict(python=sys.version,sqlite=sqlite3.sqlite_version,platform=platform.platform(),affinity=sorted(__import__('os').sched_getaffinity(0))))
(OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'all_gates':True,'random_graphs':60,'semantics':semantics,'original_oracle_confirmed':True}))
