import json,hashlib,statistics,random,math,re,sqlite3,sys,platform,subprocess
from pathlib import Path
from datetime import datetime
R=Path('.agent-runs/memory-history-20261016-1601');O=R/'reviewer';plan=json.loads((R/'plan.json').read_text());records={'producer':json.loads((R/'raw.json').read_text()),'independent':json.loads((O/'raw.json').read_text())}
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def expected_input(c):
 n=c['nodes'];ec=c['events'];state=dict(entries=[],dependencies=[],document_dependencies=[],events=[],sqlite_sequence=[dict(name='events',seq=ec)])
 for i in range(n):state['entries'].append(dict(id=f'n{i:05}',kind='claim',content='x'*128,source='synthetic:seed',scope='[]',evidence='verified',status='stale' if c['id']=='history_many512' else 'active',created_at='2000-01-01T00:00:00.000Z'))
 if c['op']=='correct':state['dependencies']=[dict(child=f'n{i:05}',parent=f'n{i-1:05}') for i in range(1,16)]
 for i in range(ec):state['events'].append(dict(sequence=i+1,entry_id=f'n{0 if n==1 else i:05}',action='created' if n>1 or i==0 else 'stale',reason='fixture',source='synthetic:seed',related_id=None,created_at='2000-01-01T00:00:00.000Z'))
 return state
expected={c['id']:sha(expected_input(c)) for c in plan['fixtures']};checks=[]
source_hash=hashlib.sha256(Path('agent_runtime/project_memory.py').read_bytes()).hexdigest()
for label,data in records.items():
 assert data['source_sha256']==source_hash and data['plan_sha256']==hashlib.sha256((R/'plan.json').read_bytes()).hexdigest()
 script=R/'measure.py' if label=='producer' else O/'measure-independent.py'
 assert data['script_sha256']==hashlib.sha256(script.read_bytes()).hexdigest()
 rng=random.Random(81601)
 for c in plan['fixtures']:
  fid=c['id'];v=data['fixtures'][fid];assert v['input_hash']==expected[fid];assert len(v['samples'])==42 and len(v['ddl'])==21
  for pair in range(-3,21):
   order=[0,1];rng.shuffle(order)
   if pair<0:continue
   rows=[s for s in v['samples'] if s['pair']==pair];assert len(rows)==2 and [s['arm'] for s in rows]==order
   for s in rows:
    assert s['order']==order and math.isfinite(s['wall_ns']) and s['wall_ns']>0
    clocks=s['new_timestamps'];new_events=0 if c['op']=='history' else 1 if c['op']=='add' else 18
    assert len(clocks)==new_events+(c['op']!='history')
    assert sorted(x[1] for x in clocks if x[0]=='events')==list(range(c['events']+1,c['events']+1+new_events))
    for table,key,field,value in clocks:
     assert field=='created_at' and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z',value);datetime.fromisoformat(value.replace('Z','+00:00'))
     assert table=='events' or (table=='entries' and key==('revision' if c['op']=='correct' else 'new-entry'))
   assert rows[0]['output_sha256']==rows[1]['output_sha256'] and rows[0]['state_sha256']==rows[1]['state_sha256']
  med={str(a):statistics.median(s['wall_ns'] for s in v['samples'] if s['arm']==a) for a in (0,1)};red=1-med['1']/med['0'];assert med==v['median_ns'] and abs(red-v['reduction'])<1e-12
  before=v['plans']['0'];after=v['plans']['1'];baseeq=' '.join(x[3] for x in before['eqp']);candeq=' '.join(x[3] for x in after['eqp'])
  assert 'SCAN events' in baseeq and 'TEMP B-TREE' not in baseeq
  assert 'USING INDEX memory_events_entry' in candeq and 'COVERING' not in candeq and 'TEMP B-TREE' not in candeq
  extra=[x for x in after['schema'] if x not in before['schema']];assert extra==[['index','memory_events_entry','events','CREATE INDEX memory_events_entry ON events(entry_id)']]
  assert [x for x in after['schema'] if x not in extra]==before['schema']
  assert before['pragma']['index_xinfo(memory_events_entry)']==[]
  assert after['pragma']['index_xinfo(memory_events_entry)']==[[0,1,'entry_id',0,'BINARY',1],[1,-1,None,0,'BINARY',0]]
  row=next(x for x in after['pragma']['index_list(events)'] if x[1]=='memory_events_entry');assert row[2:]==[0,'c',0]
  assert before['pragma']['automatic_index']==after['pragma']['automatic_index']==[[1]]
  assert before['pragma']['journal_mode']==after['pragma']['journal_mode']==[['delete']]
  assert before['files']==after['files']==['memory.sqlite3']
  growth=(after['pragma']['page_count'][0][0]-before['pragma']['page_count'][0][0])*4096
  for d in v['ddl']:assert d['wall_ns']>0 and d['bytes_after']-d['bytes_before']==growth
  gate=red>=(.30 if fid in ['history_first50000','history_last50000'] else -.15)
  assert data['gates'][fid]==gate
  checks.append(dict(record=label,fixture=fid,median_ns=med,reduction=red,gate=gate,ddl_median_ns=statistics.median(x['wall_ns'] for x in v['ddl']),file_growth_bytes=growth,relative_iqr={str(a):(statistics.quantiles([s['wall_ns'] for s in v['samples'] if s['arm']==a],n=4)[2]-statistics.quantiles([s['wall_ns'] for s in v['samples'] if s['arm']==a],n=4)[0])/med[str(a)] for a in (0,1)}))
 assert len(data['validation'])==2 and all(x['preinsert_rollback'] and x['postwrite_rollback'] and x['history_superseded'] and x['hit']==['c'] for x in data['validation'])
assert all(x['gate'] for x in checks)
(O/'data-verification.json').write_text(json.dumps(dict(checks=checks,input_hashes=expected,all_gates=True,source_sha256=source_hash,environment=dict(python=sys.version,sqlite=sqlite3.sqlite_version,platform=platform.platform(),affinity=sorted(__import__('os').sched_getaffinity(0)))),indent=2)+'\n')
print(json.dumps(dict(all_checks_passed=True,reductions={x['record']+':'+x['fixture']:x['reduction'] for x in checks})))
