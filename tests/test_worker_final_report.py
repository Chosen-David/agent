import json
import os
import signal
import unittest
from unittest.mock import patch

from agent_runtime import task_supervisor as supervisor
from agent_runtime.plan_review import PlanReviewError
from agent_runtime.scheduler import LocalScheduler
from tests import test_worker_cancellation as cancellation


class RecoveryObserved(BaseException):
    pass


class WorkerFinalReportTests(unittest.TestCase):
    def project(self):
        fixture = cancellation.WorkerCancellationTests()
        self.addCleanup(fixture.doCleanups)
        return fixture.project()

    def run_worker(self, value, change, *, recover=False, revoke_review=False):
        stop = LocalScheduler.stop
        load = supervisor.load_backend
        from agent_runtime import plan_review
        check = plan_review.check_plan_review
        observed, stopped = [], []

        def stop_at_boundary(scheduler, monitor_id):
            change()
            stopped.append(monitor_id)
            return stop(scheduler, monitor_id)

        def maintain(report):
            with value.store.transaction() as db:
                services = [row['id'] for row in db.execute('SELECT id FROM services')]
            observed.append((report, (value.state_dir / 'live.json').exists(), services))
            if recover:
                raise RecoveryObserved()

        def backend(*args):
            result = list(load(*args))
            result[2] = maintain
            return tuple(result)

        def review(*args, **kwargs):
            if revoke_review and stopped:
                raise PlanReviewError('review revoked at final delivery')
            return check(*args, **kwargs)

        signals = {kind: signal.getsignal(kind) for kind in (signal.SIGTERM, signal.SIGINT)}
        try:
            with patch.dict(os.environ, {'TMUX': 'explicit-test-marker'}), \
                 patch.object(LocalScheduler, 'stop', stop_at_boundary), \
                 patch.object(supervisor, 'load_backend', side_effect=backend), \
                 patch.object(plan_review, 'check_plan_review', side_effect=review), \
                 patch.object(supervisor.time, 'sleep'):
                if recover:
                    with self.assertRaises(RecoveryObserved):
                        supervisor.worker(value.config)
                else:
                    self.assertEqual(supervisor.worker(value.config), 0)
        finally:
            for kind, handler in signals.items():
                signal.signal(kind, handler)
        self.assertTrue(stopped)
        return observed

    def assert_recovery(self, value, observed, marker_bytes):
        self.assertEqual(len(observed), 1)
        report, live, services = observed[0]
        self.assertFalse(report['all_reportable'])
        self.assertTrue(live)
        self.assertTrue(any(service.startswith('tmux:') for service in services))
        self.assertIn('foreign-test-service', services)
        self.assertEqual((value.state_dir / 'final-report.json').read_bytes(), marker_bytes)
        self.assertEqual(json.loads((value.state_dir / 'progress.json').read_text()), report)
        self.assertFalse((value.state_dir / 'live.json').exists())
        with value.store.transaction() as db:
            self.assertEqual([row['id'] for row in db.execute('SELECT id FROM services')],
                             ['foreign-test-service'])
        return report

    def test_rejected_changed_reports_preserve_marker_and_reach_live_recovery(self):
        for valid in (False, True):
            with self.subTest(valid=valid):
                value = self.project()
                marker = (value.state_dir / 'final-report.json').read_bytes()
                path = value.root / value.plan['tasks'][0]['report_path']

                def change():
                    if valid:
                        payload = json.loads(path.read_text())
                        payload['summary'] = 'changed after accepted report'
                        path.write_text(json.dumps(payload))
                    else:
                        path.write_bytes(b'invalid report after accepted observation')

                LocalScheduler(value.store).heartbeat('foreign-test-service')
                report = self.assert_recovery(value, self.run_worker(value, change, recover=True), marker)
                node = report['requirements'][0]['nodes'][0]
                self.assertEqual(node['status'], 'needs_review')
                self.assertTrue(node['reason'])

    def test_final_review_rejection_reaches_recovery_with_current_reason(self):
        value = self.project()
        marker = (value.state_dir / 'final-report.json').read_bytes()
        LocalScheduler(value.store).heartbeat('foreign-test-service')
        report = self.assert_recovery(value, self.run_worker(
            value, lambda: None, recover=True, revoke_review=True), marker)
        self.assertIn('review revoked at final delivery', report['source_error'])

    def test_cancellation_at_stop_preserves_old_marker_and_exits_naturally(self):
        value = self.project()
        marker = (value.state_dir / 'final-report.json').read_bytes()
        cancelled = []

        def cancel():
            value.store.cancel(value.plan['run_id'], 'cancel at final delivery')
            cancelled.append(value.store.snapshot(value.plan['run_id'])['state'])

        observed = self.run_worker(value, cancel)
        self.assertEqual(value.store.snapshot(value.plan['run_id'])['state'], cancelled[0])
        self.assertEqual((value.state_dir / 'final-report.json').read_bytes(), marker)
        self.assertFalse((value.state_dir / 'live.json').exists())
        self.assertEqual(observed[0][0]['runtime_status'], 'cancelled')

    def test_unchanged_final_report_is_delivered_and_worker_exits(self):
        value = self.project()
        observed = self.run_worker(value, lambda: None)
        self.assertEqual(observed, [])
        report = json.loads((value.state_dir / 'final-report.json').read_text())
        self.assertTrue(report['all_reportable'])
        self.assertEqual(report['runtime_status'], 'done')
        self.assertFalse((value.state_dir / 'live.json').exists())


if __name__ == '__main__':
    unittest.main()
