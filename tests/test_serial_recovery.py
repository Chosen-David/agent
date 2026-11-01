"""Upgrade recovery uses durable observations, never cursor order as ownership."""
from pathlib import Path
import tempfile
import unittest

from agent_runtime.core import Engine, Outcome, Store
from test_single_main import plan


class SerialRecoveryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = Store(Path(tmp.name) / 'state.sqlite')
        self.store.create(plan())
        self.calls = []
        self.now = 1
        owner = self

        class Handler:
            idempotent = True
            def run(self, task, context):
                owner.calls.append(task['task_id'])
                return Outcome('complete', evidence=['verified'])
            def verify(self, task, evidence):
                return evidence == ['verified']
        self.handler = Handler()

    def seed(self, nodes):
        with self.store.transaction() as db:
            _, state = self.store.load(db, 'serial')
            state.pop('active_step', None)
            state['claim_cursor'] = 1
            for key, values in nodes.items():
                state['tasks'][key].update(values)
            self.store.save(db, 'serial', state)

    def tick(self, event):
        return Engine(Store(self.store.path), {'step': self.handler},
                      authorize=lambda *_: True, allow_legacy=True,
                      clock=lambda: self.now).tick('serial', event)

    def test_old_pending_restores_step_before_deadline_and_after_restart(self):
        self.seed({'A': {'status': 'todo', 'attempts': 1, 'next_at': 5,
                         'reason_kind': 'adapter_result', 'reason': 'pending'}})
        state = self.tick('early')
        self.assertEqual(self.calls, [])
        self.assertEqual(state.get('active_step'), 'A')
        self.assertEqual(state['tasks']['A']['attempts'], 1)
        self.now = 5
        self.tick('resume')
        self.tick('next')
        self.assertEqual(self.calls, ['A', 'B'])

    def test_old_wait_pending_with_refunded_attempts_is_not_fresh(self):
        self.seed({'A': {'pending_since': 1, 'pending_polls': 2, 'next_at': 5}})
        state = self.tick('wait')
        self.assertEqual(self.calls, [])
        self.assertEqual(state.get('active_step'), 'A')
        self.assertEqual(state['tasks']['A']['pending_polls'], 2)

    def test_expired_idempotent_claim_resumes_same_step(self):
        self.seed({'A': {'status': 'doing', 'attempts': 1, 'token': 'old', 'lease_until': 0}})
        self.tick('expired')
        self.assertEqual(self.calls, ['A'])

    def test_expired_unknown_claim_requires_reconciliation_before_next_step(self):
        self.handler.idempotent = False
        self.seed({'A': {'status': 'doing', 'attempts': 1, 'token': 'old', 'lease_until': 0}})
        state = self.tick('unknown')
        self.assertEqual(self.calls, [])
        self.assertEqual(state['tasks']['A']['reason_kind'], 'ambiguous')
        engine = Engine(self.store, {'step': self.handler}, authorize=lambda *_: True,
                        allow_legacy=True, clock=lambda: self.now)
        engine.reconcile('serial', 'A', ['verified'], 'host observed completion')
        self.tick('after-reconcile')
        self.assertEqual(self.calls, ['B'])

    def test_multiple_old_pending_steps_block_without_guess_or_budget_reset(self):
        spec = plan()
        spec['tasks'].append(dict(spec['tasks'][0], task_id='C'))
        self.store = Store(Path(self.store.path).with_name('multiple.sqlite'))
        self.store.create(spec)
        self.seed({key: {'attempts': 1, 'next_at': 5, 'reason': 'pending'} for key in ('A', 'B')})
        before = self.store.snapshot('serial')['state']['tasks']
        state = self.tick('multiple')
        self.assertEqual(self.calls, [])
        self.assertEqual(state['status'], 'blocked')
        self.assertIn('A', state['serial_recovery_error'])
        self.assertIn('B', state['serial_recovery_error'])
        self.assertEqual(state['tasks'], before)
        self.now = 10
        self.tick('still-multiple')
        self.assertEqual(self.calls, [])

    def test_completed_active_does_not_hide_another_old_pending_step(self):
        self.seed({'A': {'attempts': 1, 'next_at': 5},
                   'B': {'status': 'done', 'evidence': ['verified']}})
        with self.store.transaction() as db:
            _, state = self.store.load(db, 'serial')
            state['active_step'] = 'B'
            self.store.save(db, 'serial', state)
        state = self.tick('completed-active')
        self.assertEqual(state.get('active_step'), 'A')
        self.assertEqual(self.calls, [])

    def test_multiple_ambiguous_steps_resume_only_after_explicit_convergence(self):
        self.seed({key: {'status': 'blocked', 'attempts': 1,
                         'reason_kind': 'ambiguous'} for key in ('A', 'B')})
        self.assertEqual(self.tick('ambiguous')['status'], 'blocked')
        engine = Engine(self.store, {'step': self.handler}, authorize=lambda *_: True,
                        allow_legacy=True, clock=lambda: self.now)
        engine.reconcile('serial', 'A', ['verified'], 'host verified A')
        state = self.tick('one-left')
        self.assertEqual(state.get('active_step'), 'B')
        self.assertNotIn('serial_recovery_error', state)
        self.assertEqual(self.calls, [])
        engine.reconcile('serial', 'B', ['verified'], 'host verified B')
        self.assertEqual(self.tick('finished')['status'], 'done')

    def test_live_legacy_lease_is_preserved_without_new_dispatch(self):
        self.seed({'A': {'status': 'doing', 'attempts': 1, 'token': 'live', 'lease_until': 10}})
        state = self.tick('live')
        self.assertEqual(state['tasks']['A']['token'], 'live')
        self.assertEqual(state['tasks']['A']['lease_until'], 10)
        self.assertEqual(state['tasks']['A']['attempts'], 1)
        self.assertEqual(self.calls, [])

    def test_cancelled_old_pending_chain_is_not_recovered_or_executed(self):
        self.seed({'A': {'attempts': 1, 'next_at': 5}})
        self.store.cancel('serial', 'user cancelled', now=1)
        before = self.store.snapshot('serial')['state']
        self.assertEqual(self.tick('cancelled'), before)
        self.assertEqual(self.calls, [])

    def test_fresh_and_definite_failed_steps_keep_normal_readiness(self):
        self.tick('fresh')
        self.assertEqual(self.calls, ['A'])
        self.calls.clear()
        self.seed({'A': {'status': 'failed', 'attempts': 3}})
        self.tick('failed')
        self.assertEqual(self.calls, ['B'])
