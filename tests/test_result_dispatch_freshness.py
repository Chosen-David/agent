"""Live result callbacks precede claim checks; captured bindings are rechecked."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from agent_runtime import task_manifest
from agent_runtime.core import Context, Outcome, Store
from agent_runtime.contamination import _run
from agent_runtime.result_store import ResultStore, result_context
from test_result_validation import dag, independent_verify, make_fixture, ref

class ResultDispatchFreshnessTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.contract = make_fixture(self.root)
        self.task = {'task_id': 'consume', 'required_result_refs': [self.contract]}
        self.verifier_calls = 0
        class Handler:
            calls = 0
            idempotent = True
            required_capabilities = ()
            def run(self, task, context):
                self.calls += 1
                return Outcome('pending', 'fixture work', [])
        self.handler = Handler()
        self.wrapper = task_manifest.ReportingHandler(self.handler, self.root, self.verify)

    def verify(self, root, manifest, plan):
        self.verifier_calls += 1
        return independent_verify(root, manifest, plan)

    def reuse(self, measured_at=None):
        manifest = json.loads((self.root/'manifest.json').read_bytes())
        if measured_at is not None:
            manifest['execution']['completed_at'] = measured_at
            (self.root/'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        registered = ResultStore(self.root).register(self.contract, historical=True, measured_at=measured_at)
        self.task.pop('required_result_refs')
        self.task['result_reuse'] = {'run_id': manifest['run_id'],
            'record_sha256': registered['record_ref']['sha256'], 'query': 'square sums',
            'context': result_context(manifest), 'explicit_reproduction': False, 'new_claim': False}
        return self.root/registered['record_ref']['path']

    def raw_change(self):
        p = self.root/'raw.json'; p.write_bytes(p.read_bytes()+b'\n')

    def changed(self, change, boundary='current'):
        events = []
        def mutate():
            change(); events.append(boundary)
        if boundary == 'lookup':
            original = task_manifest._prior_result_search
            def lookup(*args, **kwargs):
                value = original(*args, **kwargs); mutate(); return value
            with patch.object(task_manifest, '_prior_result_search', side_effect=lookup):
                outcome = self.wrapper.run(self.task, None)
        else:
            class Claim:
                def current(self): mutate(); return True
            outcome = self.wrapper.run(self.task, Claim())
        self.assertEqual(events, [boundary])
        self.assertEqual(self.handler.calls, 0, (outcome.status, outcome.reason))
        self.assertEqual(outcome.status, 'blocked')
        self.assertIn('reconciliation', outcome.reason)

    def test_required_lookup(self): self.changed(self.raw_change, 'lookup')
    def test_required_current(self): self.changed(self.raw_change)
    def test_reuse_lookup(self): self.reuse(); self.changed(self.raw_change, 'lookup')
    def test_reuse_current(self): self.reuse(); self.changed(self.raw_change)
    def test_registry_current(self):
        p = self.reuse(); self.changed(lambda: p.write_bytes(p.read_bytes()+b'\n'))

    def test_review_evidence_current(self):
        note = self.root/'review-note.txt'; note.write_bytes(b'independent fixture observation')
        def verifier(root, manifest, plan):
            value = self.verify(root, manifest, plan)
            value['checks']['implementation']['evidence'].append(ref(root, 'review-note.txt'))
            return value
        self.wrapper.result_verifier = verifier
        self.changed(lambda: note.write_bytes(b'corrected observation'))

    def test_revocation_current(self):
        # The existing gate deliberately rejects even a partial incident record.
        incident = self.root/_run('cpu-run-1')/'incident.json'
        def revoke():
            incident.parent.mkdir(parents=True); incident.write_bytes(b'')
        self.changed(revoke)

    def test_unchanged_required_string_root_and_empty_refs(self):
        self.wrapper.root = str(self.root)
        outcome = self.wrapper.run(self.task, None)
        self.assertEqual((outcome.status, self.handler.calls), ('pending', 1))
        self.assertEqual(self.verifier_calls, 3)
        self.task.pop('required_result_refs')
        self.wrapper.result_verifier = lambda *_: self.fail('empty refs called verifier')
        outcome = self.wrapper.run(self.task, None)
        self.assertEqual((outcome.status, self.handler.calls), ('pending', 2))
        self.assertFalse((self.root/'agent_doc/results').exists())
        self.assertFalse((self.root/'.agent-memory').exists())

    def test_unchanged_reuse(self):
        self.reuse(); outcome = self.wrapper.run(self.task, None)
        self.assertEqual((outcome.status, self.handler.calls), ('pending', 1))
        self.assertEqual(self.verifier_calls, 3)

    def test_missing_verifier_and_current_false(self):
        self.wrapper.result_verifier = None
        outcome = self.wrapper.run(self.task, None)
        self.assertEqual((outcome.status, self.handler.calls), ('blocked', 0))
        self.wrapper.result_verifier = self.verify
        class Claim:
            def current(self): return False
        outcome = self.wrapper.run(self.task, Claim())
        self.assertEqual((outcome.status, self.handler.calls), ('blocked', 0))
        self.assertIn('claim no longer current', outcome.reason)

    def test_cached_lookup_still_checks_current_changes(self):
        original = task_manifest._prior_result_search
        with patch.object(task_manifest, '_prior_result_search', wraps=original) as lookup:
            first = self.wrapper.run(self.task, None)
            self.assertEqual((first.status, self.handler.calls), ('pending', 1))
            owner = self
            class Claim:
                def current(self): owner.raw_change(); return True
            second = self.wrapper.run(self.task, Claim())
            self.assertEqual(lookup.call_count, 1)
        self.assertEqual((second.status, self.handler.calls), ('blocked', 1))

    def test_actual_claim_expiry_cancel_and_token_loss_during_late_verifier(self):
        store = Store(self.root/'state.sqlite'); store.create(dag(self.contract))
        clock = [0]
        context = Context(store, 'test', 'consume', 'owned', 'key', lambda: clock[0])
        for change in ('expiry', 'cancel', 'token'):
            with self.subTest(change=change):
                clock[0] = 0
                with store.transaction() as db:
                    plan, state = store.load(db, 'test')
                    state['status'] = 'active'
                    state['tasks']['consume'].update(status='doing', token='owned', lease_until=10)
                    store.save(db, 'test', state)
                self.verifier_calls = 0
                def verifier(root, manifest, plan):
                    value = self.verify(root, manifest, plan)
                    if self.verifier_calls == 2:
                        if change == 'expiry': clock[0] = 11
                        elif change == 'cancel': store.cancel('test', 'test-host cancellation', now=1)
                        else:
                            with store.transaction() as db:
                                bound, state = store.load(db, 'test')
                                state['tasks']['consume']['token'] = 'replacement'
                                store.save(db, 'test', state)
                    return value
                self.wrapper.result_verifier = verifier
                outcome = self.wrapper.run(self.task, context)
                self.assertEqual(self.verifier_calls, 2)
                actual = store.snapshot('test')['state']
                if change == 'expiry': self.assertEqual(clock[0], 11)
                elif change == 'cancel': self.assertEqual(actual['status'], 'cancelled')
                else: self.assertEqual(actual['tasks']['consume']['token'], 'replacement')
                self.assertEqual((outcome.status, self.handler.calls), ('blocked', 0))
                self.assertIn('claim no longer current', outcome.reason)

    def test_reuse_ttl_expires_during_current(self):
        self.reuse(dt.datetime.now(dt.timezone.utc).isoformat())
        self.task['result_reuse']['max_age_seconds'] = 3600
        future = dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=2)
        real_datetime = dt.datetime
        class FutureDateTime(real_datetime):
            @classmethod
            def now(cls, tz=None): return future
        selected = self.task['result_reuse']
        self.assertEqual(ResultStore(self.root).decide_run(selected['run_id'], selected['context'],
            verifier=independent_verify, max_age_seconds=3600)['decision'], 'reuse')
        events = []
        patcher = patch('agent_runtime.result_store.dt.datetime', FutureDateTime)
        self.addCleanup(patcher.stop)
        class Claim:
            def current(self): events.append('current'); patcher.start(); return True
        outcome = self.wrapper.run(self.task, Claim())
        self.assertEqual((outcome.status, self.handler.calls), ('blocked', 0))
        self.assertIn('freshness', outcome.reason)
        self.assertEqual(events, ['current'])
        self.assertEqual(self.verifier_calls, 2)

    def test_later_verifier_invalidates_earlier_review_bindings(self):
        second = json.loads(json.dumps(self.contract))
        second.update(result_id='cpu-result-2', manifest_path='manifest-2.json')
        manifest = json.loads((self.root/'manifest.json').read_bytes())
        manifest['result_id'] = 'cpu-result-2'
        (self.root/'manifest-2.json').write_text(json.dumps(manifest), encoding='utf-8')
        self.task['required_result_refs'].append(second)
        note = self.root/'first-review.txt'; note.write_bytes(b'first observation')
        calls = []
        def verifier(root, manifest, plan):
            value = self.verify(root, manifest, plan)
            sibling = 'manifest-2.json' if manifest['result_id']=='cpu-result-2' else 'manifest.json'
            value['manifest_sha256'] = hashlib.sha256((root/sibling).read_bytes()).hexdigest()
            calls.append(manifest['result_id'])
            if manifest['result_id']=='cpu-result-1':
                value['checks']['implementation']['evidence'].append(ref(root, 'first-review.txt'))
            elif len(calls)==4: note.write_bytes(b'later verifier corrected first observation')
            return value
        self.wrapper.result_verifier = verifier
        outcome = self.wrapper.run(self.task, None)
        self.assertEqual(calls, ['cpu-result-1', 'cpu-result-2']*2)
        self.assertEqual(note.read_bytes(), b'later verifier corrected first observation')
        self.assertEqual(self.handler.calls, 0, (outcome.status, outcome.reason))
        self.assertEqual(outcome.status, 'blocked')
        self.assertIn('reconciliation', outcome.reason)

    def test_existing_reuse_age_boundary_future_and_no_age_semantics(self):
        self.reuse('2026-10-01T00:00:00+00:00')
        selection = self.task['result_reuse']
        cases = [(10, '2026-10-01T00:00:10+00:00', 'reuse'),
                 (10, '2026-10-01T00:00:11+00:00', 'verify_delta'),
                 (10, '2026-09-30T23:59:59+00:00', 'verify_delta'),
                 (None, 'unused-invalid-clock', 'reuse')]
        for cap, instant, decision in cases:
            with self.subTest(cap=cap, instant=instant):
                value = ResultStore(self.root).decide_run(selection['run_id'], selection['context'],
                    verifier=independent_verify, max_age_seconds=cap, now=instant)
                self.assertEqual(value['decision'], decision)
