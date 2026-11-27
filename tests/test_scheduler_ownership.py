import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

from agent_runtime.core import Store
from agent_runtime.scheduler import LocalScheduler, arm
from tests.test_task_runtime_review import plan

ROOT = Path(__file__).resolve().parents[1]


class SchedulerOwnership(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = Store(self.root / 'state.sqlite')
        self.store.create(plan())
        self.now = 100
        self.scheduler = LocalScheduler(self.store, lambda: self.now)
        self.scheduler.heartbeat('fixture')
        self.monitor = arm(self.scheduler, 'review')['monitor_id']
        self.engine = SimpleNamespace(tick=lambda *args: {'next_check_seconds': 10})

    def test_review_owns_store_past_due_and_wake_survives(self):
        calls = []
        def review(*args):
            calls.append(args)
            self.now = 1000
            rival = LocalScheduler(Store(self.store.path), lambda: self.now)
            rival.wake('review', 'trusted change')
            self.assertFalse(rival.drain_once(self.engine, on_due=lambda *args: calls.append(args)))
        self.assertTrue(self.scheduler.drain_once(self.engine, on_due=review))
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.scheduler.read(self.monitor)['due'], 101)
        self.assertTrue(self.scheduler.drain_once(self.engine, on_due=lambda *args: calls.append(args)))
        self.assertEqual(len(calls), 2)

    def test_tick_exception_releases_ownership(self):
        def fail(*args):
            raise RuntimeError('tick failed')
        with self.assertRaisesRegex(RuntimeError, 'tick failed'):
            self.scheduler.drain_once(SimpleNamespace(tick=fail))
        self.now = 1000
        self.assertTrue(self.scheduler.drain_once(self.engine))

    def test_process_exit_releases_ownership_without_replacing_inode(self):
        code = '''
import sys
from types import SimpleNamespace
from agent_runtime.core import Store
from agent_runtime.scheduler import LocalScheduler
scheduler = LocalScheduler(Store(sys.argv[1]), lambda: 100)
def hold(*args):
    print('review-active', flush=True)
    sys.stdin.readline()
scheduler.drain_once(SimpleNamespace(tick=lambda *args: {'next_check_seconds': 10}), on_due=hold)
'''
        child = subprocess.Popen([sys.executable, '-c', code, self.store.path], cwd=ROOT,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            import selectors
            if os.name == 'nt':
                self.skipTest('pipe readiness check requires POSIX selectors')
            with selectors.DefaultSelector() as selector:
                selector.register(child.stdout, selectors.EVENT_READ)
                self.assertTrue(selector.select(timeout=10), 'child did not enter review')
            self.assertEqual(child.stdout.readline().strip(), 'review-active')
            path = Path(self.store.path + '.drain.lock')
            inode = path.stat().st_ino
            self.now = 1000
            before = self.scheduler.read(self.monitor)
            self.assertFalse(self.scheduler.drain_once(self.engine, on_due=lambda *args: self.fail('overlap')))
            self.assertEqual(self.scheduler.read(self.monitor), before)
            child.kill()
            child.communicate(timeout=10)
            self.assertTrue(self.scheduler.drain_once(self.engine))
            self.assertEqual(path.stat().st_ino, inode)
        finally:
            if child.poll() is None:
                child.kill()
            child.communicate(timeout=10)

    @unittest.skipUnless(hasattr(os, 'symlink'), 'symlink unavailable')
    def test_redirected_lock_rejected(self):
        target = self.root / 'target'
        target.write_text('unchanged')
        Path(self.store.path + '.drain.lock').symlink_to(target)
        with self.assertRaises((ValueError, OSError)):
            self.scheduler.drain_once(self.engine)
        self.assertEqual(target.read_text(), 'unchanged')

    def test_late_wake_reports_terminal_without_mutating_cancelled_state(self):
        with self.store.transaction() as db:
            _, state = self.store.load(db, 'review')
            state['idle_ticks'] = 4
            self.store.save(db, 'review', state)
        self.store.cancel('review', 'user stopped')
        before = self.store.snapshot('review')
        receipt = self.scheduler.wake('review', 'late callback')
        self.assertEqual(self.store.snapshot('review'), before)
        self.assertEqual(receipt['delivery'], 'terminal')
        self.assertFalse(receipt['progress_confirmed'])
