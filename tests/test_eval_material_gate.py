"""Synthetic controller tests: actual arithmetic and gate, never model execution.

Oracle adapters below are task-specific. Mapping prose criteria to the oracle is
an explicit test-controller judgment, not a claimed natural-language verifier.
"""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('material_pipeline', ROOT / 'scripts/agent_eval_pipeline.py')
p = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p)


class MaterialGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Synthetic controller')
        for name, text in {
            'plugins/demo/SKILL.md': 'Read task. No grader materials.',
            'evals/fixtures/data.json': json.dumps({'baseline_ms': 80, 'candidate_ms': 80}),
            'evals/tasks.json': json.dumps({'cases': [{'id': 'a', 'skill': 'plugins/demo/SKILL.md',
                'prompt': 'Describe the comparison.', 'fixtures': ['data.json']}]}),
            'evals/rubric.json': json.dumps({'criteria': {'a': ['Report medium parity', 'Keep evidence separate']}}),
        }.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self.git('add', '.')
        self.git('commit', '-qm', 'Synthetic fixture')
        self.sha = self.git('rev-parse', 'HEAD').strip()
        self.run = self.base / 'run'
        p.prepare_run(self.repo, self.sha, self.run, require_material_review=True)
        self.review_path = self.base / 'review.json'
        self.evidence = self.base / 'oracle.json'
        self.evidence.write_text(json.dumps({'synthetic_control': True, 'actual_direction': 'parity'}))
        self.review = self.make_review()
        self.trust = self.save_review()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True, stderr=subprocess.PIPE)

    def make_review(self, factual_ok=True):
        manifest, errors = p.verify_run(self.run)
        self.assertEqual(errors, [])
        criteria = p.read(self.run / 'rubric.json')['criteria']
        return {'schema_version': 1, 'reviewer_actor': 'independent-reviewer',
            'material_hashes': p.material_bindings(self.run, manifest),
            'cases': {cid: [{'criterion': c, 'kind': 'factual' if i == 0 else 'behavioral',
                'status': 'supported' if i or factual_ok else 'not_supported',
                'verification': 'executable_oracle' if i == 0 else 'task_requirement',
                'reason': 'Synthetic controller compared exact criterion with computed evidence.' if i == 0 else
                          'Valid behavioral requirement; not an assertion of task success.',
                'evidence': [{'path': str(self.evidence), 'sha256': p.digest(self.evidence.read_bytes()),
                             'location': 'actual_direction; synthetic control'}]}
                for i, c in enumerate(checks)] for cid, checks in criteria.items()}}

    def save_review(self):
        self.review_path.write_text(json.dumps(self.review))
        return {'path': str(self.review_path), 'sha256': p.digest(self.review_path.read_bytes()),
                'reviewer_actor': 'independent-reviewer'}

    def start(self, trust=None, actor='worker'):
        receipt = self.base / 'receipt.json'
        receipt.write_text(json.dumps({'event_id': 'synthetic-start', 'kind': 'start', 'actor': actor,
            'adapter': 'host', 'case_id': 'a', 'attempt': 1}))
        return p.record_start(self.run, 'a', actor, receipt, material_review=trust)

    def assert_rejected(self, trust=None, actor='worker'):
        calls = []
        with self.assertRaises((ValueError, OSError, KeyError, TypeError)):
            p.authorize_dispatch(self.run, 'a', actor, material_review=trust)
            calls.append('would-spawn')
        self.assertEqual(calls, [])
        with self.assertRaises((ValueError, OSError, KeyError, TypeError)):
            self.start(trust, actor)
        self.assertEqual(list((self.run / 'cases/a/attempts').iterdir()), [])

    def test_valid_pre_spawn_and_record_start_no_answers_in_snapshot(self):
        p.authorize_dispatch(self.run, 'a', 'worker', material_review=self.trust)
        directory = self.start(self.trust)
        manifest, _ = p.verify_run(self.run)
        self.assertEqual(p.validate_start(self.run, manifest, directory, 'a')['actor'], 'worker')
        self.assertNotIn(self.review_path.name, [x.name for x in (self.run / 'snapshot').rglob('*')])
        self.assertFalse((self.run / 'snapshot/evals').exists())
        self.assertEqual(p.hashes(self.run / 'cases/a/inputs').keys(), {'data.json'})

    def test_missing_trust(self):
        self.assert_rejected()

    def test_forged_identity_and_reviewer_cannot_execute(self):
        self.assert_rejected(self.trust, 'independent-reviewer')
        self.review['reviewer_actor'] = 'forged-reviewer'
        self.assert_rejected(self.save_review())

    def test_worker_only_self_report_cannot_supply_trust(self):
        self.assert_rejected(self.review)

    def test_status_and_exact_criterion_coverage(self):
        initial = copy.deepcopy(self.review)
        mutations = [lambda r: r['cases']['a'][0].update(status='not_supported'),
            lambda r: r['cases']['a'][0].update(status='unreviewed'),
            lambda r: r['cases']['a'].pop(),
            lambda r: r['cases']['a'].append(copy.deepcopy(r['cases']['a'][0])),
            lambda r: r['cases']['a'][1].update(criterion=r['cases']['a'][0]['criterion']),
            lambda r: r['cases'].update(extra=[]),
            lambda r: r['cases']['a'][0].update(verification='task_requirement'),
            lambda r: r['cases']['a'][0].update(reason=''),
            lambda r: r['cases']['a'][0].update(evidence=[]),
            lambda r: r['cases']['a'][0].update(kind='anything')]
        for mutation in mutations:
            self.review = copy.deepcopy(initial)
            mutation(self.review)
            with self.subTest(review=self.review):
                self.assert_rejected(self.save_review())

    def test_malformed_review(self):
        for value in [[], None, {}, {'schema_version': True}, {'schema_version': 1, 'reviewer_actor': 'independent-reviewer'}]:
            self.review = value
            self.assert_rejected(self.save_review())

    def test_duplicate_json_fields_rejected(self):
        raw = self.review_path.read_text().replace('{', '{"schema_version": 1,', 1)
        self.review_path.write_text(raw)
        trust = dict(self.trust, sha256=p.digest(self.review_path.read_bytes()))
        self.assert_rejected(trust)

    def test_tampered_review_or_evidence(self):
        self.review_path.write_text(self.review_path.read_text() + ' ')
        self.assert_rejected(self.trust)
        self.trust = self.save_review()
        self.evidence.write_text('changed source evidence')
        self.assert_rejected(self.trust)

    def test_external_material_required(self):
        inside = self.run / 'cases/a/inputs/review.json'
        inside.write_bytes(self.review_path.read_bytes())
        trust = dict(self.trust, path=str(inside))
        # Direct external-artifact check, plus full gate (which also catches input change).
        with self.assertRaisesRegex(ValueError, 'outside worker'):
            p.external_review_artifact(self.run, trust)
        self.assert_rejected(trust)

    def test_symlink_review_rejected(self):
        link = self.base / 'review-link.json'
        link.symlink_to(self.review_path)
        self.assert_rejected(dict(self.trust, path=str(link)))

    def test_symlink_parent_and_relative_traversal_rejected(self):
        link = self.base / 'controller-link'
        link.symlink_to(self.base, target_is_directory=True)
        self.assert_rejected(dict(self.trust, path=str(link / self.review_path.name)))
        self.assert_rejected(dict(self.trust, path='../review.json'))

    def test_portable_controller_bundle_survives_relocation(self):
        controller = self.base / 'controller-evidence'
        controller.mkdir()
        shutil.copyfile(self.evidence, controller / 'oracle.json')
        for check in self.review['cases']['a']:
            check['evidence'][0]['path'] = 'controller-evidence/oracle.json'
        self.review_path = controller / 'review.json'
        trust = self.save_review()
        trust['path'] = 'controller-evidence/review.json'
        self.start(trust)
        restored = self.base / 'restored'
        restored.mkdir()
        shutil.copytree(self.run, restored / 'run')
        shutil.copytree(controller, restored / 'controller-evidence')
        self.run = restored / 'run'
        p.authorize_dispatch(self.run, 'a', 'worker', material_review=trust)
        directory = self.run / 'cases/a/attempts/0001'
        (directory / 'outputs/result.txt').write_text('Synthetic output for relocation test')
        receipt = restored / 'complete.json'
        receipt.write_text(json.dumps({'event_id': 'synthetic-complete', 'kind': 'complete',
            'actor': 'worker', 'adapter': 'host', 'case_id': 'a', 'attempt': 1, 'status': 'produced'}))
        p.collect(self.run, 'a', 1, receipt)
        grade = restored / 'grade.json'
        grade.write_text(json.dumps({'grader': 'separate-grader', 'case_id': 'a', 'attempt': 1,
            'output_hashes': p.hashes(directory / 'outputs'), 'checks': [
                {'criterion': c, 'verdict': 'pass', 'evidence': ['result.txt: synthetic relocation assertion']}
                for c in p.read(self.run / 'rubric.json')['criteria']['a']]}))
        p.grade_attempt(self.run, 'a', 1, grade)
        self.assertTrue(p.report(self.run)['complete'])

    def test_changed_material_rejected(self):
        for name in ['tasks.json', 'rubric.json', 'cases/a/task.txt', 'cases/a/inputs/data.json']:
            path = self.run / name
            original = path.read_bytes()
            path.write_bytes(original + b' ')
            with self.subTest(name=name):
                self.assert_rejected(self.trust)
            path.write_bytes(original)

    def test_old_review_rejected_after_coherent_refreeze(self):
        original_run = self.run
        self.run = self.base / 'refrozen'
        p.prepare_run(self.repo, self.sha, self.run, require_material_review=True)
        # A new run with identical material is transferable by design; changed materials are not.
        self.assertEqual(p.material_bindings(original_run, p.read(original_run / 'manifest.json')),
                         p.material_bindings(self.run, p.read(self.run / 'manifest.json')))
        tasks = p.read(self.run / 'tasks.json')
        tasks['cases'][0]['prompt'] = 'Changed question'
        path = self.base / 'changed-tasks.json'
        path.write_text(json.dumps(tasks))
        self.run = self.base / 'changed'
        p.prepare_run(self.repo, self.sha, self.run, tasks=path, require_material_review=True)
        self.assert_rejected(self.trust)

    def test_review_tampering_after_start_invalidates_record(self):
        directory = self.start(self.trust)
        self.review_path.write_text('tampered')
        with self.assertRaises(ValueError):
            p.validate_start(self.run, p.read(self.run / 'manifest.json'), directory, 'a')

    def test_manifest_policy_type(self):
        manifest = p.read(self.run / 'manifest.json')
        manifest['require_material_review'] = 'false'
        (self.run / 'manifest.json').write_text(json.dumps(manifest))
        self.assert_rejected(self.trust)

    def run_contract(self, label, fact, expected):
        """Freeze a real criterion; an explicit executable oracle supplies the verdict."""
        tasks = self.base / (label + '-tasks.json')
        rubric = self.base / (label + '-rubric.json')
        fixtures = self.base / (label + '-fixtures')
        fixtures.mkdir()
        (fixtures / 'data.json').write_text(json.dumps(fact))
        tasks.write_text(json.dumps({'cases': [{'id': 'a', 'skill': 'plugins/demo/SKILL.md',
            'prompt': 'Evaluate the stated relation using supplied data. Settlement cases require net conservation only.',
            'fixtures': ['data.json']}]}))
        criterion = fact['criterion']
        rubric.write_text(json.dumps({'criteria': {'a': [criterion, 'Keep evidence separate']}}))
        self.run = self.base / label
        p.prepare_run(self.repo, self.sha, self.run, tasks, rubric, fixtures, require_material_review=True)
        if fact['type'] == 'latency':
            scale = {'ms': 1, 's': 1000}
            b = fact['baseline'] * scale[fact['baseline_unit']]
            c = fact['candidate'] * scale[fact['candidate_unit']]
            actual = 'parity' if b == c else 'regression' if c > b else 'improvement'
            valid = actual == fact['claimed_direction']
        elif fact['type'] == 'settlement':
            net = list(fact['paid'])
            for payer, recipient, amount in fact['transfers']:
                net[payer] += amount
                net[recipient] -= amount
            actual = net
            valid = all(x == sum(fact['paid']) / len(net) for x in net)
        else:
            actual, valid = 'behavioral task requirement', True
        self.assertEqual(valid, expected, label)
        self.evidence.write_text(json.dumps({'control': label, 'actual': actual, 'valid': valid,
                                           'input': fact, 'synthetic_controller': True}))
        self.review = self.make_review(valid)
        if fact['type'] == 'behavioral':
            self.review['cases']['a'][0].update(kind='behavioral', verification='task_requirement')
        trust = self.save_review()
        if expected:
            p.authorize_dispatch(self.run, 'a', 'worker', material_review=trust)
            self.start(trust)
        else:
            self.assert_rejected(trust)

    def test_historical_wrong_and_corrected_contracts(self):
        # Exact historical numerical inputs and illustrative settlements, retained immutable in w1.
        for label, claimed, expected in [('historical-writer-wrong', 'regression', False),
                                         ('historical-writer-correct', 'parity', True)]:
            self.run_contract(label, {'type': 'latency', 'baseline': 80, 'candidate': 80,
                'baseline_unit': 'ms', 'candidate_unit': 'ms', 'claimed_direction': claimed,
                'criterion': 'Cover medium ' + claimed + ' in the writer output'}, expected)
        for label, transfers, expected in [('historical-settlement-wrong', [(1, 0, 6), (2, 0, 24)], False),
                                           ('historical-settlement-correct', [(2, 0, 24), (2, 1, 6)], True)]:
            self.run_contract(label, {'type': 'settlement', 'paid': [54, 36, 0], 'transfers': transfers,
                'criterion': 'Each roommate owes 30; verify illustrative transfers ' + str(transfers)}, expected)

    def test_preregistered_heldouts(self):
        rows = [('improvement', 80, 64, 'ms', 'ms', 'improvement', True),
                ('reversed', 80, 64, 'ms', 'ms', 'regression', False),
                ('parity', 125, 125, 'ms', 'ms', 'parity', True),
                ('false-regression', 125, 125, 'ms', 'ms', 'regression', False),
                ('normalized-units', .1, 80, 's', 'ms', 'improvement', True),
                ('wrong-units', .1, 80, 's', 'ms', 'regression', False)]
        for label, b, c, bu, cu, claim, expected in rows:
            self.run_contract(label, {'type': 'latency', 'baseline': b, 'candidate': c,
                'baseline_unit': bu, 'candidate_unit': cu, 'claimed_direction': claim,
                'criterion': f'{b}{bu} to {c}{cu} is {claim}'}, expected)
        settlements = [('reverse-pay', [(0, 2, 24), (1, 2, 6)], False),
                       ('equivalent', [(2, 0, 30), (0, 1, 6)], True),
                       ('equivalent-cycle', [(2, 0, 30), (0, 1, 6), (0, 1, 4), (1, 0, 4)], True)]
        for label, transfers, expected in settlements:
            self.run_contract(label, {'type': 'settlement', 'paid': [54, 36, 0], 'transfers': transfers,
                'criterion': 'Equal net costs; any conserving settlement allowed: ' + str(transfers)}, expected)
        self.run_contract('behavioral', {'type': 'behavioral', 'criterion': 'Preserve user files'}, True)

    def test_legacy_runs_still_work_without_review(self):
        self.run = self.base / 'legacy'
        p.prepare_run(self.repo, self.sha, self.run)
        self.assertIsNone(p.authorize_dispatch(self.run, 'a', 'worker'))
        self.start()


if __name__ == '__main__':
    unittest.main()
