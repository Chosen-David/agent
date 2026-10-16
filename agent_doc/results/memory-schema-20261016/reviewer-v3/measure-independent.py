import gc
import hashlib
import json
import platform
from pathlib import Path
import random
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
import types

from agent_runtime.project_memory import MemoryLedger

RUN = Path('.agent-runs/memory-schema-20261016/reviewer-v3')
plan = json.loads((RUN.parent / 'plan.json').read_text())
source = subprocess.check_output(['git', 'show', plan['baseline'] + ':agent_runtime/project_memory.py'])
(RUN / 'baseline.py').write_bytes(source)
baseline = types.ModuleType('agent_runtime._schema_baseline')
baseline.__package__ = 'agent_runtime'
exec(compile(source, str(RUN / 'baseline.py'), 'exec'), baseline.__dict__)
rng = random.Random(plan['timing']['seed'])
result = dict(plan=plan, baseline_source_sha256=hashlib.sha256(source).hexdigest(),
              candidate_source_sha256=hashlib.sha256(Path('agent_runtime/project_memory.py').read_bytes()).hexdigest(),
              environment=dict(python=sys.version, platform=platform.platform(), sqlite=sqlite3.sqlite_version), cases=[])
with tempfile.TemporaryDirectory() as tmp:
    for fixture in plan['fixtures']:
        root = Path(tmp) / fixture['id']; root.mkdir()
        ledger = MemoryLedger(root, create=True)
        rows, edges = [], []
        for i in range(fixture['nodes']):
            name = f'n{i:04d}'
            rows.append((name, 'claim', 'x' * fixture['content_bytes'], 'synthetic', '[]', 'verified', 'active', '2026-10-16'))
            if fixture['shape'] == 'chain' and i:
                edges.append((name, f'n{i-1:04d}'))
            if fixture['shape'] == '64 parents + leaf' and i == fixture['nodes'] - 1:
                edges += [(name, f'n{j:04d}') for j in range(i)]
        with ledger._connect(write=True) as db:
            db.executemany('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)', rows)
            db.executemany('INSERT INTO dependencies VALUES(?,?)', edges)
            if not fixture['document_table']:
                db.execute('DROP TABLE document_dependencies')
        refs = ([r[0] for r in reversed(rows)] if fixture['roots'].startswith('all') else [rows[-1][0]])
        before = baseline.MemoryLedger(root)
        expected = before.check(refs)
        assert ledger.check(refs) == expected
        db_hash = hashlib.sha256(ledger.path.read_bytes()).hexdigest()
        for _ in range(plan['timing']['warmup_per_arm']):
            before.check(refs); ledger.check(refs)
        samples = {'before': [], 'after': []}; order = []
        for _ in range(plan['timing']['pairs']):
            arms = ['before', 'after']; rng.shuffle(arms); order.append(arms)
            for arm in arms:
                op = before if arm == 'before' else ledger
                gc.collect()
                start = time.perf_counter_ns()
                for _ in range(plan['timing']['batch_per_sample']):
                    actual = op.check(refs)
                elapsed = time.perf_counter_ns() - start
                samples[arm].append(elapsed / plan['timing']['batch_per_sample'])
                assert actual == expected
        assert hashlib.sha256(ledger.path.read_bytes()).hexdigest() == db_hash
        reduction = 1 - statistics.median(samples['after']) / statistics.median(samples['before'])
        result['cases'].append(dict(fixture=fixture, refs=refs, input_sha256=hashlib.sha256(
            json.dumps([rows, edges, refs], separators=(',', ':')).encode()).hexdigest(),
            sqlite_sha256=db_hash, samples_ns_per_complete_check=samples, order=order,
            reduction=reduction, outputs_equal=True, database_unchanged=True))
result['performance_gate'] = (all(x['reduction'] >= .10 for x in result['cases'][:2])
                              and all(x['reduction'] >= -.15 for x in result['cases'][2:]))
(RUN / 'measurement-primary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'gate': result['performance_gate'], 'reductions': {
    x['fixture']['id']: x['reduction'] for x in result['cases']}}))
