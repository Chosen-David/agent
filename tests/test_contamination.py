"""CPU-only host integration: actual process exit plus persistent result gates."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.contamination import Contamination, assert_not_revoked
from agent_runtime.result_validation import inspect_result, check_task_results
from test_result_validation import make_fixture, independent_verify


class ContaminationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.calls = []
        self.control = Contamination(self.root, authorize=lambda action, bound: True)
        for name, content in [('code.py', 'bug'), ('config.json', '{}'), ('data.json', '[1]'), ('proof.txt', 'reproduced: expected 1, got 2')]:
            (self.root / name).write_text(content)
        self.binding = self.control.bind(self.spec('old'))
        self.finding = {'status': 'confirmed', 'affects_run': True, 'reason': 'off-by-one changes this run',
                        'evidence': [self.ref('proof.txt')]}

    def ref(self, name):
        return {'path': name, 'sha256': hashlib.sha256((self.root / name).read_bytes()).hexdigest()}

    def spec(self, run):
        return {'run_id': run, 'result_ids': ['result-' + run], 'task_refs': ['EXP-1'],
                'job': {'host': 'cpu-test', 'scheduler_job_id': 'owned-' + run},
                'code': [self.ref('code.py')], 'config': [self.ref('config.json')], 'data': [self.ref('data.json')],
                'inventory_complete': True,
                'owned_paths': [f'agent_doc/results/{run}', f'.agent-runs/{run}/cache',
                                f'.agent-runs/{run}/leaderboard-entry', f'.agent-runs/{run}/done']}

    def populate(self, run='old'):
        spec = self.control.load(run)
        for name in spec['owned_paths']:
            p = self.root / name
            p.mkdir(parents=True)
            (p / 'partial.json').write_text('{"sample":1}')

    def confirm(self, binding, finding):
        return binding['identity_sha256']

    def stop(self, binding):
        self.calls.append(binding['job'])
        # Revocation must already be durable even in the stopping callback.
        with self.assertRaisesRegex(ValueError, 'revoked'):
            assert_not_revoked(self.root, result_id=binding['result_ids'][0])
        return {'job': binding['job'], 'stopped': True, 'fenced': True, 'source': 'CPU fixture controller readback'}

    def contain(self, **kwargs):
        return self.control.contain('old', self.finding, confirm=self.confirm, stop=kwargs.get('stop', self.stop))

    def test_suspicion_and_inapplicable_confirmed_defect_do_not_stop(self):
        for finding in [dict(self.finding, status='suspected'), dict(self.finding, affects_run=False)]:
            self.assertEqual('verify-risk', self.control.contain('old', finding, confirm=self.confirm, stop=self.stop)['status'])
        assert_not_revoked(self.root, result_id='result-old')
        self.assertEqual([], self.calls)

    def test_confirmation_must_match_frozen_execution(self):
        with self.assertRaisesRegex(ValueError, 'not authenticated'):
            self.control.contain('old', self.finding, confirm=lambda *_: 'another-run', stop=self.stop)
        self.assertEqual([], self.calls)

    def test_partial_results_cache_leaderboard_and_done_quarantined_recoverably(self):
        self.populate()
        self.control.bind(self.spec('other'))
        self.populate('other')
        outcome = self.contain()
        self.assertEqual('quarantined', outcome['status'])
        for move in outcome['moves']:
            self.assertFalse((self.root / move['source']).exists())
            self.assertEqual('{"sample":1}', (self.root / move['quarantine'] / 'partial.json').read_text())
        self.assertTrue((self.root / 'agent_doc/results/other/partial.json').exists())
        self.assertEqual([self.binding['job']], self.calls)
        # Restart/repeated event does not re-stop or touch unrelated jobs.
        restarted = Contamination(self.root, authorize=lambda *_: True)
        self.assertEqual(outcome, restarted.contain('old', self.finding, confirm=self.confirm, stop=lambda _: self.fail('duplicate stop')))
        with self.assertRaisesRegex(ValueError, 'revoked'):
            assert_not_revoked(self.root, result_id='result-old')

    def test_missing_partial_outputs_still_get_revoked(self):
        self.assertEqual('quarantined', self.contain()['status'])
        with self.assertRaises(ValueError):
            assert_not_revoked(self.root, run_id='old')

    def test_stop_failure_blocks_cleanup_and_replacement_then_retry(self):
        self.populate()
        def fail(_):
            raise TimeoutError('owned job did not exit')
        outcome = self.contain(stop=fail)
        self.assertEqual('blocked', outcome['status'])
        self.assertTrue((self.root / 'agent_doc/results/old/partial.json').exists())
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            self.control.prepare_replacement('old', self.spec('new'), verify_fix=lambda *_: True)
        self.assertEqual('quarantined', self.contain()['status'])

    def test_evidence_disk_failure_still_stops_before_archival(self):
        from agent_runtime.contamination import atomic_write
        self.populate()
        def disk_error(root, name, data):
            if '/evidence/' in str(name):
                raise OSError('evidence disk quota')
            return atomic_write(root, name, data)
        with patch('agent_runtime.contamination.atomic_write', side_effect=disk_error):
            result = self.contain()
        self.assertEqual('blocked', result['status'])
        self.assertEqual([self.binding['job']], self.calls)
        self.assertTrue((self.root / 'agent_doc/results/old').exists())
        self.assertEqual('quarantined', self.contain()['status'])

    def test_revocation_storage_failure_still_attempts_stop_but_never_cleans(self):
        from agent_runtime.contamination import atomic_write
        self.populate()
        stopped = []
        def disk_error(root, name, data):
            if str(name).endswith('/incident.json'):
                raise OSError('revocation storage unavailable')
            return atomic_write(root, name, data)
        def stop(binding):
            stopped.append(binding['job'])
            return {'job': binding['job'], 'stopped': True, 'fenced': True, 'source': 'host readback'}
        with patch('agent_runtime.contamination.atomic_write', side_effect=disk_error):
            result = self.contain(stop=stop)
        self.assertFalse(result['durable'])
        self.assertEqual('blocked', result['status'])
        self.assertEqual([self.binding['job']], stopped)
        self.assertTrue((self.root / 'agent_doc/results/old').exists())

    def test_actual_repaired_cpu_execution_uses_fresh_output(self):
        self.populate()
        self.contain()
        (self.root / 'code.py').write_text('from pathlib import Path\nPath("result.txt").write_text(str(sum(range(4))))\n')
        new = self.spec('new')
        def verify(old, new):
            # CPU repair validation against independent closed-form reference.
            with tempfile.TemporaryDirectory() as directory:
                subprocess.run([sys.executable, str(self.root / 'code.py')], cwd=directory, check=True, timeout=3)
                self.assertEqual(str(4 * 3 // 2), (Path(directory) / 'result.txt').read_text())
            return new['identity_sha256']
        frozen = self.control.prepare_replacement('old', new, verify_fix=verify)
        output = self.root / frozen['owned_paths'][0]
        output.mkdir(parents=True)
        subprocess.run([sys.executable, str(self.root / 'code.py')], cwd=output, check=True, timeout=3)
        self.assertEqual('6', (output / 'result.txt').read_text())
        self.assertFalse((output / 'partial.json').exists())

    def test_wrong_job_or_unfenced_stop_readback_blocks(self):
        for receipt in [True, {'job': {'pid': 12}, 'stopped': True, 'fenced': True, 'source': 'wrong'},
                        {'job': self.binding['job'], 'stopped': True, 'fenced': False, 'source': 'writers still alive'}]:
            self.assertEqual('blocked', self.contain(stop=lambda _: receipt)['status'])

    def test_partial_move_failure_is_resumable(self):
        self.populate()
        rename = Path.rename
        count = 0
        def interrupted(path, destination):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError('simulated interrupted cleanup')
            return rename(path, destination)
        with patch.object(Path, 'rename', interrupted):
            result = self.contain()
        self.assertEqual('blocked', result['status'])
        self.assertEqual(1, len(result['moves']))
        self.assertEqual('quarantined', self.contain()['status'])

    def test_repair_requires_changed_identity_validation_and_current_authorization(self):
        self.contain()
        with self.assertRaisesRegex(ValueError, 'repair must change'):
            self.control.prepare_replacement('old', self.spec('new'), verify_fix=lambda a, b: b['identity_sha256'])
        (self.root / 'code.py').write_text('fixed')
        new = self.spec('new')
        with self.assertRaisesRegex(ValueError, 'independent repair'):
            self.control.prepare_replacement('old', new, verify_fix=lambda *_: True)
        self.control.authorize = lambda action, _: action != 'rerun'
        with self.assertRaisesRegex(ValueError, 'authorization'):
            self.control.prepare_replacement('old', new, verify_fix=lambda a, b: b['identity_sha256'])
        self.control.authorize = lambda *_: True
        frozen = self.control.prepare_replacement('old', new, verify_fix=lambda a, b: b['identity_sha256'])
        self.assertEqual('new', frozen['run_id'])
        assert_not_revoked(self.root, result_id='result-new')
        with self.assertRaises(ValueError):
            assert_not_revoked(self.root, result_id='result-old')

    def test_replacement_rejects_old_cache_recreated_outputs_and_mutating_fix(self):
        self.contain()
        (self.root / 'code.py').write_text('fixed')
        new = self.spec('new')
        cache = self.root / '.agent-runs/new/cache'
        cache.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'fresh output'):
            self.control.prepare_replacement('old', new, verify_fix=lambda a, b: b['identity_sha256'])
        cache.rmdir()
        old = self.root / 'agent_doc/results/old'
        old.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'recreated'):
            self.control.prepare_replacement('old', new, verify_fix=lambda a, b: b['identity_sha256'])
        old.rmdir()
        def mutate(a, b):
            (self.root / 'code.py').write_text('changed after verification')
            return b['identity_sha256']
        with self.assertRaisesRegex(ValueError, 'stale artifact'):
            self.control.prepare_replacement('old', new, verify_fix=mutate)

    def test_rejects_identity_reuse_wrong_data_unsafe_paths_and_redirects(self):
        with self.assertRaisesRegex(ValueError, 'already frozen'):
            self.control.bind(self.spec('old'))
        wrong = self.spec('new')
        wrong['data'][0]['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            self.control.bind(wrong)
        for name in ['agent_doc/guide/new', 'agent_runtime/new', 'agent_doc/results', '../new', '.agent-runs/contamination/new']:
            wrong = self.spec('new')
            wrong['owned_paths'] = [name]
            with self.assertRaises(ValueError):
                self.control.bind(wrong)
        self.populate()
        (self.root / 'agent_doc/results/old/link').symlink_to(self.root / 'code.py')
        self.assertEqual('blocked', self.contain()['status'])
        self.assertEqual('bug', (self.root / 'code.py').read_text())

    def test_existing_result_gate_rechecks_revocation_during_verifier(self):
        contract = make_fixture(self.root)
        # A completed legacy run can be affected through a registered dependent
        # result identity, without rewriting its immutable manifest or raw bytes.
        registered = self.spec('validation-owner')
        registered['result_ids'] = [contract['result_id']]
        bound = self.control.bind(registered)
        self.assertEqual('usable-with-scope', inspect_result(self.root, contract, independent_verify)['status'])
        def verifier(root, manifest, plan):
            review = independent_verify(root, manifest, plan)
            self.control.contain(bound['run_id'], self.finding, confirm=self.confirm, stop=self.stop)
            return review
        self.assertEqual('invalid', inspect_result(self.root, contract, verifier)['status'])
        self.assertEqual('invalid', inspect_result(self.root, contract, independent_verify)['status'])
        with self.assertRaisesRegex(ValueError, 'revoked'):
            check_task_results(self.root, {'experiment_result': contract}, report={'data': []})

    def test_result_store_excludes_revoked_candidates_and_refuses_cached_reuse(self):
        from agent_runtime.result_store import ResultStore, ReuseResultHandler
        from test_result_store import ResultStoreTests
        fixture = ResultStoreTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.register(verifier=fixture.verify)
        self.assertEqual('reuse', fixture.decide()['decision'])
        selection = fixture.selection()
        # Register an affected accepted result as part of the host-confirmed
        # reference closure. No re-registration or changed pass file is needed.
        bound = {'run_id': 'affected', 'result_ids': [fixture.contract['result_id']],
                 'task_refs': ['EXP-1'], 'job': {'scheduler_job_id': 'test-owned'},
                 **{role: fixture.manifest['artifacts'][mapped] for role, mapped in
                    [('code', 'code'), ('config', 'config'), ('data', 'inputs')]},
                 'inventory_complete': True, 'owned_paths': ['.agent-runs/affected/cache']}
        ctl = Contamination(fixture.root, authorize=lambda *_: True)
        ctl.bind(bound)
        evidence = fixture.manifest['artifacts']['code']
        ctl.contain('affected', dict(self.finding, evidence=evidence), confirm=self.confirm,
                    stop=lambda b: {'job': b['job'], 'stopped': False, 'fenced': False, 'source': 'stop failed'})
        self.assertEqual('rerun', fixture.decide()['decision'])
        found = ResultStore(fixture.root).search('integer square')
        self.assertEqual([], found['results'])
        self.assertIn('revoked', found['errors'][0]['error'])
        handler = ReuseResultHandler(fixture.root, fixture.verify)
        self.assertNotEqual('complete', handler.run({'result_reuse': selection}, None).status)

    def test_replacement_is_reserved_only_once(self):
        self.contain()
        (self.root / 'code.py').write_text('fixed')
        self.control.prepare_replacement('old', self.spec('new'), verify_fix=lambda a, b: b['identity_sha256'])
        with self.assertRaisesRegex(ValueError, 'already reserved'):
            self.control.prepare_replacement('old', self.spec('another'), verify_fix=lambda a, b: b['identity_sha256'])

    @unittest.skipUnless(hasattr(os, 'pidfd_open') and hasattr(signal, 'pidfd_send_signal'), 'Linux pidfd required')
    def test_actual_owned_process_stops_while_unrelated_process_survives(self):
        # Trusted TEST host already owns these handles; production supplies its
        # own scheduler/cgroup cancellation. No broad process-name or PID kill.
        jobs = [subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)']) for _ in range(2)]
        for proc in jobs:
            self.addCleanup(lambda p=proc: (p.terminate() if p.poll() is None else None, p.wait(timeout=5)))
        fd = os.pidfd_open(jobs[0].pid)
        self.addCleanup(os.close, fd)
        spec = self.spec('process')
        spec['job'] = {'host': 'this-test', 'pid': jobs[0].pid, 'pidfd_handle': fd, 'invocation': 'owned-fixture-only'}
        bound = self.control.bind(spec)
        def stop(binding):
            self.assertEqual(bound['job'], binding['job'])
            signal.pidfd_send_signal(fd, signal.SIGTERM)
            self.assertTrue(select.select([fd], [], [], 3)[0], 'owned process failed to exit')
            jobs[0].wait(timeout=3)
            return {'job': binding['job'], 'stopped': True, 'fenced': True,
                    'source': 'pidfd readiness + wait return; fixture has no children/retry dispatcher'}
        result = self.control.contain('process', self.finding, confirm=self.confirm, stop=stop)
        self.assertEqual('quarantined', result['status'])
        self.assertIsNotNone(jobs[0].returncode)
        self.assertIsNone(jobs[1].poll())


if __name__ == '__main__':
    unittest.main()
