import json,hashlib,random,statistics,math,re
from pathlib import Path
from datetime import datetime
R=Path('.agent-runs/memory-history-20261016-1601');O=R/'reviewer';d=json.loads((R/'integration.json').read_text());old=json.loads((R/'raw.json').read_text());rng=random.Random(81602);checks=[]
assert d['source_sha256']==hashlib.sha256(Path('agent_runtime/project_memory.py').read_bytes()).hexdigest()
assert d['script_sha256']==hashlib.sha256((R/'integration.py').read_bytes()).hexdigest()
growth=old['fixtures']['add50000']['ddl'][0]['bytes_after']-old['fixtures']['add50000']['ddl'][0]['bytes_before'];basebytes=old['fixtures']['add50000']['ddl'][0]['bytes_before']
for scenario in ['steady_cli_add','first_upgrade_cli_add','constructor_upgrade','constructor_repeat']:
 v=d['fixtures'][scenario];assert len(v['samples'])==42 and v['input_hash']==old['fixtures']['add50000']['input_hash']
 for pair in range(-3,21):
  order=[0,1];rng.shuffle(order)
  if pair<0:continue
  rows=[x for x in v['samples'] if x['pair']==pair];assert len(rows)==2 and [x['arm'] for x in rows]==order
  for x in rows:
   assert x['order']==order and math.isfinite(x['wall_ns']) and x['wall_ns']>0
   assert x['bytes_before']==basebytes+(growth if x['arm'] and scenario in ['steady_cli_add','constructor_repeat'] else 0)
   assert x['bytes_after']>=x['bytes_before'] and x['bytes_after']%4096==0
   if 'cli' in scenario:
    clocks=x['new_timestamps'];assert [(t[0],t[1],t[2]) for t in clocks]==[('entries','new-entry','created_at'),('events',50001,'created_at')]
    for t in clocks:
     assert re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z',t[3]);datetime.fromisoformat(t[3].replace('Z','+00:00'))
   else:
    assert x['new_timestamps']==[] and x['state_sha256']==v['input_hash']
    assert x['bytes_after']==basebytes+(growth if x['arm'] else 0)
  assert rows[0]['output_sha256']==rows[1]['output_sha256'] and rows[0]['state_sha256']==rows[1]['state_sha256']
 med={str(a):statistics.median(x['wall_ns'] for x in v['samples'] if x['arm']==a) for a in (0,1)};reduction=1-med['1']/med['0'];assert med==v['median_ns'] and abs(reduction-v['reduction'])<1e-12
 checks.append(dict(scenario=scenario,median_ns=med,reduction=reduction,absolute_added_ns=med['1']-med['0'],physical_sizes={str(a):sorted({(x['bytes_before'],x['bytes_after']) for x in v['samples'] if x['arm']==a}) for a in (0,1)},relative_iqr={str(a):(statistics.quantiles([x['wall_ns'] for x in v['samples'] if x['arm']==a],n=4)[2]-statistics.quantiles([x['wall_ns'] for x in v['samples'] if x['arm']==a],n=4)[0])/med[str(a)] for a in (0,1)}))
assert d['steady_gate']==(d['fixtures']['steady_cli_add']['reduction']>=-.15)==True
(O/'integration-verification.json').write_text(json.dumps(dict(checks=checks,samples=168,steady_gate=True,source_sha256=d['source_sha256'],script_sha256=d['script_sha256']),indent=2)+'\n');print(json.dumps(dict(samples=168,all_checks_passed=True,steady_gate=True)))
