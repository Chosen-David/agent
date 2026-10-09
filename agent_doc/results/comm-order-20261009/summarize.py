import json
from pathlib import Path
import statistics
import sys
p=Path(sys.argv[1]);raw=json.loads(p.read_text());rows=[]
for c in raw['cases']:
 r={k:c[k] for k in ('total','layout','vm','median_ms','range_ms')}
 r['vm_ratio']=c['vm']['baseline']/c['vm']['candidate']
 r['latency_ratio']=c['median_ms']['baseline']/c['median_ms']['candidate']
 if c['total']==20000 and c['layout'] in ('single','interleaved'):
  assert r['vm_ratio']>=10
  assert r['latency_ratio']>=2
 if c['total']==100:
  b,v=c['median_ms']['baseline'],c['median_ms']['candidate'];assert v<=2*b or v-b<1
 if 'overhead' in c:
  r['overhead_median_ms']={n:{op:statistics.median(x[op] for x in c['overhead'][n]) for op in ('publish_ms','ack_ms')} for n in ('baseline','candidate')}
  for op in ('publish_ms','ack_ms'):
   b=r['overhead_median_ms']['baseline'][op];v=r['overhead_median_ms']['candidate'][op];assert v<=2*b or v-b<1
 rows.append(r)
assert len(rows)==12
(p.parent/'summary.json').write_text(json.dumps(dict(status='pending independent verification',cases=rows),indent=2)+'\n')
