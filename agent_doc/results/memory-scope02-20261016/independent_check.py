"""Independent f872 differential boundary checks; no performance measurements."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

from agent_runtime.project_memory import MemoryLedger

ROOT = Path(__file__).resolve().parents[3]
REV = 'f872166a7ce4c61e21353dad83a83729d44440ca'
SOURCE = subprocess.check_output(['git', 'show', REV + ':agent_runtime/project_memory.py'], cwd=ROOT)
assert hashlib.sha256(SOURCE).hexdigest() == '5ae35f1dcad87ab759fe4aab5f7deb522c9a3ea1d01ef8118c4ca65547ef7b19'
ns = {'__name__': 'agent_runtime._independent_scope_before', '__package__': 'agent_runtime'}
exec(compile(SOURCE, REV + '/project_memory.py', 'exec'), ns)
Before = ns['MemoryLedger']
checks = 0


class Text(str):
    pass


def outcome(call):
    try:
        return ('value', call())
    except Exception as exc:
        return ('error', type(exc).__name__, str(exc))


def parity(before, after, status='active', scope='T1'):
    global checks
    a = outcome(lambda: before.list(status, scope))
    b = outcome(lambda: after.list(status, scope))
    assert a == b, (status, scope, a, b)
    checks += 1
    return a


def fixture(directory):
    after = MemoryLedger(directory, create=True)
    before = Before(directory)
    with after._connect(write=True) as db:
        for entry_id, status, scope in [('a', 'active', '["T1"]'),
                                        ('b', 'candidate', '["T10"]'),
                                        ('c', 'active', '["T1","T10"]')]:
            db.execute('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',
                       (entry_id, 'claim', 'body-' + entry_id, 'source-' + entry_id,
                        scope, 'verified', status, '2026-10-16'))
        db.execute('INSERT INTO dependencies VALUES(?,?)', ('c', 'b'))
        db.execute('INSERT INTO dependencies VALUES(?,?)', ('c', 'a'))
        db.execute('INSERT INTO document_dependencies VALUES(?,?)', ('c', '{"fixture":[1,2]}'))
    return before, after


def run():
    for raw in ('[]', '["T1","T10"]', '"T10"', '{"T1":1}', 'null', '7', 'true'):
        for entry_status in ('active', 'candidate', 'stale', 'superseded'):
            with tempfile.TemporaryDirectory() as directory:
                before, after = fixture(directory)
                with after._connect(write=True) as db:
                    db.execute('UPDATE entries SET scope=?,status=? WHERE id="a"', (raw, entry_status))
                for status in ('active', 'candidate', 'stale', 'superseded', 'all', Text('active')):
                    for scope in ('T1', 'T10', 'T', '', None, 1, ['T1'], Text('T1')):
                        parity(before, after, status, scope)

    for raw in ('bad-json', b'"\xff"', '[' * 1100 + '0' + ']' * 1100):
        for field in ('scope', 'snapshot'):
            with tempfile.TemporaryDirectory() as directory:
                before, after = fixture(directory)
                with after._connect(write=True) as db:
                    db.execute('UPDATE entries SET scope="null" WHERE id="a"')
                    if field == 'scope':
                        db.execute('UPDATE entries SET scope=? WHERE id="c"', (raw,))
                    else:
                        db.execute('UPDATE document_dependencies SET snapshot=? WHERE entry_id="c"', (raw,))
                result = parity(before, after)
                assert result[0] == 'error'
                # Keep actual candidate exception/traceback alive during write.
                saved = None
                try:
                    after.list(scope='T1')
                except Exception as exc:
                    saved = exc
                assert saved is not None
                with after._connect(write=True) as db:
                    db.execute('UPDATE entries SET content="writer succeeds" WHERE id="a"')

    for missing in ('document_dependencies', 'dependencies'):
        for statuses in (('active', 'candidate', 'active'), ('candidate',) * 3):
            with tempfile.TemporaryDirectory() as directory:
                before, after = fixture(directory)
                with after._connect(write=True) as db:
                    db.execute('DROP TABLE ' + missing)
                    for entry_id, status in zip('abc', statuses):
                        db.execute('UPDATE entries SET status=? WHERE id=?', (status, entry_id))
                for scope in ('T1', 'absent', None):
                    parity(before, after, scope=scope)

    with tempfile.TemporaryDirectory() as directory:
        before, after = fixture(directory)
        class BeforeChild(Before):
            pass
        class AfterChild(MemoryLedger):
            pass
        parity(BeforeChild(directory), AfterChild(directory))
        with patch.object(MemoryLedger, '_get', wraps=MemoryLedger._get) as get:
            after.list(scope='T10')
            assert [call.args[1] for call in get.call_args_list] == ['c']
        with after._connect(write=True) as db:
            db.execute('UPDATE entries SET status="active"')
        parity(before, after)
        with patch.object(MemoryLedger, '_get', wraps=MemoryLedger._get) as get:
            after.list(scope='T10')
            assert [call.args[1] for call in get.call_args_list] == ['a', 'b', 'c']
        with after._connect(write=True) as db:
            db.execute('DELETE FROM dependencies')
            db.execute('DELETE FROM document_dependencies')
            db.execute('DELETE FROM entries')
        parity(before, after)
        after.path.unlink()
        parity(before, after, status='invalid')

    print(json.dumps({'differential_checks': checks, 'status': 'pass',
                      'baseline': REV, 'candidate_sha256': hashlib.sha256(
                          (ROOT / 'agent_runtime/project_memory.py').read_bytes()).hexdigest()}))


if __name__ == '__main__':
    run()
