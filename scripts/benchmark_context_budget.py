"""Exact complete-context and fresh-store comparisons; no LLM quality claim."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime.knowledge import KnowledgeStore
from tests.test_knowledge_context_budget import corpus, hits

BASE = '5b1765cb1e228dff27794ca067171fd2f31c0d3a'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(out):
    if os.environ.get('PYTHONHASHSEED') != '0':
        raise RuntimeError('use PYTHONHASHSEED=0')
    out.mkdir(parents=True, exist_ok=False)
    source = subprocess.check_output(['git', 'show', BASE+':agent_runtime/knowledge.py'], cwd=ROOT)
    ns = {'__name__': 'agent_runtime.budget_baseline', '__package__': 'agent_runtime'}
    exec(compile(source, BASE+':knowledge.py', 'exec'), ns)
    old = ns['KnowledgeStore']
    code_paths = ['agent_runtime/knowledge.py', 'tests/test_knowledge_context_budget.py',
                  'scripts/benchmark_context_budget.py']
    code = {p: sha((ROOT/p).read_bytes()) for p in code_paths}
    inputs = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
              for p in sorted((ROOT/'knowledge').rglob('*')) if p.is_file()}
    plan_hash = sha((ROOT/'agent_doc/task/task_details/CONTEXT-BUDGET-28.md').read_bytes().split(b'## Progress')[0])
    raw = []
    parity = 0

    def journal(row):
        with (out/'progress.jsonl').open('a') as f:
            f.write(json.dumps(row, ensure_ascii=False)+'\n')

    journal({'baseline': BASE, 'code': code, 'inputs': inputs, 'plan_sha256': plan_hash})

    def compare(stores, request, **kwargs):
        nonlocal parity
        a, b = [s.context(request, **kwargs) for s in stores]
        if a != b:
            raise AssertionError((request, kwargs, a, b))
        parity += 1
        journal({'parity_case': parity, 'request': request, 'kwargs': kwargs,
                 'output_sha256': sha(json.dumps(a, sort_keys=True, ensure_ascii=False).encode())})
        return a

    def measure(name, invoke, target=False, memory=False):
        expected = invoke(0)
        samples = []
        for pair in range(-2, 11):
            timing = {}
            order = (0, 1) if pair % 2 == 0 else (1, 0)
            for label in order:
                start = time.perf_counter_ns()
                actual = invoke(label)
                timing[str(label)] = time.perf_counter_ns()-start
                if actual != expected:
                    raise AssertionError((name, label, 'output mismatch'))
            samples.append({'pair': pair, 'order': order, 'ns': timing})
            journal({'case': name, **samples[-1]})
        med = [statistics.median(s['ns'][str(i)] for s in samples if s['pair'] >= 0) for i in (0, 1)]
        gate = med[1] <= (med[0]*.8 if target else max(med[0]*1.1, med[0]+200000))
        row = {'case': name, 'target': target, 'samples': samples, 'median_ns': med,
               'ratio': med[1]/med[0], 'gate': gate,
               'output_sha256': sha(json.dumps(expected, sort_keys=True, ensure_ascii=False).encode())}
        if memory:
            peaks = []
            for label in (0, 1):
                tracemalloc.start()
                actual = invoke(label)
                peaks.append(tracemalloc.get_traced_memory()[1])
                tracemalloc.stop()
                if actual != expected:
                    raise AssertionError('memory output mismatch')
            row['peak_python_bytes'] = peaks
        raw.append(row)
        journal({'completed_case': row})

    with tempfile.TemporaryDirectory() as tmp:
        for count in (20, 21, 100, 300):
            root = Path(tmp)/f'chain{count}'
            corpus(root, count)
            stores = [old(root), KnowledgeStore(root)]
            request = hits(stores[0], f'test.node-{count-1:04d}', 'test.node-0000')
            for entries in (1, 8, 20):
                for chars in (1, 20000, 200000):
                    for related in (False, True):
                        compare(stores, request, max_entries=entries, max_chars=chars, include_related=related)
            measure(f'chain{count}/context', lambda i: stores[i].context(request, max_entries=20,
                    max_chars=200000, include_related=False), target=count in (100,300), memory=True)
            # Full request: reconstruct and validate store, lexical search, pack context.
            def flow(i):
                store = (old, KnowledgeStore)[i](root)
                return store.context(store.search(f'Node {count-1}', limit=1), max_entries=20,
                                     max_chars=200000, include_related=False)
            measure(f'chain{count}/load-search-context', flow)
        for shape in ('chain', 'fanout'):
            root = Path(tmp)/f'boundaries-{shape}'
            corpus(root, 21, shape)
            stores = [old(root), KnowledgeStore(root)]
            for seeds in (('test.node-0020', 'test.node-0000'),
                          ('test.node-0020', 'test.node-0020'),
                          ('test.node-0009', 'test.node-0019', 'test.node-0019')):
                for related in (False, True):
                    compare(stores, hits(stores[0], *seeds), max_entries=20,
                            max_chars=200000, include_related=related)
            request = hits(stores[0], 'test.node-0019')
            full = compare(stores, request, max_entries=20, max_chars=200000, include_related=False)
            for budget in (full['budget']['used_chars'], full['budget']['used_chars']-1):
                compare(stores, request, max_entries=20, max_chars=budget, include_related=False)
        stores = [old(ROOT/'knowledge'), KnowledgeStore(ROOT/'knowledge')]
        errors = []
        bad = [({}, {}), (None, {}), ({'snapshot': 'stale'}, {}),
               (hits(stores[0], 'unknown.id'), {'include_related': False}),
               (hits(stores[0]), {'max_entries': True}),
               (hits(stores[0]), {'max_chars': 0})]
        for kid, record in stores[0].records.items():
            if record['status'] != 'published':
                bad.append((hits(stores[0], kid), {'include_related': False}))
        for request, kwargs in bad:
            observed = []
            for store in stores:
                try:
                    store.context(request, **kwargs)
                except Exception as exc:
                    observed.append((type(exc).__name__, str(exc)))
                else:
                    raise AssertionError('invalid context unexpectedly accepted')
            if observed[0] != observed[1]:
                raise AssertionError(observed)
            errors.append({'request': request, 'kwargs': kwargs, 'exception': observed[0]})
            journal({'error_parity': errors[-1]})
        for kid, record in stores[0].records.items():
            if record['status'] != 'published':
                continue
            for entries in (1, 8, 20):
                for chars in (1, 20000):
                    compare(stores, hits(stores[0], kid), max_entries=entries, max_chars=chars)
        for query in ('matrix', '量纲', 'attention量纲', 'zzqxnonexistent'):
            request = stores[0].search(query)
            measure(f'real/{query}/context', lambda i: stores[i].context(request))
            def real_flow(i):
                store = (old, KnowledgeStore)[i](ROOT/'knowledge')
                return store.context(store.search(query))
            measure(f'real/{query}/load-search-context', real_flow)

    report = {'baseline': BASE, 'baseline_source_sha256': sha(source), 'code': code,
              'inputs': inputs, 'python': sys.version, 'platform': platform.platform(),
              'clock': 'perf_counter_ns', 'host_exclusive': False,
              'cache': 'fresh Python store for flow; OS page cache not flushed; imports excluded',
              'plan_sha256': plan_hash, 'error_parity': errors,
              'parity_cases': parity, 'cases': raw, 'accepted': all(r['gate'] for r in raw)}
    for p, digest in {**code, **inputs}.items():
        if sha((ROOT/p).read_bytes()) != digest:
            raise AssertionError('code/input changed during run')
    (out/'raw.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'accepted': report['accepted'], 'parity_cases': parity,
                      'ratios': {r['case']: r['ratio'] for r in raw}}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    run(parser.parse_args().out)
