"""Fixed-reference, whole file-backed search; loaded-store latency only."""
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime import knowledge

BASE = '33ff30a0e068c4ad6e17cb6bf18a79b041fdef11'
QUERIES = ('!!!', '🙂', 'Ω', 'memory retrieval', 'low rank', '量纲',
           'topk', 'zzqxnonexistent', 'ＡＢＣ')


def digest(value):
    return hashlib.sha256(value).hexdigest()


def run():
    source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/knowledge.py'], cwd=ROOT)
    old = types.ModuleType('agent_runtime._empty_baseline')
    old.__package__ = 'agent_runtime'
    exec(compile(source, BASE, 'exec'), old.__dict__)
    store = knowledge.KnowledgeStore(ROOT / 'knowledge')
    metadata = dict(baseline=BASE, baseline_source=digest(source),
                    candidate_source=digest(Path(knowledge.__file__).read_bytes()),
                    input_hash=digest(json.dumps(store.records, sort_keys=True).encode()),
                    snapshot=store.snapshot, records=len(store.records),
                    python=sys.version, platform=platform.platform(),
                    clock='perf_counter_ns', unit='ms', load_included=False)
    print(json.dumps({'metadata': metadata}), flush=True)
    for query in QUERIES:
        expected = old.KnowledgeStore.search(store, query)
        samples = []
        for pair in range(-1, 7):
            order = ('baseline', 'candidate') if pair % 2 == 0 else ('candidate', 'baseline')
            elapsed = {}
            for label in order:
                method = old.KnowledgeStore.search if label == 'baseline' else knowledge.KnowledgeStore.search
                start = time.perf_counter_ns()
                outputs = [method(store, query) for _ in range(5)]
                elapsed[label] = (time.perf_counter_ns() - start) / 5e6
                assert all(output == expected for output in outputs), (query, label)
            if pair >= 0:
                samples.append(dict(pair=pair, order=order, **elapsed))
        med = {label: statistics.median(s[label] for s in samples) for label in order}
        threshold = med['baseline'] * .5 if query in QUERIES[:3] else max(med['baseline'] * 1.15, med['baseline'] + .5)
        print(json.dumps(dict(query=query, samples_ms=samples, median_ms=med,
                              output_hash=digest(json.dumps(expected, sort_keys=True).encode()),
                              parity=True, reduction=1-med['candidate']/med['baseline'],
                              threshold_ms=threshold, passed=med['candidate'] <= threshold)), flush=True)


if __name__ == '__main__':
    run()
