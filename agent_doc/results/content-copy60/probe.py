"""Frozen isolated-module feasibility probe; never edits runtime sources."""
import copy
import hashlib
import json
import platform
from pathlib import Path
import statistics
import subprocess
import sys
import time
import tracemalloc
import types

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
SOURCE = ROOT / 'agent_runtime/knowledge.py'
BASE = '4bdb071f5dc9b83c36cdc1b36df5a28a1a1f7823'
BASE_BYTES = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/knowledge.py'], cwd=ROOT)
OLD = '        out = json.loads(json.dumps(d))'
NEW = r'''        body = d.get('content') if type(d) is dict else None
        if (type(d) is dict and type(body) is str
                and all(type(k) is str and k.isascii() for k in d)
                and not re.search(r'[\ud800-\udfff]', body)):
            metadata = json.loads(json.dumps({k: v for k, v in d.items() if k != 'content'}))
            out = {k: body if k == 'content' else metadata[k] for k in d}
        else:
            out = json.loads(json.dumps(d))'''

def load(candidate):
    source = BASE_BYTES.decode().replace('\r\n', '\n')
    assert source.count(OLD) == 1
    module = types.ModuleType('probe_candidate' if candidate else 'probe_baseline')
    module.__file__ = str(SOURCE)
    module.__package__ = 'agent_runtime'
    exec(compile(source.replace(OLD, NEW) if candidate else source, str(SOURCE), 'exec'), module.__dict__)
    return module.KnowledgeStore

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

def main():
    output = Path(__file__).with_name('replay-raw.json')
    if output.exists():
        raise FileExistsError('preserve existing replay evidence: ' + str(output))
    baseline, candidate = [cls(ROOT / 'knowledge') for cls in (load(False), load(True))]
    checks = 0
    for kid in baseline.records:
        a, b = [s.get(kid, include_unpublished=True) for s in (baseline, candidate)]
        assert a == b and list(a) == list(b)
        checks += 1
    kid = next(iter(baseline.records))
    original = copy.deepcopy(baseline.records[kid])
    class Text(str):
        pass
    variants = ['', '中文😀', '\ud800', '\ud83d\ude00', Text('custom')]
    for body in variants:
        for position in (0, 3, len(original)):
            pairs = [(k,v) for k,v in original.items() if k != 'content']
            pairs.insert(position, ('content',body))
            for store in (baseline,candidate):
                store.records[kid] = copy.deepcopy(dict(pairs))
                store.records[kid]['extra'] = {'nested': (1,2), 4: [3]}
            a,b = [s.get(kid, include_unpublished=True) for s in (baseline,candidate)]
            assert a == b and list(a) == list(b)
            b['extra']['4'].append(9)
            assert candidate.records[kid]['extra'][4] == [3]
            checks += 1
    for mode in ('object','cycle','numeric-key'):
        results = []
        for store in (baseline,candidate):
            store.records[kid] = copy.deepcopy(original)
            if mode == 'object': store.records[kid]['extra'] = object()
            if mode == 'cycle': store.records[kid]['extra'] = store.records[kid]
            if mode == 'numeric-key': store.records[kid][1] = 'numeric'
            try:
                result = store.get(kid, include_unpublished=True)
                results.append((result,list(result)))
            except Exception as exc:
                results.append((type(exc).__name__,str(exc)))
        assert results[0] == results[1]
        checks += 1
    for store in (baseline,candidate):
        store.records[kid] = copy.deepcopy(original)
        native = store.get
        calls = []
        def hook(key):
            calls.append(key)
            return native(key)
        store.get = hook
        store._metadata(kid)
        assert calls == [kid]
        del store.get
        checks += 1
    rows = []
    started = time.perf_counter()
    for query in ('matrix','probability','attention','optimization'):
        for limit in (1,5):
            search = baseline.search(query,limit=limit)
            for related in (False,True):
                def call(store):
                    return store.context(search,include_related=related,max_entries=8,max_chars=20000)
                outputs = [call(s) for s in (baseline,candidate)]
                assert outputs[0] == outputs[1]
                for _ in range(2):
                    for s in (baseline,candidate): call(s)
                samples = [[],[]]
                for pair in range(11):
                    for i in ((0,1) if pair%2 == 0 else (1,0)):
                        start = time.perf_counter_ns()
                        for _ in range(10): call((baseline,candidate)[i])
                        samples[i].append((time.perf_counter_ns()-start)/10)
                peaks = []
                for s in (baseline,candidate):
                    tracemalloc.start()
                    call(s)
                    peaks.append(tracemalloc.get_traced_memory()[1])
                    tracemalloc.stop()
                ratio = statistics.median(samples[1])/statistics.median(samples[0])
                rows.append(dict(query=query,limit=limit,related=related,samples_ns=samples,peaks=peaks,ratio=ratio,output_hash=digest(outputs[0]),input_hash=digest(search)))
                assert time.perf_counter()-started < 180
    primary = next(r for r in rows if (r['query'],r['limit'],r['related']) == ('matrix',5,True))
    accepted = primary['ratio'] <= .9 and all(r['ratio'] <= 1.1 and r['peaks'][1] <= 1.1*r['peaks'][0] for r in rows)
    report = dict(base=BASE,source_sha256=hashlib.sha256(BASE_BYTES).hexdigest(),plan_sha256=hashlib.sha256(Path(__file__).with_name('plan.md').read_bytes()).hexdigest(),python=sys.version,platform=platform.platform(),snapshot=baseline.snapshot,checks=checks,rows=rows,accepted=accepted,candidate=NEW)
    with output.open('x') as stream:
        stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checks':checks,'accepted':accepted,'primary_ratio':primary['ratio'],'ratios':[r['ratio'] for r in rows]}))

if __name__ == '__main__':
    main()
