"""Independent dual-main regressions, frozen separately from implementation tests.

CPU-only trusted-host fixtures prove protocol behavior, never live model quality.
Case specification preceded implementation answers. No reserved target material.
"""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import subprocess
import sys
from unittest.mock import patch
import unittest

from agent_runtime.core import Engine, Outcome, Store
from agent_runtime import project_docs as docs
from agent_runtime.plan_review import (CHECKS, PlanReviewError, ReviewSession, protected_lineage,
                                       check_plan_review, plan_sha256, sha)
from agent_runtime.task_manifest import (prepare, review as report_review, ReportingHandler, atomic_json)
from agent_runtime.publication import PublicationError, PublicationLedger
from agent_runtime.task_supervisor import start as managed_start


class CPUHost:
    """Explicit test double: identities are authenticated against private records."""
    def __init__(self):
        self.records = {}
        self.requests = []
        self.histories = []
        self.decision = 'approve'
        self.blocking = False
        self.unknown = None
        self.same_context = False
        self.revoked = False
        self.budget_valid = True
        self.fail = False

    def planner(self, plan):
        return {'invocation_id': 'host-planner-1', 'context_id': 'host-planner-context',
                'host_source': 'independent-cpu-fixture'}

    def reviewer(self, request, plan, previous):
        self.requests.append(copy.deepcopy(request))
        self.histories.append(copy.deepcopy(previous))
        if self.fail:
            raise RuntimeError('synthetic host failure after launch')
        checks = {name: {'status': 'unknown' if name == self.unknown else 'pass',
                         'reason': 'CPU fixture contract check; no model claim'} for name in CHECKS}
        findings = []
        if self.decision != 'approve' or self.blocking:
            findings.append({'blocking': True, 'target': 'tasks[0].done_when',
                             'feedback': 'Synthetic criterion requires correction.',
                             'requested_change': 'Bind the exact independently checked output.',
                             'acceptance_check': 'Rerun the named negative control.'})
        response = {'full_review': 'Complete CPU-only review text. ' * 160,
                    'verdict': {'decision': self.decision, 'summary': 'Independent contract fixture',
                                'findings': findings, 'checks': checks}}
        proof = {'id': 'proof-' + request['request_id'], 'usage': {'tokens': None, 'cost': None}}
        observed = {'request_sha256': sha(request), 'review_sha256': sha(response),
                    'planner': copy.deepcopy(request['planner']),
                    'reviewer': {'invocation_id': 'host-review-' + request['request_id'],
                                 'context_id': ('host-planner-context' if self.same_context
                                                else 'fresh-review-' + request['request_id']),
                                 'host_source': 'independent-cpu-fixture'},
                    'fresh_context': True, 'budget_valid': self.budget_valid}
        self.records[proof['id']] = (copy.deepcopy(request), copy.deepcopy(response),
                                    copy.deepcopy(proof), observed)
        return {'review': response, 'proof': proof}

    def authenticate(self, request, response, proof):
        if self.revoked:
            raise PlanReviewError('host approval revoked')
        record = self.records.get(proof.get('id')) if isinstance(proof, dict) else None
        if not record or (request, response, proof) != record[:3]:
            raise PlanReviewError('host records do not authenticate these bytes')
        return copy.deepcopy(record[3])


class CPUHandler:
    idempotent = True
    required_capabilities = frozenset()
    def __init__(self):
        self.calls = 0
    def run(self, task, context):
        self.calls += 1
        return Outcome('complete', evidence=['cpu-proof'])
    def verify(self, task, evidence):
        return evidence == ['cpu-proof']


class IndependentPlanReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='independent-main-review-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'TASK.md').write_text('# Fixture\n\n## 2026-10-07\n\n- [ ] [R1] Produce checked fixture\n')
        docs.migrate(self.root, '2026-10-07')
        self.host = CPUHost()
        self.now = 1000.0
        self.plan = self.make_plan('run-one')
        self.session = self.make_session()

    def make_plan(self, run_id):
        plan = prepare(self.root, run_id, 'manual', 'explicit synthetic local fixture')
        plan['tasks'][0].update(action='cpu', max_attempts=2, estimated_seconds=1,
                                done_when={'exact_fixture': True}, allowed_writes=['output.txt'])
        return plan

    def make_session(self, **kwargs):
        return ReviewSession(self.root, self.plan['plan_review']['lineage_id'],
                             planner_identity=self.host.planner, reviewer=self.host.reviewer,
                             authenticate=self.host.authenticate, clock=lambda: self.now, **kwargs)

    def approve(self, plan=None):
        plan = self.plan if plan is None else plan
        plan['plan_review_receipt'] = self.session.submit(plan)
        return plan

    def checked(self, plan=None):
        return check_plan_review(self.plan if plan is None else plan, self.root, self.session.verify)

    def engine(self, plan=None, authorized=True):
        plan = self.plan if plan is None else plan
        store = Store(self.root / (plan['run_id'] + '.sqlite'))
        store.create(plan)
        handler = CPUHandler()
        engine = Engine(store, {'cpu': handler}, authorize=lambda *_: authorized,
                        project_root=self.root, plan_review_verifier=self.session.verify,
                        clock=lambda: self.now)
        return store, handler, engine

    def test_new_prepare_requires_review_and_missing_adapter_blocks_direct_dispatch(self):
        self.assertEqual(self.plan['plan_review']['schema_version'], 'main-plan-review/v1')
        store, handler, _ = self.engine()
        engine = Engine(store, {'cpu': handler}, authorize=lambda *_: True, project_root=self.root)
        state = engine.tick(self.plan['run_id'], 'missing-review')
        self.assertEqual(state['status'], 'blocked')
        self.assertEqual(handler.calls, 0)
        self.assertEqual(state['tasks']['R1']['attempts'], 0)

    def test_authenticated_cpu_approval_dispatches_once_but_does_not_grant_permission(self):
        self.approve()
        store, handler, engine = self.engine(authorized=False)
        self.assertEqual(engine.tick(self.plan['run_id'], 'denied')['status'], 'blocked')
        self.assertEqual(handler.calls, 0)
        engine.authorize = lambda *_: True
        self.assertEqual(engine.tick(self.plan['run_id'], 'approved')['status'], 'done')
        self.assertEqual(handler.calls, 1)
        self.assertEqual(self.checked()['status'], 'approved')

    def test_same_actual_context_is_rejected_despite_distinct_invocation_labels(self):
        self.host.same_context = True
        with self.assertRaisesRegex(PlanReviewError, 'self-approval|independent'):
            self.approve()

    def test_boolean_or_model_declared_identity_is_not_authentication(self):
        self.session.authenticate = lambda *_: True
        with self.assertRaisesRegex(PlanReviewError, 'bindings|boolean'):
            self.approve()

    def test_approve_with_blocking_finding_cannot_produce_receipt(self):
        self.host.blocking = True
        with self.assertRaisesRegex(PlanReviewError, 'blocking'):
            self.approve()

    def test_resources_are_a_required_independent_check_and_unknown_blocks_approval(self):
        self.assertIn('resources', CHECKS)
        self.host.unknown = 'resources'
        with self.assertRaisesRegex(PlanReviewError, 'critical checks|blocking'):
            self.approve()

    def test_all_executable_fields_including_unknown_adapter_inputs_are_bound(self):
        self.plan['tasks'][0]['adapter_private_options'] = {'command': 'safe-cpu-fixture'}
        self.approve()
        changes = [lambda p: p['tasks'][0].update(action='different'),
                   lambda p: p['tasks'][0].update(allowed_writes=['doc/guide/guide.md']),
                   lambda p: p['tasks'][0].update(done_when={'accept_anything': True}),
                   lambda p: p['tasks'][0]['adapter_private_options'].update(command='changed'),
                   lambda p: p.update(authorization_reference='new authorization claim'),
                   lambda p: p.update(resource_budget={'paid_gpu': True})]
        for change in changes:
            with self.subTest(change=repr(change)):
                mutated = copy.deepcopy(self.plan)
                change(mutated)
                with self.assertRaises((PlanReviewError, ValueError)):
                    self.checked(mutated)

    def test_full_feedback_is_preserved_and_bound_without_truncation(self):
        self.host.decision = 'revise'
        first = self.session.submit(self.plan)
        self.assertGreater(len(first['review']['full_review']), 3000)
        new = self.make_plan('run-two')
        self.host.decision = 'approve'
        self.approve(new)
        self.assertEqual(self.host.histories[1], [first])
        changed = copy.deepcopy(new)
        changed['plan_review_receipt']['review']['full_review'] += ' edited'
        with self.assertRaises(PlanReviewError):
            self.checked(changed)

    def test_adopted_advice_mutation_invalidates_without_reporting_wrapper(self):
        advice = self.root / 'doc/advice/plan.md'
        advice.write_text('Use synthetic fixture acceptance.\n')
        self.plan = self.make_plan('advice-plan')
        docs.bind_advice(self.plan, [{'path': 'doc/advice/plan.md',
            'sha256': hashlib.sha256(advice.read_bytes()).hexdigest(), 'task_refs': ['R1'],
            'disposition': 'adopt', 'reason': 'Matches fixture task.', 'guide_alignment': 'compatible'}])
        self.approve()
        advice.write_text('Change execution method after approval.\n')
        with self.assertRaises((PlanReviewError, ValueError)):
            self.checked()

    def test_progress_append_remains_valid_but_stable_plan_change_invalidates(self):
        self.approve()
        detail = self.root / 'doc/task/task_details/R1.md'
        old = detail.read_text()
        detail.write_text(old + '\nObserved CPU fixture progress.\n')
        self.assertEqual(self.checked()['status'], 'approved')
        detail.write_text(old.replace('## Plan\n', '## Plan\n\nChanged stable acceptance.\n'))
        with self.assertRaises((PlanReviewError, ValueError)):
            self.checked()

    def test_explicit_evidence_byte_mutation_invalidates(self):
        evidence = self.root / 'source-evidence.txt'
        evidence.write_bytes(b'original evidence')
        self.plan['plan_review']['evidence_refs'] = [{'path': evidence.name,
            'sha256': hashlib.sha256(evidence.read_bytes()).hexdigest()}]
        self.approve()
        evidence.write_bytes(b'changed evidence')
        with self.assertRaisesRegex(PlanReviewError, 'evidence changed'):
            self.checked()

    def test_cycle_budget_survives_new_run_ids_and_cannot_be_raised(self):
        self.host.decision = 'revise'
        for number in range(3):
            self.session.submit(self.make_plan('revision-' + str(number)))
        with self.assertRaisesRegex(PlanReviewError, 'budget exhausted'):
            self.session.submit(self.make_plan('fourth-run'))
        with self.assertRaisesRegex(PlanReviewError, 'reset logical review budget'):
            self.make_session(max_cycles=4).submit(self.make_plan('raised-budget'))
        self.assertEqual(len(self.host.requests), 3)

    def test_unknown_usage_stays_unknown_and_host_hard_budget_failure_blocks(self):
        self.approve()
        self.assertIsNone(self.plan['plan_review_receipt']['proof']['usage']['tokens'])
        self.assertIsNone(self.plan['plan_review_receipt']['proof']['usage']['cost'])
        self.host.budget_valid = False
        with self.assertRaisesRegex(PlanReviewError, 'budget'):
            self.session.submit(self.make_plan('unknown-hard-budget'))

    def test_failed_review_launch_is_not_free_retry(self):
        self.host.fail = True
        with self.assertRaises(RuntimeError):
            self.session.submit(self.plan)
        self.host.fail = False
        with self.assertRaisesRegex(PlanReviewError, 'ambiguous'):
            self.session.submit(self.make_plan('retry-new-run'))
        self.assertEqual(len(self.host.requests), 1)

    def test_receipt_cannot_replay_across_run_or_superseded_revision(self):
        self.approve()
        copied = copy.deepcopy(self.plan)
        copied['run_id'] = 'other-run'
        with self.assertRaisesRegex(PlanReviewError, 'stale|replayed'):
            self.checked(copied)
        self.approve(self.make_plan('new-reviewed-run'))
        with self.assertRaisesRegex(PlanReviewError, 'superseded'):
            self.checked()

    def test_approved_done_chain_is_rechecked_after_host_revocation(self):
        self.approve()
        store, handler, engine = self.engine()
        self.assertEqual(engine.tick(self.plan['run_id'], 'complete')['status'], 'done')
        self.host.revoked = True
        self.assertEqual(engine.tick(self.plan['run_id'], 'after-revocation')['status'], 'blocked')
        self.assertEqual(handler.calls, 1)
        report = report_review(store.snapshot(self.plan['run_id']), self.root,
                               plan_review_verifier=self.session.verify)
        self.assertFalse(report['all_reportable'])
        self.assertRegex(report['source_error'], 'revoked|verification rejected/unavailable')

    def test_same_requirement_cannot_strip_review_or_change_lineage(self):
        self.approve()
        for mode in ('strip', 'rename'):
            with self.subTest(mode=mode):
                plan = self.make_plan('escape-' + mode)
                if mode == 'strip':
                    plan.pop('plan_review')
                else:
                    plan['plan_review']['lineage_id'] = 'new-unspent-lineage'
                with self.assertRaises(PlanReviewError):
                    Store(self.root / ('escape-' + mode + '.sqlite')).create(plan)

    def test_reidentified_stripped_plan_needs_explicit_host_legacy_optin(self):
        self.approve()
        escaped = copy.deepcopy(self.plan)
        escaped['run_id'] = 'reidentified-escape'
        for key in ('plan_review', 'plan_review_receipt', 'task_source', 'project_documents'):
            escaped.pop(key, None)
        for task in escaped['tasks']:
            task.pop('task_refs', None)
            task.pop('document_refs', None)
        store, handler, engine = self.engine(escaped)
        state = engine.tick(escaped['run_id'], 'escape-attempt')
        self.assertEqual(state['status'], 'blocked')
        self.assertEqual(handler.calls, 0)


    def test_post_action_revocation_fences_effect_and_requires_reconciliation(self):
        self.approve()
        store, handler, engine = self.engine()
        handler.idempotent = False
        def actual_effect(task, context):
            handler.calls += 1
            self.host.revoked = True
            return Outcome('complete', 'Synthetic effect already happened', ['cpu-proof'])
        handler.run = actual_effect
        state = engine.tick(self.plan['run_id'], 'revoke-after-effect')
        node = state['tasks']['R1']
        self.assertEqual(state['status'], 'blocked')
        self.assertEqual(node['status'], 'blocked')
        self.assertIsNone(node.get('token'))
        self.assertTrue(node['evidence'], 'Keep effect evidence for explicit reconciliation')
        # Further blocked observations must not erase the post-effect fence.
        engine.tick(self.plan['run_id'], 'still-revoked')
        # Reopen the durable Store and Engine, not merely the same in-memory object.
        store = Store(store.path)
        engine = Engine(store, {'cpu': handler}, authorize=lambda *_: True,
                        project_root=self.root, plan_review_verifier=self.session.verify,
                        clock=lambda: self.now)
        self.host.revoked = False
        self.now += 31
        engine.tick(self.plan['run_id'], 'review-restored')
        self.assertEqual(handler.calls, 1, 'Do not replay a non-idempotent completed effect')
        state = engine.reconcile(self.plan['run_id'], 'R1', ['cpu-proof'], 'host inspected effect')
        self.assertEqual(state['status'], 'done')

    def test_managed_start_fails_before_tmux_launch_without_real_review_adapter(self):
        plan_path = self.root / 'plan.json'
        atomic_json(plan_path, self.plan)
        with patch('agent_runtime.task_supervisor.shutil.which', return_value='/synthetic/tmux'):
            with patch('agent_runtime.task_supervisor.tmux') as tmux:
                with self.assertRaisesRegex(PlanReviewError, 'receipt missing|verifier unavailable'):
                    managed_start(plan_path, self.root, self.root / '.agent-runs/managed')
                tmux.assert_not_called()

    def test_reporting_wrapper_stops_changed_result_lookup_before_action(self):
        # This dependency matters to data producers; unrelated tasks can continue.
        protocol = self.root / 'validation-plan.json'
        protocol.write_text('{"scope":"synthetic fixture only"}\n')
        task = self.plan['tasks'][0]
        contract = {'result_id': 'synthetic-result', 'producer_task_id': 'R1',
                    'producer_actor': task['owner'], 'manifest_path': 'doc/results/fixture/manifest.json',
                    'validation_plan': {'path': protocol.name,
                                        'sha256': hashlib.sha256(protocol.read_bytes()).hexdigest()},
                    'scope': 'Synthetic plan-review fixture; data not yet produced'}
        task['experiment_result'] = contract
        task['prior_result_review'] = {'decision': 'rerun', 'reason': 'No prior matching CPU data.',
                                       'record_refs': []}
        gate = copy.deepcopy(task)
        gate.pop('experiment_result')
        gate.update(task_id='verify-R1', action='verify_experiment_result', owner='independent-verifier',
                    depends_on=['R1'], result_validation=contract,
                    report_path='.agent-runs/fixture/verify-R1.json')
        self.plan['tasks'].append(gate)
        self.approve()
        store = Store(self.root / 'wrapped.sqlite')
        store.create(self.plan)
        handler = CPUHandler()
        wrapper = ReportingHandler(handler, self.root)
        engine = Engine(store, {'cpu': wrapper}, authorize=lambda *_: True,
                        project_root=self.root, plan_review_verifier=self.session.verify,
                        clock=lambda: self.now)
        old = self.plan['tasks'][0]['prior_result_search']
        changed = copy.deepcopy(old)
        changed.update(status='unavailable', partial=True, errors=[{'error': 'synthetic changed lookup'}])
        with patch('agent_runtime.task_manifest._prior_result_search', return_value=changed):
            state = engine.tick(self.plan['run_id'], 'changed-prior-results')
        self.assertEqual(state['status'], 'blocked')
        self.assertEqual(handler.calls, 0)
        self.assertIn('prior-result', state['tasks']['R1']['reason'])

    def test_publication_reauthenticates_saved_plan_and_keeps_permission_separate(self):
        def git(*args):
            proc = subprocess.run(['git', '-C', str(self.root), *args], text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            return proc.stdout.strip()
        git('init', '-b', 'main')
        git('config', 'user.name', 'Independent CPU Fixture')
        git('config', 'user.email', 'fixture@example.invalid')
        (self.root / '.gitignore').write_text('.agent-runs/\n*.sqlite\n')
        (self.root / 'app.py').write_text("print('baseline')\n")
        git('add', '.')
        git('commit', '-m', 'CPU fixture baseline')
        git('remote', 'add', 'origin', str(self.root / '.agent-runs/local-unused-remote.git'))
        (self.root / 'app.py').write_text("print('candidate')\n")
        git('add', 'app.py')
        self.approve()
        state_path = self.root / '.agent-runs/publication.json'
        ledger = PublicationLedger(self.root, state_path, authorize=lambda *_: True,
                                   accept=lambda *_: True, plan=self.plan,
                                   plan_review_verifier=self.session.verify)
        frozen = ledger.freeze({'app.py': ['R1']}, remote='origin', branch='main',
                               authorization_reference='synthetic explicit local fixture')
        proof_path = self.root / '.agent-runs/independent-check.json'
        proof_path.write_text('synthetic independent output check\n')
        evidence = [{'path': str(proof_path), 'sha256': hashlib.sha256(proof_path.read_bytes()).hexdigest(),
                     'task_refs': ['R1'], 'candidate_sha256': frozen['candidate']['sha256']}]
        without_verifier = PublicationLedger(self.root, state_path, authorize=lambda *_: True,
                                              accept=lambda *_: True)
        with self.assertRaisesRegex(PublicationError, 'review.*unavailable|verifier unavailable'):
            without_verifier.mark_tested(evidence)
        no_permission = PublicationLedger(self.root, state_path, authorize=None, accept=lambda *_: True,
                                          plan_review_verifier=self.session.verify)
        with self.assertRaisesRegex(PublicationError, 'authorization'):
            no_permission.mark_tested(evidence)
        self.assertTrue(ledger.mark_tested(evidence)['tested'])
        self.host.revoked = True
        with self.assertRaisesRegex(PublicationError, 'revoked|verification rejected/unavailable'):
            ledger.observe_commit()

    def test_historical_legacy_requires_runtime_optin_and_labels_degradation(self):
        plan = prepare(self.root, 'legacy', 'manual', 'historical fixture', review_required=False)
        plan['tasks'][0].update(action='cpu', done_when={'exact_fixture': True})
        store, handler, engine = self.engine(plan)
        self.assertEqual(engine.tick(plan['run_id'], 'no-host-optin')['status'], 'blocked')
        self.assertEqual(handler.calls, 0)
        legacy_engine = Engine(store, {'cpu': handler}, authorize=lambda *_: True,
                               project_root=self.root, allow_legacy=True, clock=lambda: self.now)
        self.assertEqual(legacy_engine.tick(plan['run_id'], 'explicit-host-legacy')['status'], 'done')
        self.assertEqual(check_plan_review(plan, self.root, allow_legacy=True)['status'], 'legacy-unprotected')


    def test_explicit_reconciliation_clears_stale_review_error_without_extra_tick(self):
        self.approve()
        store, handler, engine = self.engine()
        handler.idempotent = False
        def actual_effect(task, context):
            handler.calls += 1
            self.host.revoked = True
            return Outcome('complete', 'Synthetic effect already happened', ['cpu-proof'])
        handler.run = actual_effect
        self.assertEqual(engine.tick(self.plan['run_id'], 'effect')['status'], 'blocked')
        self.host.revoked = False
        state = engine.reconcile(self.plan['run_id'], 'R1', ['cpu-proof'], 'fresh host verification')
        self.assertEqual(state['status'], 'done')
        self.assertFalse(state.get('plan_review_error'))
        self.assertEqual(handler.calls, 1)

    def test_relative_plan_path_requires_explicit_trusted_root(self):
        self.plan['task_source']['path'] = 'doc/task/TASK.md'
        self.approve()
        store = Store(self.root / 'relative.sqlite')
        with self.assertRaisesRegex(PlanReviewError, 'root'):
            store.create(self.plan)
        store.create(self.plan, project_root=self.root)
        handler = CPUHandler()
        engine = Engine(store, {'cpu': handler}, authorize=lambda *_: True,
                        project_root=self.root, plan_review_verifier=self.session.verify,
                        clock=lambda: self.now)
        self.assertEqual(engine.tick(self.plan['run_id'], 'relative-root')['status'], 'done')
        self.assertEqual(handler.calls, 1)

    def test_resolve_recovers_same_authenticated_response_without_new_review_or_refund(self):
        recovered = {}
        def response_lost(request, plan, previous):
            recovered['request'] = copy.deepcopy(request)
            recovered['result'] = self.host.reviewer(request, plan, previous)
            raise RuntimeError('synthetic connection lost after the original response')
        self.session.reviewer = response_lost
        with self.assertRaises(RuntimeError):
            self.session.submit(self.plan)
        receipt = self.session.resolve(self.plan, recovered['request']['request_id'], recovered['result'])
        self.plan['plan_review_receipt'] = receipt
        self.assertEqual(self.checked()['status'], 'approved')
        self.assertEqual(len(self.host.requests), 1)
        self.assertEqual(receipt['request']['cycle'], 1)
        self.assertEqual(self.session.resolve(self.plan, recovered['request']['request_id'], recovered['result']), receipt)

    def test_resolve_cannot_extend_expired_request_budget(self):
        recovered = {}
        def response_lost(request, plan, previous):
            recovered['request'] = copy.deepcopy(request)
            recovered['result'] = self.host.reviewer(request, plan, previous)
            raise RuntimeError('synthetic original response pending')
        self.session.reviewer = response_lost
        with self.assertRaises(RuntimeError):
            self.session.submit(self.plan)
        self.now = recovered['request']['deadline'] + 1
        with self.assertRaisesRegex(PlanReviewError, 'time budget exhausted'):
            self.session.resolve(self.plan, recovered['request']['request_id'], recovered['result'])
        self.assertEqual(len(self.host.requests), 1)


    def scoped_fixture(self):
        index = self.root / 'doc/task/TASK.md'
        index.write_text(index.read_text() + '\n- [ ] [R2] Unrelated historical requirement ([detail](task_details/R2.md))\n')
        (self.root / 'doc/task/task_details/R2.md').write_text(
            '# [R2] Unrelated historical requirement\n\nTask-ID: R2\nDate: 2026-10-07\n\n## Plan\n\nPreserve historical status.\n\n## Progress\n\nStill unrelated.\n')
        full = self.make_plan('publication-scope')
        for task in full['tasks']:
            task.update(action='cpu', done_when={'exact_fixture': True})
        self.plan = copy.deepcopy(full)
        self.plan['tasks'] = [t for t in self.plan['tasks'] if t['task_id'] == 'R1']
        self.session = self.make_session(publication_task_refs=['R1'])
        return full

    def test_publication_scope_is_trusted_exact_and_does_not_enroll_history(self):
        self.scoped_fixture()
        self.approve()
        status = check_plan_review(self.plan, self.root, self.session.verify,
                                   purpose='publication', publication_task_refs=['R1'])
        self.assertEqual(status['status'], 'approved')
        self.assertIsNone(protected_lineage({'tasks': [{'task_refs': ['R2']}]}, self.root))
        with self.assertRaises(ValueError):
            check_plan_review(self.plan, self.root, self.session.verify)
        with self.assertRaises(ValueError):
            check_plan_review(self.plan, self.root, self.session.verify,
                              purpose='publication', publication_task_refs=['R1', 'R2'])

    def test_default_all_requirements_and_forged_json_scope_still_fail_without_pollution(self):
        self.scoped_fixture()
        self.plan['publication_task_refs'] = ['R1']
        self.plan['purpose'] = 'publication'
        ordinary = self.make_session()
        with self.assertRaisesRegex(ValueError, 'omits TASK.md requirements'):
            ordinary.submit(self.plan)
        self.assertIsNone(protected_lineage({'tasks': [{'task_refs': ['R1', 'R2']}]}, self.root))
        with self.assertRaisesRegex(ValueError, 'omits TASK.md requirements'):
            Store(self.root / 'invalid-scope.sqlite').create(self.plan)
        self.assertIsNone(protected_lineage({'tasks': [{'task_refs': ['R1', 'R2']}]}, self.root))

    def test_publication_only_receipt_cannot_dispatch_even_when_scope_covers_all(self):
        self.session = self.make_session(publication_task_refs=['R1'])
        self.approve()
        # A publication-only receipt is refused before registration as executable work.
        store = Store(self.root / 'publication-cannot-execute.sqlite')
        with self.assertRaisesRegex(PlanReviewError, 'purpose|scope'):
            store.create(self.plan)
        handler = CPUHandler()
        engine = Engine(store, {'cpu': handler}, authorize=lambda *_: True,
                        project_root=self.root, plan_review_verifier=self.session.verify)
        with self.assertRaisesRegex(PlanReviewError, 'purpose|scope'):
            engine._review_plan(self.plan)
        self.assertEqual(handler.calls, 0)

    def test_changed_trusted_scope_after_reopen_fails_without_protection_pollution(self):
        full = self.scoped_fixture()
        self.approve()
        changed = self.make_session(publication_task_refs=['R1', 'R2'])
        full['run_id'] = 'forbidden-scope-expansion'
        with self.assertRaises(PlanReviewError):
            changed.submit(full)
        self.assertIsNone(protected_lineage({'tasks': [{'task_refs': ['R2']}]}, self.root),
                          'Rejected scope changes must not reserve unrelated requirements')
        req = self.plan['plan_review_receipt']['request']
        with self.assertRaises(PlanReviewError):
            changed.verify(self.root, req, self.plan['plan_review_receipt']['review'],
                           self.plan['plan_review_receipt']['proof'])


if __name__ == '__main__':
    unittest.main()
