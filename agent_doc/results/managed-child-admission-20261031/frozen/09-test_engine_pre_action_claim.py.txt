"""Real Engine/SQLite boundary checks with synthetic host policy and clocks."""
import json
import sqlite3
import unittest

from agent_runtime.core import ArtifactHandler, Engine, Store
from tests import test_plan_review as review_fixtures


class PreActionClaimTests(unittest.TestCase):
    def boundary(self, mode):
        fixture = review_fixtures.PlanReviewTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.root = fixture.root.resolve()
        fixture.approve()
        store = Store(fixture.root / 'claim.sqlite')
        store.create(fixture.plan, project_root=fixture.root)
        entered, invalidated, permitted = [], [], []
        grant, policy_error, authorize_calls = [True], [False], [0]
        marker = fixture.root / 'handler-started.txt'

        class Handler(ArtifactHandler):
            def run(self, task, context):
                entered.append(context.current())
                permitted.append(grant[0] and not policy_error[0])
                marker.write_bytes(b'handler entered')
                return super().run(task, context)

        handler = Handler(fixture.root)

        def mutate(where):
            applicable = ((where == 'review' and mode in ('expiry', 'cancel', 'token', 'authority-revoked', 'authority-error'))
                          or (where == 'authorize' and mode == 'authorization-expiry'))
            if invalidated or not applicable:
                return
            # Callbacks may run inside Engine's write transaction: observe only.
            db = sqlite3.connect(store.path)
            try:
                state = json.loads(db.execute("SELECT state FROM chains WHERE id='r1'").fetchone()[0])
            finally:
                db.close()
            if state['tasks']['T1']['status'] != 'doing':
                return
            if where == 'review' and mode in ('expiry', 'cancel', 'token', 'authority-revoked', 'authority-error'):
                invalidated.append(mode)
                if mode == 'expiry':
                    fixture.now[0] += 5
                elif mode == 'cancel':
                    store.cancel('r1', 'synthetic cancellation during live review', now=fixture.now[0])
                elif mode == 'token':
                    with store.transaction() as db:
                        _, state = store.load(db, 'r1')
                        state['tasks']['T1']['token'] = 'different-owner-token'
                        store.save(db, 'r1', state)
                elif mode == 'authority-revoked':
                    grant[0] = False
                else:
                    policy_error[0] = True
            elif where == 'authorize' and mode == 'authorization-expiry':
                invalidated.append(mode)
                fixture.now[0] += 5

        def verify(*args):
            result = fixture.session.verify(*args)
            mutate('review')
            return result

        def authorize(*args):
            authorize_calls[0] += 1
            mutate('authorize')
            if policy_error[0]:
                raise RuntimeError('synthetic policy service unavailable after review')
            return mode != 'denied' and grant[0]

        engine = Engine(store, {'verify_artifacts': handler}, authorize=authorize,
                        project_root=fixture.root, plan_review_verifier=verify,
                        clock=lambda: fixture.now[0], lease_seconds=5)
        state = engine.tick('r1', 'first-wake')
        print('ENGINE_CLAIM_PROBE ' + json.dumps({
            'mode': mode, 'entered_current': entered, 'entry_authorized': permitted,
            'authorization_calls': authorize_calls[0],
            'marker_hex': marker.read_bytes().hex() if marker.exists() else None,
            'status': state['status'], 'attempts': state['tasks']['T1']['attempts'],
            'mutation': invalidated}, sort_keys=True))
        if mode == 'healthy':
            self.assertEqual(authorize_calls[0], 2)
            self.assertEqual(entered, [True])
            self.assertEqual(marker.read_bytes(), b'handler entered')
            self.assertEqual(state['status'], 'done')
        else:
            if mode != 'denied':
                self.assertEqual(invalidated, [mode])
            self.assertEqual(entered, [], 'handler must not start with a stale claim')
            self.assertFalse(marker.exists(), 'stale claim wrote an external marker')
            self.assertNotEqual(state['status'], 'done')
        if mode in ('authority-revoked', 'authority-error'):
            self.assertEqual(permitted, [])
            self.assertEqual(state['status'], 'blocked')
            self.assertEqual(state['tasks']['T1']['attempts'], 1)
            self.assertEqual(engine.tick('r1', 'denied-next-wake')['status'], 'blocked')
            self.assertEqual(entered, [])
        elif mode == 'cancel':
            self.assertEqual(state['status'], 'cancelled')
        elif mode == 'token':
            self.assertEqual(state['tasks']['T1']['token'], 'different-owner-token')
        elif mode == 'denied':
            self.assertEqual(state['tasks']['T1']['attempts'], 0)
        elif mode in ('expiry', 'authorization-expiry'):
            self.assertEqual(state['tasks']['T1']['attempts'], 1)
            self.assertEqual(state['tasks']['T1']['status'], 'doing')
            fixture.now[0] += 1
            restarted = Engine(Store(store.path), {'verify_artifacts': handler},
                               authorize=authorize, project_root=fixture.root,
                               plan_review_verifier=verify, clock=lambda: fixture.now[0], lease_seconds=5)
            self.assertEqual(restarted.tick('r1', 'first-wake')['tasks']['T1']['attempts'], 1)
            self.assertEqual(entered, [])
            recovered = restarted.tick('r1', 'new-wake')
            self.assertEqual(entered, [True])
            self.assertEqual(recovered['status'], 'done')
            self.assertEqual(recovered['tasks']['T1']['attempts'], 2)
            self.assertEqual(marker.read_bytes(), b'handler entered')

    def test_authority_revoked_during_review(self):
        self.boundary('authority-revoked')

    def test_policy_unavailable_after_review(self):
        self.boundary('authority-error')

    def test_review_exact_expiry(self):
        self.boundary('expiry')

    def test_review_cancellation(self):
        self.boundary('cancel')

    def test_review_owner_token_change(self):
        self.boundary('token')

    def test_authorization_exact_expiry(self):
        self.boundary('authorization-expiry')

    def test_healthy_review_enters_once(self):
        self.boundary('healthy')

    def test_denied_authorization_never_claims(self):
        self.boundary('denied')


class AuthorizationBindingTests(unittest.TestCase):
    def boundary(self, kind):
        fixture = review_fixtures.PlanReviewTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        root = fixture.root
        target = None
        if kind == 'advice':
            from agent_runtime import project_docs as docs
            from agent_runtime.task_manifest import prepare
            import hashlib
            target = root / 'agent_doc/advice/late.md'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'Synthetic adopted advice.\n')
            old = fixture.plan['tasks'][0]
            fixture.plan = prepare(root, 'r1', 'manual', 'synthetic test instruction', lineage_id='logical-T1')
            fixture.plan['tasks'][0].update(action=old['action'], done_when=old['done_when'])
            docs.bind_advice(fixture.plan, [{'path': 'agent_doc/advice/late.md',
                'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'task_refs': ['T1'],
                'disposition': 'adopt', 'reason': 'Synthetic acceptance fixture.',
                'guide_alignment': 'compatible'}])
        elif kind == 'evidence':
            import hashlib
            target = root / 'review-evidence.txt'
            target.write_bytes(b'Synthetic approved evidence.\n')
            fixture.plan['plan_review']['evidence_refs'].append({
                'path': 'review-evidence.txt', 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
        elif kind == 'task-source':
            target = root / 'TASK.md'
        fixture.approve()
        store = Store(root / 'bindings.sqlite')
        store.create(fixture.plan, project_root=root)
        entered, changed = [], []
        calls = [0]
        marker = root / 'binding-handler.txt'

        class Handler(ArtifactHandler):
            def run(self, task, context):
                entered.append(context.current())
                marker.write_bytes(b'unreviewed entry')
                return super().run(task, context)

        def authorize(plan, task, handler):
            calls[0] += 1
            db = sqlite3.connect(store.path)
            try:
                state = json.loads(db.execute("SELECT state FROM chains WHERE id='r1'").fetchone()[0])
            finally:
                db.close()
            if not changed and state['tasks']['T1']['status'] == 'doing':
                changed.append(kind)
                if kind == 'task-input':
                    task.setdefault('inputs', {})['unreviewed_adapter_field'] = 'changed'
                elif kind == 'receipt':
                    plan['plan_review_receipt']['proof'] = 'unreviewed-proof'
                else:
                    target.write_bytes(target.read_bytes() + b'changed\n')
            return True

        handler = Handler(root)
        engine = Engine(store, {'verify_artifacts': handler}, authorize=authorize,
                        project_root=root, plan_review_verifier=fixture.session.verify,
                        clock=lambda: fixture.now[0], lease_seconds=5)
        state = engine.tick('r1', 'authorization-binding')
        print('AUTHORITY_BINDING_PROBE ' + json.dumps({
            'kind': kind, 'changed': changed, 'entered_current': entered,
            'marker_hex': marker.read_bytes().hex() if marker.exists() else None,
            'status': state['status'], 'authorization_calls': calls[0]}, sort_keys=True))
        self.assertEqual(changed, [kind])
        self.assertEqual(entered, [], 'authorization must not bypass reviewed input bindings')
        self.assertFalse(marker.exists())
        self.assertNotEqual(state['status'], 'done')

    def test_authorizer_task_input_mutation(self):
        self.boundary('task-input')

    def test_authorizer_receipt_mutation(self):
        self.boundary('receipt')

    def test_authorizer_task_source_mutation(self):
        self.boundary('task-source')

    def test_authorizer_review_evidence_mutation(self):
        self.boundary('evidence')

    def test_authorizer_adopted_advice_mutation(self):
        self.boundary('advice')


class LegacyAuthorizationBindingTests(unittest.TestCase):
    def boundary(self, kind):
        fixture = review_fixtures.PlanReviewTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        root = fixture.root
        fixture.plan.pop('plan_review')
        store = Store(root / 'legacy.sqlite')
        store.create(fixture.plan, project_root=root)
        entered, changed = [], []
        marker = root / 'legacy-handler.txt'

        class Handler(ArtifactHandler):
            def run(self, task, context):
                entered.append(context.current())
                marker.write_bytes(b'legacy entry')
                return super().run(task, context)

        def authorize(plan, task, handler):
            db = sqlite3.connect(store.path)
            try:
                state = json.loads(db.execute("SELECT state FROM chains WHERE id='r1'").fetchone()[0])
            finally:
                db.close()
            if not changed and state['tasks']['T1']['status'] == 'doing':
                changed.append(kind)
                if kind == 'policy':
                    plan['plan_review'] = {'schema_version': 'invalid'}
                elif kind == 'lineage':
                    from agent_runtime.plan_review import _db
                    db = _db(root)
                    try:
                        db.execute('INSERT INTO review_protected VALUES (?, ?)', ('T1', 'late-lineage'))
                        db.commit()
                    finally:
                        db.close()
                else:
                    task.setdefault('inputs', {})['legacy_adapter_field'] = 'allowed'
            return True

        state = Engine(store, {'verify_artifacts': Handler(root)}, authorize=authorize,
                       project_root=root, allow_legacy=True,
                       clock=lambda: fixture.now[0], lease_seconds=5).tick('r1', 'legacy-binding')
        print('LEGACY_BINDING_PROBE ' + json.dumps({'kind': kind, 'changed': changed,
            'entered_current': entered, 'marker_hex': marker.read_bytes().hex() if marker.exists() else None,
            'status': state['status']}, sort_keys=True))
        self.assertEqual(changed, [kind])
        if kind == 'adapter-input':
            self.assertEqual(entered, [True])
            self.assertEqual(marker.read_bytes(), b'legacy entry')
            self.assertEqual(state['status'], 'done')
        else:
            self.assertEqual(entered, [])
            self.assertFalse(marker.exists())
            self.assertNotEqual(state['status'], 'done')

    def test_legacy_late_policy_is_blocked(self):
        self.boundary('policy')

    def test_legacy_late_protection_is_blocked(self):
        self.boundary('lineage')

    def test_legacy_adapter_input_compatibility(self):
        self.boundary('adapter-input')


if __name__ == '__main__':
    unittest.main()
