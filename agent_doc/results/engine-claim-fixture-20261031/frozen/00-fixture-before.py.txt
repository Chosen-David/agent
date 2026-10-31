"""Deterministic CPU protocol fixtures, not live model or quality measurements."""
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from agent_runtime.core import ArtifactHandler, Engine, Store
from agent_runtime.plan_review import (CHECKS, PlanReviewError, ReviewSession, check_plan_review,
                                       plan_sha256, sha)
from agent_runtime.task_manifest import ReportingHandler, atomic_json, prepare, review


class PlanReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'TASK.md').write_text('- [ ] [T1] Verify output\n')
        self.plan = prepare(self.root, 'r1', 'manual', 'synthetic test instruction', lineage_id='logical-T1')
        task = self.plan['tasks'][0]
        task.update(action='verify_artifacts', done_when={'artifacts': [
            {'path': 'result.txt', 'sha256': hashlib.sha256(b'ok').hexdigest()}]})
        (self.root / 'result.txt').write_bytes(b'ok')
        atomic_json(self.root / task['report_path'], {'task_id': 'T1', 'summary': 'CPU fixture',
            'data': [{'kind': 'synthetic', 'description': 'two fixed bytes, not real model output'}]})
        self.identities = []
        self.records = {}
        self.calls = []
        self.now = [100.0]
        self.decision = 'approve'
        self.revoked = False
        self.self_review = False
        self.session = ReviewSession(self.root, 'logical-T1', planner_identity=self.planner,
            reviewer=self.reviewer, authenticate=self.authenticate, max_cycles=3, max_seconds=90,
            clock=lambda: self.now[0])

    def planner(self, plan):
        return {'invocation_id': 'planner-' + plan['run_id'], 'context_id': 'planner-context', 'host_source': 'cpu-test-host'}

    def reviewer(self, request, plan, previous):
        self.calls.append(copy.deepcopy((request, previous)))
        reviewer = {'invocation_id': 'review-' + request['request_id'],
                    'context_id': 'fresh-' + request['request_id'], 'host_source': 'cpu-test-host'}
        if self.self_review:
            reviewer = request['planner']
        findings = [] if self.decision == 'approve' else [{'blocking': True, 'target': 'tasks.T1.done_when',
            'feedback': 'Exact complete feedback: keep\nall lines, 不要截断。',
            'requested_change': 'Version the acceptance criterion', 'acceptance_check': 'Compare exact artifact hash'}]
        value = {'full_review': 'Full review.\nEvery paragraph is preserved. 不截断。',
                 'verdict': {'decision': self.decision, 'summary': 'CPU fixture review', 'findings': findings,
                             'checks': {k: {'status': 'pass', 'reason': 'CPU fixture checked ' + k} for k in CHECKS}}}
        proof = request['request_id']
        self.records[proof] = {'request_sha256': sha(request), 'review_sha256': sha(value),
                              'planner': request['planner'], 'reviewer': reviewer,
                              'fresh_context': True, 'budget_valid': True}
        return {'review': value, 'proof': proof}

    def authenticate(self, request, value, proof):
        if self.revoked:
            return None
        return copy.deepcopy(self.records.get(proof))

    def approve(self):
        self.plan['plan_review_receipt'] = self.session.submit(self.plan)
        return self.plan

    def engine(self, verifier=True, authorize=True):
        store = Store(self.root / 'run.sqlite')
        store.create(self.plan)
        handler = ReportingHandler(ArtifactHandler(self.root), self.root)
        engine = Engine(store, {'verify_artifacts': handler}, authorize=lambda *_: authorize,
                        project_root=self.root, plan_review_verifier=self.session.verify if verifier else None)
        return store, engine

    def test_prepare_protected_and_missing_receipt_cannot_dispatch(self):
        store, engine = self.engine()
        state = engine.tick('r1', 'wake')
        self.assertEqual(state['status'], 'blocked')
        self.assertEqual(state['tasks']['T1']['attempts'], 0)
        self.assertIn('receipt missing', state['plan_review_error'])

    def test_adapter_driven_complete_and_fresh_terminal_revocation(self):
        self.approve()
        store, engine = self.engine()
        self.assertEqual(engine.tick('r1', 'wake')['status'], 'done')
        self.assertTrue(review(store.snapshot('r1'), self.root, plan_review_verifier=self.session.verify)['all_reportable'])
        self.assertEqual(len(self.calls), 1)
        self.revoked = True
        self.assertEqual(engine.tick('r1', 'terminal-recheck')['status'], 'blocked')
        self.assertFalse(review(store.snapshot('r1'), self.root, plan_review_verifier=self.session.verify)['all_reportable'])

    def test_same_context_or_missing_authentication_rejected(self):
        self.self_review = True
        with self.assertRaisesRegex(PlanReviewError, 'self-approval'):
            self.approve()
        self.assertEqual(len(self.calls), 1)
        with self.assertRaisesRegex(PlanReviewError, 'ambiguous'):
            self.approve()

    def test_fake_json_or_missing_verifier_not_identity(self):
        self.approve()
        for verifier in (None, lambda *_: True):
            with self.assertRaises(PlanReviewError): check_plan_review(self.plan, self.root, verifier)

    def test_all_unknown_adapter_fields_and_acceptance_hash_bound(self):
        self.approve()
        for edit in (lambda p: p.update(hidden_command='new adapter input'),
                     lambda p: p['tasks'][0]['done_when']['artifacts'][0].update(sha256='0'*64)):
            plan = copy.deepcopy(self.plan); edit(plan)
            with self.assertRaisesRegex(PlanReviewError, 'stale'):
                check_plan_review(plan, self.root, self.session.verify)

    def test_revisions_keep_feedback_and_cross_run_budget(self):
        self.decision = 'revise'; self.approve()
        first = copy.deepcopy(self.plan['plan_review_receipt'])
        with self.assertRaisesRegex(PlanReviewError, 'revise'):
            check_plan_review(self.plan, self.root, self.session.verify)
        self.decision = 'approve'
        for number in (2, 3):
            self.plan['run_id'] = 'r' + str(number)
            self.approve()
        self.assertEqual(self.calls[1][1][0], first)
        self.assertEqual(self.calls[2][1][0]['review']['full_review'], first['review']['full_review'])
        self.plan['run_id'] = 'r4'
        with self.assertRaisesRegex(PlanReviewError, 'budget exhausted'): self.approve()
        self.assertEqual(len(self.calls), 3)

    def test_downgrade_and_lineage_reset_refused(self):
        self.approve(); store, _ = self.engine()
        for field in ('plan_review',):
            stale = copy.deepcopy(self.plan); stale.pop(field); stale['run_id'] = 'r2'
            with self.assertRaisesRegex(PlanReviewError, 'downgrade'): store.create(stale)
        stale = copy.deepcopy(self.plan); stale['plan_review']['lineage_id'] = 'reset'; stale['run_id'] = 'r3'
        with self.assertRaisesRegex(PlanReviewError, 'lineage'): Store(self.root / 'another.sqlite').create(stale)

    def test_review_never_grants_tool_authority(self):
        self.approve(); store, engine = self.engine(authorize=False)
        state = engine.tick('r1', 'wake')
        self.assertEqual(state['tasks']['T1']['attempts'], 0)
        self.assertEqual(state['tasks']['T1']['reason_kind'], 'permission')

    def test_explicit_legacy_is_unprotected_and_old_plan_readable(self):
        legacy = prepare(self.root, 'legacy', 'auto', 'fixture', review_required=False)
        self.assertEqual(check_plan_review(legacy, self.root, allow_legacy=True)['status'], 'legacy-unprotected')

    def test_evidence_changes_invalidate_review(self):
        (self.root / 'evidence.txt').write_bytes(b'original')
        self.plan['plan_review']['evidence_refs'] = [{'path': 'evidence.txt', 'sha256': hashlib.sha256(b'original').hexdigest()}]
        self.approve()
        (self.root / 'evidence.txt').write_bytes(b'changed')
        with self.assertRaisesRegex(PlanReviewError, 'evidence changed'):
            check_plan_review(self.plan, self.root, self.session.verify)

    def test_old_receipt_invalid_after_new_review(self):
        self.approve(); old = copy.deepcopy(self.plan)
        self.plan['run_id'] = 'r2'; self.approve()
        with self.assertRaisesRegex(PlanReviewError, 'superseded'):
            check_plan_review(old, self.root, self.session.verify)

    def test_recovered_original_response_keeps_consumed_cycle(self):
        captured = {}
        original = self.reviewer
        def interrupted(request, plan, previous):
            captured.update(request=request, result=original(request, plan, previous))
            raise RuntimeError('response delivery interrupted')
        self.session.reviewer = interrupted
        with self.assertRaises(RuntimeError): self.session.submit(self.plan)
        with self.assertRaisesRegex(PlanReviewError, 'ambiguous'): self.session.submit(self.plan)
        receipt = self.session.resolve(self.plan, captured['request']['request_id'], captured['result'])
        self.assertEqual(receipt['request']['cycle'], 1)
        self.plan['plan_review_receipt'] = receipt
        self.assertEqual(check_plan_review(self.plan, self.root, self.session.verify)['status'], 'approved')
        changed = copy.deepcopy(captured['result']); changed['review']['full_review'] += ' changed'
        with self.assertRaises(PlanReviewError):
            self.session.resolve(self.plan, captured['request']['request_id'], changed)

    def test_relative_plan_requires_explicit_trusted_root(self):
        self.plan['task_source']['path'] = 'TASK.md'
        self.approve()
        store = Store(self.root / 'portable.sqlite')
        with self.assertRaisesRegex(PlanReviewError, 'project root'):
            store.create(self.plan)
        store.create(self.plan, project_root=self.root)
        self.assertEqual(check_plan_review(self.plan, self.root, self.session.verify)['status'], 'approved')

    def test_distinct_main_profiles_and_specialists_stay_available(self):
        import json
        root = Path(__file__).resolve().parents[1]
        profiles = json.loads((root/'config/main_registry.json').read_text())['profiles']
        self.assertEqual({x['id'] for x in profiles}, {'planner-main', 'review-main'})
        self.assertEqual(len(json.loads((root/'config/role_registry.json').read_text())['roles']), 16)
        for role in json.loads((root/'config/role_registry.json').read_text())['roles']:
            self.assertTrue((root/role['skill']).parent.joinpath('references/dual_main_workflow.md').is_file())
        for profile in profiles:
            self.assertTrue((root/profile['prompt']).is_file())

    def test_trusted_publication_scope_never_authorizes_dispatch_or_other_requirements(self):
        from agent_runtime.plan_review import protected_lineage
        (self.root/'TASK.md').write_text('- [ ] [T1] Release current feature\n- [ ] [OLD] Preserve unrelated pending work\n')
        plan = prepare(self.root, 'release', 'manual', 'explicit release scope', lineage_id='release-T1')
        plan['tasks'] = [t for t in plan['tasks'] if t['task_refs'] == ['T1']]
        # JSON cannot choose scope, and failed validation cannot reserve OLD/T1.
        plan['publication_task_refs'] = ['T1']
        with self.assertRaises(ValueError): self.session.submit(plan)
        self.assertIsNone(protected_lineage(plan, self.root))
        session = ReviewSession(self.root, 'release-T1', planner_identity=self.planner, reviewer=self.reviewer,
                                authenticate=self.authenticate, publication_task_refs=['T1'])
        plan['plan_review_receipt'] = session.submit(plan)
        self.assertEqual(check_plan_review(plan, self.root, session.verify, purpose='publication',
                                          publication_task_refs=['T1'])['status'], 'approved')
        with self.assertRaises(ValueError): check_plan_review(plan, self.root, session.verify)
        self.assertIsNone(protected_lineage({'tasks':[{'task_refs':['OLD']}]}, self.root))
        with self.assertRaises(ValueError):
            check_plan_review(plan, self.root, session.verify, purpose='publication', publication_task_refs=['T1','OLD'])


if __name__ == '__main__':
    unittest.main()
