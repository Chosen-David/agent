import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import random
import statistics
import sys
import time
import tracemalloc
from graphlib import TopologicalSorter, CycleError

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime.handoff_basis import claim_graph

spec = importlib.util.spec_from_file_location('agent_runtime.claim12_baseline', RUN / 'baseline.py')
baseline = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = baseline
spec.loader.exec_module(baseline)


def record_for(parents, statuses=None):
    names = list(parents)
    return {'artifacts': [{'id': 'proof'}], 'evidence_claims': [
        dict(id=cid, status=(statuses or {}).get(cid, 'supported'),
             knowledge_ids=[], memory_ids=[], artifact_ids=['proof'],
             depends_on=list(parents[cid]), assumptions=[])
        for cid in names]}


def chain(n):
    return record_for({f'c{i}': ([f'c{i-1}'] if i else []) for i in range(n)})


def fixtures():
    return {
        'chain512': chain(512),
        'shared256': record_for({f'c{i}': [f'c{j}' for j in range(max(0,(i//4-1)*4),i//4*4)]
                                 for i in range(256)}),
        'small8': chain(8), 'empty': record_for({}),
        'star512': record_for({f'c{i}': (['c0'] if i else []) for i in range(512)}),
        'dense256': record_for({f'c{i}': [f'c{j}' for j in range(i)] for i in range(256)})}


def outcome(fn, record):
    try:
        value = fn(record)
        return ('ok', json.dumps(value, sort_keys=True))
    except Exception as exc:
        return (type(exc).__name__, str(exc))


def correctness():
    count = 0
    def compare(r, valid=None):
        nonlocal count
        before = deepcopy(r)
        a, b = outcome(baseline.claim_graph, r), outcome(claim_graph, r)
        assert a == b, (a, b)
        assert r == before
        if valid is not None:
            assert (a[0] == 'ok') == valid, (a, valid)
        if a[0] == 'ok':
            got = claim_graph(r)
            assert list(got) == [c['id'] for c in r['evidence_claims']]
            assert all(got[c['id']] is c for c in r['evidence_claims'])
        count += 1
    for mask in range(512):
        p = {f'c{i}': [f'c{j}' for j in range(3) if mask & (1 << (3*i+j))] for i in range(3)}
        try:
            list(TopologicalSorter(p).static_order()); valid = True
        except CycleError:
            valid = False
        compare(record_for(p), valid)
    rng = random.Random(8012)
    for _ in range(120):
        n = rng.randrange(1, 90)
        p = {f'c{i}': [f'c{j}' for j in range(n) if rng.random() < .025] for i in range(n)}
        compare(record_for(p))
    for n in (0,1,8,64,65,66,67,128,512,1200):
        compare(chain(n), True)
    for r in fixtures().values():
        compare(r, True)
    for kind in ('cycle', 'unknown', 'unsupported', 'cycle-unknown', 'cycle-unsupported'):
        r = chain(100)
        if 'cycle' in kind:
            r['evidence_claims'][-2]['depends_on'] = ['c99']
        if 'unknown' in kind:
            r['evidence_claims'][60]['depends_on'].append('missing')
        if 'unsupported' in kind:
            r['evidence_claims'][60]['status'] = 'candidate'
        compare(r, False)
    for field, value in [('depends_on', ['c1','c1']), ('depends_on', None), ('status','bad'),
                         ('assumptions',None), ('id',[]), ('memory_ids',[[]])]:
        r = chain(100); r['evidence_claims'][40][field] = value
        compare(r, False)
    return count


def measure(fn, record, batch):
    start = time.perf_counter_ns()
    for _ in range(batch):
        fn(record)
    return (time.perf_counter_ns() - start) / batch / 1e6


def benchmark():
    result = {}
    batches = {'chain512':1,'shared256':1,'small8':100,'empty':1000,'star512':1,'dense256':1}
    for name, r in fixtures().items():
        batch = batches[name]
        before = json.dumps(r,sort_keys=True,separators=(',',':'))
        for _ in range(3):
            measure(baseline.claim_graph,r,batch); measure(claim_graph,r,batch)
        samples = []
        for i in range(21):
            pair = {}
            for label,fn in ([('baseline',baseline.claim_graph),('candidate',claim_graph)] if i%2==0 else
                             [('candidate',claim_graph),('baseline',baseline.claim_graph)]):
                pair[label] = measure(fn,r,batch)
            samples.append(pair)
        assert before == json.dumps(r,sort_keys=True,separators=(',',':'))
        med = {label:statistics.median(p[label] for p in samples) for label in ('baseline','candidate')}
        peaks = {}
        for label,fn in [('baseline',baseline.claim_graph),('candidate',claim_graph)]:
            tracemalloc.start(); fn(r); peaks[label] = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
        result[name] = {'input_sha256':hashlib.sha256(before.encode()).hexdigest(),
                        'batch':batch,'samples_ms':samples,'median_ms':med,
                        'reduction_percent':100*(1-med['candidate']/med['baseline']),
                        'python_peak_bytes_single_call':peaks}
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--out',default='producer.json'); p.add_argument('--correctness-only',action='store_true')
    args = p.parse_args()
    data = {'source_sha256':hashlib.sha256((ROOT/'agent_runtime/handoff_basis.py').read_bytes()).hexdigest(),
            'baseline_sha256':hashlib.sha256((RUN/'baseline.py').read_bytes()).hexdigest(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'environment':{'python':sys.version,'platform':platform.platform(),'hashseed':__import__('os').environ.get('PYTHONHASHSEED'),'cpu':platform.processor()},
            'correctness_cases':correctness()}
    if not args.correctness_only:
        data['benchmark'] = benchmark()
    (RUN/args.out).write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k!='benchmark'}))
    if 'benchmark' in data:
        print({k:round(v['reduction_percent'],3) for k,v in data['benchmark'].items()})
