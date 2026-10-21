"""Local CPU registration/retrieval/reuse; no hosted model or performance claim."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import agent_runtime.result_store as result_store
from agent_runtime.result_store import (ResultStore, ResultStoreError, ReuseResultHandler,
    check_task_reuse, register_task_result, result_context)
from agent_runtime.core import ArtifactHandler
from agent_runtime.task_manifest import ReportingHandler, atomic_json
from test_result_validation import make_fixture, independent_verify


class ResultStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='prior-results-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.producer_commands = []
        actual_run = subprocess.run
        def observed_run(command, *args, **kwargs):
            result = actual_run(command, *args, **kwargs)
            if len(command) > 1 and Path(command[1]).name == 'code.py':
                self.producer_commands.append(list(command))
            return result
        observer = patch('subprocess.run', side_effect=observed_run)
        observer.start()
        self.addCleanup(observer.stop)
        self.prefix = 'agent_doc/results/cpu-run-1/'
        self.base = self.root / self.prefix
        self.contract = make_fixture(self.base)
        manifest = json.loads((self.base / 'manifest.json').read_text())
        self.contract['manifest_path'] = self.prefix + 'manifest.json'
        self.contract['validation_plan']['path'] = self.prefix + 'validation-plan.json'
        manifest['validation_plan'] = self.contract['validation_plan']
        for refs in manifest['artifacts'].values():
            for ref in refs:
                ref['path'] = self.prefix + ref['path']
        manifest['execution']['command'] = [sys.executable, self.prefix + 'code.py']
        self.manifest = manifest
        self.write_manifest()
        self.context = result_context(manifest)
        self.store = ResultStore(self.root)

    def write_manifest(self):
        (self.base / 'manifest.json').write_text(json.dumps(self.manifest, indent=2) + '\n')

    def verify(self, root, manifest, plan):
        result = independent_verify(root / self.prefix, manifest, plan)
        for check in result['checks'].values():
            for ref in check['evidence']:
                ref['path'] = self.prefix + ref['path']
        return result

    def register(self, **kwargs):
        return self.store.register(self.contract, **kwargs)

    def decide(self, context=None, **kwargs):
        return self.store.decide_run('cpu-run-1', self.context if context is None else context,
                                     verifier=self.verify, **kwargs)

    def selection(self):
        return {'run_id': 'cpu-run-1', 'record_sha256': self.store.show('cpu-run-1')['record_ref']['sha256'],
                'query': 'integer square', 'context': self.context,
                'explicit_reproduction': False, 'new_claim': False}

    def test_native_registration_pending_then_current_exact_acceptance(self):
        registered = self.register()
        self.assertEqual(registered['record']['origin'], 'native')
        self.assertEqual(registered['record']['validation_at_registration']['status'], 'pending')
        self.assertEqual(self.store.decide_run('cpu-run-1', self.context)['decision'], 'verify_delta')
        decision = self.decide()
        self.assertEqual(decision['decision'], 'reuse')
        self.assertFalse(decision['automatic_skip_authorized'])
        self.assertEqual(decision['validation_status'], 'usable-with-scope')

    def test_persisted_exponent_overflow_is_not_a_finite_result_value(self):
        artifact = self.root / 'historical.txt'
        artifact.write_text('bounded historical evidence')
        self.store.register_history('history-overflow', 'finite metadata fixture', [{
            'path': 'historical.txt',
            'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
        }])
        record = self.root / 'agent_doc/results/history-overflow/record.json'
        raw = record.read_text().rstrip()
        record.write_text(raw[:-1] + ',"extra":1e400}')
        before = record.read_bytes()
        with self.assertRaisesRegex(ResultStoreError, 'nonfinite'):
            self.store.show('history-overflow')
        self.assertEqual(record.read_bytes(), before)
        result = self.store.search('finite metadata')
        self.assertEqual(result['status'], 'incomplete')
        self.assertIn('history-overflow', [item['run_id'] for item in result['errors']])

    def test_persisted_record_and_search_cli_require_utf8(self):
        artifact = self.root / 'utf16-history.txt'
        artifact.write_text('UTF-8 source artifact')
        self.store.register_history('history-utf16', 'UTF-16 record fixture', [{
            'path': artifact.name,
            'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
        }])
        record = self.root / 'agent_doc/results/history-utf16/record.json'
        value = json.loads(record.read_text())
        record.write_bytes(json.dumps(value).encode('utf-16'))
        before = record.read_bytes()
        with self.assertRaisesRegex(ResultStoreError, 'UTF-8'):
            self.store.show('history-utf16')
        script = Path(__file__).resolve().parents[1] / 'scripts/result_store.py'
        result = subprocess.run([sys.executable, str(script), '--root', str(self.root),
                                 'search', 'UTF-16 record fixture'], capture_output=True,
                                text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload['status'], 'incomplete')
        self.assertIn('history-utf16', [item['run_id'] for item in payload['errors']])
        self.assertEqual(record.read_bytes(), before)

    def test_explicit_handler_and_consumers_recheck_not_skip_by_search(self):
        self.register()
        task = {'action': 'reuse_validated_result', 'result_reuse': self.selection()}
        handler = ReuseResultHandler(self.root, self.verify)
        outcome = handler.run(task, None)
        self.assertEqual(outcome.status, 'complete')
        self.assertTrue(handler.verify(task, outcome.evidence))
        self.assertEqual(check_task_reuse(self.root, task, self.verify), outcome.evidence)
        self.assertEqual(ReuseResultHandler(self.root).run(task, None).status, 'pending')
        (self.base / 'raw.json').write_text('{}')
        self.assertFalse(handler.verify(task, outcome.evidence))

    def test_real_reporting_hook_registers_producer_and_consumes_old_result(self):
        task = {'task_id': 'produce', 'action': 'verify_artifacts', 'report_path': 'reports/produce.json',
                'experiment_result': self.contract, 'result_storage': 'central',
                'prior_result_review': {'decision': 'rerun', 'record_refs': [],
                    'reason': 'Initial fixture output exists in an unregistered run directory; no accepted prior record'},
                'done_when': {'artifacts': self.manifest['artifacts']['outputs']}}
        atomic_json(self.root / task['report_path'], {'task_id': 'produce', 'summary': 'Actual CPU observations',
                    'data': [{'kind': 'measured', 'description': 'Frozen integer samples'}]})
        producer = ReportingHandler(ArtifactHandler(self.root), self.root, self.verify)
        outcome = producer.run(task, None)
        self.assertEqual(outcome.status, 'complete', outcome.reason)
        self.assertTrue(producer.verify(task, outcome.evidence))
        self.assertEqual(self.store.show('cpu-run-1')['record']['origin'], 'native')
        self.assertEqual(self.store.show('cpu-run-1')['record']['validation_at_registration']['status'], 'pending')
        reuse = {'task_id': 'reuse', 'action': 'reuse_validated_result', 'report_path': 'reports/reuse.json',
                 'result_reuse': self.selection()}
        atomic_json(self.root / reuse['report_path'], {'task_id': 'reuse', 'summary': 'Prior result reused',
                    'data': [{'kind': 'derived', 'description': 'Existing validated measurement; no new production'}]})
        handler = ReportingHandler(ReuseResultHandler(self.root, self.verify), self.root, self.verify)
        outcome = handler.run(reuse, None)
        self.assertEqual(outcome.status, 'complete', outcome.reason)
        self.assertIn('prior_result_reuse', outcome.evidence[-1]['task_report'])
        self.assertTrue(handler.verify(reuse, outcome.evidence))

    def test_no_repeat_counts_actual_producer_invocations_for_three_intents(self):
        self.assertEqual(len(self.producer_commands), 1)
        self.register()
        task = {'action': 'reuse_validated_result', 'result_reuse': self.selection()}
        handler = ReuseResultHandler(self.root, self.verify)
        for _ in range(2):
            outcome = handler.run(task, None)
            self.assertEqual(outcome.status, 'complete')
            self.assertTrue(handler.verify(task, outcome.evidence))
        self.assertEqual(len(self.producer_commands), 1, 'scoped reuse must not rerun the producer')
        changed = copy.deepcopy(self.context)
        changed['artifacts']['inputs'][0]['sha256'] = 'b' * 64
        self.assertEqual(self.decide(changed)['decision'], 'verify_delta')
        self.assertEqual(len(self.producer_commands), 1, 'planning a delta cannot secretly run the producer')
        self.assertEqual(self.decide(explicit_reproduction=True)['decision'], 'rerun')
        self.assertEqual(len(self.producer_commands), 1)
        # The authorized new/different and explicit-repeat producer rounds are
        # separate native run directories; the old registered bytes survive.
        frozen = (self.base / 'raw.json').read_bytes()
        for run_id, inputs in [('changed-input', [0, 2, 9]), ('requested-repeat', [0, 1, 2, 7, 19])]:
            base = self.root / 'agent_doc/results' / run_id
            base.mkdir()
            (base / 'code.py').write_bytes((self.base / 'code.py').read_bytes())
            (base / 'inputs.json').write_text(json.dumps({'n': inputs}))
            (base / 'config.json').write_bytes((self.base / 'config.json').read_bytes())
            subprocess.run([sys.executable, 'code.py'], cwd=base, check=True, capture_output=True)
            observed = json.loads((base / 'raw.json').read_text())['samples']
            self.assertEqual({row['n'] for row in observed}, set(inputs))
        self.assertEqual(len(self.producer_commands), 3)
        self.assertEqual((self.base / 'raw.json').read_bytes(), frozen)

    def test_reproduction_and_new_claim_never_reused(self):
        self.register()
        for field in ('explicit_reproduction', 'new_claim'):
            self.assertEqual(self.decide(**{field: True})['decision'], 'rerun')
            selection = self.selection()
            selection[field] = True
            with self.assertRaises(ResultStoreError):
                check_task_reuse(self.root, {'result_reuse': selection}, self.verify)
            with self.assertRaises(ResultStoreError):
                check_task_reuse(self.root, {'result_reuse': self.selection(), field: True}, self.verify)

    def test_changed_units_hardware_code_and_inputs_require_delta(self):
        self.register()
        for field in ('scope', 'code_revision', 'metrics', 'execution', 'artifacts'):
            context = copy.deepcopy(self.context)
            if field == 'metrics':
                context[field][0]['unit'] = 'milliseconds'
            elif field == 'execution':
                context[field]['environment_description'] = 'different GPU'
            elif field == 'artifacts':
                context[field]['inputs'][0]['sha256'] = 'a' * 64
            else:
                context[field] += ' changed'
            result = self.decide(context)
            self.assertEqual(result['decision'], 'verify_delta')
            self.assertIn(field, [d['field'] for d in result['differences']])

    def test_missing_or_equally_unknown_is_not_matching_evidence(self):
        self.register()
        self.assertEqual(self.decide({})['decision'], 'verify_delta')
        (self.base / 'record.json').unlink()  # Test fixture reset, no product mutation API.
        self.manifest['execution']['environment_description'] = 'unknown'
        self.write_manifest()
        self.context = result_context(self.manifest)
        self.register()
        decision = self.decide()
        self.assertEqual(decision['decision'], 'verify_delta')
        self.assertIn('execution', decision['missing_conditions'])

    def test_stale_raw_manifest_and_registry_labels_cannot_reuse(self):
        self.register()
        path = self.base / 'record.json'
        record = json.loads(path.read_text())
        record['context']['execution']['environment_description'] = 'fictional GPU'
        path.write_text(json.dumps(record))
        changed = copy.deepcopy(self.context)
        changed['execution']['environment_description'] = 'fictional GPU'
        result = self.decide(changed)
        self.assertEqual(result['decision'], 'rerun')
        self.assertEqual(result['validation_status'], 'stale')
        record['context'] = self.context
        path.write_text(json.dumps(record))
        (self.base / 'raw.json').write_text('[]')
        self.assertEqual(self.decide()['decision'], 'rerun')

    def test_persisted_pass_and_self_review_do_not_authorize(self):
        self.register()
        path = self.base / 'record.json'
        record = json.loads(path.read_text())
        record['validation_at_registration'] = {'status': 'usable-with-scope', 'proof': {'status': 'usable-with-scope'}}
        path.write_text(json.dumps(record))
        self.assertNotEqual(self.store.decide_run('cpu-run-1', self.context)['decision'], 'reuse')
        def self_review(root, manifest, plan):
            value = self.verify(root, manifest, plan)
            value['verifier']['actor'] = manifest['producer_actor']
            return value
        self.assertEqual(self.store.decide_run('cpu-run-1', self.context, verifier=self_review)['decision'], 'rerun')
        self.assertEqual(self.decide()['decision'], 'rerun')

    def test_frozen_accepted_proof_and_review_evidence_are_current(self):
        self.register(verifier=self.verify)
        self.assertEqual(self.decide()['decision'], 'reuse')
        def changed_review(root, manifest, plan):
            review = self.verify(root, manifest, plan)
            review['verifier']['run_id'] = 'other-review'
            return review
        self.assertEqual(self.store.decide_run('cpu-run-1', self.context, verifier=changed_review)['decision'], 'rerun')

    def test_freshness_uses_measurement_time_not_registration(self):
        self.manifest['execution']['completed_at'] = '2026-10-06T10:00:00Z'
        self.write_manifest()
        self.register(measured_at='2026-10-06T10:00:00Z')
        self.assertEqual(self.decide(max_age_seconds=600, now='2026-10-06T10:05:00Z')['decision'], 'reuse')
        self.assertEqual(self.decide(max_age_seconds=60, now='2026-10-06T10:05:00Z')['decision'], 'verify_delta')
        self.assertEqual(self.decide(max_age_seconds=600, now='2026-10-05T10:05:00Z')['decision'], 'verify_delta')
        with self.assertRaises(ValueError):
            self.decide(max_age_seconds=float('nan'))

    def test_catalog_only_fresh_timestamp_cannot_override_bound_execution_time(self):
        self.register(measured_at='2026-10-06T10:00:00Z')
        result = self.decide(max_age_seconds=600, now='2026-10-06T10:05:00Z')
        self.assertEqual(result['decision'], 'verify_delta')
        self.assertTrue(any('not bound' in reason for reason in result['reasons']))

    def test_duplicate_id_collision_and_exact_producer_replay(self):
        task = {'experiment_result': self.contract, 'result_storage': 'central'}
        first = register_task_result(self.root, task)
        second = register_task_result(self.root, task)
        self.assertEqual(first, second)
        with self.assertRaises(ResultStoreError):
            self.register()
        self.manifest['metrics'][0]['value'] += 1
        self.write_manifest()
        with self.assertRaises(ResultStoreError):
            register_task_result(self.root, task)

    def test_historical_refs_preserved_unknown_and_native_location_required(self):
        outside = self.root / 'old-result.json'
        outside.write_text('{"metric": 42}')
        before = outside.read_bytes()
        ref = {'path': outside.name, 'sha256': hashlib.sha256(before).hexdigest()}
        record = self.store.register_history('old-run', 'old unvalidated integer result', [ref])
        self.assertEqual(record['record']['origin'], 'historical-external-reference')
        self.assertEqual(outside.read_bytes(), before)
        decision = self.store.decide_run('old-run', {})
        self.assertEqual(decision['decision'], 'verify_delta')
        self.assertEqual(decision['validation_status'], 'unknown')
        legacy_root = self.root / 'legacy'
        contract = make_fixture(legacy_root)
        with self.assertRaisesRegex(ResultStoreError, 'belong in'):
            ResultStore(legacy_root).register(contract)
        registered = register_task_result(legacy_root, {'experiment_result': contract})
        self.assertEqual(registered['record']['origin'], 'legacy-contract-reference')
        self.assertTrue((legacy_root / 'raw.json').exists())

    def test_bounded_search_reports_partial_and_invalid_record(self):
        self.register()
        for i in range(4):
            self.store.register_history('hist-' + str(i), 'integer old result',
                [{'path': self.prefix + 'raw.json', 'sha256': hashlib.sha256((self.base / 'raw.json').read_bytes()).hexdigest()}])
        found = self.store.search('integer', max_scan=2, limit=1)
        self.assertTrue(found['partial'])
        self.assertLessEqual(found['scanned'], 2)
        self.assertEqual(len(found['results']), 1)
        self.assertEqual(found['results'][0]['applicability'], 'unchecked')
        (self.base / 'record.json').write_text('{"run_id":1,"run_id":2}')
        self.assertTrue(self.store.search('integer')['errors'])

    def test_bounded_search_selects_same_directories_for_reversed_enumeration(self):
        root = self.root / 'stable-scan'
        root.mkdir()
        artifact = root / 'historical.json'
        artifact.write_text('{"measurement":1}\n')
        ref = {'path': artifact.name, 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}
        store = ResultStore(root)
        for run_id in ('zeta', 'alpha', 'middle'):
            store.register_history(run_id, 'stable ordering evidence', [ref])
        original_scandir = os.scandir

        class ReversedScandir:
            def __init__(self, path):
                with original_scandir(path) as entries:
                    self.entries = list(entries)[::-1]
            def __enter__(self):
                return iter(self.entries)
            def __exit__(self, *_):
                return False

        expected = ['alpha', 'middle']
        normal = store.search('stable ordering evidence', max_scan=2, limit=20)
        with patch('agent_runtime.result_store.os.scandir', ReversedScandir):
            reversed_result = store.search('stable ordering evidence', max_scan=2, limit=20)
        self.assertEqual([item['run_id'] for item in normal['results']], expected)
        self.assertEqual([item['run_id'] for item in reversed_result['results']], expected)

    def test_regular_file_does_not_consume_directory_scan_budget(self):
        root = self.root / 'scan-budget'
        home = root / 'agent_doc/results'
        home.mkdir(parents=True)
        artifact = root / 'artifact.json'
        artifact.write_text('{}\n')
        ref = {'path': artifact.name, 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}
        store = ResultStore(root)
        store.register_history('alpha', 'budget evidence', [ref])
        store.register_history('beta', 'budget evidence', [ref])
        (home / 'README.md').write_text('catalog notes\n')
        result = store.search('budget evidence', max_scan=2, limit=20)
        self.assertEqual(result['scanned'], 2)
        self.assertFalse(result['partial'])
        self.assertEqual([item['run_id'] for item in result['results']], ['alpha', 'beta'])

    def test_symlink_after_selected_directory_is_still_rejected(self):
        root = self.root / 'late-symlink'
        home = root / 'agent_doc/results'
        home.mkdir(parents=True)
        (home / 'alpha').mkdir()
        (home / 'z-link').symlink_to(root, target_is_directory=True)
        with self.assertRaisesRegex(ResultStoreError, 'symlink'):
            ResultStore(root).search('anything', max_scan=1)

    def test_over_capacity_search_returns_no_native_order_prefix(self):
        root = self.root / 'over-capacity'
        home = root / 'agent_doc/results'
        home.mkdir(parents=True)
        for name in ('first', 'second', 'third', 'fourth'):
            (home / name).mkdir()
        store = ResultStore(root)
        with patch.object(result_store, 'DIRECTORY_ENTRY_LIMIT', 3, create=True):
            result = store.search('anything', max_scan=3)
        self.assertEqual(result['results'], [])
        self.assertEqual(result['scanned'], 0)
        self.assertTrue(result['partial'])
        self.assertEqual(result['status'], 'incomplete')
        artifact = root / 'artifact.json'
        artifact.write_text('{}\n')
        ref = {'path': artifact.name, 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}
        with patch.object(result_store, 'DIRECTORY_ENTRY_LIMIT', 3):
            with self.assertRaisesRegex(ResultStoreError, 'exceeds 3 entries'):
                store.register_history('fifth', 'must fail closed', [ref])
        self.assertFalse((home / 'fifth').exists())

    def test_registration_capacity_matrix_and_existing_run_recovery(self):
        root = self.root / 'capacity'
        home = root / 'agent_doc/results'
        home.mkdir(parents=True)
        artifact = root / 'artifact.json'
        artifact.write_text('{}\n')
        ref = {'path': artifact.name, 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}
        for name in ('one', 'two'):
            (home / name).mkdir()
        store = ResultStore(root)
        with patch.object(result_store, 'DIRECTORY_ENTRY_LIMIT', 3):
            store.register_history('third', 'capacity evidence', [ref])
            self.assertEqual(len(list(home.iterdir())), 3)
            with self.assertRaisesRegex(ResultStoreError, '3 entries'):
                store.register_history('fourth', 'must not create a fourth entry', [ref])
            self.assertFalse((home / 'fourth').exists())
            (home / 'third/record.json').unlink()
            store.register_history('third', 'recover existing reserved directory', [ref])
            self.assertTrue((home / 'third/record.json').is_file())

    @unittest.skipIf(os.name == 'nt', 'POSIX process/lock termination test')
    def test_process_death_releases_capacity_lock_without_overflow(self):
        root = self.root / 'process-capacity'
        home = root / 'agent_doc/results'
        home.mkdir(parents=True)
        artifact = root / 'artifact.json'
        artifact.write_text('{}\n')
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        for name in ('one', 'two'):
            (home / name).mkdir()
        ready = root / 'ready'
        repo = Path(__file__).resolve().parents[1]
        env = os.environ.copy()
        env['PYTHONPATH'] = str(repo)
        holder_code = (
            'import os, pathlib, sys, time; import agent_runtime.result_store as rs; '
            'root=pathlib.Path(sys.argv[1]); ready=pathlib.Path(sys.argv[2]); '
            'lock=rs._registry_lock(root); lock.__enter__(); '
            '(root/"agent_doc/results/third").mkdir(); ready.write_text("held"); time.sleep(30)')
        contender_code = (
            'import hashlib, pathlib, sys; import agent_runtime.result_store as rs; '
            'rs.DIRECTORY_ENTRY_LIMIT=3; root=pathlib.Path(sys.argv[1]); '
            'ref={"path":"artifact.json","sha256":sys.argv[2]}; '
            'rs.ResultStore(root).register_history("fourth","capacity evidence",[ref])')
        holder = subprocess.Popen([sys.executable, '-c', holder_code, str(root), str(ready)],
                                  cwd=repo, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                  text=True)
        self.addCleanup(lambda: holder.poll() is None and holder.kill())
        deadline = time.monotonic() + 5
        while not ready.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(ready.exists(), 'holder did not acquire the registry lock')
        contender = subprocess.Popen([sys.executable, '-c', contender_code, str(root), digest],
                                     cwd=repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: contender.poll() is None and contender.kill())
        time.sleep(0.15)
        self.assertIsNone(contender.poll(), 'contender must block before its directory creation')
        self.assertEqual(sorted(path.name for path in home.iterdir()), ['one', 'third', 'two'])
        holder.kill()
        holder.communicate(timeout=5)
        _, contender_error = contender.communicate(timeout=5)
        self.assertNotEqual(contender.returncode, 0, contender_error)
        self.assertFalse((home / 'fourth').exists())
        ref = {'path': artifact.name, 'sha256': digest}
        with patch.object(result_store, 'DIRECTORY_ENTRY_LIMIT', 3):
            ResultStore(root).register_history('third', 'recover after terminated owner', [ref])
        self.assertEqual(len(list(home.iterdir())), 3)

    def test_multiprocess_capacity_and_same_run_publication_are_atomic(self):
        repo = Path(__file__).resolve().parents[1]
        env = os.environ.copy()
        env['PYTHONPATH'] = str(repo)
        worker = (
            'import pathlib, sys, time; import agent_runtime.result_store as rs; '
            'root=pathlib.Path(sys.argv[1]); gate=pathlib.Path(sys.argv[2]); '
            'rs.DIRECTORY_ENTRY_LIMIT=int(sys.argv[4]); '
            'ref={"path":"artifact.json","sha256":sys.argv[5]}; '
            'exec("while not gate.exists():\\n time.sleep(0.005)"); '
            'rs.ResultStore(root).register_history(sys.argv[3],"concurrent evidence",[ref])')

        def race(root, run_ids, initial=()):
            home = root / 'agent_doc/results'
            home.mkdir(parents=True)
            for name in initial:
                (home / name).mkdir()
            artifact = root / 'artifact.json'
            artifact.write_text('{}\n')
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            gate = root / 'gate'
            processes = [subprocess.Popen(
                [sys.executable, '-c', worker, str(root), str(gate), run_id, '3', digest],
                cwd=repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                for run_id in run_ids]
            gate.write_text('go\n')
            outputs = [process.communicate(timeout=10) for process in processes]
            return home, processes, outputs

        distinct_root = self.root / 'distinct-race'
        home, processes, outputs = race(distinct_root, ('third-a', 'third-b'), ('one', 'two'))
        self.assertEqual(sorted(process.returncode for process in processes), [0, 1], outputs)
        self.assertEqual(len(list(home.iterdir())), 3)
        self.assertEqual(sum((home / name / 'record.json').is_file()
                             for name in ('third-a', 'third-b')), 1)

        same_root = self.root / 'same-race'
        home, processes, outputs = race(same_root, ('shared', 'shared'))
        self.assertEqual(sorted(process.returncode for process in processes), [0, 1], outputs)
        self.assertEqual([path.name for path in home.iterdir()], ['shared'])
        self.assertTrue((home / 'shared/record.json').is_file())

        casefold_root = self.root / 'casefold-race'
        home, processes, outputs = race(casefold_root, ('Shared', 'shared'))
        self.assertEqual(sorted(process.returncode for process in processes), [0, 1], outputs)
        self.assertEqual(len(list(home.iterdir())), 1)
        self.assertEqual([path.name.casefold() for path in home.iterdir()], ['shared'])

    def test_registry_lock_rejects_symlink_fifo_and_symlinked_parent(self):
        cases = ['symlink', 'parent-symlink']
        if hasattr(os, 'mkfifo'):
            cases.insert(1, 'fifo')
        for case in cases:
            with self.subTest(case=case):
                root = self.root / ('unsafe-lock-' + case)
                root.mkdir()
                outside = self.root / ('outside-' + case)
                outside.mkdir()
                if case == 'parent-symlink':
                    (root / '.agent-runs').symlink_to(outside, target_is_directory=True)
                else:
                    state = root / '.agent-runs'
                    state.mkdir()
                    lock = state / 'result-store.lock'
                    if case == 'symlink':
                        lock.symlink_to(outside / 'lock')
                    else:
                        os.mkfifo(lock)
                with self.assertRaises((OSError, ValueError)):
                    with result_store._registry_lock(root):
                        self.fail('unsafe lock must not be acquired')

    def test_registry_lock_is_stable_regular_file(self):
        root = self.root / 'stable-lock'
        root.mkdir()
        for _ in range(2):
            with result_store._registry_lock(root):
                lock = root / result_store.REGISTRY_LOCK
                self.assertTrue(lock.is_file())
                self.assertEqual(lock.read_bytes(), b'\0')
        self.assertTrue((root / result_store.REGISTRY_LOCK).is_file())

    def test_registry_lock_closes_descriptor_when_explicit_unlock_fails(self):
        root = self.root / 'unlock-failure'
        root.mkdir()
        observed = []

        def fail_unlock(fd):
            observed.append(fd)
            raise OSError('synthetic unlock failure')

        with patch('agent_runtime.result_store._unlock_registry_fd', fail_unlock):
            with self.assertRaisesRegex(OSError, 'synthetic unlock failure'):
                with result_store._registry_lock(root):
                    pass
        self.assertEqual(len(observed), 1)
        with self.assertRaises(OSError) as closed:
            os.fstat(observed[0])
        self.assertEqual(closed.exception.errno, result_store.errno.EBADF)

    def test_windows_registry_lock_retries_and_locks_first_byte(self):
        calls = []
        attempts = [0]
        fake = SimpleNamespace(LK_NBLCK=1, LK_UNLCK=2)
        def locking(fd, mode, size):
            calls.append((os.lseek(fd, 0, os.SEEK_CUR), mode, size))
            if mode == fake.LK_NBLCK and attempts[0] == 0:
                attempts[0] += 1
                raise OSError(result_store.errno.EACCES, 'synthetic contention')
        fake.locking = locking
        with tempfile.TemporaryFile() as stream, patch.dict(sys.modules, {'msvcrt': fake}), \
                patch('agent_runtime.result_store.time.sleep') as sleep:
            stream.write(b'\0')
            stream.seek(0)
            result_store._lock_registry_fd(stream.fileno(), platform='nt')
            result_store._unlock_registry_fd(stream.fileno(), platform='nt')
        self.assertEqual(calls, [(0, 1, 1), (0, 1, 1), (0, 2, 1)])
        sleep.assert_called_once_with(0.01)

    def test_read_only_missing_store_does_not_create_files(self):
        empty = self.root / 'empty'
        empty.mkdir()
        self.assertEqual(ResultStore(empty).search('query')['status'], 'no_hits')
        self.assertEqual(list(empty.iterdir()), [])

    def test_chinese_paraphrase_lexical_overlap_is_retrieved_not_certified(self):
        self.store.register_history('zh-run', 'CPU整型平方和数值验证，保留原始数据',
            [{'path': self.prefix + 'raw.json', 'sha256': hashlib.sha256((self.base / 'raw.json').read_bytes()).hexdigest()}])
        result = self.store.search('重新检查平方和已有测量结果')
        self.assertEqual(result['results'][0]['run_id'], 'zh-run')
        self.assertEqual(result['results'][0]['applicability'], 'unchecked')

    def test_exact_context_recovers_candidate_despite_zero_query_word_overlap(self):
        self.register()
        query = '不使用旧标题的完全不同说法'
        self.assertEqual(self.store.search(query)['status'], 'no_hits')
        result = self.store.decide(query, self.context, verifier=self.verify)
        self.assertEqual(result['search']['results'][0]['match'], 'exact-context')
        self.assertEqual(result['results'][0]['decision'], 'reuse')

    def test_partial_or_broken_scan_is_not_called_complete_no_hits(self):
        self.register()
        (self.base / 'record.json').write_text('{')
        result = self.store.search('unmatched-xyz')
        self.assertEqual(result['status'], 'incomplete')

    def test_protected_root_symlink_and_path_traversal_rejected(self):
        guide = self.root / 'agent_doc/guide'
        guide.mkdir()
        for supplied in (guide, self.root / 'alias'):
            if supplied.name == 'alias':
                supplied.symlink_to(guide, target_is_directory=True)
            with self.assertRaises(ValueError):
                ResultStore(supplied)._save({'run_id': 'bad'})
        self.assertEqual(list(guide.iterdir()), [])
        with self.assertRaises(ValueError):
            self.store.show('../guide')
        (self.root / 'agent_doc/results/link').symlink_to(guide, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.store.search('query')

    def test_cli_context_search_and_readonly_decision(self):
        self.register()
        context_path = self.root / 'request-context.json'
        context_path.write_text(json.dumps(self.context))
        script = Path(__file__).resolve().parents[1] / 'scripts/result_store.py'
        run = subprocess.run([sys.executable, str(script), '--root', str(self.root),
                              'decide', 'integer', '--context', str(context_path)],
                             text=True, capture_output=True, check=True)
        result = json.loads(run.stdout)
        self.assertEqual(result['results'][0]['decision'], 'verify_delta')


if __name__ == '__main__':
    unittest.main()
