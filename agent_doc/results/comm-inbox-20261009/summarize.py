import json
from pathlib import Path
import statistics
import sys
p=Path(sys.argv[1]);raw=json.loads(p.read_text());summary=[]
for c in raw['cases']:
 row={k:c[k] for k in ('history','pending','runs','vm','median_ms','migration')}
 row['latency_range_ms']={n:[min(r[n] for r in c['raw']),max(r[n] for r in c['raw'])] for n in ('baseline','candidate')}
 row['overhead_median_ms']={n:{op:statistics.median(r[op] for r in c['overhead'][n]) for op in ('publish_ms','ack_ms')} for n in ('baseline','candidate')}
 row['vm_ratio']=c['vm']['baseline']/c['vm']['candidate']
 row['latency_ratio']=c['median_ms']['baseline']/c['median_ms']['candidate']
 assert c['migration']['ms']<10000
 if c['history']==20000 and c['runs']==1:assert row['vm_ratio']>=2
 for op in ('publish_ms','ack_ms'):
  b=row['overhead_median_ms']['baseline'][op];v=row['overhead_median_ms']['candidate'][op]
  assert v<=2*b or v-b<1
 summary.append(row)
assert len(summary)==12
(p.parent/'summary.json').write_text(json.dumps(dict(status='pending independent verification',cases=summary),indent=2)+'\n')
