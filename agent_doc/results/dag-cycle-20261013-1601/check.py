"""Public validator differential and paired synthetic CPU benchmark; no models."""
import copy
import graphlib
import hashlib
import itertools
import json
import random
import statistics
import subprocess
import sys
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.core import validate

BASE = '56ccc46d1458dd7df257b68d296616eb34014c58'
source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/core.py'], cwd=ROOT)
module = types.ModuleType('agent_runtime._cycle_baseline')
module.__package__ = 'agent_runtime'
sys.modules[module.__name__] = module
exec(compile(source, 'baseline.py', 'exec'), module.__dict__)


def plan(n, shape='chain'):
    tasks = []
    for i in range(n):
        deps = (range(i) if shape == 'dense' else
                ([0] if i else []) if shape == 'star' else ([i - 1] if i else []))
        tasks.append(dict(task_id=str(i), depends_on=[str(j) for j in deps],
                          action='synthetic', owner='probe', done_when='verified',
                          max_attempts=2, estimated_seconds=1, risk='low'))
    return dict(schema_version='task-dag/v1', run_id='probe', user_goal='validator CPU',
                authorization_reference='bounded synthetic CPU', tasks=tasks,
                supervision=dict(min_seconds=1, max_seconds=60, rationale='bounded'))


def outcome(fn, p):
    try:
        fn(p)
        return ['success']
    except Exception as e:
        return [type(e).__name__, str(e)]


cases = []
for bits in itertools.product([0, 1], repeat=9):
    p = plan(3)
    for i in range(3):
        p['tasks'][i]['depends_on'] = [str(j) for j in range(3) if bits[3*i+j]]
    cases.append(p)
randomizer = random.Random(1601)
for n in [63, 64, 65, 66, 67, 128, 512]:
    for shape in ['chain', 'star']:
        p = plan(n, shape); cases.append(p)
        p = copy.deepcopy(p); p['tasks'].reverse(); cases.append(p)
        p = copy.deepcopy(p); p['tasks'][-1]['depends_on'].append(str(n-1)); cases.append(p)
    for count in [4*n-1, 4*n, 4*n+1]:
        edges = [(i,j) for i in range(n) for j in range(i)]
        randomizer.shuffle(edges)
        p = plan(n)
        for t in p['tasks']: t['depends_on'] = []
        for i,j in edges[:count]: p['tasks'][i]['depends_on'].append(str(j))
        cases.append(p)
    for _ in range(10):
        p = plan(n)
        for i,t in enumerate(p['tasks']):
            t['depends_on'] = [str(j) for j in range(i) if randomizer.random()<min(.1,2/n)]
        cases.append(p)
        p=copy.deepcopy(p); p['tasks'][0]['depends_on']=[str(n-1)]
        p['tasks'][-1]['depends_on'].append('0'); cases.append(p)
for dep in [None, [], {}, False, 1, 'missing', '']:
    p=plan(64); p['tasks'][1]['depends_on']=[dep]; cases.append(p)
for field in ['action','owner','done_when','max_attempts','estimated_seconds','risk']:
    p=plan(64); del p['tasks'][1][field]; cases.append(p)
for n in [64,65,1000]:
    p=plan(n); p['tasks'][1]['depends_on']*=3; cases.append(p)
    p=plan(n); p['tasks'][0]['depends_on']=['0']; cases.append(p)
    p=plan(n); p['supervision']['min_seconds']=0; cases.append(p)
    p=plan(n); p['extra']=float('nan'); cases.append(p)
class OddHash(str):
    def __hash__(self): return 0
class PlainStr(str): pass
for cls in [OddHash, PlainStr]:
    p=plan(64); p['tasks'][0]['task_id']=cls('0'); cases.append(p)
    p=plan(64); p['tasks'][1]['depends_on']=[cls('0')]; cases.append(p)
for n in [66,67,128]:
    # Residual edges still refer to both peeled levels and must not count them.
    p=plan(n)
    for t in p['tasks'][2:]: t['depends_on'] += ['0','1']
    cases.append(p)
    p=copy.deepcopy(p); p['tasks'][2]['depends_on'].append(str(n-1)); cases.append(p)
    for cls in [OddHash,PlainStr]:
        p=plan(n); p['tasks'][0]['task_id']=cls('0'); cases.append(p)
        p=plan(n); p['tasks'][2]['depends_on'].append(cls('0')); cases.append(p)

outcomes=[]; oracle_count=0
for index,p in enumerate(cases):
    before=repr(p)
    b,c=outcome(module.validate,p),outcome(validate,p)
    if b!=c or repr(p)!=before: raise RuntimeError(f'case {index}: {b} != {c} or mutation')
    outcomes.append(c)
    if all(type(t['task_id']) is str and all(type(d) is str for d in t['depends_on'])
           for t in p['tasks']) and c in [['success'],['ValueError','dependency cycle']]:
        try:
            list(graphlib.TopologicalSorter({t['task_id']:t['depends_on'] for t in p['tasks']}).static_order())
            expected=['success']
        except graphlib.CycleError: expected=['ValueError','dependency cycle']
        if c!=expected: raise RuntimeError(f'oracle case {index}')
        oracle_count+=1

raw={}
if '--correctness-only' not in sys.argv:
    for name,n,shape,repeats in [('small',1,'chain',1000),('chain512',512,'chain',1),
                                 ('chain1000',1000,'chain',1),('star512',512,'star',1),
                                 ('dense1000',1000,'dense',1)]:
        p=plan(n,shape)
        for fn in [module.validate,validate]:
            for _ in range(2): fn(p)
        pairs=[]
        for r in range(9):
            pair={}
            ordered=[('baseline',module.validate),('candidate',validate)]
            if r%2: ordered.reverse()
            for label,fn in ordered:
                start=time.perf_counter_ns()
                for _ in range(repeats): fn(p)
                pair[label]=(time.perf_counter_ns()-start)/repeats/1e6
            pairs.append(pair)
        b=statistics.median(x['baseline'] for x in pairs)
        c=statistics.median(x['candidate'] for x in pairs)
        reduction=1-c/b
        raw[name]=dict(pairs_ms=pairs,baseline_ms=b,candidate_ms=c,reduction=reduction,
                       gate_pass=reduction>=.2 if name.startswith('chain') else reduction>=-.1,
                       input_sha256=hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest())
print(json.dumps(dict(baseline_commit=BASE,baseline_sha256=hashlib.sha256(source).hexdigest(),
                     candidate_sha256=hashlib.sha256((ROOT/'agent_runtime/core.py').read_bytes()).hexdigest(),
                     checks=len(cases),oracle_checks=oracle_count,
                     outcomes_sha256=hashlib.sha256(json.dumps(outcomes).encode()).hexdigest(),
                     python=sys.version,raw=raw),indent=2))
