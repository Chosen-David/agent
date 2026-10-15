"""Independent baseline differential and raw-pair validation; CPU synthetic only."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import sqlite3
import statistics
import subprocess
import tempfile
from unittest.mock import patch

from agent_runtime import project_memory as candidate
from agent_runtime.project_docs import migrate, snapshot_project_docs

ROOT = Path(__file__).resolve().parents[3]
RESULT = Path(__file__).resolve().parent
CONFIG_HASH = 'a02199c4894bf47c6ea385390d2f2d8fba92776b92fcd2c2e72ff786d5b5cfe9'
SOURCE_HASH = 'b9f939410eee1e7c7477982ff9b0a1c95bd7d952ec706b5b179707d0d598ccf6'
config = json.loads((RESULT / 'config.json').read_text())
assert hashlib.sha256((RESULT / 'config.json').read_bytes()).hexdigest() == CONFIG_HASH
assert hashlib.sha256((ROOT / 'agent_runtime/project_memory.py').read_bytes()).hexdigest() == SOURCE_HASH
source = subprocess.check_output(['git', 'show', config['baseline_revision'] + ':agent_runtime/project_memory.py'], cwd=ROOT)
assert hashlib.sha256(source).hexdigest() == config['baseline_source_sha256']
baseline = {'__name__': 'agent_runtime._independent_check_before', '__package__': 'agent_runtime'}
exec(compile(source, config['baseline_revision'] + '/project_memory.py', 'exec'), baseline)
Before = baseline['MemoryLedger']
After = candidate.MemoryLedger
counts = {'differential': 0, 'freshness': 0, 'structural': 0, 'raw_cases': 0}


def capture(fn):
    try:
        return ('value', fn())
    except Exception as exc:
        return ('error', type(exc).__name__, str(exc))


def compare(before, after, refs):
    left, right = capture(lambda: before.check(refs)), capture(lambda: after.check(refs))
    assert left == right, (refs, left, right)
    counts['differential'] += 1
    return left


def seed(root, statuses=('active',) * 4, edges=(('b', 'a'), ('c', 'a'), ('d', 'b'), ('d', 'c'))):
    after = After(root, create=True)
    with after._connect(write=True) as db:
        for name, status in zip('abcd', statuses):
            db.execute('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',
                       (name, 'claim', name * 31, 'independent synthetic', '["T1"]',
                        'verified', status, '2026-10-16'))
        db.executemany('INSERT INTO dependencies VALUES(?,?)', edges)
    return Before(root), after


def sql(after, statement, args=()):
    # Deliberate malformed SQLite fixtures, never production data.
    with sqlite3.connect(after.path) as db:
        db.execute('PRAGMA foreign_keys=OFF')
        db.execute(statement, args)


# Every ordered nonempty root subset, with status failures at roots/ancestors.
with tempfile.TemporaryDirectory() as directory:
    before, after = seed(directory)
    refs_set = [list(p) for n in range(1, 5) for p in itertools.permutations('abcd', n)]
    for states in itertools.product(('active', 'candidate', 'stale', 'superseded'), repeat=3):
        for name, state in zip('abc', states):
            sql(after, 'UPDATE entries SET status=? WHERE id=?', (state, name))
        for refs in refs_set:
            compare(before, after, refs)
    for name in 'abc':
        sql(after, 'UPDATE entries SET status="active" WHERE id=?', (name,))
    malformed = [None, [], (), '', 'a', {}, set(), 1, [None], ['a', 'a'], ['bad id'], ['a', 2], ['missing'], ['d', 'missing']]
    for refs in malformed + [tuple(p) for p in refs_set]:
        compare(before, after, refs)
    # Caller mutations must not persist; each public check has its own packets.
    for ledger in (before, after):
        original = ledger.check(['d', 'a'])
        old = ledger.check(['d', 'a'])
        old[0]['deps'].append('caller-only')
        old[0]['scope'].append('caller-only')
        old[0]['content'] = 'caller-only'
        assert ledger.check(['d', 'a']) == original
        counts['freshness'] += 1
    attrs = dict(vars(after))
    after.check(['d', 'a'])
    assert vars(after) == attrs
    counts['structural'] += 1
    # Count reads and inspect the live local roots map at dependency visits.
    original_get = After._get
    calls, root_keys = [], []
    def observed(db, entry_id):
        import inspect
        calls.append(entry_id)
        frame = inspect.currentframe().f_back
        while frame and frame.f_code.co_name != '_check':
            frame = frame.f_back
        if frame:
            root_keys.append(set(frame.f_locals['roots']))
        return original_get(db, entry_id)
    with patch.object(After, '_get', side_effect=observed):
        after.check(['d', 'a'])
    assert calls == ['d', 'b', 'a', 'c'], calls
    assert all(keys <= {'d', 'a'} for keys in root_keys), root_keys
    counts['structural'] += 1
    # A completed check cannot mask a correction in a later transaction.
    compare(before, after, ['d'])
    after.correct('a', 'a2', 'corrected', 'independent fixture', 'new intent')
    compare(before, after, ['d'])
    compare(before, after, ['a2'])
    counts['freshness'] += 1

# Decode edge cases, including malformed text and SQLite BLOB JSON.
for field in ('scope', 'document'):
    for entry_id in ('a', 'd'):
        for value in ('[', 'null', '{}', '"text"', '7', '[]', b'\xff', b'[]'):
            with tempfile.TemporaryDirectory() as directory:
                before, after = seed(directory)
                if field == 'scope':
                    sql(after, 'UPDATE entries SET scope=? WHERE id=?', (value, entry_id))
                else:
                    sql(after, 'INSERT INTO document_dependencies VALUES(?,?)', (entry_id, value))
                for refs in (['d'], ['a', 'd'], ('d', 'a')):
                    compare(before, after, refs)

for variant in ('legacy-doc', 'missing-deps', 'missing-entries', 'dangling', 'cycle', 'self-cycle'):
    with tempfile.TemporaryDirectory() as directory:
        before, after = seed(directory)
        if variant == 'legacy-doc':
            sql(after, 'DROP TABLE document_dependencies')
        elif variant == 'missing-deps':
            sql(after, 'DROP TABLE dependencies')
        elif variant == 'missing-entries':
            sql(after, 'DROP TABLE entries')
        elif variant == 'dangling':
            sql(after, 'INSERT INTO dependencies VALUES("a","missing")')
        elif variant == 'cycle':
            sql(after, 'INSERT INTO dependencies VALUES("a","d")')
        else:
            sql(after, 'INSERT INTO dependencies VALUES("a","a")')
        for refs in (['d'], ['a'], ['c', 'a', 'd'], ('d', 'b', 'a')):
            compare(before, after, refs)
        # Failed checks must not cache failure or bypass a repaired schema.
        if variant == 'missing-deps':
            sql(after, 'CREATE TABLE dependencies(child TEXT,parent TEXT)')
            compare(before, after, ['d'])
            counts['freshness'] += 1

# Real project task-document snapshot changes, with no human-guide writes.
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    (root / 'TASK.md').write_text('## 2026-10-16\n- [ ] [T1] Original task\n')
    snapshot = migrate(root, '2026-10-16')
    before, after = seed(root)
    after.add('bound', 'claim', 'bound fixture', 'independent fixture', evidence='verified', document_refs=snapshot)
    after.add('dependent', 'claim', 'dependent fixture', 'independent fixture', evidence='verified', deps=['bound'])
    for refs in (['bound'], ['dependent'], ['dependent', 'bound']):
        compare(before, after, refs)
    check_docs = candidate.check_document_refs
    with patch.object(candidate, 'check_document_refs', wraps=check_docs) as checked:
        after.check(['dependent', 'bound'])
        after.check(['bound'])
        assert checked.call_count == 2
    counts['structural'] += 1
    refs_without_context = ['bound']
    with after._connect() as db:
        left = capture(lambda: Before._check(db, refs_without_context))
        right = capture(lambda: After._check(db, refs_without_context))
        assert left == right
        counts['differential'] += 1
    task = root / 'agent_doc/task/TASK.md'
    previous = task.read_text()
    task.write_text(previous.replace('Original task', 'Changed task'))
    for refs in (['bound'], ['dependent'], ['dependent', 'bound']):
        compare(before, after, refs)
    task.write_text(previous)
    compare(before, after, ['dependent', 'bound'])
    counts['freshness'] += 1

# Recompute all arithmetic, order, identities and exact frozen config from raw.
for raw_name in ('raw-primary.json', 'independent-raw.json'):
    raw = json.loads((RESULT / raw_name).read_text())
    assert raw['config'] == config
    assert raw['baseline_source_sha256'] == config['baseline_source_sha256']
    assert raw['candidate_source_sha256'] == SOURCE_HASH
    assert len(raw['cases']) == len(config['cases']) == 6
    rng = random.Random(config['seed'])
    for fixed, case in zip(config['cases'], raw['cases']):
        assert all(case[k] == v for k, v in fixed.items())
        assert case['returned'] == fixed['refs_count']
        expected_orders = []
        for _ in range(config['repeats']):
            order = ['before_ms', 'after_ms']
            rng.shuffle(order)
            expected_orders.append(order)
        assert case['orders'] == expected_orders
        for label in ('before_ms', 'after_ms'):
            values = case['samples'][label]
            assert len(values) == config['repeats'] == 21
            assert all(math.isfinite(v) and v > 0 for v in values)
            assert case['median'][label] == statistics.median(values)
        reduction = 1 - case['median']['after_ms'] / case['median']['before_ms']
        assert case['reduction'] == reduction
        threshold = config['acceptance']['large_min_reduction'] if case['name'].startswith('many-roots') else -config['acceptance']['control_max_regression']
        assert reduction >= threshold, (raw_name, case['name'], reduction)
        counts['raw_cases'] += 1
    if raw_name == 'raw-primary.json':
        primary_digests = [c['database_sha256'] for c in raw['cases']]
    else:
        assert primary_digests == [c['database_sha256'] for c in raw['cases']]

assert hashlib.sha256((ROOT / 'agent_runtime/project_memory.py').read_bytes()).hexdigest() == SOURCE_HASH
print(json.dumps({'verdict': 'pass', 'counts': counts, 'candidate_sha256': SOURCE_HASH, 'config_sha256': CONFIG_HASH}, indent=2))
