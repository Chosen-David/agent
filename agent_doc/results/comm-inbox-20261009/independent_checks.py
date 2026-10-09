import hashlib,json,math,statistics,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from agent_runtime.communication import Mailbox,canonical
from scripts.benchmark_communication_inbox import load_baseline
R=Path(__file__).resolve().parents[3]; D=Path(__file__).parent
manifest=json.loads((D/'manifest.json').read_text()); bindings={}
for group,refs in manifest['artifacts'].items():
 for ref in refs:
  actual=hashlib.sha256((R/ref['path']).read_bytes()).hexdigest()
  assert actual==ref['sha256'],ref['path']
  bindings[ref['path']]=actual
assert manifest['validation_plan']['sha256']==bindings[manifest['validation_plan']['path']]
baseline=(D/'baseline_communication.py').read_text();candidate=(R/'agent_runtime/communication.py').read_text()
added='                CREATE INDEX IF NOT EXISTS communication_pending_recipient\n                    ON communication_deliveries(recipient,seq)\n                    WHERE receipt IS NULL;\n'
assert candidate.replace(added,'')==baseline
assert subprocess.check_output(['git','show','bb5bf5b8edaebd8910f9a7af28830c668113d339:agent_runtime/communication.py'],cwd=R)==(D/'baseline_communication.py').read_bytes()
reports={}
for filename,n in [('raw.json',21),('independent_raw.json',5)]:
 raw=json.loads((D/filename).read_text()); assert raw['config']==dict(history=[0,1000,20000],pending=[0,5],runs=[1,4],warmups=3,repeats=n,units='ms',seed='deterministic')
 keys=[(c['history'],c['pending'],c['runs']) for c in raw['cases']]
 assert set(keys)=={(h,p,r) for h in [0,1000,20000] for p in [0,5] for r in [1,4]} and len(keys)==12
 rows=[]
 for c in raw['cases']:
  h,p,r=c['history'],c['pending'],c['runs']
  # All history target deliveries are ACKed; the final p events are target/pending.
  oracle=[dict(seq=i,event=dict(event_id=str(i),run_id='target',payload='界'*32)) for i in range(h+1,h+p+1)]
  assert c['expected']==oracle
  assert len(c['raw'])==n and all(set(pair)=={'baseline','candidate'} for pair in c['raw'])
  med={k:statistics.median(pair[k] for pair in c['raw']) for k in ['baseline','candidate']}
  assert c['median_ms']==med
  for pair in c['raw']:
   assert all(isinstance(v,(int,float)) and math.isfinite(v) and v>0 for v in pair.values())
  vmratio=c['vm']['baseline']/c['vm']['candidate'];assert all(type(v)is int and v>0 for v in c['vm'].values())
  if h==20000 and r==1:assert vmratio>=2
  overhead={}
  for k in ['baseline','candidate']:
   assert len(c['overhead'][k])==n
   for pair in c['overhead'][k]:assert set(pair)=={'publish_ms','ack_ms'} and all(math.isfinite(v) and v>0 for v in pair.values())
   overhead[k]={op:statistics.median(pair[op] for pair in c['overhead'][k]) for op in ['publish_ms','ack_ms']}
  for op in ['publish_ms','ack_ms']:
   b,v=overhead['baseline'][op],overhead['candidate'][op];assert v<=2*b or v-b<1
  assert 0<c['migration']['ms']<10000 and 0<c['migration']['reopen_ms']
  row={k:c[k] for k in ['history','pending','runs','vm','median_ms','migration']}
  row.update(latency_range_ms={k:[min(pair[k] for pair in c['raw']),max(pair[k] for pair in c['raw'])] for k in ['baseline','candidate']},overhead_median_ms=overhead,vm_ratio=vmratio,latency_ratio=med['baseline']/med['candidate'])
  rows.append(row)
 if filename=='raw.json': assert json.loads((D/'summary.json').read_text())==dict(status='pending independent verification',cases=rows)
 reports[filename]=rows
# Independently constructed interleaving with 4 runs, 2 recipients, arbitrary ACKs,
# >100 pending per recipient, restart and migration. Expectations are Python lists.
classes={'baseline':load_baseline(D/'baseline_communication.py'),'candidate':Mailbox}
property_checks=0
with tempfile.TemporaryDirectory() as temp:
 for label,cls in classes.items():
  root=Path(temp)/label;root.mkdir();(root/'proof').write_bytes(b'proof')
  ref=dict(id='proof',path='proof',sha256=hashlib.sha256(b'proof').hexdigest())
  plans=[dict(schema_version=1,run_id=f'R{x}',input_version='v1',max_events=200,routes=[dict(sender='code',recipient=rec,task_id='T',kind='artifact') for rec in ['A','B']]) for x in range(4)]
  boxes=[cls(root/'db',plan,root) for plan in plans];pending={(x,rec):[] for x in range(4) for rec in ['A','B']}
  for i in range(520):
   x=i%4;ev=dict(event_id=str(i),run_id=f'R{x}',input_version='v1',sender='code',task_id='T',kind='artifact',summary='界',action='verify',refs=[ref])
   seq=boxes[x].publish(ev)['seq']
   for rec in ['A','B']:
    if (i+(rec=='B'))%7==0:boxes[x].acknowledge(rec,seq,dict(status='rejected',reason='independent fixture'))
    else:pending[x,rec].append(dict(seq=seq,event=ev))
  migrated=[Mailbox(root/'db',plan,root) for plan in plans]
  for x in range(4):
   assert migrated[x].status()==boxes[x].status()
   for rec in ['A','B']:
    for limit in [1,20,100]:
     assert boxes[x].inbox(rec,limit=limit)==pending[x,rec][:limit]
     assert migrated[x].inbox(rec,limit=limit)==pending[x,rec][:limit];property_checks+=2
    for bad in [0,101,True,-1,1.0]:
     try:migrated[x].inbox(rec,limit=bad)
     except ValueError:property_checks+=1
     else:raise AssertionError('bad limit accepted')
    try:migrated[x].inbox('unknown')
    except ValueError:property_checks+=1
    else:raise AssertionError('unknown recipient accepted')
(D/'independent_checks.json').write_text(json.dumps(dict(status='pass',bindings=bindings,recomputed=reports,independent_interleaving_checks=property_checks),indent=2)+'\n')
print('pass: hashes/source, 12-case raw and rerun matrix, independent oracle, aggregates, thresholds,',property_checks,'interleaving/boundary checks')
