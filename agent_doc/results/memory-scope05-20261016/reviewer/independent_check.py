"""Independent bounded MEM-SCOPE-05 semantics and raw-data verification.

Run from any cwd: PYTHONPATH=REPO python FILE --root REPO --evidence-dir DIR.
Does not time code or modify production data. Printed JSON is generated evidence.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import subprocess
import sys
import tempfile
from unittest.mock import patch


parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--evidence-dir', type=Path, required=True)
args = parser.parse_args()
root = args.root.resolve()
sys.path.insert(0, str(root))
from agent_runtime.project_memory import MemoryLedger as After

BASE = 'ab8a368746233996cb39233036a1631de1d911f2'
BASE_SHA = 'c3f41593b64b09d2af190d9ddcb64bbf784720083f4b718a5bdaf5318109f159'
CAND_SHA = '2f2b7b9c439333438be982a8200d0ed213352c76707d2b07454b113855821e98'
sha = lambda data: hashlib.sha256(data).hexdigest()
source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/project_memory.py'], cwd=root)
assert sha(source) == BASE_SHA
assert sha((root / 'agent_runtime/project_memory.py').read_bytes()) == CAND_SHA
namespace = {'__name__': 'agent_runtime._scope05_independent_before', '__package__': 'agent_runtime'}
exec(compile(source, BASE + '/project_memory.py', 'exec'), namespace)
Before = namespace['MemoryLedger']
counts = Counter()
failures = []
exploratory = []


class Text(str):
    pass


def outcome(call):
    try:
        return ('value', call())
    except Exception as exc:
        # MemoryError classes are separately compiled; compare public class name/message.
        return ('error', type(exc).__name__, str(exc))


def compare(before, after, status='active', scope=None, group='matrix'):
    a = outcome(lambda: before.list(status, scope))
    b = outcome(lambda: after.list(status, scope))
    counts[group] += 1
    if a != b:
        failures.append({'group': group, 'status': repr(status), 'scope': repr(scope),
                         'before': repr(a), 'after': repr(b)})
    return a, b


def fixture(directory, n=4, pattern='mixed', status='active'):
    after = After(directory, create=True)
    for i in range(n):
        scopes = {'mixed': ['T1'] if i % 2 else ['T10'],
                  'all': ['T1'], 'none': ['T10'], 'empty': []}[pattern]
        after.add(f'r{i:03}', 'claim', ('payload-' + str(i)) * (i + 1), 'independent',
                  deps=[f'r{i-1:03}'] if i else [], scope=scopes, evidence='verified')
    with after._connect(write=True) as db:
        db.execute('UPDATE entries SET status=?,created_at=?', (status, 'fixed-tie'))
        # Full document packets (not document validation): independently valid JSON.
        if n:
            db.execute('INSERT INTO document_dependencies VALUES(?,?)',
                       ('r000', '{"independent":{"full":[1,2]},"empty":[]}'))
    return Before(directory), after


statuses = ('active', 'candidate', 'stale', 'superseded', 'all', Text('active'), 'invalid', None)
scopes = (None, 'T1', 'T10', 'T', '', 'absent', Text('T1'), 1, True, ['T1'], {'T1': 1}, b'T1')
for n in (0, 1, 4):
    for stored in ('active', 'candidate', 'stale', 'superseded'):
        for pattern in ('mixed', 'all', 'none', 'empty'):
            with tempfile.TemporaryDirectory() as directory:
                before, after = fixture(directory, n, pattern, stored)
                for status in statuses:
                    for scope in scopes:
                        compare(before, after, status, scope, 'valid-field-matrix')
                if n:
                    with after._connect(write=True) as db:
                        db.execute("UPDATE entries SET status='candidate' WHERE id='r000'")
                    for status in statuses[:5]:
                        for scope in scopes:
                            compare(before, after, status, scope, 'mixed-status')

# Single metadata damage only; complete decode must precede membership errors.
payloads = ('null', '7', 'true', '"T10"', '{"T1":1}', '["T1","T10"]',
            'not-json', b'"\xff"', '[' * (sys.getrecursionlimit() + 10) + '0' + ']' * (sys.getrecursionlimit() + 10))
for stored in ('active', 'candidate', 'stale', 'superseded'):
    for field in ('scope', 'document'):
        for payload in payloads:
            with tempfile.TemporaryDirectory() as directory:
                before, after = fixture(directory, status=stored)
                with after._connect(write=True) as db:
                    if field == 'scope':
                        db.execute('UPDATE entries SET scope=? WHERE id=?', (payload, 'r003'))
                    else:
                        db.execute('INSERT INTO document_dependencies VALUES(?,?)', ('r003', payload))
                for status in statuses[:5]:
                    for scope in scopes[:8]:
                        compare(before, after, status, scope, 'isolated-metadata')
                # A retained traceback must not retain a read transaction/lock.
                held = None
                try:
                    after.list(stored, 'T1')
                except Exception as exc:
                    held = exc
                with after._connect(write=True) as db:
                    db.execute('UPDATE entries SET source=source WHERE id=?', ('r000',))
                counts['writer-after-retained-error-or-return'] += 1

for field in ('scope', 'document'):
    with tempfile.TemporaryDirectory() as directory:
        before, after = fixture(directory)
        with after._connect(write=True) as db:
            db.execute("UPDATE entries SET scope='null' WHERE id='r000'")
            if field == 'scope':
                db.execute("UPDATE entries SET scope='bad-json' WHERE id='r003'")
            else:
                db.execute("INSERT INTO document_dependencies VALUES('r003','bad-json')")
        result, _ = compare(before, after, 'active', 'T1', 'decode-before-membership')
        assert result[1] == 'JSONDecodeError'

# Old document schema and isolated missing/malformed dependency schemas.
for ddl in ('DROP TABLE document_dependencies', 'DROP TABLE dependencies',
            'ALTER TABLE dependencies RENAME COLUMN child TO wrong_child',
            'ALTER TABLE dependencies RENAME COLUMN parent TO wrong_parent'):
    for n in (0, 4):
        for stored in ('active', 'candidate'):
            with tempfile.TemporaryDirectory() as directory:
                before, after = fixture(directory, n=n, status=stored)
                with after._connect(write=True) as db:
                    db.execute(ddl)
                for status in statuses[:5]:
                    for scope in scopes[:6]:
                        compare(before, after, status, scope, 'isolated-legacy-schema')

for BaseClass in (Before, After):
    class Child(BaseClass):
        @staticmethod
        def _get(db, entry_id):
            packet = BaseClass._get(db, entry_id)
            packet['subclass-marker'] = True
            return packet
    with tempfile.TemporaryDirectory() as directory:
        before, after = fixture(directory)
        child = Child(directory)
        target = before if BaseClass is Before else after
        for status in statuses[:5]:
            for scope in scopes:
                got = outcome(lambda: child.list(status, scope))
                expected = outcome(lambda: target.list(status, scope))
                if expected[0] == 'value':
                    for packet in expected[1]:
                        packet['subclass-marker'] = True
                assert got == expected
                counts['ledger-subclass-fallback'] += 1

# Structural evidence: exact base class path, uniform fallback, mixed preservation.
for pattern, expected in (('mixed', ['r001', 'r003']), ('all', ['r000','r001','r002','r003']),
                          ('none', ['r000','r001','r002','r003'])):
    with tempfile.TemporaryDirectory() as directory:
        before, after = fixture(directory, pattern=pattern)
        with patch.object(After, '_get', wraps=After._get) as get:
            after.list('active', 'T1')
            assert [c.args[1] for c in get.call_args_list] == expected
        counts['structural-hydration'] += 1
with tempfile.TemporaryDirectory() as directory:
    before, after = fixture(directory)
    with after._connect(write=True) as db:
        db.execute("UPDATE entries SET status='candidate' WHERE id='r000'")
    with patch.object(After, '_get', wraps=After._get) as get:
        after.list('active', 'T1')
        assert [c.args[1] for c in get.call_args_list] == ['r001','r003']
    counts['structural-hydration'] += 1

# Actual public API transitions on the same database; no cached mutable packets.
with tempfile.TemporaryDirectory() as directory:
    after = After(directory, create=True)
    before = Before(directory)
    after.add('candidate', 'claim', 'proposal', 'source', scope=['T1'])
    after.accept('candidate', 'accepted', 'independent-review', 'accepted')
    after.add('child', 'claim', 'derived', 'source', deps=['accepted'], scope=['T1'], evidence='verified')
    for status in statuses[:5]:
        compare(before, after, status, 'T1', 'public-api-before-correction')
    returned = after.list('active', 'T1')
    returned[0]['content'] = 'caller mutation'
    returned[0]['scope'].append('mutation')
    returned[0]['deps'].append('mutation')
    compare(before, after, 'active', 'T1', 'freshness')
    after.correct('accepted', 'corrected', 'new content', 'user-statement', 'changed')
    for status in statuses[:5]:
        compare(before, after, status, 'T1', 'public-api-after-correction')
    assert [p['id'] for p in after.list('active', 'T1')] == ['corrected']

# Explicitly excluded raw TEXT corruption: record discrepancies, do not count parity.
with tempfile.TemporaryDirectory() as directory:
    before, after = fixture(directory)
    with after._connect(write=True) as db:
        db.execute("UPDATE entries SET content=CAST(x'ff' AS TEXT) WHERE id='r000'")
    exploratory.append({'case': 'invalid UTF8 unselected content; excluded before tests',
                        'before': repr(outcome(lambda: before.list('active', 'T1'))),
                        'after': repr(outcome(lambda: after.list('active', 'T1')))})

# NULL requires a non-API relaxed schema: inspect routing only, excluded from parity.
with tempfile.TemporaryDirectory() as directory:
    before, after = fixture(directory)
    with after._connect(write=True) as db:
        result = db.execute('SELECT NULL IS NOT NULL, NULL IS NOT ?, ? IS NOT ?',
                            (b'[]', b'[]', b'[]')).fetchone()
        assert tuple(result) == (0, 1, 0)
    counts['raw-guard-null-blob-logic'] += 1

config = json.loads((args.evidence_dir / 'config.json').read_text())
integrity = []
for name in ('raw-primary-v2.json', 'reviewer/raw-independent-v2.json'):
    path = args.evidence_dir / name
    if not path.exists():
        continue
    raw = json.loads(path.read_text())
    assert raw['config'] == config
    assert raw['candidate_source_sha256'] == CAND_SHA
    assert raw['baseline_source_sha256'] == BASE_SHA
    assert len(raw['cases']) == len(config['cases']) == 7
    rng = random.Random(config['seed'])
    records = []
    for number, (case, expected) in enumerate(zip(raw['cases'], config['cases'])):
        assert {key: case[key] for key in expected} == expected
        orders = []
        for _ in range(config['repeats']):
            order = ['before_ms', 'after_ms']
            rng.shuffle(order)
            orders.append(order)
        assert case['orders'] == orders
        assert set(case['samples']) == {'before_ms','after_ms'}
        for label, samples in case['samples'].items():
            assert len(samples) == config['repeats'] == 21
            assert all(type(v) in (float,int) and math.isfinite(v) and v > 0 for v in samples)
            assert statistics.median(samples) == case['median'][label]
        reduction = 1 - case['median']['after_ms'] / case['median']['before_ms']
        assert reduction == case['reduction']
        with tempfile.TemporaryDirectory() as directory:
            after = After(directory, create=True)
            with after._connect(write=True) as db:
                for i in range(case['entries']):
                    db.execute('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',
                               (f'm{i:06}', 'claim', 'x' * case['content_bytes'], 'synthetic fixture',
                                '["T1"]' if i % case['match_every'] == 0 else '["T10"]',
                                'verified', 'active' if i < case['active'] else 'stale', '2026-10-16'))
            assert sha(after.path.read_bytes()) == case['database_sha256']
        expected_count = sum(case['scope'] is None or i % case['match_every'] == 0
                             for i in range(case['active']))
        assert case['returned'] == expected_count
        gate = reduction >= .25 if number < 2 else reduction >= -.15
        records.append({'name': case['name'], 'returned': case['returned'],
                        'before_ms': case['median']['before_ms'], 'after_ms': case['median']['after_ms'],
                        'reduction': reduction, 'gate': gate,
                        'before_first': sum(o[0] == 'before_ms' for o in orders),
                        'minmax_ms': {k: [min(v),max(v)] for k,v in case['samples'].items()}})
    integrity.append({'path': name, 'sha256': sha(path.read_bytes()), 'cases': records,
                      'all_gates': all(r['gate'] for r in records), 'environment': raw['environment']})

assert sha((root / 'agent_runtime/project_memory.py').read_bytes()) == CAND_SHA
report = {'scope': 'API-valid packets and isolated metadata/legacy-schema cases; bounded synthetic warm-local data',
          'reference': BASE, 'reference_sha256': BASE_SHA, 'candidate_sha256': CAND_SHA,
          'counts': dict(counts), 'total_checks': sum(counts.values()),
          'failures': failures, 'exploratory_excluded': exploratory, 'raw_integrity': integrity,
          'hashes': {str(path.relative_to(root)): sha(path.read_bytes()) for path in
                     (root / 'agent_runtime/project_memory.py', root / 'tests/test_memory_retrieval.py',
                      root / 'scripts/bench_memory_retrieval.py', args.evidence_dir / 'config.json')}}
print(json.dumps(report, indent=2))
if failures:
    raise SystemExit(1)
