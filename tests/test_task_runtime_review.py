"""Independent regression checks for supervisor review R4/R5 and policy failure.

Temporary local files/SQLite only. Controlled interleavings model competing
scheduler processes without relying on thread timing. No external services.
"""
import hashlib
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from agent_runtime.core import ArtifactHandler, Engine, Outcome, Store
from agent_runtime.scheduler import LocalScheduler, arm

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 16 * 1024 * 1024


def plan():
    return {'schema_version': 'task-dag/v1', 'run_id': 'review',
            'user_goal': 'bounded regression', 'authorization_reference': 'local test',
            'supervision': {'min_seconds': 1, 'max_seconds': 60, 'rationale': 'test'},
            'tasks': [{'task_id': 'a', 'action': 'test', 'owner': 'host',
                       'done_when': {'test': True}, 'max_attempts': 3,
                       'estimated_seconds': 20, 'risk': 'low'}]}


class ReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.store = Store(self.root / 'db')
        self.store.create(plan())
        self.now = 100.
        self.scheduler = LocalScheduler(self.store, lambda: self.now)
        self.scheduler.heartbeat('test')
        self.monitor = arm(self.scheduler, 'review')['monitor_id']

    def artifact_task(self, name='proof'):
        return {'done_when': {'artifacts': [{'path': name, 'sha256': hashlib.sha256(b'ok').hexdigest()}]}}

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO requires POSIX')
    def test_fifo_rejected_without_blocking(self):
        os.mkfifo(self.root / 'proof')
        # A broken implementation must fail by timeout, never hang the test suite.
        code = '''
import sys
from agent_runtime.core import ArtifactHandler
try:
    ArtifactHandler(sys.argv[1])._evidence({'done_when': {'artifacts': [{'path': 'proof', 'sha256': '0'*64}]}})
except ValueError as exc:
    assert 'regular file' in str(exc), str(exc)
else:
    raise AssertionError('FIFO accepted')
'''
        result = subprocess.run([sys.executable, '-c', code, str(self.root)],
                                cwd=ROOT, capture_output=True, text=True, timeout=3)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_oversize_regular_file_rejected(self):
        with (self.root / 'proof').open('wb') as stream:
            stream.truncate(LIMIT + 1)
        with self.assertRaisesRegex(ValueError, '16 MiB'):
            ArtifactHandler(self.root)._evidence(self.artifact_task())

    def test_growth_after_fstat_cannot_bypass_read_bound(self):
        path = self.root / 'proof'
        with path.open('wb') as stream:
            stream.truncate(LIMIT + 1)
        real_mode = path.stat().st_mode
        # Simulates a file growing immediately after fstat: actual bytes exceed
        # the accepted metadata. Reading still uses the real regular file fd.
        with patch('agent_runtime.core.os.fstat', return_value=SimpleNamespace(st_mode=real_mode, st_size=0)):
            with self.assertRaisesRegex(ValueError, 'grew beyond'):
                ArtifactHandler(self.root)._evidence(self.artifact_task())

    def test_wake_during_tick_survives_old_drain_writeback(self):
        outer = self
        class WakeDuringTick:
            def tick(self, *_):
                outer.scheduler.wake('review', 'trusted change')
                self.woken = outer.scheduler.read(outer.monitor)['due']
                return {'next_check_seconds': 60}
        engine = WakeDuringTick()
        self.assertTrue(self.scheduler.drain_once(engine))
        self.assertEqual(engine.woken, 101)
        self.assertEqual(self.scheduler.read(self.monitor)['due'], 101)

    def test_old_drain_cannot_overwrite_newer_drain(self):
        outer = self
        class NewDrain:
            def tick(self, *_):
                return {'next_check_seconds': 10}
        class OldDrain:
            def tick(self, *_):
                outer.now = 101  # First reservation expires while old tick runs.
                self.rival = LocalScheduler(Store(outer.store.path), lambda: outer.now)
                outer.assertTrue(self.rival.drain_once(NewDrain()))
                outer.assertEqual(self.rival.read(outer.monitor)['due'], 111)
                return {'next_check_seconds': 60}
        self.assertTrue(self.scheduler.drain_once(OldDrain()))
        self.assertEqual(self.scheduler.read(self.monitor)['due'], 111)

    def test_monitor_version_migration_preserves_existing_record(self):
        path = self.root / 'old-db'
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE monitors (id TEXT PRIMARY KEY, chain_id TEXT UNIQUE, status TEXT, due REAL)')
            db.execute("INSERT INTO monitors VALUES ('old','r','active',123)")
        migrated = Store(path)
        with migrated.transaction() as db:
            row = dict(db.execute("SELECT * FROM monitors WHERE id='old'").fetchone())
        self.assertEqual(row, {'id': 'old', 'chain_id': 'r', 'status': 'active', 'due': 123., 'version': 0})

    def test_authorization_exception_does_not_kill_service_or_run_action(self):
        class Handler:
            idempotent = True
            required_capabilities = frozenset()
            calls = 0
            def run(self, *_):
                self.calls += 1
                return Outcome('complete', evidence=['proof'])
            def verify(self, *_): return True
        handler = Handler()
        def unavailable(*_): raise ConnectionError('test policy service offline')
        engine = Engine(self.store, {'test': handler}, authorize=unavailable,
                        clock=lambda: self.now, allow_legacy=True)
        # Runs one bounded foreground loop. Returning normally proves that the
        # callback exception did not escape drain_once and terminate serve.
        self.scheduler.serve(engine, max_seconds=.05)
        state = self.store.snapshot('review')['state']
        self.assertEqual(state['status'], 'blocked')
        self.assertEqual(state['tasks']['a']['attempts'], 0)
        self.assertEqual(handler.calls, 0)
        self.assertEqual(self.scheduler.read(self.monitor)['status'], 'active')


if __name__ == '__main__':
    unittest.main()
