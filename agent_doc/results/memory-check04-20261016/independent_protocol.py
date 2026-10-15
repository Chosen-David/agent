import hashlib
import importlib.util
import json
from pathlib import Path
import random
import subprocess
from unittest.mock import patch
from agent_runtime import project_memory as after

ns={'__name__':'agent_runtime._baseline_protocol','__package__':'agent_runtime'}
exec(subprocess.check_output(['git','show','2d7ddc46b13b24ecc0c3611b1d8dcb63df7e6b10:agent_runtime/project_memory.py']),ns)
Before=ns['MemoryLedger']
traces=[]
for stale in (None,'0','1','2'):
    outcomes=[]
    for cls,is_before in ((Before,True),(after.MemoryLedger,False)):
        trace=[]
        def get(db,ref):
            trace.append(['get',ref])
            return {'id':ref,'status':'active','deps':{'2':['1','0'],'1':['0'],'0':[]}[ref],
                    'document_refs':{'ref':ref}}
        def check(root,ref):
            trace.append(['document',ref['ref']])
            if ref['ref']==stale:
                raise ValueError('injected document stale')
        with patch.object(cls,'_get',staticmethod(get)):
            context=patch.dict(ns,{'check_document_refs':check}) if is_before else patch.object(after,'check_document_refs',check)
            with context:
                try:
                    value=cls._check(None,['2','0'],Path('.'))
                    result=('ok',value)
                except Exception as exc:
                    result=('error',type(exc).__name__,str(exc))
        outcomes.append((result,trace))
    assert outcomes[0]==outcomes[1], outcomes
    traces.append({'failing_document':stale,'trace':outcomes[0][1]})

config=json.loads(Path('.agent-runs/memory-check04-20261016/plan.json').read_text())
raw=json.loads(Path('.agent-runs/memory-check04-20261016/raw-primary.json').read_text())
rng=random.Random(41016)
inputs=[]
for spec,case in zip(config['fixtures'],raw['cases'],strict=True):
    n=spec['nodes']
    ids=[f'm{i:04d}' for i in range(n)]
    rows=[(name,'claim','x'*spec['content_bytes'],'synthetic','[]','verified','active','2026-10-16') for name in ids]
    adjacency={i:[] for i in range(n)}
    if spec['shape']=='chain':
        adjacency.update({i:[i-1] for i in range(1,n)})
    elif spec['id']=='wide':
        adjacency[n-1]=list(range(n-1))
    elif spec['id']=='layered':
        for level in range(1,32):
            for i in range(level*4,(level+1)*4):
                adjacency[i]=list(range((level-1)*4,level*4))
    edges=[(ids[i],ids[j]) for i in range(n) for j in adjacency[i]]
    roots=spec['roots'] if type(spec['roots']) is list else list(range(n-1,-1,-1))
    refs=[ids[i] for i in roots]
    payload=json.dumps({'rows':rows,'edges':edges,'refs':refs},sort_keys=True).encode()
    assert hashlib.sha256(payload).hexdigest()==case['input_sha256']
    for kind,count in [('wall',21),('traced',7)]:
        for pair in case[kind]:
            order=['before','after']
            rng.shuffle(order)
            assert order==pair['order']
    inputs.append({'id':spec['id'],'nodes':n,'edges':len(edges),'roots':len(refs),'input_sha256':case['input_sha256']})
output={'document_order_parity':traces,'independent_fixture_hashes':inputs,'randomized_order_matches_seed':True}
Path('.agent-runs/memory-check04-20261016/reviewer/protocol-checks.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({'document_cases':len(traces),'fixture_hashes':len(inputs),'randomized_order':True}))
