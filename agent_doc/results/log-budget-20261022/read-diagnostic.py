import hashlib,json,sys,tracemalloc,types
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parents[1]))
rows=[]
for source in ('baseline-observer.py','candidate-observer.py'):
 m=types.ModuleType('agent_runtime._read_diagnostic');m.__package__='agent_runtime'
 exec(compile((P/source).read_bytes(),source,'exec'),m.__dict__)
 tracemalloc.start()
 raw=m.read_bound(P,'job.log',max_bytes=32*1024*1024)
 peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop()
 rows.append({'source':source,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'python_peak_bytes':peak})
assert rows[0]['sha256']==rows[1]['sha256'] and rows[0]['bytes']==rows[1]['bytes']==300000
(P/'read-diagnostic.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Exact successful read bytes match; diagnostic allocations only.')
