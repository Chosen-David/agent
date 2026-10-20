"""Portable terminal checks: real persisted artifacts, bounded synthetic actions."""
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import unittest

from agent_runtime.core import ArtifactHandler, Engine, Store
from tests import test_task_runtime as fixtures
from tests.test_task_runtime import SyntheticHandler, plan, task


class TerminalRevalidation(unittest.TestCase):
    setUp = fixtures.RuntimeContracts.setUp
    engine = fixtures.RuntimeContracts.engine
    state = fixtures.RuntimeContracts.state

    def test_completed_artifact_change_survives_restart_without_replay(self):
        root = Path(self.tmp.name)
        (root / 'proof').write_bytes(b'accepted')
        source = task('source', action='verify_artifacts')
        source['done_when'] = {'artifacts': [
            {'path': 'proof', 'sha256': hashlib.sha256(b'accepted').hexdigest()}]}
        self.store.create(plan(source, task('consumer', ['source']), task('unrelated')))
        handler = SyntheticHandler()
        def restart():
            return Engine(Store(self.db_path), {'verify_artifacts': ArtifactHandler(root), 'synthetic': handler},
                          authorize=lambda *_: True, clock=self.clock, allow_legacy=True)
        for event in ('source', 'consumer', 'unrelated'):
            state = restart().tick('test-run', event)
        self.assertEqual(state['status'], 'done')
        original = copy.deepcopy(state['tasks'])
        (root / 'proof').write_bytes(b'changed')
        state = restart().tick('test-run', 'fresh-check')
        self.assertEqual(state['status'], 'blocked')
        for name in ('source', 'consumer'):
            self.assertEqual(state['tasks'][name]['status'], 'blocked')
            self.assertTrue(state['tasks'][name]['requires_reconciliation'])
            self.assertEqual(state['tasks'][name]['evidence'], original[name]['evidence'])
            self.assertEqual(state['tasks'][name]['attempts'], original[name]['attempts'])
        self.assertEqual(state['tasks']['unrelated']['status'], 'done')
        self.assertEqual(self.state(), state)
        (root / 'proof').write_bytes(b'accepted')
        self.assertEqual(restart().tick('test-run', 'restored')['status'], 'blocked')
        self.assertEqual(len(handler.calls), 2)
        engine = restart()
        state = engine.reconcile('test-run', 'source', original['source']['evidence'], 'host rechecked source')
        self.assertEqual(state['status'], 'blocked')
        state = engine.reconcile('test-run', 'consumer', original['consumer']['evidence'], 'host rechecked consumer')
        self.assertEqual(state['status'], 'done')
        self.assertEqual(len(handler.calls), 2)

    def test_fresh_terminal_check_handles_false_missing_and_throwing_verifier(self):
        class Raising(SyntheticHandler):
            def verify(self, task, evidence):
                raise RuntimeError('unavailable evidence')
        for failure in ('false', 'missing', 'exception'):
            with self.subTest(failure=failure):
                p = plan(); p['run_id'] = failure
                self.store.create(p)
                handler = SyntheticHandler()
                engine = self.engine(handler)
                self.assertEqual(engine.tick(failure, 'first')['status'], 'done')
                if failure == 'false':
                    handler.verified = False
                elif failure == 'missing':
                    engine.handlers.clear()
                else:
                    engine.handlers['synthetic'] = Raising()
                state = engine.tick(failure, 'fresh')
                self.assertEqual(state['status'], 'blocked')
                self.assertTrue(state['tasks']['a']['requires_reconciliation'])
                self.assertEqual(len(handler.calls), 1)

    def test_duplicate_done_event_and_cancelled_chain_do_not_replay(self):
        handler = SyntheticHandler()
        self.store.create(plan())
        engine = self.engine(handler)
        state = engine.tick('test-run', 'first')
        handler.verified = False
        self.assertEqual(engine.tick('test-run', 'first'), state)
        state = engine.tick('test-run', 'fresh')
        self.assertEqual(state['status'], 'blocked')
        self.assertEqual(engine.tick('test-run', 'fresh'), state)
        self.store.cancel('test-run', 'explicit cancellation')
        handler.verified = True
        self.assertEqual(engine.tick('test-run', 'cancelled-check')['status'], 'cancelled')
        self.assertEqual(len(handler.calls), 1)
        with self.assertRaises(ValueError):
            engine.reconcile('test-run', 'a', [{'proof': True}], 'host')

    def test_valid_terminal_event_is_durable_and_deduplicated(self):
        class Counted(SyntheticHandler):
            def __init__(self):
                super().__init__()
                self.checks = 0
            def verify(self, task, evidence):
                self.checks += 1
                return True
        handler = Counted()
        self.store.create(plan())
        engine = self.engine(handler)
        engine.tick('test-run', 'first')
        before = handler.checks
        self.assertEqual(engine.tick('test-run', 'fresh')['status'], 'done')
        self.assertGreater(handler.checks, before)
        after = handler.checks
        engine.tick('test-run', 'fresh')
        self.assertEqual(handler.checks, after)
        with sqlite3.connect(self.db_path) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM events').fetchone()[0], 2)
        self.store.cancel('test-run', 'stop')
        engine.tick('test-run', 'cancelled')
        self.assertEqual(handler.checks, after)
        self.assertEqual(len(handler.calls), 1)

    def test_reverse_order_diamond_fences_only_invalid_closure(self):
        class Selective(SyntheticHandler):
            idempotent = False
            bad = set()
            def verify(self, task, evidence):
                return task['task_id'] not in self.bad
        handler = Selective()
        self.store.create(plan(task('join', ['left', 'right']), task('right', ['root']),
                               task('left', ['root']), task('root'), task('other')))
        engine = self.engine(handler)
        for i in range(5):
            state = engine.tick('test-run', 'produce-' + str(i))
        self.assertEqual(state['status'], 'done')
        handler.bad = {'root', 'right'}
        state = engine.tick('test-run', 'invalidate')
        self.assertEqual(state['status'], 'blocked')
        for name in ('root', 'left', 'right', 'join'):
            self.assertTrue(state['tasks'][name]['requires_reconciliation'])
        self.assertEqual(state['tasks']['other']['status'], 'done')
        with self.assertRaises(ValueError):
            engine.reconcile('test-run', 'join', [{'proof': True}], 'out of order')
        handler.bad = set()
        for name in ('root', 'left', 'right', 'join'):
            state = engine.reconcile('test-run', name, [{'proof': True}], 'host checked')
        self.assertEqual(state['status'], 'done')
        self.assertEqual(len(handler.calls), 5)

    def test_portable_cli_persists_current_terminal_invalidation(self):
        root = Path(self.tmp.name)
        (root / 'proof').write_bytes(b'ok')
        source = task('a', action='verify_artifacts')
        source['done_when'] = {'artifacts': [
            {'path': 'proof', 'sha256': hashlib.sha256(b'ok').hexdigest()}]}
        path = root / 'plan.json'
        path.write_text(json.dumps(plan(source)))
        def cli(*args):
            result = subprocess.run([sys.executable, '-m', 'agent_runtime', '--db', self.db_path,
                                     '--legacy-unprotected', *args], cwd=fixtures.ROOT,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        cli('init', str(path))
        self.assertEqual(cli('tick', 'test-run', '--artifact-root', str(root),
                             '--event-id', 'first')['status'], 'done')
        (root / 'proof').write_bytes(b'changed')
        self.assertEqual(cli('tick', 'test-run', '--artifact-root', str(root),
                             '--event-id', 'fresh')['status'], 'blocked')
        current = cli('status', 'test-run')['state']
        self.assertTrue(current['tasks']['a']['requires_reconciliation'])
        self.assertEqual(current['tasks']['a']['attempts'], 1)


if __name__ == '__main__':
    unittest.main()
