"""Paired MemoryLedger.list benchmark against a pinned Git source, synthetic only."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import random
import re
import sqlite3
import statistics
import subprocess
import tempfile
import time

from agent_runtime.project_memory import MemoryLedger


def benchmark(config):
    revision = config['baseline_revision']
    if not re.fullmatch('[0-9a-f]{40}', revision):
        raise ValueError('baseline must be an exact Git commit')
    root = Path(__file__).resolve().parents[1]
    source = subprocess.check_output(
        ['git', 'show', revision + ':agent_runtime/project_memory.py'], cwd=root)
    before_hash = hashlib.sha256(source).hexdigest()
    if before_hash != config['baseline_source_sha256']:
        raise ValueError('baseline source hash mismatch')
    namespace = {'__name__': 'agent_runtime._memory_benchmark_before',
                 '__package__': 'agent_runtime'}
    exec(compile(source, revision + '/project_memory.py', 'exec'), namespace)
    Before = namespace['MemoryLedger']
    rng = random.Random(config['seed'])
    cases = []
    for case in config['cases']:
        with tempfile.TemporaryDirectory() as directory:
            after = MemoryLedger(directory, create=True)
            before = Before(directory)
            with after._connect(write=True) as db:
                for i in range(case['entries']):
                    db.execute('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',
                               (f'm{i:06}', 'claim', 'x' * case['content_bytes'],
                                'synthetic fixture',
                                '["T1"]' if i % case['match_every'] == 0 else '["T10"]',
                                'verified', 'active' if i < case['active'] else 'stale',
                                '2026-10-16'))
            digest = hashlib.sha256(after.path.read_bytes()).hexdigest()
            kwargs = {'status': 'active', 'scope': case['scope']}
            expected = before.list(**kwargs)
            if after.list(**kwargs) != expected:
                raise ValueError('packet mismatch before timing')
            calls = {'before_ms': lambda: before.list(**kwargs),
                     'after_ms': lambda: after.list(**kwargs)}
            for fn in calls.values():
                fn()
            samples = {key: [] for key in calls}
            orders = []
            for _ in range(config['repeats']):
                order = list(calls)
                rng.shuffle(order)
                orders.append(order)
                for label in order:
                    start = time.perf_counter_ns()
                    value = calls[label]()
                    elapsed = (time.perf_counter_ns() - start) / 1e6
                    if value != expected:
                        raise ValueError('measured packet mismatch')
                    samples[label].append(elapsed)
            if hashlib.sha256(after.path.read_bytes()).hexdigest() != digest:
                raise ValueError('measurement changed database')
            med = {key: statistics.median(values) for key, values in samples.items()}
            cases.append(dict(case, database_sha256=digest, returned=len(expected),
                              samples=samples, orders=orders, median=med,
                              reduction=1 - med['after_ms'] / med['before_ms']))
    return {'scope': 'full list entry, warm local SQLite, synthetic, no model/KV',
            'config': config, 'baseline_source_sha256': before_hash,
            'candidate_source_sha256': hashlib.sha256(
                (root / 'agent_runtime/project_memory.py').read_bytes()).hexdigest(),
            'environment': {'python': platform.python_version(),
                            'compiler': platform.python_compiler(),
                            'platform': platform.platform(), 'sqlite': sqlite3.sqlite_version},
            'cases': cases}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = benchmark(json.loads(args.config.read_text()))
    # A measurement is immutable evidence, never silently replace a previous run.
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps([dict(case=c['name'], median=c['median'], reduction=c['reduction'],
                           returned=c['returned']) for c in result['cases']], indent=2))
