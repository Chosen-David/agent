"""Independent SQL oracle, pagination properties, actual pipe budget and WAL observations."""
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from agent_runtime.project_memory import MemoryLedger, MemoryError

LABEL = sys.argv[1] if len(sys.argv) > 1 else 'v1'
results = []
def require(value, message):
    if not value:
        raise AssertionError(message)
def record(name, fn):
    try:
        result = fn()
        results.append({'name': name, 'verdict': 'pass', 'observations': result})
    except Exception:
        results.append({'name': name, 'verdict': 'fail', 'traceback': traceback.format_exc()})
def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
def sha(value):
    return hashlib.sha256(value).hexdigest()
def oracle(ledger, status='all', scope=None):
    with closing(sqlite3.connect(ledger.path)) as db, db:
        db.row_factory = sqlite3.Row
        expected = []
        for row in db.execute('SELECT * FROM entries ORDER BY created_at,id'):
            entry = dict(row)
            entry['scope'] = json.loads(entry['scope'])
            doc = db.execute('SELECT snapshot FROM document_dependencies WHERE entry_id=?', (entry['id'],)).fetchone()
            entry['document_refs'] = None if doc is None else json.loads(doc[0])
            entry['deps'] = sorted(r[0] for r in db.execute('SELECT parent FROM dependencies WHERE child=?', (entry['id'],)))
            if (status == 'all' or entry['status'] == status) and (scope is None or scope in entry['scope']):
                expected.append(entry)
        return expected
def refuse(fn):
    try:
        fn()
    except MemoryError:
        return
    raise AssertionError('expected fail-closed MemoryError')
def seed(ledger):
    for i in range(17):
        ledger.add(f'e{i:02}', 'claim', f'body {i} 汉字 😀\n' * (i + 1),
                   'source: 用户原话 🥇', deps=[f'e{i-1:02}'] if i else [],
                   scope=['T1' if i % 2 else 'T10', 'all'], evidence='verified')
    with closing(sqlite3.connect(ledger.path)) as db, db:
        db.execute("UPDATE entries SET created_at='2026-10-20'")
        for i, status in enumerate(['candidate', 'stale', 'superseded']):
            db.execute('UPDATE entries SET status=? WHERE id=?', (status, f'e{i:02}'))

def properties():
    count = 0
    with tempfile.TemporaryDirectory() as tmp:
        ledger = MemoryLedger(tmp, create=True)
        seed(ledger)
        for status in ('all', 'active', 'candidate', 'stale', 'superseded'):
            for scope in (None, 'all', 'T1', 'T10', 'T', ''):
                expected = oracle(ledger, status, scope)
                for limit in (1, 2, 3, 7, 17, 100):
                    got = []; cursor = snapshot = None
                    for _ in range(18):
                        page = ledger.index(status, scope, limit=limit, after_id=cursor, expected_snapshot=snapshot)
                        require(page['total_entries'] == len(expected), 'total count')
                        require(page['start'] == len(got), 'page start')
                        require(page['partial'] == (page['next_after_id'] is not None), 'partial/cursor')
                        got.extend(page['entries'])
                        cursor, snapshot = page['next_after_id'], page['snapshot']
                        if cursor is None:
                            break
                    else:
                        raise AssertionError('nonterminating pagination')
                    require([r['id'] for r in got] == [r['id'] for r in expected], 'oracle order/no missing or repeats')
                    for row, entry in zip(got, expected):
                        projection = {k: v for k, v in entry.items() if k != 'content'}
                        projection.update(content_sha256=sha(entry['content'].encode('utf-8')),
                                          content_chars=len(entry['content']), entry_sha256=sha(canon(entry).encode('utf-8')))
                        require(row == projection, 'metadata or hash differs from SQL oracle')
                    count += 1
        page = ledger.index('all', limit=1)
        options = {'status': 'all', 'after_id': page['next_after_id'], 'expected_snapshot': page['snapshot']}
        for column, value in [('content', 'changed'), ('source', 'changed'), ('kind', 'observation'),
                              ('evidence', 'candidate'), ('created_at', '2026-10-21'), ('scope', '["different"]')]:
            with closing(sqlite3.connect(ledger.path)) as db, db:
                old = db.execute(f'SELECT {column} FROM entries WHERE id="e16"').fetchone()[0]
                db.execute(f'UPDATE entries SET {column}=? WHERE id="e16"', (value,))
            refuse(lambda: ledger.index(**options))
            with closing(sqlite3.connect(ledger.path)) as db, db:
                db.execute(f'UPDATE entries SET {column}=? WHERE id="e16"', (old,))
        with closing(sqlite3.connect(ledger.path)) as db, db:
            db.execute("UPDATE dependencies SET parent='e14' WHERE child='e16'")
        refuse(lambda: ledger.index(**options))
        with closing(sqlite3.connect(ledger.path)) as db, db:
            db.execute("UPDATE dependencies SET parent='e15' WHERE child='e16'")
            db.execute("INSERT INTO document_dependencies VALUES('e16','{\"version\":1}')")
        refuse(lambda: ledger.index(**options))
        with closing(sqlite3.connect(ledger.path)) as db, db:
            db.execute("DELETE FROM document_dependencies WHERE entry_id='e16'")
        # A selection, rather than unrelated excluded history, defines a snapshot.
        active = ledger.index()
        with closing(sqlite3.connect(ledger.path)) as db, db:
            db.execute('UPDATE entries SET content="unselected changed" WHERE id="e00"')
        require(ledger.index()['snapshot'] == active['snapshot'], 'unselected data changed selected identity')
        # Active descendants of stale evidence are still navigation-only.
        require(any(r['id'] == 'e03' for r in ledger.index()['entries']), 'active child absent')
        refuse(lambda: ledger.check(['e03']))
        baseline_legacy = ledger.index('all')['entries']
        with closing(sqlite3.connect(ledger.path)) as db, db:
            db.execute('DROP TABLE document_dependencies')
        require(ledger.index('all')['entries'] == baseline_legacy, 'legacy table absence changed projection')
    return {'oracle_pagination_combinations': count, 'mutation_fields': 6, 'trust_gate': 'navigation listed active child; check refused stale ancestry'}

def actual_pipe_budget():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = MemoryLedger(tmp, create=True)
        ledger.add('one', 'claim', '中文 😀\n', 'source', evidence='verified')
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        command = [sys.executable, '-m', 'agent_runtime.project_memory', '--root', tmp, 'index']
        wire = subprocess.check_output(command, cwd=ROOT, env=env)
        packet = json.loads(wire)
        logical_cap = len(canon(packet)) + 1
        limited = subprocess.run(command + ['--max-chars', str(logical_cap)], cwd=ROOT, env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        detail = {'default_wire_chars': len(wire.decode('utf-8')), 'default_wire_bytes': len(wire),
                  'newline_suffix_hex': wire[-2:].hex(), 'requested_cap': logical_cap,
                  'limited_exit': limited.returncode, 'limited_chars': len(limited.stdout.decode('utf-8')),
                  'limited_stderr': limited.stderr.decode('utf-8')}
        (OUT / ('independent-pipe-' + LABEL + '.json')).write_text(json.dumps(detail, indent=2) + '\n', encoding='utf-8')
        require(limited.returncode != 0 or len(limited.stdout.decode('utf-8')) <= logical_cap,
                'actual binary CLI stdout exceeds hard character budget: ' + repr(detail))
        exact_cap = len(wire.decode('utf-8'))
        for cap in (exact_cap - 1, exact_cap, exact_cap + 1):
            trial = subprocess.run(command + ['--max-chars', str(cap)], cwd=ROOT, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            require((trial.returncode == 0) == (cap >= exact_cap), 'exact native pipe cap boundary')
            require(trial.returncode != 0 or len(trial.stdout.decode('utf-8')) <= cap, 'pipe cap overflow')
        return detail

def files(path):
    return {p.name: {'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())} for p in path.parent.iterdir() if p.is_file()}
def wal_observation():
    observations = []
    for live_writer in (True, False):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = MemoryLedger(tmp, create=True)
            db = sqlite3.connect(ledger.path)
            try:
                require(db.execute('PRAGMA journal_mode=WAL').fetchone()[0] == 'wal', 'WAL unavailable')
                db.execute("INSERT INTO entries VALUES('x','claim','body','source','[]','verified','active','now')")
                db.commit()
                if not live_writer:
                    db.close(); db = None
                before = files(ledger.path)
                state = ledger.storage()
                after = files(ledger.path)
                with closing(sqlite3.connect(ledger.path)) as observed:
                    require(state['entries_by_status'] == dict(observed.execute('SELECT status,count(*) FROM entries GROUP BY status')), 'status totals')
                    require(state['page_size_bytes'] == observed.execute('PRAGMA page_size').fetchone()[0], 'page size')
                require(state['logical_bytes'] == state['page_count'] * state['page_size_bytes'], 'page arithmetic')
                require(0 <= state['free_pages'] <= state['page_count'], 'page ranges')
                observations.append({'live_writer': live_writer, 'before': before, 'after': after, 'state': state,
                                     'files_identical': before == after})
            finally:
                if db is not None:
                    db.close()
    return observations

record('independent_sql_properties', properties)
record('actual_pipe_hard_character_budget', actual_pipe_budget)
record('storage_wal_physical_observations', wal_observation)
payload = {'python': sys.version, 'sqlite': sqlite3.sqlite_version, 'label': LABEL,
           'source_sha256': sha((ROOT / 'agent_runtime/project_memory.py').read_bytes()),
           'checker_sha256': sha(Path(__file__).read_bytes()), 'checks': results}
(OUT / ('independent-boundary-' + LABEL + '.json')).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'checks': [{'name': r['name'], 'verdict': r['verdict']} for r in results]}))
sys.exit(int(any(r['verdict'] != 'pass' for r in results)))
