from pathlib import Path
import json,hashlib,random,statistics,math,re
from datetime import datetime
r=Path('.agent-runs/memory-index-probe-20261016-1406');d=json.loads((r/'integration.json').read_text());rng=random.Random(71407);checks=[]
for scenario in ['steady_cli_add','first_upgrade_cli_add','constructor_upgrade','constructor_repeat']:
 v=d[scenario];assert v['input_hash']==json.loads((r/'raw.json').read_text())['fixtures']['impact_sparse5000']['input_hash'];assert len(v['samples'])==42
 for pair in range(-3,21):
  order=[0,1];rng.shuffle(order)
  if pair<0:continue
  s=[s for s in v['samples'] if s['pair']==pair];assert len(s)==2 and [x['arm'] for x in s]==order
  for x in s:
   assert x['order']==order and x['wall_ns']>0 and math.isfinite(x['wall_ns'])
   if 'cli_add' in scenario:
    assert [(t[0],t[1],t[2]) for t in x['timestamps']]==[('entries','new-entry','created_at'),('events',5001,'created_at')]
    for t in x['timestamps']:
     assert re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z',t[3]);datetime.fromisoformat(t[3].replace('Z','+00:00'))
   else:assert x['timestamps']==[]
   expected_before=1880064 if x['arm']==1 and scenario in ['steady_cli_add','constructor_repeat'] else 1773568
   assert x['bytes_before']==expected_before
   assert x['bytes_after']>=x['bytes_before'] and x['bytes_after']%4096==0
   if 'cli_add' not in scenario:assert x['bytes_after']==(1880064 if x['arm'] else 1773568)
  assert s[0]['output_hash']==s[1]['output_hash'] and s[0]['state_hash']==s[1]['state_hash']
 med={str(a):statistics.median(x['wall_ns'] for x in v['samples'] if x['arm']==a) for a in (0,1)};red=1-med['1']/med['0'];assert med==v['median_ns'] and abs(red-v['reduction'])<1e-12
 checks.append(dict(scenario=scenario,median_ns=med,reduction=red,physical_sizes={str(a):sorted({(x['bytes_before'],x['bytes_after']) for x in v['samples'] if x['arm']==a}) for a in (0,1)},relative_iqr={str(a):(statistics.quantiles([x['wall_ns'] for x in v['samples'] if x['arm']==a],n=4)[2]-statistics.quantiles([x['wall_ns'] for x in v['samples'] if x['arm']==a],n=4)[0])/med[str(a)] for a in (0,1)},checks_pass=True))
assert d['steady_gate']==(d['steady_cli_add']['reduction']>=-.15)==True
(r/'reviewer/implementation-data-check.json').write_text(json.dumps({'checks':checks,'gate':True,'source_sha256':hashlib.sha256(Path('agent_runtime/project_memory.py').read_bytes()).hexdigest(),'integration_sha256':hashlib.sha256((r/'integration.py').read_bytes()).hexdigest()},indent=2)+'\n');print('All integration raw checks pass')
