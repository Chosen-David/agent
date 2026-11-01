"""Upgrade recovery uses durable observations, never cursor order as ownership."""
from pathlib import Path
import tempfile
import unittest

from agent_runtime.core import Engine, Outcome, Store
from tests.test_single_main import plan


class SerialRecoveryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = Store(Path(tmp.name) / 'state.sqlite')
        self.store.create(plan())
        self.calls = []
        self.now = 1
        owner = self

        class Handler:
            idempotent = True
            def run(self, task, context):
                owner.calls.append(task['task_id'])
                return Outcome('complete', evidence=['verified'])
            def verify(self, task, evidence):
                return evidence == ['verified']
        self.handler = Handler()

    def seed(self, nodes):
        with self.store.transaction() as db:
            _, state = self.store.load(db, 'serial')
            state.pop('active_step', None)
            state['claim_cursor'] = 1
            for key, values in nodes.items():
                state['tasks'][key].update(values)
            self.store.save(db, 'serial', state)

    def tick(self, event):
        return Engine(Store(self.store.path), {'step': self.handler},
                      authorize=lambda *_: True, allow_legacy=True,
                      clock=lambda: self.now).tick('serial', event)

    def test_old_pending_restores_step_before_deadline_and_after_restart(self):
        self.seed({'A': {'status': 'todo', 'attempts': 1, 'next_at': 5,
                         'reason_kind': 'adapter_result', 'reason': 'pending'}})
        state = self.tick('early')
        self.assertEqual(self.calls, [])
        self.assertEqual(state.get('active_step'), 'A')
        self.assertEqual(state['tasks']['A']['attempts'], 1)
        self.now = 5
        self.tick('resume')
        self.tick('next')
        self.assertEqual(self.calls, ['A', 'B'])

    def test_old_wait_pending_with_refunded_attempts_is_not_fresh(self):
        self.seed({'A': {'pending_since': 1, 'pending_polls': 2, 'next_at': 5}})
        state = self.tick('wait')
        self.assertEqual(self.calls, [])
        self.assertEqual(state.get('active_step'), 'A')
        self.assertEqual(state['tasks']['A']['pending_polls'], 2)

    def test_expired_idempotent_claim_resumes_same_step(self):
        self.seed({'A': {'status': 'doing', 'attempts': 1, 'token': 'old', 'lease_until': 0}})
        self.tick('expired')
        self.assertEqual(self.calls, ['A'])

    def test_expired_unknown_claim_requires_reconciliation_before_next_step(self):
        self.handler.idempotent = False
        self.seed({'A': {'status': 'doing', 'attempts': 1, 'token': 'old', 'lease_until': 0}})
        state = self.tick('unknown')
        self.assertEqual(self.calls, [])
        self.assertEqual(state['tasks']['A']['reason_kind'], 'ambiguous')
        engine = Engine(self.store, {'step': self.handler}, authorize=lambda *_: True,
                        allow_legacy=True, clock=lambda: self.now)
        engine.reconcile('serial', 'A', ['verified'], 'host observed completion')
        self.tick('after-reconcile')
        self.assertEqual(self.calls, ['B'])

    def test_nonidempotent_exception_keeps_unknown_effect_across_restart(self):
        for phase in ('run', 'verify', 'invalid_outcome'):
            with self.subTest(phase=phase):
                store = Store(Path(self.store.path).with_name(phase + '.sqlite'))
                store.create(plan())
                effect = Path(self.store.path).with_name(phase + '.txt')
                calls = []

                class Handler:
                    idempotent = False
                    raised = False

                    def run(self, task, context):
                        calls.append(task['task_id'])
                        if task['task_id'] == 'A':
                            effect.write_text('external effect', encoding='utf-8')
                            if phase == 'run':
                                raise RuntimeError('effect happened; response lost')
                            if phase == 'invalid_outcome':
                                return None
                        return Outcome('complete', evidence=['verified'])

                    def verify(self, task, evidence):
                        if task['task_id'] == 'A':
                            if phase == 'verify' and not self.raised:
                                self.raised = True
                                raise OSError('verification unavailable')
                            return evidence == ['verified'] and effect.read_text() == 'external effect'
                        return evidence == ['verified']

                handler = Handler()
                def engine(authorized=True):
                    return Engine(Store(store.path), {'step': handler},
                                  authorize=lambda *_: authorized, allow_legacy=True,
                                  clock=lambda: self.now)

                first = engine().tick('serial', 'effect')
                self.assertEqual(first['tasks']['A']['status'], 'blocked')
                state = engine().tick('serial', 'restart')
                self.assertEqual(calls, ['A'])
                self.assertEqual(state.get('active_step'), 'A')
                node = state['tasks']['A']
                self.assertEqual(node['reason_kind'], 'ambiguous')
                self.assertTrue(node['requires_reconciliation'])
                self.assertEqual(node['attempts'], 1)
                self.assertEqual(node['effect_observation']['status'],
                                 'complete' if phase == 'verify' else 'unknown')
                self.assertEqual(node['evidence'], ['verified'] if phase == 'verify' else [])
                for authorized, evidence in ((False, ['verified']), (True, ['invalid'])):
                    with self.assertRaises(ValueError):
                        engine(authorized).reconcile('serial', 'A', evidence, 'host inspection')
                self.assertEqual(calls, ['A'])
                engine().reconcile('serial', 'A', ['verified'], 'host inspected actual file')
                self.assertEqual(engine().tick('serial', 'settled')['status'], 'done')
                self.assertEqual(calls, ['A', 'B'])
                self.assertEqual(effect.read_text(), 'external effect')

    def test_definite_blocked_result_allows_unrelated_next_step(self):
        calls = []

        class Handler:
            idempotent = False
            def run(self, task, context):
                calls.append(task['task_id'])
                return (Outcome('blocked', 'definite rejection; no pending effect')
                        if task['task_id'] == 'A' else Outcome('complete', evidence=['verified']))
            def verify(self, task, evidence):
                return evidence == ['verified']

        for event in ('rejected', 'unrelated'):
            Engine(Store(self.store.path), {'step': Handler()}, authorize=lambda *_: True,
                   allow_legacy=True, clock=lambda: self.now).tick('serial', event)
        self.assertEqual(calls, ['A', 'B'])

    def test_pending_job_keeps_step_when_failure_attempts_are_exhausted(self):
        for phase in ('retry', 'exception', 'expired_lease'):
            with self.subTest(phase=phase):
                store = Store(Path(self.store.path).with_name(phase + '.sqlite'))
                spec = plan()
                spec['tasks'][0].update(max_attempts=1, wait_policy={
                    'max_polls': 100, 'max_seconds': 600, 'diagnose_after_seconds': 300})
                store.create(spec)
                job = Path(self.store.path).with_name(phase + '.job')
                calls, keys = [], []
                now = [1]

                class Handler:
                    idempotent = True
                    def run(self, task, context):
                        calls.append(task['task_id'])
                        keys.append(context.idempotency_key)
                        if task['task_id'] == 'B':
                            return Outcome('complete', evidence=['verified'])
                        if len(calls) == 1:
                            job.write_text('running', encoding='utf-8')
                            return Outcome('pending', 'existing job is still running')
                        if phase == 'exception':
                            raise TimeoutError('job status endpoint unavailable')
                        if phase == 'expired_lease':
                            raise KeyboardInterrupt('worker interrupted during observation')
                        return Outcome('retry', 'job status unavailable; job outcome unknown')
                    def verify(self, task, evidence):
                        return (evidence == ['verified'] and
                                (task['task_id'] == 'B' or job.read_text() == 'completed'))

                def engine():
                    return Engine(Store(store.path), {'step': Handler()}, authorize=lambda *_: True,
                                  allow_legacy=True, clock=lambda: now[0], lease_seconds=1)

                engine().tick('serial', 'pending')
                now[0] = 2
                if phase == 'expired_lease':
                    with self.assertRaises(KeyboardInterrupt):
                        engine().tick('serial', 'lost-observation')
                else:
                    engine().tick('serial', 'lost-observation')
                now[0] = 3
                state = engine().tick('serial', 'restart')
                self.assertEqual(calls, ['A', 'A'])
                self.assertEqual(state.get('active_step'), 'A')
                node = state['tasks']['A']
                self.assertEqual((node['status'], node['reason_kind']), ('blocked', 'wait_budget'))
                self.assertEqual((node['attempts'], node['pending_polls'], node['pending_since']), (1, 1, 1))
                self.assertTrue(node['diagnosis_required'])
                self.assertEqual(keys[0], keys[1])
                self.assertEqual(job.read_text(), 'running')
                with self.assertRaises(ValueError):
                    engine().reconcile('serial', 'A', ['verified'], 'status still unknown')
                job.write_text('completed', encoding='utf-8')
                engine().reconcile('serial', 'A', ['verified'], 'host observed actual completion')
                self.assertEqual(engine().tick('serial', 'settled')['status'], 'done')
                self.assertEqual(calls, ['A', 'A', 'B'])

    def test_definite_job_failure_after_pending_releases_unrelated_step(self):
        spec = plan()
        spec['tasks'][0]['wait_policy'] = {
            'max_polls': 10, 'max_seconds': 600, 'diagnose_after_seconds': 300}
        store = Store(Path(self.store.path).with_name('definite-job-failure.sqlite'))
        store.create(spec)
        calls = []

        class Handler:
            idempotent = True
            def run(self, task, context):
                calls.append(task['task_id'])
                if task['task_id'] == 'A':
                    return Outcome('pending') if len(calls) == 1 else Outcome('failed', 'job ended in failure')
                return Outcome('complete', evidence=['verified'])
            def verify(self, task, evidence):
                return evidence == ['verified']

        for now in range(1, 5):
            Engine(Store(store.path), {'step': Handler()}, authorize=lambda *_: True,
                   allow_legacy=True, clock=lambda: now).tick('serial', str(now))
        self.assertEqual(calls, ['A', 'A', 'B'])
        self.assertEqual(store.snapshot('serial')['state']['tasks']['A']['status'], 'failed')

    def test_blocked_pending_observation_retains_job_until_verified_reconciliation(self):
        for phase in ('adapter_blocked', 'permission_after_review', 'review_after_claim'):
          for idempotent in (True, False):
            with self.subTest(phase=phase, idempotent=idempotent):
                store = Store(Path(self.store.path).with_name(f'{phase}-{idempotent}.sqlite'))
                spec = plan()
                spec['tasks'][0]['wait_policy'] = {
                    'max_polls': 10, 'max_seconds': 600, 'diagnose_after_seconds': 300}
                store.create(spec)
                job = Path(store.path).with_suffix('.job')
                calls, keys = [], []
                allowed = [True]

                class Handler:
                    def run(self, task, context):
                        calls.append(task['task_id'])
                        keys.append(context.idempotency_key)
                        if task['task_id'] == 'B':
                            return Outcome('complete', evidence=['verified'])
                        if not job.exists():
                            job.write_text('running')
                            return Outcome('pending', 'job still running', ['job:owned'])
                        return Outcome('blocked', 'observation access denied', ['observer:denied'])
                    def verify(self, task, evidence):
                        return (evidence == ['verified'] and
                                (task['task_id'] == 'B' or job.read_text() == 'completed'))

                handler = Handler()
                handler.idempotent = idempotent
                def engine():
                    return Engine(Store(store.path), {'step': handler},
                                  authorize=lambda *_: allowed[0], allow_legacy=True,
                                  clock=lambda: self.now)

                engine().tick('serial', 'pending')
                self.now += 1
                observer = engine()
                if phase == 'permission_after_review':
                    checks = []
                    def authorize(*_):
                        checks.append(True)
                        return len(checks) == 1  # Claim allowed, action authorization revoked.
                    observer.authorize = authorize
                elif phase == 'review_after_claim':
                    from agent_runtime.plan_review import PlanReviewError
                    claimed = [False]
                    def authorize(*_):
                        claimed[0] = True
                        return True
                    def review(_plan):
                        if claimed[0]:
                            raise PlanReviewError('review revoked after claim')
                    observer.authorize = authorize
                    observer._review_plan = review
                observer.tick('serial', 'blocked-observation')
                if phase == 'permission_after_review':
                    self.assertEqual(len(checks), 2)
                allowed[0] = True
                self.now += 1
                state = engine().tick('serial', 'restart')
                expected = ['A', 'A'] if phase == 'adapter_blocked' else ['A']
                self.assertEqual(calls, expected)
                self.assertEqual(state.get('active_step'), 'A')
                node = state['tasks']['A']
                reason = 'plan_review_after_effect' if phase == 'review_after_claim' else 'ambiguous'
                self.assertEqual((node['status'], node['reason_kind']), ('blocked', reason))
                self.assertTrue(node['requires_reconciliation'])
                self.assertEqual(node['effect_observation']['status'], 'pending')
                self.assertEqual(node['effect_observation']['evidence'], ['job:owned'])
                self.assertEqual((node['attempts'], node['pending_polls']), (1, 1))
                self.assertEqual(len(set(keys)), 1)
                self.assertEqual(job.read_text(), 'running')
                with self.assertRaises(ValueError):
                    engine().reconcile('serial', 'A', ['verified'], 'job not finished')
                job.write_text('completed')
                allowed[0] = False
                with self.assertRaises(ValueError):
                    engine().reconcile('serial', 'A', ['verified'], 'no authorization')
                allowed[0] = True
                engine().reconcile('serial', 'A', ['verified'], 'host verified actual completion')
                engine().tick('serial', 'next')
                self.assertEqual(calls, expected + ['B'])

    def test_old_blocked_refunded_pending_restores_ownership(self):
        for kind in ('permission', 'adapter', 'adapter_result'):
            with self.subTest(kind=kind):
                self.calls.clear()
                self.store = Store(Path(self.store.path).with_name(kind + '-blocked.sqlite'))
                self.store.create(plan())
                self.seed({'A': {'status': 'blocked', 'attempts': 0,
                                 'pending_since': 1, 'pending_polls': 2,
                                 'next_at': 5, 'reason_kind': kind, 'evidence': ['job:owned']}})
                state = self.tick('restore')
                self.assertEqual(self.calls, [])
                self.assertEqual(state.get('active_step'), 'A')
                node = state['tasks']['A']
                self.assertEqual((node['attempts'], node['pending_polls'], node['pending_since']), (0, 2, 1))
                self.assertEqual(node['evidence'], ['job:owned'])

    def test_multiple_old_pending_steps_block_without_guess_or_budget_reset(self):
        spec = plan()
        spec['tasks'].append(dict(spec['tasks'][0], task_id='C'))
        self.store = Store(Path(self.store.path).with_name('multiple.sqlite'))
        self.store.create(spec)
        self.seed({key: {'attempts': 1, 'next_at': 5, 'reason': 'pending'} for key in ('A', 'B')})
        before = self.store.snapshot('serial')['state']['tasks']
        state = self.tick('multiple')
        self.assertEqual(self.calls, [])
        self.assertEqual(state['status'], 'blocked')
        self.assertIn('A', state['serial_recovery_error'])
        self.assertIn('B', state['serial_recovery_error'])
        self.assertEqual(state['tasks'], before)
        self.now = 10
        self.tick('still-multiple')
        self.assertEqual(self.calls, [])

    def test_completed_active_does_not_hide_another_old_pending_step(self):
        self.seed({'A': {'attempts': 1, 'next_at': 5},
                   'B': {'status': 'done', 'evidence': ['verified']}})
        with self.store.transaction() as db:
            _, state = self.store.load(db, 'serial')
            state['active_step'] = 'B'
            self.store.save(db, 'serial', state)
        state = self.tick('completed-active')
        self.assertEqual(state.get('active_step'), 'A')
        self.assertEqual(self.calls, [])

    def test_multiple_ambiguous_steps_resume_only_after_explicit_convergence(self):
        self.seed({key: {'status': 'blocked', 'attempts': 1,
                         'reason_kind': 'ambiguous'} for key in ('A', 'B')})
        self.assertEqual(self.tick('ambiguous')['status'], 'blocked')
        engine = Engine(self.store, {'step': self.handler}, authorize=lambda *_: True,
                        allow_legacy=True, clock=lambda: self.now)
        engine.reconcile('serial', 'A', ['verified'], 'host verified A')
        state = self.tick('one-left')
        self.assertEqual(state.get('active_step'), 'B')
        self.assertNotIn('serial_recovery_error', state)
        self.assertEqual(self.calls, [])
        engine.reconcile('serial', 'B', ['verified'], 'host verified B')
        self.assertEqual(self.tick('finished')['status'], 'done')

    def test_live_legacy_lease_is_preserved_without_new_dispatch(self):
        self.seed({'A': {'status': 'doing', 'attempts': 1, 'token': 'live', 'lease_until': 10}})
        state = self.tick('live')
        self.assertEqual(state['tasks']['A']['token'], 'live')
        self.assertEqual(state['tasks']['A']['lease_until'], 10)
        self.assertEqual(state['tasks']['A']['attempts'], 1)
        self.assertEqual(self.calls, [])

    def test_unknown_after_effect_is_not_treated_as_completed_revalidation(self):
        self.seed({'A': {'status': 'blocked', 'attempts': 1,
                         'reason_kind': 'plan_review_after_effect',
                         'requires_reconciliation': True,
                         'effect_observation': {'status': 'unknown'}}})
        state = self.tick('unknown-after-effect')
        self.assertEqual(state.get('active_step'), 'A')
        self.assertTrue(state['tasks']['A']['requires_reconciliation'])
        self.assertEqual(self.calls, [])

    def test_reconciled_history_does_not_reopen_execution_after_review_loss(self):
        import copy
        from agent_runtime.plan_review import PlanReviewError
        for observation in ('pending', 'unknown'):
            for extra_wake in (False, True):
                with self.subTest(observation=observation, extra_wake=extra_wake):
                    store = Store(Path(self.store.path).with_name(f'{observation}-{extra_wake}.sqlite'))
                    self.now = 1
                    fixture_plan = plan()
                    fixture_plan['tasks'][0]['wait_policy'] = dict(max_polls=10, max_seconds=600, diagnose_after_seconds=300)
                    store.create(fixture_plan)
                    job = Path(store.path).with_suffix('.job')
                    calls, review_valid = [], [True]

                    class Handler:
                        idempotent = observation == 'pending'
                        def run(self, task, context):
                            calls.append(task['task_id'])
                            if task['task_id'] == 'B':
                                return Outcome('complete', evidence=['verified'])
                            job.write_text('running')
                            if observation == 'unknown':
                                raise OSError('response lost after job admission')
                            if calls.count('A') == 1:
                                return Outcome('pending', evidence=['job:id'])
                            return Outcome('blocked', reason='observer unavailable')
                        def verify(self, task, evidence):
                            return (evidence == ['verified'] and
                                    (task['task_id'] == 'B' or job.read_text() == 'completed'))

                    handler = Handler()
                    def engine():
                        result = Engine(Store(store.path), {'step': handler},
                                        authorize=lambda *_: True, allow_legacy=True,
                                        clock=lambda: self.now)
                        def review(_plan):
                            if not review_valid[0]:
                                raise PlanReviewError('review revoked')
                        result._review_plan = review
                        return result

                    engine().tick('serial', 'admit')
                    self.now += 1
                    if observation == 'pending':
                        engine().tick('serial', 'observation-lost')
                    before = copy.deepcopy(store.snapshot('serial')['state']['tasks']['A'])
                    job.write_text('completed')
                    engine().reconcile('serial', 'A', ['verified'], 'host checked completed job')
                    with store.transaction() as db:
                        _, state = store.load(db, 'serial')
                        state['tasks']['B']['next_at'] = 1000
                        store.save(db, 'serial', state)
                    if extra_wake:
                        engine().tick('serial', 'clear-completed-owner')
                    review_valid[0] = False
                    engine().tick('serial', 'review-lost')
                    review_valid[0] = True
                    self.now = 1000
                    state = engine().tick('serial', 'review-restored')
                    self.assertEqual(calls, ['A', 'A', 'B'] if observation == 'pending' else ['A', 'B'])
                    node = state['tasks']['A']
                    self.assertEqual(node['status'], 'blocked')
                    self.assertTrue(node['requires_reconciliation'])
                    self.assertNotEqual(state['status'], 'done')
                    self.assertEqual(job.read_text(), 'completed')
                    self.assertEqual(node['effect_observation'],
                                     dict(before['effect_observation'], reconciled=True))
                    for key in ('attempts', 'pending_polls', 'pending_since'):
                        self.assertEqual(node.get(key), before.get(key))

    def test_rejected_reconciliation_does_not_settle_or_release_observation(self):
        from agent_runtime.plan_review import PlanReviewError
        for phase in ('permission', 'evidence', 'terminal_recheck', 'review_recheck'):
            with self.subTest(phase=phase):
                store = Store(Path(self.store.path).with_name(phase + '-settlement.sqlite'))
                store.create(plan())
                raw = dict(status='pending', evidence=['job:id'], reason='observer lost')
                with store.transaction() as db:
                    _, state = store.load(db, 'serial')
                    state['active_step'] = 'A'
                    state['tasks']['A'].update(status='blocked', reason_kind='ambiguous',
                                               requires_reconciliation=True, effect_observation=raw)
                    store.save(db, 'serial', state)
                checks, reviews = [], []
                class Handler:
                    idempotent = False
                    def verify(self, task, evidence):
                        checks.append(True)
                        return phase != 'evidence' and not (phase == 'terminal_recheck' and len(checks) > 1)
                engine = Engine(store, {'step': Handler()}, authorize=lambda *_: phase != 'permission',
                                allow_legacy=True, clock=lambda: self.now)
                def review(_plan):
                    reviews.append(True)
                    if phase == 'review_recheck' and len(reviews) > 1:
                        raise PlanReviewError('review lost during settlement')
                engine._review_plan = review
                if phase in ('permission', 'evidence'):
                    with self.assertRaises(ValueError):
                        engine.reconcile('serial', 'A', ['verified'], 'host attempted settlement')
                else:
                    engine.reconcile('serial', 'A', ['verified'], 'host attempted settlement')
                state = store.snapshot('serial')['state']
                self.assertEqual(state['active_step'], 'A')
                self.assertEqual(state['tasks']['A']['effect_observation'], raw)
                self.assertNotEqual(state['tasks']['A']['status'], 'done')

    def test_failed_final_reconciliation_can_recover_without_action_replay(self):
        import copy
        for observation in ('pending', 'unknown'):
            for failure in ('false', 'exception'):
                with self.subTest(observation=observation, failure=failure):
                    self.now = 1
                    store = Store(Path(self.store.path).with_name(f'recheck-{observation}-{failure}.sqlite'))
                    spec = plan()
                    spec['tasks'][0]['wait_policy'] = dict(max_polls=10, max_seconds=600,
                                                          diagnose_after_seconds=300)
                    store.create(spec)
                    receipt = Path(store.path).with_suffix('.receipt')
                    calls, invalidate = [], [True]
                    class Handler:
                        idempotent = observation == 'pending'
                        def run(self, task, context):
                            calls.append(task['task_id'])
                            if task['task_id'] == 'B':
                                return Outcome('complete', evidence=['checked'])
                            if observation == 'unknown':
                                raise OSError('job admitted, response lost')
                            if calls.count('A') == 1:
                                return Outcome('pending', evidence=['job:id'])
                            return Outcome('blocked', reason='observer unavailable')
                        def verify(self, task, evidence):
                            if task['task_id'] == 'B':
                                return evidence == ['checked']
                            if not receipt.exists():
                                if failure == 'exception':
                                    raise OSError('receipt temporarily unavailable')
                                return False
                            if invalidate[0]:
                                invalidate[0] = False
                                receipt.unlink()
                            return evidence == ['checked']
                    handler = Handler()
                    def engine():
                        return Engine(Store(store.path), {'step': handler}, authorize=lambda *_: True,
                                      allow_legacy=True, clock=lambda: self.now)
                    engine().tick('serial', 'admit')
                    self.now = 2
                    if observation == 'pending':
                        engine().tick('serial', 'observer-lost')
                    before = copy.deepcopy(store.snapshot('serial')['state']['tasks']['A'])
                    receipt.write_text('completed')
                    attempted = engine().reconcile('serial', 'A', ['checked'], 'host submitted completion')
                    expected = ['A', 'A'] if observation == 'pending' else ['A']
                    self.assertNotEqual(attempted['tasks']['A']['status'], 'done')
                    state = engine().tick('serial', 'fresh-observer')
                    self.assertEqual(calls, expected)
                    self.assertEqual(state['active_step'], 'A')
                    self.assertEqual(state['tasks']['A']['effect_observation'], before['effect_observation'])
                    receipt.write_text('completed')
                    state = engine().reconcile('serial', 'A', ['checked'], 'host rechecked current receipt')
                    self.assertEqual(state['tasks']['A']['status'], 'done')
                    for key in ('attempts', 'pending_polls', 'pending_since'):
                        self.assertEqual(state['tasks']['A'].get(key), before.get(key))
                    self.assertEqual(state['tasks']['A']['effect_observation'],
                                     dict(before['effect_observation'], reconciled=True))
                    self.assertEqual(engine().tick('serial', 'next-step')['status'], 'done')
                    self.assertEqual(calls, expected + ['B'])

    def test_cancelled_old_pending_chain_is_not_recovered_or_executed(self):
        self.seed({'A': {'attempts': 1, 'next_at': 5}})
        self.store.cancel('serial', 'user cancelled', now=1)
        before = self.store.snapshot('serial')['state']
        self.assertEqual(self.tick('cancelled'), before)
        self.assertEqual(self.calls, [])

    def test_fresh_and_definite_failed_steps_keep_normal_readiness(self):
        self.tick('fresh')
        self.assertEqual(self.calls, ['A'])
        self.calls.clear()
        self.seed({'A': {'status': 'failed', 'attempts': 3}})
        self.tick('failed')
        self.assertEqual(self.calls, ['B'])
