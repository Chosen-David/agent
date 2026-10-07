"""Real SQLite correction propagation and task acceptance; no model calls."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.core import Outcome
from agent_runtime.project_memory import MemoryError, MemoryLedger
from agent_runtime.task_manifest import ReportingHandler, atomic_json, prepare, result_report, review


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = MemoryLedger(self.root, create=True)

    def seed(self):
        self.ledger.add('intent-v1', 'intention', 'Compare throughput', 'chat:turn1 quote',
                        scope=['T1'], evidence='user_confirmed')
        self.ledger.add('raw-v1', 'observation', 'run1 produced 20 items', 'runs/1/data.json sha256:x',
                        evidence='verified')
        self.ledger.add('claim-v1', 'claim', 'A meets the intended goal', 'run1 independent check',
                        deps=['intent-v1', 'raw-v1'], evidence='verified')
        self.ledger.add('chart-v1', 'artifact', 'throughput.svg', 'run1 chart checksum',
                        deps=['claim-v1'], evidence='verified')
        self.ledger.add('report-v1', 'artifact', 'report.md', 'run1 report checksum',
                        deps=['chart-v1'], evidence='verified')
        self.ledger.add('other-v1', 'procedure', 'Run unrelated lint', 'review:11', evidence='verified')

    def correct(self, new_id='intent-v2'):
        return self.ledger.correct('intent-v1', new_id, 'Compare latency',
                                   'chat:turn9 user quote: I meant latency', 'misunderstood metric')

    def test_correction_stales_transitive_outputs_preserves_observations_and_bytes(self):
        self.seed()
        raw_path = self.root / 'raw.bin'
        raw_path.write_bytes(b'original measurement')
        self.assertEqual({v['id'] for v in self.ledger.impact('intent-v1')},
                         {'claim-v1', 'chart-v1', 'report-v1'})
        self.correct()
        for ref in ('claim-v1', 'chart-v1', 'report-v1'):
            self.assertEqual(self.ledger.history(ref)['entry']['status'], 'stale')
            with self.assertRaises(MemoryError):
                self.ledger.check([ref])
        self.assertEqual({v['id'] for v in self.ledger.list()}, {'intent-v2', 'raw-v1', 'other-v1'})
        self.assertEqual(self.ledger.history('intent-v1')['entry']['content'], 'Compare throughput')
        self.assertEqual(self.ledger.history('report-v1')['events'][-1]['related_id'], 'intent-v1')
        self.assertEqual(raw_path.read_bytes(), b'original measurement')
        self.ledger.check(['raw-v1', 'other-v1', 'intent-v2'])
        # Adding the correct interpretation creates new evidence; it cannot resurrect the old report.
        self.ledger.add('claim-v2', 'claim', 'latency still needs measurement', 'review:12',
                        deps=['intent-v2'], evidence='verified')
        self.assertEqual(self.ledger.history('report-v1')['entry']['status'], 'stale')

    def test_candidates_require_explicit_new_revision_acceptance(self):
        self.ledger.add('guess', 'assumption', 'Maybe caching helps', 'reflection:1')
        self.assertEqual(self.ledger.list(), [])
        with self.assertRaises(MemoryError):
            self.ledger.check(['guess'])
        self.ledger.accept('guess', 'validated', 'experiment:heldout-1', 'independent acceptance')
        self.assertEqual(self.ledger.check(['validated'])[0]['evidence'], 'verified')
        self.assertEqual(self.ledger.history('guess')['entry']['status'], 'superseded')

    def test_invalid_dependencies_and_duplicate_ids_rejected_without_partial_writes(self):
        self.seed()
        self.ledger.add('candidate', 'claim', 'unverified', 'reflection:2')
        self.correct()
        for dep in ('missing', 'intent-v1', 'claim-v1', 'candidate'):
            with self.subTest(dep=dep), self.assertRaises(MemoryError):
                self.ledger.add('attempt', 'claim', 'bad lineage', 'source', [dep], evidence='verified')
        with self.assertRaises(MemoryError):
            self.ledger.add('raw-v1', 'observation', 'overwrite', 'new source')
        with self.assertRaises(MemoryError):
            self.ledger.add('no-source', 'claim', 'unsupported', '')
        with self.assertRaises(MemoryError):
            self.ledger.add('self', 'claim', 'cycle', 'source', ['self'])
        self.assertFalse(any(v['id'] == 'attempt' for v in self.ledger.list('all')))

    def test_correction_rolls_back_every_mutation_on_error(self):
        self.seed()
        old = self.ledger.list('all')
        original_event = self.ledger._event
        def fail_at_descendant(db, entry_id, action, *args):
            if action == 'stale':
                raise sqlite3.OperationalError('injected write failure')
            return original_event(db, entry_id, action, *args)
        with patch.object(MemoryLedger, '_event', side_effect=fail_at_descendant):
            with self.assertRaisesRegex(MemoryError, 'injected'):
                self.correct()
        self.assertEqual(self.ledger.list('all'), old)
        self.assertEqual(len(self.ledger.history('intent-v1')['events']), 1)
        with self.assertRaisesRegex(MemoryError, 'invalidated lineage'):
            self.ledger.correct('intent-v1', 'bad-revision', 'new', 'user quote', 'reason', ['report-v1'])

    def test_concurrent_corrections_serialize_with_one_winner(self):
        self.seed()
        def writer(index):
            try:
                return self.correct(f'revision-{index}')
            except MemoryError:
                return None
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(writer, range(4)))
        self.assertEqual(sum(r is not None for r in results), 1)
        self.assertEqual(len([v for v in self.ledger.list() if v['kind'] == 'intention']), 1)
        self.assertEqual(len(self.ledger.history('intent-v1')['events']), 2)

    def test_missing_corrupt_or_malformed_refs_fail_closed(self):
        with self.assertRaises(MemoryError):
            MemoryLedger(self.root / 'other').check(['id'])
        self.assertFalse((self.root / 'other').exists())
        for refs in ([], 'intent', [None], ['id', 'id']):
            with self.assertRaises(MemoryError):
                self.ledger.check(refs)
        self.ledger.path.write_bytes(b'not sqlite')
        with self.assertRaises(MemoryError):
            self.ledger.check(['id'])

    def test_symlink_and_dangling_ledger_paths_rejected_by_api_and_cli(self):
        external = MemoryLedger(self.root / 'external', create=True)
        external.add('outside', 'observation', 'preserve external data', 'fixture', evidence='verified')
        original = external.path.read_bytes()
        for directory in (True, False):
            for dangling in (True, False):
                with self.subTest(directory=directory, dangling=dangling):
                    project = self.root / f'project-{directory}-{dangling}'
                    project.mkdir()
                    link = project / '.agent-memory'
                    if not directory:
                        link.mkdir()
                        link = link / 'memory.sqlite3'
                    target = external.path.parent if directory else external.path
                    if dangling:
                        target = self.root / f'missing-{directory}'
                    link.symlink_to(target, target_is_directory=directory)
                    for create in (False, True):
                        with self.assertRaisesRegex(MemoryError, 'symlink'):
                            MemoryLedger(project, create=create)
                    command = [sys.executable, '-m', 'agent_runtime.project_memory',
                               '--root', str(project), 'add', '--id', 'intrusion',
                               '--kind', 'claim', '--content', 'new', '--source', 'test']
                    failed = subprocess.run(command, capture_output=True, text=True)
                    self.assertEqual(failed.returncode, 2)
                    self.assertIn('symlink', json.loads(failed.stderr)['error'])
                    self.assertEqual(external.path.read_bytes(), original)
                    if dangling:
                        self.assertFalse(target.exists())

    def test_nonregular_paths_and_symlink_replacement_after_open_rejected(self):
        external_file = self.root / 'outside.bin'
        external_file.write_bytes(b'unchanged')
        self.ledger.path.unlink()
        self.ledger.path.symlink_to(external_file)
        with self.assertRaisesRegex(MemoryError, 'symlink'):
            self.ledger.list()
        self.assertEqual(external_file.read_bytes(), b'unchanged')
        self.ledger.path.unlink()
        self.ledger.path.mkdir()
        with self.assertRaisesRegex(MemoryError, 'regular file'):
            self.ledger.list()
        self.ledger.path.rmdir()
        if hasattr(os, 'mkfifo'):
            os.mkfifo(self.ledger.path)
            with self.assertRaisesRegex(MemoryError, 'regular file'):
                self.ledger.list()
            self.ledger.path.unlink()
        self.ledger.path.parent.rmdir()
        self.ledger.path.parent.write_text('not a directory')
        with self.assertRaisesRegex(MemoryError, 'directory'):
            MemoryLedger(self.root, create=True)

    def report_fixture(self):
        self.seed()
        (self.root / 'TASK.md').write_text('- [ ] [T1] Answer correct research question\n')
        plan = prepare(self.root / 'TASK.md', 'run1', 'auto', 'user instruction')
        task = plan['tasks'][0]
        task['memory_refs'] = ['intent-v1', 'report-v1']
        atomic_json(self.root / task['report_path'], {'task_id': 'T1', 'summary': 'fixture report',
                    'data': [{'kind': 'synthetic', 'description': 'fixture values'}]})
        class Handler:
            idempotent = True
            required_capabilities = ()
            calls = 0
            def run(self, task, context):
                self.calls += 1
                return Outcome('complete', 'fixture', [{'fixture': True}])
            def verify(self, task, evidence):
                return evidence == [{'fixture': True}]
        base = Handler()
        return plan, task, base, ReportingHandler(base, self.root)

    def test_correction_before_dispatch_prevents_handler_execution(self):
        _, task, base, wrapper = self.report_fixture()
        self.correct()
        self.assertEqual(wrapper.run(task, {}).status, 'blocked')
        self.assertEqual(base.calls, 0)
        with self.assertRaises(MemoryError):
            result_report(self.root, task)

    def test_correction_after_acceptance_marks_done_report_needs_review(self):
        plan, task, _, wrapper = self.report_fixture()
        outcome = wrapper.run(task, {})
        self.assertTrue(wrapper.verify(task, outcome.evidence))
        snapshot = {'plan': plan, 'state': {'status': 'done', 'tasks': {
            'T1': {'status': 'done', 'reason': 'accepted', 'evidence': outcome.evidence}}}}
        self.assertTrue(review(snapshot, self.root)['all_reportable'])
        self.correct()
        self.assertFalse(wrapper.verify(task, outcome.evidence))
        report = review(snapshot, self.root)
        self.assertFalse(report['all_reportable'])
        self.assertEqual(report['requirements'][0]['nodes'][0]['status'], 'needs_review')
        self.assertEqual(snapshot['state']['tasks']['T1']['status'], 'done')

    def test_correction_during_execution_or_independent_verification_blocks_acceptance(self):
        _, task, base, wrapper = self.report_fixture()
        with patch.object(base, 'run', side_effect=lambda *_: (self.correct(), Outcome('complete', 'x', []))[1]):
            self.assertEqual(wrapper.run(task, {}).status, 'blocked')
        # New task refs require actual revalidated revisions, not a renamed old report.
        task['memory_refs'] = ['intent-v2']
        outcome = wrapper.run(task, {})
        with patch.object(base, 'verify', side_effect=lambda *_: (
                self.ledger.correct('intent-v2', 'intent-v3', 'New scope', 'chat:turn10 quote', 'changed goal'), True)[1]):
            self.assertFalse(wrapper.verify(task, outcome.evidence))

    def test_independent_verifier_still_required(self):
        _, task, base, wrapper = self.report_fixture()
        outcome = wrapper.run(task, {})
        with patch.object(base, 'verify', return_value=False):
            self.assertFalse(wrapper.verify(task, outcome.evidence))

    def test_cli_reports_json_and_nonzero_for_stale_refs(self):
        self.seed()
        command = [sys.executable, '-m', 'agent_runtime.project_memory', '--root', str(self.root)]
        success = subprocess.run(command + ['check', 'report-v1'], capture_output=True, text=True)
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertEqual(json.loads(success.stdout)[0]['id'], 'report-v1')
        self.correct()
        failed = subprocess.run(command + ['check', 'report-v1'], capture_output=True, text=True)
        self.assertEqual(failed.returncode, 2)
        self.assertIn('stale', json.loads(failed.stderr)['error'])


class DocumentMemoryTests(unittest.TestCase):
    def test_guide_revision_invalidates_bound_interpretations_not_raw_measurements(self):
        from agent_runtime.project_docs import migrate, snapshot_project_docs
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'TASK.md').write_text('## 2026-10-07\n- [ ] [T1] Validate result\n')
            migrate(root, '2026-10-07')
            guide = root / 'doc/guide/guide.md'; guide.write_text('Owner metric A')
            ledger = MemoryLedger(root, create=True)
            ledger.add('raw', 'observation', 'Original measured bytes', 'fixture:measurement', evidence='verified')
            ledger.add('claim', 'claim', 'Accepted under metric A', 'fixture:independent-review',
                       deps=['raw'], evidence='verified', document_refs=snapshot_project_docs(root))
            ledger.add('report', 'artifact', 'Dependent report', 'fixture:report', deps=['claim'], evidence='verified')
            ledger.check(['report'])
            guide.write_text('Owner metric B')
            for entry in ('claim', 'report'):
                with self.assertRaisesRegex(MemoryError, 'document dependencies'):
                    ledger.check([entry])
            self.assertEqual(ledger.check(['raw'])[0]['content'], 'Original measured bytes')
            self.assertEqual(ledger.history('claim')['entry']['content'], 'Accepted under metric A')

    def test_progress_does_not_invalidate_memory_but_current_binding_required_for_revision(self):
        from agent_runtime.project_docs import migrate, snapshot_project_docs, write_task_progress
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'TASK.md').write_text('## 2026-10-07\n- [ ] [T1] Validate result\n')
            snapshot = migrate(root, '2026-10-07')
            ledger = MemoryLedger(root, create=True)
            ledger.add('intent', 'intention', 'Original plan', 'owner:1', evidence='user_confirmed', document_refs=snapshot)
            write_task_progress(root, 'T1', 'Routine evidence append',
                                expected_plan_sha256=snapshot['task_details']['T1']['sha256'])
            ledger.check(['intent'])
            with self.assertRaisesRegex(MemoryError, 'new current'):
                ledger.correct('intent', 'intent-v2', 'Correction', 'owner:2', 'reason')
            ledger.correct('intent', 'intent-v2', 'Correction', 'owner:2', 'reason',
                           document_refs=snapshot_project_docs(root))
            ledger.check(['intent-v2'])


if __name__ == '__main__':
    unittest.main()
