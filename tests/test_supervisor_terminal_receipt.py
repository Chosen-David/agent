"""Resume receipts recheck real completed effects; tmux transport is simulated."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from agent_runtime import task_supervisor as supervisor
from agent_runtime.task_manifest import atomic_json
from tests import test_managed_supervisor as fixture
from tests import test_result_validation as results


class TerminalReceiptTests(unittest.TestCase):
    def project(self, complete=True):
        value = fixture.WorkerTests()
        value.setUp()
        self.addCleanup(value.doCleanups)
        value.config['session'] = 'agent-' + hashlib.sha256(str(value.state_dir).encode()).hexdigest()[:16]
        atomic_json(value.config_path, value.config)
        if complete:
            (value.root / 'result.txt').write_bytes(b'ok')
            child = value.launch()
            fixture.wait_for((value.state_dir / 'final-report.json').exists)
            child.wait(timeout=4)
            self.assertEqual(child.returncode, 0)
            self.assertTrue(json.loads((value.state_dir / 'final-report.json').read_text())['all_reportable'])
        atomic_json(value.root / 'plan.json', value.plan)
        return value

    def resume(self, value, existing=True):
        def tmux(*args, **kwargs):
            self.assertIn(args[0], ('has-session', 'list-panes'))
            return subprocess.CompletedProcess([], 0 if existing else 1, '1\n', '')
        with patch.object(supervisor.shutil, 'which', return_value='/fixture/tmux'), \
             patch.object(supervisor, 'tmux', side_effect=tmux):
            return supervisor.start(value.root / 'plan.json', value.root, value.state_dir, allow_legacy=True)

    def both_sessions(self, function):
        for existing in (True, False):
            with self.subTest(existing_session=existing):
                original = self.resume
                self.resume = lambda value: original(value, existing=existing)
                try:
                    function()
                finally:
                    self.resume = original

    def test_unchanged_genuine_completion_remains_reportable(self):
        self.both_sessions(self._unchanged_genuine_completion_remains_reportable)

    def _unchanged_genuine_completion_remains_reportable(self):
        value = self.project()
        self.assertEqual(self.resume(value)['status'], 'completed')
        self.assertTrue(json.loads((value.state_dir / 'final-report.json').read_text())['all_reportable'])

    def test_changed_artifact_or_valid_report_cannot_reuse_final_marker(self):
        self.both_sessions(self._changed_artifact_or_valid_report_cannot_reuse_final_marker)

    def _changed_artifact_or_valid_report_cannot_reuse_final_marker(self):
        for mutation in ('artifact', 'report'):
            with self.subTest(mutation=mutation):
                value = self.project()
                marker = value.state_dir / 'final-report.json'
                original = marker.read_bytes()
                before = deepcopy(value.store.snapshot(value.plan['run_id'])['state']['tasks']['T1'])
                if mutation == 'artifact':
                    (value.root / 'result.txt').write_bytes(b'changed')
                else:
                    atomic_json(value.root / value.plan['tasks'][0]['report_path'], {
                        'task_id': 'T1', 'summary': 'changed report',
                        'data': [{'kind': 'synthetic', 'description': 'different valid report bytes'}]})
                receipt = self.resume(value)
                self.assertEqual(receipt['status'], 'blocked')
                self.assertEqual(receipt['runtime_status'], 'blocked')
                self.assertIn('verification', receipt['reason'])
                after = value.store.snapshot(value.plan['run_id'])['state']['tasks']['T1']
                self.assertEqual(after['evidence'], before['evidence'])
                self.assertEqual(after['attempts'], before['attempts'])
                self.assertEqual(marker.read_bytes(), original)
                self.assertFalse(json.loads((value.state_dir / 'progress.json').read_text())['all_reportable'])

    def test_cancellation_precedes_old_final_marker_and_crash_block(self):
        self.both_sessions(self._cancellation_precedes_old_final_marker_and_crash_block)

    def _cancellation_precedes_old_final_marker_and_crash_block(self):
        for crash_blocked in (False, True):
            with self.subTest(crash_blocked=crash_blocked):
                value = self.project()
                marker = value.state_dir / 'final-report.json'
                original = marker.read_bytes()
                value.store.cancel(value.plan['run_id'], 'explicit test cancellation')
                with patch.object(supervisor, 'read_crash_state', return_value={
                        'status': 'blocked' if crash_blocked else 'ready'}):
                    receipt = self.resume(value)
                self.assertEqual(receipt['status'], 'cancelled')
                self.assertEqual(receipt['runtime_status'], 'cancelled')
                self.assertEqual(marker.read_bytes(), original)

    def test_nonterminal_store_with_marker_does_not_certify_completion(self):
        self.both_sessions(self._nonterminal_store_with_marker_does_not_certify_completion)

    def _nonterminal_store_with_marker_does_not_certify_completion(self):
        value = self.project(complete=False)
        marker = value.state_dir / 'final-report.json'
        marker.write_bytes(b'old non-authoritative marker')
        receipt = self.resume(value)
        self.assertEqual(receipt['status'], 'blocked')
        self.assertEqual(receipt['runtime_status'], 'active')
        self.assertEqual(marker.read_bytes(), b'old non-authoritative marker')
        self.assertEqual(value.store.snapshot(value.plan['run_id'])['state']['tasks']['T1']['attempts'], 0)


    def test_cancellation_after_initial_status_skips_terminal_verification(self):
        self.both_sessions(self._cancellation_after_initial_status_skips_terminal_verification)

    def _cancellation_after_initial_status_skips_terminal_verification(self):
        value = self.project()
        original = (value.state_dir / 'final-report.json').read_bytes()
        actual_status = supervisor.status
        calls = []
        def cancel_after_read(config):
            receipt = actual_status(config)
            if not calls:
                value.store.cancel(value.plan['run_id'], 'cancel after initial read')
            calls.append(True)
            return receipt
        with patch.object(supervisor, 'status', side_effect=cancel_after_read),              patch.object(supervisor.ManagedEngine, '_check_done', side_effect=AssertionError('cancelled task verified')):
            receipt = self.resume(value)
        self.assertEqual(receipt['status'], 'cancelled')
        self.assertEqual((value.state_dir / 'final-report.json').read_bytes(), original)

    def test_cancellation_during_publication_cannot_become_completed(self):
        self.both_sessions(self._cancellation_during_publication_cannot_become_completed)

    def _cancellation_during_publication_cannot_become_completed(self):
        value = self.project()
        original = (value.state_dir / 'final-report.json').read_bytes()
        actual_publish = supervisor.publish
        def cancel_after_publish(*args, **kwargs):
            report = actual_publish(*args, **kwargs)
            value.store.cancel(value.plan['run_id'], 'cancel during publication')
            return report
        with patch.object(supervisor, 'publish', side_effect=cancel_after_publish):
            receipt = self.resume(value)
        self.assertEqual(receipt['status'], 'cancelled')
        self.assertEqual((value.state_dir / 'final-report.json').read_bytes(), original)


    def test_scientific_gate_requires_current_trusted_verifier_on_resume(self):
        for mode in ('valid', 'missing', 'rejected'):
            with self.subTest(verifier=mode):
                case = results.ResultValidationTests()
                case.setUp()
                self.addCleanup(case.doCleanups)
                plan, store, engine, _ = case.integrated_chain()
                for number in range(3):
                    engine.tick(plan['run_id'], 'complete-' + str(number))
                self.assertEqual(store.snapshot(plan['run_id'])['state']['status'], 'done')
                state_dir = case.root / 'resume'
                state_dir.mkdir()
                Path(store.path).rename(state_dir / 'state.sqlite')
                store = supervisor.Store(state_dir / 'state.sqlite')
                config = {'run_id': plan['run_id'], 'project_root': str(case.root),
                          'state_dir': str(state_dir), 'adapter': None, 'allow_legacy': True,
                          'session': 'agent-' + hashlib.sha256(str(state_dir).encode()).hexdigest()[:16]}
                report = supervisor.publish(config, store, result_verifier=results.independent_verify)
                self.assertTrue(report['all_reportable'])
                marker = state_dir / 'final-report.json'
                atomic_json(marker, report)
                original = marker.read_bytes()
                atomic_json(case.root / 'plan.json', plan)
                def rejected(root, manifest, protocol):
                    verdict = results.independent_verify(root, manifest, protocol)
                    verdict['checks']['data_integrity']['verdict'] = 'fail'
                    return verdict
                verifier = {'valid': results.independent_verify, 'missing': None, 'rejected': rejected}[mode]
                handlers = {
                    'verify_artifacts': results.ReportingHandler(results.ArtifactHandler(case.root), case.root,
                                                                  result_verifier=verifier),
                    'verify_experiment_result': results.ReportingHandler(
                        results.ResultValidationHandler(case.root, verifier), case.root, result_verifier=verifier)}
                def tmux(*args, **kwargs):
                    self.assertIn(args[0], ('has-session', 'list-panes'))
                    return subprocess.CompletedProcess([], 0, '1\n', '')
                with patch.object(supervisor.shutil, 'which', return_value='/fixture/tmux'),                      patch.object(supervisor, 'tmux', side_effect=tmux),                      patch.object(supervisor, 'load_backend', return_value=(
                         handlers, lambda *_: True, None, verifier, None)):
                    receipt = supervisor.start(case.root / 'plan.json', case.root, state_dir, allow_legacy=True)
                self.assertEqual(receipt['status'], 'completed' if mode == 'valid' else 'blocked')
                if mode != 'valid':
                    self.assertEqual(marker.read_bytes(), original)


class TerminalRecoveryTests(unittest.TestCase):
    """Actual startup revalidation/SQLite; tmux transport only is simulated."""
    def project(self, dependent=False):
        import tempfile
        from types import SimpleNamespace
        temporary = tempfile.TemporaryDirectory(prefix='terminal-recovery-')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        task_file = root / 'TASK.md'
        task_file.write_text('- [ ] [T1] Parent\n' + ('- [ ] [T2] Child\n' if dependent else ''))
        plan = supervisor.prepare(task_file, 'terminal-recovery', 'manual', 'bounded CPU fixture',
                                  review_required=False)
        plan['supervision'].update(min_seconds=1, max_seconds=2)
        for index, task in enumerate(plan['tasks']):
            name = task['task_id'] + '.txt'
            (root / name).write_bytes(b'ok')
            task.update(action='verify_artifacts', max_attempts=2, estimated_seconds=1,
                        depends_on=['T1'] if index else [],
                        done_when={'artifacts': [{'path': name, 'sha256': hashlib.sha256(b'ok').hexdigest()}]})
            atomic_json(root / task['report_path'], {'task_id': task['task_id'], 'summary': 'fixture',
                        'data': [{'kind': 'synthetic', 'description': 'local bytes'}]})
        state_dir = root / 'run'
        store = supervisor.Store(state_dir / 'state.sqlite')
        store.create(plan)
        config = {'run_id': plan['run_id'], 'project_root': str(root), 'state_dir': str(state_dir),
                  'session': 'agent-' + hashlib.sha256(str(state_dir).encode()).hexdigest()[:16],
                  'adapter': None, 'allow_legacy': True}
        handlers, authorize, _, verifier, plan_verifier = supervisor.load_backend(config, store)
        engine = supervisor.ManagedEngine(config, store, handlers, authorize,
                         result_verifier=verifier, plan_review_verifier=plan_verifier)
        for index in range(len(plan['tasks'])):
            engine.tick(plan['run_id'], 'complete-' + str(index))
        self.assertEqual(store.snapshot(plan['run_id'])['state']['status'], 'done')
        report = supervisor.publish(config, store)
        self.assertTrue(report['all_reportable'])
        atomic_json(state_dir / 'final-report.json', report)
        atomic_json(state_dir / 'launch.json', config)
        atomic_json(root / 'plan.json', plan)
        return SimpleNamespace(root=root, state_dir=state_dir, store=store, plan=plan,
                               config=config, engine=engine)

    def resume(self, value):
        return TerminalReceiptTests.resume(self, value)

    def assert_history(self, value, before):
        after = value.store.snapshot(value.plan['run_id'])['state']['tasks']
        for key, old in before.items():
            for field in ('evidence', 'attempts', 'dispatches'):
                self.assertEqual(after[key].get(field), old.get(field))

    def test_startup_rejection_can_reconcile_restored_artifact_or_report_without_replay(self):
        for mutation in ('artifact', 'report'):
            with self.subTest(mutation=mutation):
                value = self.project()
                before = deepcopy(value.store.snapshot(value.plan['run_id'])['state']['tasks'])
                marker = (value.state_dir / 'final-report.json').read_bytes()
                path = (value.root / 'T1.txt' if mutation == 'artifact' else
                        value.root / value.plan['tasks'][0]['report_path'])
                original = path.read_bytes()
                path.write_bytes(b'changed')
                receipt = self.resume(value)
                self.assertEqual(receipt['status'], 'blocked')
                state = value.store.snapshot(value.plan['run_id'])['state']
                self.assertEqual(state['tasks']['T1']['status'], 'blocked')
                self.assertEqual(state['tasks']['T1']['reason_kind'], 'terminal_evidence')
                self.assertTrue(state['tasks']['T1']['requires_reconciliation'])
                self.assertEqual((value.state_dir / 'final-report.json').read_bytes(), marker)
                self.assert_history(value, before)
                path.write_bytes(original)
                # Returning bytes alone must not silently restore acceptance.
                self.assertEqual(self.resume(value)['status'], 'blocked')
                evidence = before['T1']['evidence']
                authorize = value.engine.authorize
                value.engine.authorize = lambda *_: False
                with self.assertRaises(ValueError):
                    value.engine.reconcile(value.plan['run_id'], 'T1', evidence, 'denied fixture')
                value.engine.authorize = authorize
                with self.assertRaises(ValueError):
                    value.engine.reconcile(value.plan['run_id'], 'T1', ['wrong'], 'wrong proof')
                with patch.object(supervisor.ArtifactHandler, 'run', side_effect=AssertionError('action replay')):
                    value.engine.reconcile(value.plan['run_id'], 'T1', evidence, 'host checked restored bytes')
                    self.assertEqual(self.resume(value)['status'], 'completed')
                self.assert_history(value, before)

    def test_startup_dependency_invalidation_requires_each_restored_acceptance(self):
        value = self.project(dependent=True)
        before = deepcopy(value.store.snapshot(value.plan['run_id'])['state']['tasks'])
        (value.root / 'T1.txt').write_bytes(b'changed')
        self.assertEqual(self.resume(value)['status'], 'blocked')
        state = value.store.snapshot(value.plan['run_id'])['state']
        for key in ('T1', 'T2'):
            self.assertEqual(state['tasks'][key]['status'], 'blocked')
            self.assertTrue(state['tasks'][key]['requires_reconciliation'])
        self.assertIn('depends on invalid evidence', state['tasks']['T2']['reason'])
        (value.root / 'T1.txt').write_bytes(b'ok')
        with self.assertRaises(ValueError):
            value.engine.reconcile(value.plan['run_id'], 'T2', before['T2']['evidence'], 'too early')
        with patch.object(supervisor.ArtifactHandler, 'run', side_effect=AssertionError('action replay')):
            value.engine.reconcile(value.plan['run_id'], 'T1', before['T1']['evidence'], 'restored parent')
            self.assertEqual(self.resume(value)['status'], 'blocked')
            value.engine.reconcile(value.plan['run_id'], 'T2', before['T2']['evidence'], 'revalidated child')
            self.assertEqual(self.resume(value)['status'], 'completed')
        self.assert_history(value, before)

    def test_startup_does_not_reclassify_old_failed_or_cancelled_ledgers(self):
        for status in ('failed', 'cancelled'):
            with self.subTest(status=status):
                value = self.project()
                if status == 'cancelled':
                    value.store.cancel(value.plan['run_id'], 'explicit fixture cancellation')
                else:
                    with value.store.transaction() as db:
                        _, state = value.store.load(db, value.plan['run_id'])
                        state['tasks']['T1'].update(status='failed', reason='explicit trusted failure',
                                                  reason_kind='adapter_result')
                        state['status'] = 'failed'
                        value.store.save(db, value.plan['run_id'], state)
                before = deepcopy(value.store.snapshot(value.plan['run_id'])['state'])
                receipt = self.resume(value)
                self.assertEqual(receipt['runtime_status'], status)
                self.assertEqual(value.store.snapshot(value.plan['run_id'])['state'], before)


if __name__ == '__main__':
    unittest.main()
