from copy import deepcopy
import os
import signal
import unittest
from unittest.mock import Mock, patch

from agent_runtime import task_supervisor as supervisor
from agent_runtime.plan_review import PlanReviewError
from agent_runtime.scheduler import LocalScheduler
from tests import test_managed_supervisor as fixture


class WorkerCancellationTests(unittest.TestCase):
    def project(self):
        value = fixture.WorkerTests()
        value.setUp()
        self.addCleanup(value.doCleanups)
        (value.root / 'result.txt').write_bytes(b'ok')
        child = value.launch()
        fixture.wait_for((value.state_dir / 'final-report.json').exists)
        child.wait(timeout=4)
        self.assertEqual(child.returncode, 0, child.stderr.read())
        return value

    def engine(self, value):
        handlers, authorize, _, verifier, plan_verifier = supervisor.load_backend(value.config, value.store)
        return supervisor.ManagedEngine(value.config, value.store, handlers, authorize,
                                        result_verifier=verifier, plan_review_verifier=plan_verifier)

    def test_cancelled_revalidation_preserves_state_without_callbacks(self):
        value = self.project()
        value.store.cancel(value.plan['run_id'], 'explicit stop')
        snapshot = value.store.snapshot(value.plan['run_id'])
        state = deepcopy(snapshot['state'])
        engine = self.engine(value)
        review = Mock(side_effect=PlanReviewError('revoked'))
        with patch.object(engine, '_review_plan', review), \
             patch.object(engine.handlers['verify_artifacts'], 'verify') as verify:
            self.assertFalse(engine._check_done(snapshot['plan'], state))
        review.assert_not_called()
        verify.assert_not_called()
        self.assertEqual(state, snapshot['state'])

    def test_worker_cancellation_between_done_report_and_revoked_review_is_terminal(self):
        value = self.project()
        marker = value.state_dir / 'final-report.json'
        old_marker = marker.read_bytes()
        original_publish = supervisor.publish
        original_review = supervisor.ManagedEngine._review_plan
        cancelled_state = []
        sleeps = []

        def publish(*args, **kwargs):
            report = original_publish(*args, **kwargs)
            if report['runtime_status'] == 'done' and not cancelled_state:
                value.store.cancel(value.plan['run_id'], 'explicit stop after done observation')
                cancelled_state.append(deepcopy(value.store.snapshot(value.plan['run_id'])['state']))
            return report

        def review(engine, plan):
            if cancelled_state:
                raise PlanReviewError('trusted review revoked after cancellation')
            return original_review(engine, plan)

        class BoundedStop(Exception):
            pass

        def sleep(seconds):
            sleeps.append(seconds)
            if len(sleeps) > 1:
                raise BoundedStop('cancelled worker continued after a second pass')

        LocalScheduler(value.store).heartbeat('foreign-test-service')
        old_signals = {kind: signal.getsignal(kind) for kind in (signal.SIGTERM, signal.SIGINT)}
        result = None
        try:
            with patch.dict(os.environ, {'TMUX': 'explicit-test-marker'}), \
                 patch.object(supervisor, 'publish', side_effect=publish), \
                 patch.object(supervisor.ManagedEngine, '_review_plan', review), \
                 patch.object(supervisor.time, 'sleep', side_effect=sleep):
                try:
                    result = supervisor.worker(value.config)
                except BoundedStop:
                    pass  # Bound the failing baseline; assertions still require natural exit.
        finally:
            for kind, handler in old_signals.items():
                signal.signal(kind, handler)
        self.assertEqual(value.store.snapshot(value.plan['run_id'])['state'], cancelled_state[0])
        self.assertEqual(result, 0)
        self.assertEqual(marker.read_bytes(), old_marker)
        self.assertFalse((value.state_dir / 'live.json').exists())
        with value.store.transaction() as db:
            self.assertEqual([row['id'] for row in db.execute('SELECT id FROM services')],
                             ['foreign-test-service'])

    def test_non_cancelled_invalid_artifact_is_still_rejected(self):
        value = self.project()
        (value.root / 'result.txt').write_bytes(b'changed')
        snapshot = value.store.snapshot(value.plan['run_id'])
        state = snapshot['state']
        engine = self.engine(value)
        engine._check_done(snapshot['plan'], state)
        engine._summary(snapshot['plan'], state)
        self.assertEqual(state['status'], 'failed')
        self.assertEqual(state['tasks']['T1']['status'], 'failed')

    def test_non_cancelled_revoked_review_is_still_blocked(self):
        value = self.project()
        snapshot = value.store.snapshot(value.plan['run_id'])
        state = snapshot['state']
        engine = self.engine(value)
        with patch.object(engine, '_review_plan', side_effect=PlanReviewError('revoked')):
            self.assertFalse(engine._check_done(snapshot['plan'], state))
        self.assertEqual(state['status'], 'blocked')
        self.assertTrue(state['tasks']['T1']['requires_reconciliation'])


if __name__ == '__main__':
    unittest.main()
