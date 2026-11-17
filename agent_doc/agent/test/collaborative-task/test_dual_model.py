import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from agent_runtime.core import Store
from agent_runtime.plan_review import PlanReviewError, ReviewSession, check_plan_review, sha
from agent_runtime.task_manifest import prepare
from tests import test_plan_review as fixtures

DUAL = 'dual-model-plan-review/v1'


class DualModelTests(unittest.TestCase):
    def fixture(self, reviewer_model='model-b', provider='provider-b'):
        case = fixtures.PlanReviewTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        case.plan['plan_review']['schema_version'] = DUAL
        (case.root / 'spec.md').write_text('Return exactly the approved two bytes.')
        (case.root / 'test_result.py').write_text("assert open('result.txt').read() == 'ok'\n")
        case.plan['plan_review']['task_contract'] = {
            'stage': 'acceptance-design', 'specification': self.bind(case, 'spec.md'),
            'acceptance': [self.bind(case, 'test_result.py')], 'implementation': []}
        original = case.reviewer

        def planner(plan):
            return dict(case.planner(plan), provider_id='provider-a', model_id='model-a')

        def reviewer(request, plan, previous):
            result = original(request, plan, previous)
            result['review']['verdict']['checks'].update({key: {'status': 'pass',
                'reason': 'Synthetic protocol fixture, no live model'}
                for key in ('spec_compliance', 'code_quality')})
            case.records[result['proof']]['review_sha256'] = sha(result['review'])
            case.records[result['proof']]['reviewer'].update(
                provider_id=provider, model_id=reviewer_model)
            return result

        case.session = ReviewSession(case.root, 'logical-T1', planner_identity=planner,
            reviewer=reviewer, authenticate=case.authenticate, max_cycles=3,
            max_seconds=90, clock=lambda: case.now[0], dual_model=True, reviewer_model_id='model-b')
        return case

    def bind(self, case, name):
        return {'path': name, 'sha256': hashlib.sha256((case.root / name).read_bytes()).hexdigest()}

    def implementation(self, case):
        case.plan.pop('plan_review_receipt', None)
        case.plan['run_id'] = 'implementation'
        (case.root / 'result_code.py').write_text("open('result.txt', 'w').write('ok')\n")
        case.plan['plan_review']['task_contract'].update(stage='implementation',
            implementation=[self.bind(case, 'result_code.py')])

    def test_implementation_requires_current_approved_design(self):
        case = self.fixture()
        self.implementation(case)
        with self.assertRaisesRegex(PlanReviewError, 'design must be reviewed'):
            case.approve()
        self.assertEqual(case.calls, [])

    def test_two_checkpoints_bind_spec_tests_and_actual_code(self):
        case = self.fixture()
        case.approve()
        self.implementation(case)
        case.approve()
        self.assertEqual(len(case.calls), 2)
        self.assertEqual(case.plan['plan_review_receipt']['request']['task_contract']['stage'], 'implementation')
        check_plan_review(case.plan, case.root, case.session.verify)
        (case.root / 'result_code.py').write_text('changed after review')
        with self.assertRaisesRegex(PlanReviewError, 'evidence changed'):
            check_plan_review(case.plan, case.root, case.session.verify)

    def test_revoked_design_invalidates_implementation_receipt(self):
        case = self.fixture()
        case.approve()
        design = case.plan['plan_review_receipt']
        self.implementation(case)
        case.approve()
        case.records[design['proof']]['budget_valid'] = False
        with self.assertRaises(PlanReviewError):
            check_plan_review(case.plan, case.root, case.session.verify)

    def test_dual_review_requires_both_quality_dimensions(self):
        case = self.fixture()
        reviewer = case.session.reviewer

        def missing(request, plan, previous):
            result = reviewer(request, plan, previous)
            del result['review']['verdict']['checks']['code_quality']
            case.records[result['proof']]['review_sha256'] = sha(result['review'])
            return result

        case.session.reviewer = missing
        with self.assertRaisesRegex(PlanReviewError, 'critical review checks'):
            case.approve()

    def test_modified_acceptance_cannot_reuse_design_approval(self):
        case = self.fixture()
        case.approve()
        self.implementation(case)
        (case.root / 'test_result.py').write_text('assert True\n')
        case.plan['plan_review']['task_contract']['acceptance'] = [self.bind(case, 'test_result.py')]
        with self.assertRaisesRegex(PlanReviewError, 'stale'):
            case.approve()
        self.assertEqual(len(case.calls), 1)

    def test_rejected_design_does_not_unlock_implementation(self):
        case = self.fixture()
        case.decision = 'revise'
        case.approve()
        self.implementation(case)
        case.decision = 'approve'
        with self.assertRaisesRegex(PlanReviewError, 'rejected or stale'):
            case.approve()
        self.assertEqual(len(case.calls), 1)

    def test_incomplete_task_contract_is_rejected_before_callbacks(self):
        for value in (None, {}, {'stage': 'implementation'}):
            with self.subTest(contract=value):
                case = self.fixture()
                case.plan['plan_review']['task_contract'] = value
                with self.assertRaises(PlanReviewError):
                    case.approve()
                self.assertEqual(case.calls, [])

    def test_distinct_authenticated_models_can_dispatch(self):
        case = self.fixture()
        case.approve()
        result = check_plan_review(case.plan, case.root, case.session.verify)
        self.assertEqual(result['status'], 'approved')
        self.assertEqual(case.plan['plan_review_receipt']['request']['planner']['model_id'], 'model-a')
        _, engine = case.engine()
        self.assertEqual(engine.tick('r1', 'wake')['status'], 'done')

    def test_same_model_on_different_provider_is_rejected(self):
        case = self.fixture(reviewer_model='model-a')
        with self.assertRaisesRegex(PlanReviewError, 'configured reviewer model|distinct authenticated models'):
            case.approve()
        self.assertEqual(len(case.calls), 1)

    def test_missing_and_noncanonical_model_identity_is_rejected(self):
        for value in (None, '', ' ', ' model-b', 'model-b ', [], True):
            with self.subTest(model=value):
                case = self.fixture(reviewer_model=value)
                with self.assertRaises(PlanReviewError):
                    case.approve()

    def test_provider_identity_required(self):
        case = self.fixture(provider='')
        with self.assertRaises(PlanReviewError):
            case.approve()

    def test_same_context_still_rejected_with_distinct_models(self):
        case = self.fixture()
        case.self_review = True
        with self.assertRaises(PlanReviewError):
            case.approve()

    def test_missing_planner_model_blocks_before_reviewer(self):
        case = self.fixture()
        case.session.planner_identity = case.planner
        with self.assertRaises(PlanReviewError):
            case.approve()
        self.assertEqual(case.calls, [])

    def test_backend_must_explicitly_support_dual_model(self):
        case = self.fixture()
        case.session = ReviewSession(case.root, 'logical-T1', planner_identity=case.planner,
            reviewer=case.reviewer, authenticate=case.authenticate)
        with self.assertRaisesRegex(PlanReviewError, 'host review mode'):
            case.approve()
        self.assertEqual(case.calls, [])

    def test_same_main_and_dual_model_cannot_both_be_enabled(self):
        case = self.fixture()
        with self.assertRaises(PlanReviewError):
            ReviewSession(case.root, 'logical-T1', single_main=True, dual_model=True)
        with self.assertRaises(PlanReviewError):
            ReviewSession(case.root, 'logical-T1', dual_model='true')

    def test_authenticated_model_change_invalidates_receipt(self):
        case = self.fixture()
        case.approve()
        receipt = case.plan['plan_review_receipt']
        case.records[receipt['proof']]['reviewer']['model_id'] = 'model-a'
        with self.assertRaises(PlanReviewError):
            check_plan_review(case.plan, case.root, case.session.verify)

    def test_protected_task_cannot_downgrade_before_review(self):
        case = self.fixture()
        Store(case.root / 'state.sqlite').create(case.plan)
        old = copy.deepcopy(case.plan)
        old['run_id'] = 'downgraded'
        old['plan_review']['schema_version'] = 'main-plan-review/v1'
        with self.assertRaises(PlanReviewError):
            Store(case.root / 'state.sqlite').create(old)

    def test_restart_cannot_relax_schema_or_reset_budget(self):
        case = self.fixture()
        case.approve()
        receipt = case.plan['plan_review_receipt']
        legacy = ReviewSession(case.root, 'logical-T1', authenticate=case.authenticate)
        with self.assertRaises(PlanReviewError):
            legacy.verify(case.root, receipt['request'], receipt['review'], receipt['proof'])
        case.plan['run_id'] = 'next-run'
        case.plan.pop('plan_review_receipt')
        case.session.max_cycles = 4
        with self.assertRaisesRegex(PlanReviewError, 'cannot reset'):
            case.approve()
        self.assertEqual(len(case.calls), 1)

    def test_unrequested_reviewer_model_is_rejected(self):
        case = self.fixture(reviewer_model='model-c')
        with self.assertRaisesRegex(PlanReviewError, 'configured reviewer model'):
            case.approve()

    def test_dual_backend_requires_pinned_reviewer_model(self):
        case = self.fixture()
        for model in (None, '', ' model-b', 'model-b ', True):
            with self.subTest(model=model):
                with self.assertRaises(PlanReviewError):
                    ReviewSession(case.root, 'logical-T1', dual_model=True,
                                  reviewer_model_id=model)

    def test_restarted_backend_cannot_replace_reviewer(self):
        case = self.fixture()
        case.approve()
        receipt = case.plan['plan_review_receipt']
        changed = ReviewSession(case.root, 'logical-T1', dual_model=True,
            reviewer_model_id='model-c', authenticate=case.authenticate)
        with self.assertRaisesRegex(PlanReviewError, 'configured reviewer model'):
            changed.verify(case.root, receipt['request'], receipt['review'], receipt['proof'])

    def test_prepare_api_and_real_cli_choose_protected_modes(self):
        case = self.fixture()
        self.assertEqual(prepare(case.root, 'api', 'manual', 'fixture',
                         review_schema=DUAL)['plan_review']['schema_version'], DUAL)
        for mode, schema in (('human', 'single-main-plan-review/v1'), ('dual-ai', DUAL)):
            with self.subTest(mode=mode):
                out = case.root / (mode + '.json')
                run = subprocess.run([sys.executable, '-m', 'agent_runtime.task_supervisor',
                    'prepare', '--project-root', str(case.root), '--run-id', mode,
                    '--authorization-reference', 'synthetic CLI test', '--out', str(out),
                    '--collaboration-mode', mode], cwd=ROOT, capture_output=True, text=True, timeout=30)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                self.assertEqual(json.loads(out.read_text())['plan_review']['schema_version'], schema)
                self.assertNotIn('plan_review_receipt', json.loads(out.read_text()))

    def test_cli_cannot_combine_dual_model_with_unprotected(self):
        case = self.fixture()
        out = case.root / 'bad.json'
        run = subprocess.run([sys.executable, '-m', 'agent_runtime.task_supervisor', 'prepare',
            '--project-root', str(case.root), '--run-id', 'bad', '--authorization-reference', 'fixture',
            '--out', str(out), '--collaboration-mode', 'dual-ai', '--legacy-unprotected'],
            cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(run.returncode, 0)
        self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
