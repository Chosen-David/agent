"""Frozen full-entry baseline/candidate pairs; current module binding is outside timing."""
import importlib.util
import json
import os
from pathlib import Path
import random
import statistics
import sys
import tempfile
import time
import tracemalloc

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import discovery_fixture as f
import agent_runtime.handoff_basis as candidate

spec = importlib.util.spec_from_file_location('agent_runtime._impact14_baseline', HERE/'baseline.py')
baseline = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = baseline
spec.loader.exec_module(baseline)
KEY = 'agent_runtime.handoff_basis'
CASES = f.CASES + [('artifact-small8',8,'chain','artifact'),
                    ('artifact-shared256',256,'shared','artifact'),
                    ('artifact-dense128',128,'dense','artifact'),
                    ('artifact-mixed512',512,'mixed','artifact')]


def call(module, box):
    saved = sys.modules[KEY]
    sys.modules[KEY] = module
    try:
        return box.impact()
    finally:
        sys.modules[KEY] = saved


def legacy(graph, bad):
    while True:
        expanded = bad | {cid for cid,c in graph.items() if set(c['depends_on']) & bad}
        if expanded == bad:
            return bad
        bad = expanded


def correctness():
    rng = random.Random(14)
    for k in range(250):
        n = [0,1,8,63,64,65,128][k%7]
        graph = {str(i): {'depends_on':[str(j) for j in range(i) if rng.random()<.07]}
                 for i in range(n)}
        seeds = {str(i) for i in range(n) if rng.random()<.1}
        before = f.canonical(graph)
        # Independent oracle: ask whether a seed is an ancestor, per node.
        want = set(seeds)
        for cid in graph:
            pending, seen = [cid], set()
            while pending:
                node = pending.pop()
                if node in seeds:
                    want.add(cid); break
                if node not in seen:
                    seen.add(node); pending.extend(graph[node]['depends_on'])
        got = candidate._claim_descendants(graph,seeds)
        if got != want or f.canonical(graph)!=before:
            raise RuntimeError('independent ancestor oracle failed')
        if got != legacy(graph,seeds):
            raise RuntimeError('legacy closure differential failed')
    return 250


def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True)
    args=p.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    report=dict(base='01c60f5ac39d1a57085b90efec3788878ef33e3b',
                source_hashes={str(x.relative_to(f.ROOT)): f.digest(x.read_bytes()) for x in
                    [f.ROOT/'agent_runtime/handoff_basis.py',f.ROOT/'agent_runtime/communication.py']},
                baseline_sha256=f.digest((HERE/'baseline.py').read_bytes()),
                harness_sha256=f.digest(Path(__file__).read_bytes()),
                fixture_sha256=f.digest((HERE/'discovery_fixture.py').read_bytes()),
                plan_sha256=f.digest((HERE/'plan-v2.md').read_bytes()),
                environment=dict(python=sys.version,platform=f.platform.platform(),
                    sqlite=f.sqlite3.sqlite_version,cpu_count=os.cpu_count(),hashseed=os.environ.get('PYTHONHASHSEED'),
                    sharing='shared CPU, no affinity/lockfreq/GPU/model'),
                correctness=correctness(),warmups=3,repeats=21,cases=[])
    for name,n,shape,mutation in CASES:
        with tempfile.TemporaryDirectory(prefix='impact14-') as temp:
            box,record,request=f.fixture(Path(temp),n,shape,mutation)
            before=f.snapshot(box)
            input_record=dict(n=n,shape=shape,mutation=mutation,record=record,request=request)
            entry=dict(name=name,input=input_record,input_sha256=f.digest(f.canonical(input_record).encode()),
                       samples=[],before=before)
            for _ in range(3):
                if call(baseline,box)!=call(candidate,box):
                    raise RuntimeError('warmup differential failed')
            for pair in range(21):
                values={}; times={}
                order=[('baseline',baseline),('candidate',candidate)]
                if pair%2: order.reverse()
                for actor,module in order:
                    # Bind outside clock, restore even if actual API raises.
                    saved=sys.modules[KEY];sys.modules[KEY]=module
                    try:
                        start=time.perf_counter_ns(); values[actor]=box.impact()
                        times[actor]=time.perf_counter_ns()-start
                    finally:sys.modules[KEY]=saved
                if values['baseline']!=values['candidate']:
                    raise RuntimeError('full-entry differential failed')
                expected_n=n//2 if shape=='mixed' else n
                if shape=='mixed':
                    row=values['candidate'][0]
                    if row['claim_ids']!=[f'c{i:04}' for i in range(expected_n)]:
                        raise RuntimeError('unaffected candidate branch included')
                else:f.oracle(values['candidate'],n,mutation)
                if min(times.values())<=0:raise RuntimeError('nonpositive clock')
                entry['samples'].append(times)
            med={a:statistics.median(v[a] for v in entry['samples']) for a in ('baseline','candidate')}
            entry['median_ns']=med
            entry['reduction']=1-med['candidate']/med['baseline']
            threshold=.25 if name=='artifact-chain512' else .15 if name=='artifact-shared256' else -.15
            entry['threshold']=threshold;entry['gate']=entry['reduction']>=threshold
            if name in ('artifact-chain512','artifact-shared256'):
                entry['tracemalloc_peak_bytes']={}
                for actor,module in [('baseline',baseline),('candidate',candidate)]:
                    tracemalloc.start();call(module,box)
                    entry['tracemalloc_peak_bytes'][actor]=tracemalloc.get_traced_memory()[1]
                    tracemalloc.stop()
            entry['after']=f.snapshot(box)
            if before!=entry['after']:raise RuntimeError('state changed')
            report['cases'].append(entry)
    report['all_gates']=all(x['gate'] for x in report['cases'])
    (args.out/'raw.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([dict(name=c['name'],reduction=c['reduction'],gate=c['gate']) for c in report['cases']]))

if __name__=='__main__':main()
