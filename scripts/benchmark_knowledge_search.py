"""Fixed-baseline whole indexed_search pairs; no model or quality-gain claim."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime import knowledge_index as candidate
from scripts.benchmark_knowledge_index import corpus, digest, snapshot

BASE = 'de05d95c725029cca53239f0eb6e0f63d4fb9c19'
QUERIES = ['memory retrieval', 'low rank', '量纲', 'topk', 'zzqxnonexistent', '!!!']


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def baseline():
    source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/knowledge_index.py'], cwd=ROOT)
    module = types.ModuleType('agent_runtime._search_baseline')
    module.__package__ = 'agent_runtime'
    exec(compile(source, BASE, 'exec'), module.__dict__)
    return module, hashlib.sha256(source).hexdigest()


def fixture(count, words):
    if count is None:
        return corpus(0)
    store = corpus(8)
    for i, d in enumerate(store.records.values()):
        chunks = []
        for j in range(count):
            tokens = (['memory', 'retrieval'], ['memory'], ['unrelated'])[j % 3]
            body = tokens + [f'padding{i}'] * (words - len(tokens))
            chunks.append(f'# Section {j}\n' + ' '.join(body) + '\n')
        d.update(title=f'Fixture {i}', aliases=['zqxalias'], content=''.join(chunks))
        d['sha256'] = digest({k: v for k, v in d.items() if k != 'sha256'})
    return snapshot(store)


def paired(store, query, count, words, repeats=7, inner=5, **options):
    old, base_hash = baseline()
    samples = []
    with tempfile.TemporaryDirectory(prefix='search-pair-') as tmp:
        db = Path(tmp) / 'seed.db'
        old.build_index(store, db)
        seed_hash = file_hash(db)
        expected = old.indexed_search(store, db, query, **options)
        for pair in range(-1, repeats):
            order = ['baseline', 'candidate'] if pair % 2 == 0 else ['candidate', 'baseline']
            elapsed = {}
            for label in order:
                module = old if label == 'baseline' else candidate
                start = time.perf_counter_ns()
                outputs = [module.indexed_search(store, db, query, **options) for _ in range(inner)]
                elapsed[label] = (time.perf_counter_ns() - start) / (1e6 * inner)
                if not all(output == expected for output in outputs):
                    raise AssertionError((count, words, query, label, 'output mismatch'))
                if not math.isfinite(elapsed[label]) or elapsed[label] <= 0:
                    raise AssertionError('invalid timing')
            if pair >= 0:
                samples.append(dict(pair=pair, order=order, **elapsed))
        if file_hash(db) != seed_hash:
            raise AssertionError('read-only search changed database')
    med = {key: statistics.median(s[key] for s in samples) for key in ('baseline', 'candidate')}
    required = count in (1, 2) and words == 512
    threshold = med['baseline'] * .85 if required else max(med['baseline'] * 1.15, med['baseline'] + .5)
    return dict(config=dict(sections=count, words=words, query=query, options=options,
                            records=len(store.records), repeats=repeats, inner=inner,
                            input_sha256=digest(store.records), seed_sha256=seed_hash,
                            baseline_sha256=base_hash, candidate_sha256=file_hash(candidate.__file__)),
                samples_ms=samples, median_ms=med,
                range_ms={k: [min(s[k] for s in samples), max(s[k] for s in samples)] for k in med},
                output_sha256=digest(expected), results=len(expected['results']), parity=True,
                reduction=1-med['candidate']/med['baseline'], threshold_ms=threshold,
                performance_pass=med['candidate'] <= threshold)


def boundary_checks():
    old, _ = baseline()
    checked = []
    for count in (0, 1, 2, 16):
        store = fixture(count, 16)
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'search.db'
            old.build_index(store, db)
            for query in ('zqxalias', 'memory retrieval', 'zzqxnonexistent', '!!!'):
                for options in ({'limit': 1}, {'limit': 20}, {'domain': 'test'},
                                {'domain': 'missing'}, {'structure': 'index'}, {'structure': 'missing'}):
                    a = old.indexed_search(store, db, query, **options)
                    b = candidate.indexed_search(store, db, query, **options)
                    if a != b:
                        raise AssertionError((count, query, options))
                    checked.append(dict(sections=count, query=query, options=options, output_sha256=digest(a)))
    return dict(boundaries=checked, parity=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sections', nargs='+', type=int, default=[1, 2, 16, 256])
    parser.add_argument('--words', nargs='+', type=int, default=[16, 512])
    parser.add_argument('--repeats', type=int, default=7)
    parser.add_argument('--inner', type=int, default=5)
    args = parser.parse_args()
    if os.environ.get('PYTHONHASHSEED') != '0':
        parser.error('run with PYTHONHASHSEED=0')
    if args.repeats < 1 or args.inner < 1 or min(args.sections) < 1 or min(args.words) < 2:
        parser.error('positive repeat/inner/sections; words >=2 required')
    dependencies = ['agent_runtime/knowledge.py', 'agent_runtime/project_docs.py',
                    'scripts/benchmark_knowledge_index.py', 'scripts/benchmark_knowledge_search.py',
                    'agent_doc/results/fts-section22-20261019/validation-plan.json']
    print(json.dumps(dict(environment=dict(python=sys.version, sqlite=sqlite3.sqlite_version,
                         platform=platform.platform(), cpu_count=os.cpu_count(),
                         cpu_info=Path('/proc/cpuinfo').read_text().split('\n\n')[0],
                         hashseed=os.environ['PYTHONHASHSEED']),
                          dependencies={p: file_hash(ROOT/p) for p in dependencies},
                          baseline_commit=BASE,
                          protocol='whole indexed_search wall ms/call; one warm pair; seven alternating pairs; ratio medians')), flush=True)
    print(json.dumps(boundary_checks()), flush=True)
    real = fixture(None, None)
    for query in QUERIES:
        print(json.dumps(paired(real, query, None, None, args.repeats, args.inner, limit=5)), flush=True)
    for count in args.sections:
        for words in args.words:
            print(json.dumps(paired(fixture(count, words), 'memory retrieval', count, words,
                                    args.repeats, args.inner, limit=5)), flush=True)


if __name__ == '__main__':
    main()
