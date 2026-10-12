"""Compare actual git baseline and candidate public validate; synthetic CPU only."""
import copy
import hashlib
import itertools
import json
import statistics
import subprocess
import sys
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.core import validate

source = subprocess.check_output(['git','show','6886c3ff3f4c5238d733d9da9ac349933f3020de:agent_runtime/core.py'],cwd=ROOT)
module = types.ModuleType('agent_runtime._baseline_core')
module.__package__ = 'agent_runtime'
sys.modules[module.__name__] = module
exec(compile(source,'baseline-core.py','exec'), module.__dict__)

def plan(n, dense=False):
    tasks = []
    for i in range(n):
        deps = [f't{j}' for j in range(0 if dense else max(0,i-32),i)]
        tasks.append(dict(task_id=f't{i}',depends_on=deps,action='synthetic',owner='probe',
                          done_when='independent verification',max_attempts=2,
                          estimated_seconds=1,risk='low'))
    return dict(schema_version='task-dag/v1',run_id='probe',user_goal='bounded validation',
                authorization_reference='synthetic input only',tasks=tasks,
                supervision=dict(min_seconds=1,max_seconds=60,rationale='bounded'))

def outcome(fn, p):
    try:
        fn(p)
        return ['success']
    except Exception as exc:
        return [type(exc).__name__,str(exc)]

cases = []
class OddHash(str):
    def __hash__(self):
        return 0
class PlainStr(str):
    pass
class RaisingEqual(str):
    __hash__ = str.__hash__
    def __eq__(self, other):
        raise RuntimeError('custom equality')
for bits in itertools.product([0,1],repeat=9):
    p=plan(3)
    for i in range(3):
        p['tasks'][i]['depends_on']=[f't{j}' for j in range(3) if bits[i*3+j]]
    cases.append(p)
for dependency in [[],{},None,False,1,1.5,'missing','', ['t0'], {'id':'t0'}]:
    p=plan(2); p['tasks'][1]['depends_on']=[dependency]; cases.append(p)
for ids in [['中文','Ω'],['','x'],['a','a'],[None,'a'],[[],'b']]:
    p=plan(2)
    for t,ident in zip(p['tasks'],ids): t['task_id']=ident; t['depends_on']=[]
    cases.append(p)
for identifier,dep in [(OddHash('t0'),'t0'),(PlainStr('t0'),'t0'),('t0',OddHash('t0'))]:
    p=plan(2); p['tasks'][0]['task_id']=identifier; p['tasks'][1]['depends_on']=[dep]
    cases.append(p)
p=plan(2); p['tasks'][0]['task_id']=RaisingEqual('t0'); cases.append(p)
p=plan(2); p['tasks'][1]['depends_on']='t0'; del p['tasks'][1]['risk']; cases.append(p)
p=plan(2); p['tasks'][1]['task_id']='t0'; del p['tasks'][1]['risk']; cases.append(p)
for field in ['action','owner','done_when','max_attempts','estimated_seconds','risk']:
    p=plan(1); del p['tasks'][0][field]; cases.append(p)
p=plan(2); p['tasks'][1]['depends_on']=['t0','t0']; cases.append(p)
p=plan(3); p['tasks'].reverse(); cases.append(p)
checks=[]
for i,p in enumerate(cases):
    before=copy.deepcopy(p)
    b,c=outcome(module.validate,p),outcome(validate,p)
    if b!=c or repr(p)!=repr(before): raise RuntimeError(f'differential case {i}: {b}, {c}')
    checks.append(b)

raw={}
for name,n,dense,repeats in [('small',1,False,1000),('sparse',512,False,1),('dense',1000,True,1)]:
    p=plan(n,dense)
    for fn in [module.validate,validate]:
        for _ in range(2): fn(p)
    pairs=[]
    for r in range(7):
        pair={}
        for label,fn in ([('baseline',module.validate),('candidate',validate)] if r%2==0
                         else [('candidate',validate),('baseline',module.validate)]):
            start=time.perf_counter_ns()
            for _ in range(repeats): fn(p)
            pair[label]=(time.perf_counter_ns()-start)/repeats/1e6
        pairs.append(pair)
    b=statistics.median(x['baseline'] for x in pairs)
    c=statistics.median(x['candidate'] for x in pairs)
    raw[name]=dict(pairs_ms=pairs,baseline_ms=b,candidate_ms=c,reduction=1-c/b,
                   input_sha256=hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest())

print(json.dumps(dict(baseline_sha256=hashlib.sha256(source).hexdigest(),
                      candidate_sha256=hashlib.sha256((ROOT/'agent_runtime/core.py').read_bytes()).hexdigest(),
                      differential_checks=len(checks),result_digest=hashlib.sha256(json.dumps(checks).encode()).hexdigest(),
                      python=sys.version,raw=raw),indent=2))
