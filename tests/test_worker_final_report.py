import json
from copy import deepcopy
import os
import signal
import unittest
from unittest.mock import patch

from agent_runtime import task_supervisor as supervisor
from agent_runtime.core import Store
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
                before = value.store.snapshot(value.plan['run_id'])['state']['tasks']['T1']
                report = self.assert_recovery(value, self.run_worker(value, change, recover=True), marker)
                node = report['requirements'][0]['nodes'][0]
                self.assertEqual(node['status'], 'failed')
                self.assertTrue(node['reason'])
                self.assert_terminal_evidence_preserved(value, {'T1': before})

    def assert_terminal_evidence_preserved(self, value, before):
        state = value.store.snapshot(value.plan['run_id'])['state']
        self.assertEqual(state['status'], 'failed')
        for task_id, old in before.items():
            node = state['tasks'][task_id]
            self.assertEqual(node['status'], 'failed')
            for field in ('evidence', 'attempts', 'dispatches'):
                self.assertEqual(node.get(field), old.get(field))

    def test_artifact_changes_at_monitor_stop_reach_live_recovery(self):
        for mutation in ('bytes', 'missing', 'directory'):
            with self.subTest(mutation=mutation):
                value = self.project()
                marker = (value.state_dir / 'final-report.json').read_bytes()
                before = value.store.snapshot(value.plan['run_id'])['state']['tasks']

                def change():
                    artifact = value.root / 'result.txt'
                    if mutation == 'bytes':
                        artifact.write_bytes(b'changed at monitor stop')
                    else:
                        artifact.unlink()
                        if mutation == 'directory':
                            artifact.mkdir()

                LocalScheduler(value.store).heartbeat('foreign-test-service')
                self.assert_recovery(value, self.run_worker(value, change, recover=True), marker)
                self.assert_terminal_evidence_preserved(value, before)

    def test_post_stop_verifier_exception_is_not_a_success_report(self):
        value = self.project()
        marker = (value.state_dir / 'final-report.json').read_bytes()
        before = value.store.snapshot(value.plan['run_id'])['state']['tasks']
        stopped = []
        verify = supervisor.ArtifactHandler.verify

        def verify_at_boundary(handler, task, evidence):
            if stopped:
                raise RuntimeError('verification unavailable after monitor stop')
            return verify(handler, task, evidence)

        LocalScheduler(value.store).heartbeat('foreign-test-service')
        with patch.object(supervisor.ArtifactHandler, 'verify', verify_at_boundary):
            self.assert_recovery(value, self.run_worker(
                value, lambda: stopped.append(True), recover=True), marker)
        self.assert_terminal_evidence_preserved(value, before)

    def test_post_stop_check_invalidates_completed_dependency_without_replay(self):
        value = cancellation.fixture.WorkerTests()
        value.setUp()
        self.addCleanup(value.doCleanups)
        child = deepcopy(value.plan['tasks'][0])
        child.update(task_id='T2', depends_on=['T1'])
        child['report_path'] = child['report_path'].replace('T1', 'T2')
        child['done_when']['artifacts'][0]['path'] = 'child.txt'
        value.plan['tasks'].append(child)
        supervisor.atomic_json(value.root / child['report_path'], {
            'task_id': 'T2', 'summary': 'dependent fixture',
            'data': [{'kind': 'synthetic', 'description': 'local dependency evidence'}]})
        for name in ('result.txt', 'child.txt'):
            (value.root / name).write_bytes(b'ok')
        value.state_dir = value.root / 'dependent-run'
        value.store = Store(value.state_dir / 'state.sqlite')
        value.store.create(value.plan)
        value.config['state_dir'] = str(value.state_dir)
        value.config_path = value.state_dir / 'launch.json'
        supervisor.atomic_json(value.config_path, value.config)
        process = value.launch()
        cancellation.fixture.wait_for((value.state_dir / 'final-report.json').exists)
        process.wait(timeout=4)
        self.assertEqual(process.returncode, 0, process.stderr.read())
        marker = (value.state_dir / 'final-report.json').read_bytes()
        before = value.store.snapshot(value.plan['run_id'])['state']['tasks']
        LocalScheduler(value.store).heartbeat('foreign-test-service')
        with patch.object(supervisor.ArtifactHandler, 'run', side_effect=AssertionError('terminal replay')):
            self.assert_recovery(value, self.run_worker(
                value, lambda: (value.root / 'result.txt').write_bytes(b'changed'), recover=True), marker)
        self.assert_terminal_evidence_preserved(value, before)
        state = value.store.snapshot(value.plan['run_id'])['state']
        self.assertIn('depends on invalid evidence', state['tasks']['T2']['reason'])

    def test_unchanged_artifact_is_verified_after_stop_without_running_actions(self):
        value = self.project()
        stopped, checks = [], []
        verify = supervisor.ArtifactHandler.verify

        def verify_at_boundary(handler, task, evidence):
            checks.append(bool(stopped))
            return verify(handler, task, evidence)

        with patch.object(supervisor.ArtifactHandler, 'verify', verify_at_boundary), \
             patch.object(supervisor.ArtifactHandler, 'run', side_effect=AssertionError('terminal replay')):
            self.assertEqual(self.run_worker(value, lambda: stopped.append(True)), [])
        self.assertIn(True, checks)
        self.assertTrue(json.loads((value.state_dir / 'final-report.json').read_text())['all_reportable'])

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
