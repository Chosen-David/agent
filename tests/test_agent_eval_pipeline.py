"""Behavioral tests of recording gates; these never claim model execution."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('pipeline', Path(__file__).resolve().parents[1] / 'scripts/agent_eval_pipeline.py')
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')
        self.put('plugins/demo/SKILL.md', 'Read the task and produce result.')
        self.put('plugins/demo/tests/answer.txt', 'must not copy')
        self.put('scripts/publish_report.py', '# pinned publication entry point\n')
        self.put('evals/fixtures/input.txt', 'original')
        self.tasks = {'cases': [{'id': c, 'skill': 'plugins/demo/SKILL.md', 'prompt': 'Compute an answer', 'fixtures': ['input.txt']} for c in ('a', 'b')]}
        self.rubric = {'criteria': {c: ['numeric correctness', 'source fidelity'] for c in ('a', 'b')}}
        self.put('evals/tasks.json', json.dumps(self.tasks))
        self.put('evals/rubric.json', json.dumps(self.rubric))
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        self.sha = self.git('rev-parse', 'HEAD').strip()
        self.run = self.base / 'run'
        pipeline.prepare_run(self.repo, self.sha, self.run)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True, stderr=subprocess.PIPE)

    def put(self, name, text):
        target = self.repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def record(self, name, data):
        path = self.base / (name + '.json')
        path.write_text(json.dumps(data))
        return path

    def start(self, cid='a', attempt=1, adapter='host', event=None):
        receipt = {'event_id': event or f'start-{cid}-{attempt}', 'kind': 'start', 'actor': 'worker',
                   'adapter': adapter, 'case_id': cid, 'attempt': attempt}
        return pipeline.record_start(self.run, cid, 'worker', self.record('start', receipt))

    def finish(self, directory, cid='a', attempt=1, status='produced', adapter='host', output=True):
        if output:
            (directory / 'outputs/result.txt').write_text('42 with source input.txt')
        receipt = {'event_id': f'end-{cid}-{attempt}', 'kind': 'complete', 'actor': 'worker', 'adapter': adapter,
                   'case_id': cid, 'attempt': attempt, 'status': status}
        return pipeline.collect(self.run, cid, attempt, self.record('end', receipt))

    def grade(self, directory, cid='a', attempt=1, **override):
        data = {'grader': 'reviewer', 'case_id': cid, 'attempt': attempt,
                'output_hashes': pipeline.hashes(directory / 'outputs'),
                'checks': [{'criterion': criterion, 'verdict': 'pass', 'evidence': ['result.txt:1 compared with input.txt:1']}
                           for criterion in self.rubric['criteria'][cid]]}
        data.update(override)
        return pipeline.grade_attempt(self.run, cid, attempt, self.record('grade', data))

    def test_pinned_source_and_no_grader_material(self):
        self.put('plugins/demo/SKILL.md', 'uncommitted replacement')
        self.assertEqual((self.run / 'snapshot/plugins/demo/SKILL.md').read_text(), 'Read the task and produce result.')
        self.assertFalse((self.run / 'snapshot/evals').exists())
        self.assertFalse((self.run / 'snapshot/plugins/demo/tests').exists())
        self.assertEqual((self.run / 'snapshot/scripts/publish_report.py').read_text(),
                         '# pinned publication entry point\n')

    def test_happy_path_fixed_denominator(self):
        for cid in ('a', 'b'):
            directory = self.start(cid)
            self.finish(directory, cid)
            self.grade(directory, cid)
        result = pipeline.report(self.run)
        self.assertTrue(result['complete'])
        self.assertEqual((result['expected'], result['passed'], result['first_pass']), (2, 2, 2))
        self.assertEqual((result['correct_to_wrong'], result['wrong_to_correct']), (0, 0))

    def graded_attempt(self, cid, attempt, verdict, adapter='host'):
        directory = self.start(cid, attempt, adapter=adapter)
        self.finish(directory, cid, attempt, adapter=adapter)
        self.grade(directory, cid, attempt,
                   checks=[{'criterion': c, 'verdict': verdict, 'evidence': ['result.txt:1']}
                           for c in self.rubric['criteria'][cid]])
        return directory

    def test_semantic_transitions_compare_first_with_final(self):
        self.graded_attempt('a', 1, 'pass')
        self.graded_attempt('a', 2, 'pass')
        self.graded_attempt('a', 3, 'fail')
        self.graded_attempt('b', 1, 'fail')
        self.graded_attempt('b', 2, 'pass')
        result = pipeline.report(self.run)
        self.assertEqual((result['correct_to_wrong'], result['wrong_to_correct']), (1, 1))
        self.assertEqual((result['expected'], result['first_pass'], result['passed']), (2, 1, 1))
        self.assertFalse(result['complete'])
        self.assertEqual(result['cases'][0]['attempts'][-1]['semantic_verdict'], 'fail')

    def test_intermediate_repair_is_not_final_improvement(self):
        self.graded_attempt('a', 1, 'fail')
        self.graded_attempt('a', 2, 'pass')
        self.graded_attempt('a', 3, 'fail')
        result = pipeline.report(self.run)
        self.assertEqual((result['correct_to_wrong'], result['wrong_to_correct']), (0, 0))
        self.assertEqual(result['passed'], 0)

    def test_ungradable_or_ungraded_is_not_wrong(self):
        for cid, first, last in [('a', 'pass', 'ungradable'), ('b', 'ungradable', 'pass')]:
            self.graded_attempt(cid, 1, first)
            self.graded_attempt(cid, 2, last)
        result = pipeline.report(self.run)
        self.assertEqual((result['correct_to_wrong'], result['wrong_to_correct']), (0, 0))
        directory = self.start('b', 3)
        self.finish(directory, 'b', 3)
        result = pipeline.report(self.run)
        self.assertEqual(result['cases'][1]['attempts'][-1]['status'], 'ungraded')
        self.assertIsNone(result['cases'][1]['attempts'][-1]['semantic_verdict'])
        self.assertEqual((result['correct_to_wrong'], result['wrong_to_correct']), (0, 0))

    def test_infrastructure_recovery_and_blocking_are_not_semantic_changes(self):
        directory = self.start('a')
        self.finish(directory, 'a', status='infra_error', output=False)
        self.graded_attempt('a', 2, 'pass')
        self.graded_attempt('b', 1, 'pass')
        directory = self.start('b', 2)
        self.finish(directory, 'b', 2, status='blocked', output=False)
        result = pipeline.report(self.run)
        self.assertEqual((result['correct_to_wrong'], result['wrong_to_correct']), (0, 0))
        self.assertEqual((result['first_pass'], result['passed']), (1, 1))

    def test_tampered_grade_and_snapshot_do_not_count_semantic_repair(self):
        self.graded_attempt('a', 1, 'fail')
        directory = self.graded_attempt('a', 2, 'pass')
        self.assertEqual(pipeline.report(self.run)['wrong_to_correct'], 1)
        (directory / 'outputs/result.txt').write_text('unreviewed')
        result = pipeline.report(self.run)
        self.assertEqual((result['correct_to_wrong'], result['wrong_to_correct']), (0, 0))
        (directory / 'outputs/result.txt').write_text('42 with source input.txt')
        self.assertEqual(pipeline.report(self.run)['wrong_to_correct'], 1)
        (self.run / 'snapshot/plugins/demo/SKILL.md').write_text('tampered')
        result = pipeline.report(self.run)
        self.assertTrue(result['integrity_errors'])
        self.assertEqual((result['correct_to_wrong'], result['wrong_to_correct']), (0, 0))

    def test_mock_semantic_grades_do_not_count_as_real_repair(self):
        self.run = self.base / 'mock-transitions'
        pipeline.prepare_run(self.repo, self.sha, self.run, adapter={'name': 'mock'})
        self.graded_attempt('a', 1, 'fail', adapter='mock')
        self.graded_attempt('a', 2, 'pass', adapter='mock')
        result = pipeline.report(self.run)
        self.assertEqual((result['correct_to_wrong'], result['wrong_to_correct']), (0, 0))
        self.assertTrue(all(a['semantic_verdict'] is None for a in result['cases'][0]['attempts']))

    def test_unexecuted_case_never_disappears(self):
        directory = self.start()
        self.finish(directory)
        self.grade(directory)
        result = pipeline.report(self.run)
        self.assertEqual((result['expected'], result['passed']), (2, 1))
        self.assertFalse(result['complete'])

    def test_empty_grading_rejected(self):
        directory = self.start()
        self.finish(directory)
        with self.assertRaises(ValueError):
            self.grade(directory, checks=[])

    def test_missing_output_rejected(self):
        directory = self.start()
        self.finish(directory, output=False)
        with self.assertRaises(ValueError):
            self.grade(directory)
        self.assertEqual(pipeline.report(self.run)['passed'], 0)

    def test_self_grading_rejected(self):
        directory = self.start()
        self.finish(directory)
        with self.assertRaises(ValueError):
            self.grade(directory, grader='worker')

    def test_wrong_or_duplicate_criteria_rejected(self):
        directory = self.start()
        self.finish(directory)
        with self.assertRaises(ValueError):
            self.grade(directory, checks=[{'criterion': 'numeric correctness', 'verdict': 'pass', 'evidence': ['result.txt:1']}] * 2)

    def test_evidence_required(self):
        directory = self.start()
        self.finish(directory)
        with self.assertRaises(ValueError):
            self.grade(directory, checks=[{'criterion': c, 'verdict': 'pass', 'evidence': []} for c in self.rubric['criteria']['a']])

    def test_changed_output_after_grading_fails(self):
        directory = self.start()
        self.finish(directory)
        self.grade(directory)
        (directory / 'outputs/result.txt').write_text('different')
        self.assertEqual(pipeline.report(self.run)['passed'], 0)

    def test_changed_output_before_grading_rejected(self):
        directory = self.start()
        self.finish(directory)
        (directory / 'outputs/result.txt').write_text('different')
        with self.assertRaises(ValueError):
            self.grade(directory)

    def test_changed_input_and_snapshot_invalidate(self):
        directory = self.start()
        self.finish(directory)
        self.grade(directory)
        (self.run / 'cases/a/inputs/input.txt').write_text('tampered')
        (self.run / 'snapshot/plugins/demo/SKILL.md').write_text('tampered')
        report = pipeline.report(self.run)
        self.assertEqual(report['passed'], 0)
        self.assertEqual(len(report['integrity_errors']), 2)
        with self.assertRaises(ValueError):
            self.start('b')

    def test_duplicate_dispatch_and_collection_rejected(self):
        directory = self.start()
        with self.assertRaises(ValueError):
            self.start()
        self.finish(directory)
        with self.assertRaises(FileExistsError):
            self.finish(directory)

    def test_duplicate_host_event_rejected(self):
        self.start(event='one-event')
        with self.assertRaises(ValueError):
            self.start('b', event='one-event')

    def test_error_retry_keeps_history_and_first_pass(self):
        directory = self.start()
        self.finish(directory, status='infra_error', output=False)
        second = self.start(attempt=2)
        self.finish(second, attempt=2)
        self.grade(second, attempt=2)
        report = pipeline.report(self.run)
        self.assertEqual((report['passed'], report['first_pass']), (1, 0))
        self.assertEqual(report['cases'][0]['attempts'][0]['status'], 'infra_error')

    def test_mock_is_never_real_execution(self):
        self.run = self.base / 'mock-run'
        pipeline.prepare_run(self.repo, self.sha, self.run, adapter={'name': 'mock'})
        directory = self.start(adapter='mock')
        self.finish(directory, adapter='mock')
        self.grade(directory)
        self.assertEqual(pipeline.report(self.run)['passed'], 0)

    def test_frozen_adapter_required(self):
        with self.assertRaises(ValueError):
            self.start(adapter='mock')

    def test_retry_budget_is_enforced(self):
        for attempt in range(1, 4):
            directory = self.start(attempt=attempt)
            self.finish(directory, attempt=attempt, status='infra_error', output=False)
        with self.assertRaises(ValueError):
            self.start(attempt=4)

    def test_implementation_change_invalidates_run(self):
        original = pipeline.__file__
        changed = self.base / 'changed.py'
        changed.write_text('different implementation')
        try:
            pipeline.__file__ = str(changed)
            self.assertIn('pipeline implementation changed', pipeline.report(self.run)['integrity_errors'])
            with self.assertRaises(ValueError):
                self.start()
        finally:
            pipeline.__file__ = original

    def test_cli_strict_report_exits_nonzero(self):
        result = subprocess.run(['python', pipeline.__file__, 'report', '--run', str(self.run), '--require-complete'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)['complete'])

    def test_receipt_mismatch_rejected(self):
        bad = self.record('bad', {'event_id': 'x', 'kind': 'start', 'actor': 'different', 'adapter': 'host', 'case_id': 'a', 'attempt': 1})
        with self.assertRaises(ValueError):
            pipeline.record_start(self.run, 'a', 'worker', bad)

    def test_symlink_output_rejected(self):
        directory = self.start()
        (directory / 'outputs/link').symlink_to(self.repo / 'evals/rubric.json')
        with self.assertRaises(ValueError):
            self.finish(directory)

    def test_path_escape_and_duplicate_case_rejected(self):
        for bad in ('../secret', '/absolute', 'folder/../../secret'):
            with self.assertRaises(ValueError):
                pipeline.safe_relative(bad)
        self.tasks['cases'].append(self.tasks['cases'][0])
        tasks = self.record('tasks', self.tasks)
        with self.assertRaises(ValueError):
            pipeline.prepare_run(self.repo, self.sha, self.base / 'invalid', tasks=tasks)

    def test_incomplete_rubric_rejected(self):
        rubric = self.record('rubric', {'criteria': {'a': []}})
        with self.assertRaises(ValueError):
            pipeline.prepare_run(self.repo, self.sha, self.base / 'invalid', rubric=rubric)

    def test_persisted_receipts_rechecked_on_report(self):
        directory = self.start()
        self.finish(directory)
        self.grade(directory)
        path = directory / 'collection.json'
        original = path.read_text()
        for key, value in [('actor', 'other'), ('case_id', 'b'), ('attempt', 2),
                           ('kind', 'start'), ('status', 'blocked'), ('event_id', '')]:
            with self.subTest(key=key):
                data = json.loads(original)
                data['receipt'][key] = value
                path.write_text(json.dumps(data))
                self.assertEqual(pipeline.report(self.run)['passed'], 0)
        path.write_text(original)
        start = pipeline.read(directory / 'start.json')
        start['receipt']['actor'] = 'other'
        (directory / 'start.json').write_text(json.dumps(start))
        self.assertEqual(pipeline.report(self.run)['passed'], 0)

    def test_empty_manifest_does_not_erase_frozen_cases(self):
        manifest = pipeline.read(self.run / 'manifest.json')
        manifest.update(expected_cases=[], cases={})
        (self.run / 'manifest.json').write_text(json.dumps(manifest))
        report = pipeline.report(self.run)
        self.assertFalse(report['complete'])
        self.assertEqual(report['expected'], 2)

    def test_malformed_grade_shapes_fail_closed(self):
        directory = self.start()
        self.finish(directory)
        for data in ([], {'checks': ['pass']}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                pipeline.grade_attempt(self.run, 'a', 1, self.record('bad-grade', data))
        self.grade(directory)
        data = pipeline.read(directory / 'grade.json')
        data['checks'] = ['pass', 'pass']
        (directory / 'grade.json').write_text(json.dumps(data))
        self.assertEqual(pipeline.report(self.run)['passed'], 0)

    def test_pass_requires_real_output_reference(self):
        directory = self.start()
        self.finish(directory)
        for refs in (None, ['../result.txt'], ['missing.txt'], []):
            checks = [{'criterion': c, 'verdict': 'pass', 'evidence': ['../../missing.txt:1']}
                      for c in self.rubric['criteria']['a']]
            if refs is not None:
                for check in checks:
                    check['artifact_refs'] = refs
            with self.subTest(refs=refs), self.assertRaises(ValueError):
                self.grade(directory, checks=checks)

    def test_explicit_artifact_reference_and_ungradable(self):
        directory = self.start()
        self.finish(directory)
        checks = [{'criterion': 'numeric correctness', 'verdict': 'pass',
                   'evidence': ['Reviewed calculation against input'], 'artifact_refs': ['result.txt']},
                  {'criterion': 'source fidelity', 'verdict': 'ungradable', 'evidence': ['Source unavailable']}]
        self.grade(directory, checks=checks)
        self.assertEqual(pipeline.report(self.run)['passed'], 0)

    def test_missing_case_directory_is_invalid_report(self):
        (self.run / 'cases/a').rename(self.run / 'cases/moved')
        result = pipeline.report(self.run)
        self.assertEqual(result['expected'], 2)
        self.assertFalse(result['complete'])

    def test_reused_completion_event_is_rejected(self):
        directory = self.start()
        receipt = {'event_id': 'start-a-1', 'kind': 'complete', 'actor': 'worker',
                   'case_id': 'a', 'attempt': 1, 'adapter': 'host', 'status': 'blocked'}
        with self.assertRaises(ValueError):
            pipeline.collect(self.run, 'a', 1, self.record('end', receipt))

    def test_renamed_attempt_directory_invalidates(self):
        directory = self.start()
        self.finish(directory)
        self.grade(directory)
        directory.rename(directory.parent / '0002')
        self.assertEqual(pipeline.report(self.run)['passed'], 0)

    def test_ancestor_symlink_escape_is_rejected(self):
        directory = self.start()
        self.finish(directory)
        self.grade(directory)
        outside = self.base / 'escaped-attempt'
        directory.rename(outside)
        directory.symlink_to(outside, target_is_directory=True)
        self.assertFalse(pipeline.report(self.run)['complete'])
        self.assertEqual(pipeline.report(self.run)['passed'], 0)

    def test_case_directory_symlink_escape_is_rejected(self):
        directory = self.start()
        self.finish(directory)
        self.grade(directory)
        case = self.run / 'cases/a'
        outside = self.base / 'escaped-case'
        case.rename(outside)
        case.symlink_to(outside, target_is_directory=True)
        self.assertFalse(pipeline.report(self.run)['complete'])
        with self.assertRaises(ValueError):
            self.start('b')

    def test_manifest_change_after_dispatch_rejected(self):
        directory = self.start()
        manifest = pipeline.read(self.run / 'manifest.json')
        manifest['adapter']['model'] = 'changed'
        (self.run / 'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            self.finish(directory)


if __name__ == '__main__':
    unittest.main()
