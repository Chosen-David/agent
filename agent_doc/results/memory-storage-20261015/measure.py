"""Paired full-entry SQLite retrieval benchmark; synthetic, no LLM/KV claims."""
import hashlib
import json
from pathlib import Path
import platform
import random
import sqlite3
import statistics
import sys
import tempfile
import time

from agent_runtime.project_memory import MemoryLedger


def baseline(ledger, status='active', scope=None):
    with ledger._connect() as db:
        ids = db.execute('SELECT id FROM entries ORDER BY created_at,id').fetchall()
        values = [ledger._get(db, r[0]) for r in ids]
        return [v for v in values if (status == 'all' or v['status'] == status)
                and (scope is None or scope in v['scope'])]


def run(repeats=21):
    rng = random.Random(1510)
    results = []
    cases = [('small', 8, 8, 128), ('all-active', 400, 400, 128),
             ('history-small', 2000, 20, 128), ('history-large', 2000, 20, 8192)]
    for name, count, active, width in cases:
        with tempfile.TemporaryDirectory() as directory:
            ledger = MemoryLedger(directory, create=True)
            with ledger._connect(write=True) as db:
                for i in range(count):
                    db.execute('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',
                               (f'm{i:05}', 'claim', 'x' * width, 'synthetic fixture',
                                '["T1"]', 'verified', 'active' if i < active else 'stale',
                                '2026-10-15'))
            digest = hashlib.sha256(ledger.path.read_bytes()).hexdigest()
            expected = baseline(ledger)
            if ledger.list() != expected:
                raise ValueError('full packet mismatch')
            # Warm both paths before alternating order on identical DB bytes.
            baseline(ledger); ledger.list()
            samples = {'before_ms': [], 'after_ms': []}
            for _ in range(repeats):
                order = [('before_ms', lambda: baseline(ledger)), ('after_ms', ledger.list)]
                rng.shuffle(order)
                for label, fn in order:
                    start = time.perf_counter_ns()
                    value = fn()
                    elapsed = (time.perf_counter_ns() - start) / 1e6
                    if value != expected:
                        raise ValueError('measured packet mismatch')
                    samples[label].append(elapsed)
            if hashlib.sha256(ledger.path.read_bytes()).hexdigest() != digest:
                raise ValueError('benchmark mutated database')
            med = {k: statistics.median(v) for k, v in samples.items()}
            results.append(dict(case=name, entries=count, active=active, content_bytes=width,
                                database_sha256=digest, samples=samples, median=med,
                                reduction=1-med['after_ms']/med['before_ms']))
    return {'scope': 'full MemoryLedger.list(), warm local SQLite, synthetic fixtures',
            'environment': {'python':sys.version, 'platform':platform.platform(),
                            'sqlite':sqlite3.sqlite_version}, 'seed':1510, 'repeats':repeats,
            'cases':results}


if __name__ == '__main__':
    result = run()
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps([{k:v for k,v in c.items() if k != 'samples'} for c in result['cases']], indent=2))
