"""Bounded context-only candidate experiment; production files remain unchanged."""
import argparse
import gc
import hashlib
import inspect
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import textwrap
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime.knowledge import KnowledgeStore, _require


def candidate():
    context_source = textwrap.dedent(inspect.getsource(KnowledgeStore.context))
    related_source = textwrap.dedent(inspect.getsource(KnowledgeStore.related))
    assert context_source.count('entry = self.get(kid)') == 1
    assert related_source.count('d = self.get(kid)') == 1
    context_source = context_source.replace('entry = self.get(kid)', 'entry = self._metadata(kid)')
    related_source = related_source.replace('d = self.get(kid)', 'd = self._metadata(kid)')
    ns = {'_require': _require, 'json': json}
    source = context_source + '\n' + related_source
    exec(compile(source, '<context-metadata-candidate>', 'exec'), ns)
    class Candidate(KnowledgeStore):
        context = ns['context']
        related = ns['related']

        def _metadata(self, kid):
            # Preserve custom public get hooks rather than bypassing subclasses.
            if getattr(self.get, '__func__', None) is not KnowledgeStore.get:
                return self.get(kid)
            self.ref(kid)
            d = self.records[kid]
            _require(d['status'] == 'published', 'entry is not published: ' + kid)
            closure, pending = set(), [kid]
            while pending:
                key = pending.pop()
                if key in closure:
                    continue
                closure.add(key)
                pending.extend(dep['id'] for dep in self.records[key]['requires'])
            refs = [self.ref(key) for key in sorted(closure)]
            return {'requires': d['requires'], 'relations': d['relations'], 'knowledge_refs': refs}
    source += '\n' + textwrap.dedent(inspect.getsource(Candidate._metadata))
    return Candidate, source


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run(out):
    if os.environ.get('PYTHONHASHSEED') != '0':
        raise RuntimeError('require PYTHONHASHSEED=0')
    out.mkdir(parents=True, exist_ok=False)
    cls, source = candidate()
    paths = [ROOT/'agent_runtime/knowledge.py', Path(__file__).resolve(),
             ROOT/'agent_doc/task/task_details/CONTEXT-METADATA-35.md']
    paths += sorted(p for p in (ROOT/'knowledge').rglob('*') if p.is_file())
    bindings = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in paths}
    def journal(value):
        with (out/'progress.jsonl').open('a') as handle:
            handle.write(json.dumps(value, ensure_ascii=False)+'\n')
            handle.flush()
    environment = dict(python=sys.version, platform=platform.platform(),
        cpu=next((line for line in Path('/proc/cpuinfo').read_text().splitlines()
                  if line.startswith('model name')), 'unknown'),
        affinity=sorted(os.sched_getaffinity(0)), gc_enabled=gc.isenabled(),
        gc_threshold=gc.get_threshold(), clock=vars(time.get_clock_info('perf_counter')),
        command=['PYTHONHASHSEED=0', 'timeout', '120', sys.executable,
                 'scripts/benchmark_context_metadata.py', '--out', str(out)])
    journal({'status': 'incomplete', 'bindings': bindings, 'environment': environment,
             'candidate_source': source})
    stores = [KnowledgeStore(ROOT/'knowledge'), cls(ROOT/'knowledge')]
    rows = []
    for query in ('matrix', '量纲', 'attention量纲', 'zzqxnonexistent'):
        for limit in (5, 20):
            request = stores[0].search(query, limit=limit)
            for mode in ('context', 'fresh'):
                def invoke(i):
                    if mode == 'context':
                        return stores[i].context(request)
                    store = (KnowledgeStore, cls)[i](ROOT/'knowledge')
                    return store.context(store.search(query, limit=limit))
                expected = invoke(0)
                samples = []
                for pair in range(-2, 11):
                    timing = {}
                    order = (0, 1) if pair % 2 == 0 else (1, 0)
                    for label in order:
                        start = time.perf_counter_ns()
                        actual = invoke(label)
                        elapsed = time.perf_counter_ns() - start
                        if actual != expected:
                            raise AssertionError((query, limit, mode, 'parity'))
                        del actual
                        timing[str(label)] = elapsed
                    samples.append({'pair': pair, 'order': order, 'ns': timing})
                    journal({'query': query, 'limit': limit, 'mode': mode, 'sample': samples[-1]})
                med = [statistics.median(s['ns'][str(i)] for s in samples if s['pair'] >= 0)
                       for i in (0, 1)]
                peaks = []
                for label in (0, 1):
                    tracemalloc.start()
                    actual = invoke(label)
                    peaks.append(tracemalloc.get_traced_memory()[1])
                    tracemalloc.stop()
                    if actual != expected:
                        raise AssertionError('memory parity')
                    del actual
                target = (query, limit, mode) == ('matrix', 5, 'context')
                rows.append(dict(query=query, limit=limit, mode=mode, samples=samples,
                    median_ns=med, ratio=med[1]/med[0], peaks=peaks,
                    time_gate=med[1] <= (med[0]*.9 if target else max(med[0]*1.1, med[0]+200000)),
                    memory_gate=peaks[1] <= max(peaks[0]*2, peaks[0]+65536),
                    output_sha256=digest(json.dumps(expected, sort_keys=True, ensure_ascii=False).encode())))
                journal({'completed_case': rows[-1]})
                del expected
    for p, sha in bindings.items():
        if digest((ROOT/p).read_bytes()) != sha:
            raise AssertionError('binding changed: '+p)
    result = dict(bindings=bindings, candidate_source=source, environment=environment,
                  exclusive=False, rows=rows,
                  accepted=all(r['time_gate'] and r['memory_gate'] for r in rows))
    (out/'raw.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    journal({'status': 'complete', 'raw_sha256': digest((out/'raw.json').read_bytes())})
    print(json.dumps({'accepted': result['accepted'], 'cases': len(rows)}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    run(parser.parse_args().out)

