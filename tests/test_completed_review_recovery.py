"""Completed effects retain a fence across review revocation and restart."""
import copy
import unittest

from agent_runtime.core import Engine, Store
from tests import test_plan_review_independent as fixtures


class CompletedReviewRecovery(unittest.TestCase):
    def setUp(self):
        self.case = fixtures.IndependentPlanReviewTests()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.case.approve()
        self.store, self.handler, self.engine = self.case.engine()
        self.handler.idempotent = False
        self.run_id = self.case.plan['run_id']

    def restart(self, authorized=True):
        return Engine(Store(self.store.path), {'cpu': self.handler},
                      authorize=lambda *_: authorized, project_root=self.case.root,
                      plan_review_verifier=self.case.session.verify, clock=lambda: self.case.now)

    def multiple(self):
        plan = self.case.make_plan('multi-run')
        child = copy.deepcopy(plan['tasks'][0])
        child.update(task_id='R1-child', depends_on=['R1'],
                     report_path='.agent-runs/multi/child.json', allowed_writes=['child.txt'])
        other = copy.deepcopy(plan['tasks'][0])
        other.update(task_id='R1-other', depends_on=[],
                     report_path='.agent-runs/multi/other.json', allowed_writes=['other.txt'])
        plan['tasks'].extend((child, other))
        self.case.approve(plan)
        store, handler, engine = self.case.engine(plan)
        handler.idempotent = False
        return plan['run_id'], store, handler, engine

    def test_revoked_done_effect_keeps_proof_and_requires_reconciliation(self):
        original = self.engine.tick(self.run_id, 'complete')['tasks']['R1']
        self.case.host.revoked = True
        state = self.engine.tick(self.run_id, 'revoked')
        node = state['tasks']['R1']
        self.assertEqual(state['status'], 'blocked')
        self.assertEqual(node['status'], 'blocked')
        self.assertTrue(node.get('requires_reconciliation'))
        self.assertEqual(node['reason_kind'], 'plan_review_after_effect')
        for key in ('evidence', 'attempts', 'dispatches', 'next_at'):
            self.assertEqual(node[key], original[key])
        self.assertEqual(self.handler.calls, 1)

    def test_restoring_authentication_cannot_self_accept_old_completion(self):
        self.engine.tick(self.run_id, 'complete')
        self.case.host.revoked = True
        self.engine.tick(self.run_id, 'revoked')
        self.case.host.revoked = False
        engine = self.restart()
        for event in ('restored', 'another-wake'):
            state = engine.tick(self.run_id, event)
            self.assertEqual(state['status'], 'blocked')
        self.assertEqual(self.handler.calls, 1)
        with self.assertRaises(ValueError):
            self.restart(authorized=False).reconcile(self.run_id, 'R1', ['cpu-proof'], 'host')
        with self.assertRaises(ValueError):
            engine.reconcile(self.run_id, 'R1', [], 'host')
        state = engine.reconcile(self.run_id, 'R1', ['cpu-proof'], 'host rechecked completed effect')
        self.assertEqual(state['status'], 'done')
        self.assertEqual(self.handler.calls, 1)

    def test_cancelled_completed_chain_stays_cancelled_across_revocation(self):
        self.engine.tick(self.run_id, 'complete')
        self.store.cancel(self.run_id, 'explicit user stop')
        original = copy.deepcopy(self.store.snapshot(self.run_id)['state'])
        self.case.host.revoked = True
        self.assertEqual(self.engine.tick(self.run_id, 'revoked'), original)
        self.case.host.revoked = False
        self.assertEqual(self.restart().tick(self.run_id, 'restored'), original)
        with self.assertRaises(ValueError):
            self.restart().reconcile(self.run_id, 'R1', ['cpu-proof'], 'host')
        self.assertEqual(self.handler.calls, 1)

    def test_completed_prefix_fence_blocks_descendants_after_review_restoration(self):
        run_id, store, handler, engine = self.multiple()
        self.assertEqual(engine.tick(run_id, 'first')['tasks']['R1']['status'], 'done')
        self.case.host.revoked = True
        engine.tick(run_id, 'revoked')
        self.case.host.revoked = False
        state = engine.tick(run_id, 'restored')
        self.assertEqual(state['tasks']['R1']['status'], 'blocked')
        self.assertTrue(state['tasks']['R1'].get('requires_reconciliation'))
        self.assertEqual(state['tasks']['R1-child']['attempts'], 0)
        # An independent, previously unstarted task may run after authentication
        # returns; the dependent task still waits for explicit reconciliation.
        self.assertEqual(handler.calls, 2)
        engine.reconcile(run_id, 'R1', ['cpu-proof'], 'host rechecked parent effect')
        state = engine.tick(run_id, 'child')
        self.assertEqual(state['status'], 'done')
        self.assertEqual(handler.calls, 3)

    def test_all_completed_nodes_stay_fenced_in_mixed_dag(self):
        run_id, store, handler, engine = self.multiple()
        for event in ('one', 'two', 'three'):
            state = engine.tick(run_id, event)
        self.assertEqual(state['status'], 'done')
        self.case.host.revoked = True
        state = engine.tick(run_id, 'revoked')
        self.assertTrue(all(n.get('requires_reconciliation') for n in state['tasks'].values()))
        self.case.host.revoked = False
        self.assertEqual(engine.tick(run_id, 'restored')['status'], 'blocked')
        for name in ('R1', 'R1-child', 'R1-other'):
            state = engine.reconcile(run_id, name, ['cpu-proof'], 'host checked effect')
        self.assertEqual(state['status'], 'done')
        self.assertEqual(handler.calls, 3)


if __name__ == '__main__':
    unittest.main()
