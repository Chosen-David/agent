"""Managed/portable child admission with real I/O and synthetic host policy."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from agent_runtime import task_manifest
from agent_runtime.core import ArtifactHandler, Engine, Store
from tests import test_plan_review as fixtures
from tests.test_result_validation import make_fixture, independent_verify
from agent_runtime.result_validation import ResultValidationHandler

if os.name != 'nt':
    from agent_runtime.task_supervisor import ManagedEngine, load_backend

ADAPTER = '''from pathlib import Path
from agent_runtime.core import Outcome

def build(root, store, run_id):
    class Child:
        idempotent = True
        required_capabilities = frozenset()
        grant = True
        policy_error = False
        policy_errors = 0
        policy_calls = 0
        on_authorize = None
        last_task = None
        def run(self, task, context):
            self.entries.append({'current': context.current(), 'permitted': self.grant,
                                 'search_bound': 'prior_result_search' in task})
            (Path(root) / 'child-effect.txt').write_bytes(b'actual child entry')
            return Outcome('pending', 'synthetic child observation')
        def verify(self, task, evidence):
            return False
    child = Child()
    child.entries, child.identities = [], []
    def authorize(plan, task, actual_handler):
        child.policy_calls += 1
        child.identities.append(actual_handler is child)
        child.last_task = task
        if child.on_authorize is not None:
            child.on_authorize(plan, task)
        if child.policy_error:
            child.policy_errors += 1
            raise RuntimeError('synthetic effect policy unavailable')
        return child.grant and actual_handler is child
    return {'handlers': {'verify_artifacts': child}, 'authorize': authorize}
'''


class BoundaryFixture:
    def boundary(self, mode, managed=False):
        f = fixtures.PlanReviewTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        root = f.root
        f.plan['supervision'].update(min_seconds=1, max_seconds=2)
        f.plan['tasks'][0]['estimated_seconds'] = 1
        legacy = mode.startswith('legacy-')
        with_result = mode in ('verifier-revoked', 'result-mutated', 'cached-revoked')
        if with_result:
            contract = make_fixture(root)
            consumer = f.plan['tasks'][0]
            producer, gate = copy.deepcopy(consumer), copy.deepcopy(consumer)
            producer.update(task_id='produce', owner='implementation-agent', action='produce_fixture',
                depends_on=[], experiment_result=contract, report_path='.agent-runs/produce-report.json',
                prior_result_review={'decision': 'rerun', 'reason': 'Fresh controlled arithmetic fixture.', 'record_refs': []},
                done_when={'artifacts': [{'path': 'manifest.json', 'sha256': hashlib.sha256((root / 'manifest.json').read_bytes()).hexdigest()}]})
            gate.update(task_id='verify', owner='independent-fixture-verifier', action='verify_experiment_result',
                depends_on=['produce'], result_validation=contract, report_path='.agent-runs/verify-report.json')
            consumer.update(depends_on=['verify'], required_result_refs=[contract])
            f.plan['tasks'] = [producer, gate, consumer]
            for task in (producer, gate):
                task_manifest.atomic_json(root / task['report_path'], {'task_id': task['task_id'],
                    'summary': 'Controlled arithmetic fixture',
                    'data': [{'kind': 'synthetic', 'description': 'Precreated fixed CPU data, independently recomputed.'}]})
        if legacy:
            f.plan.pop('plan_review')
            f.plan['tasks'][0].pop('prior_result_search', None)
        else:
            f.approve()
        state_dir = root / 'managed-state'
        store = Store(state_dir / 'state.sqlite')
        store.create(f.plan, project_root=root)
        adapter = root / 'trusted_test_adapter.py'
        adapter.write_bytes(ADAPTER.encode('utf8'))
        config = {'run_id': 'r1', 'state_dir': str(state_dir), 'project_root': str(root),
                  'session': 'synthetic-managed-config', 'adapter': str(adapter), 'allow_legacy': legacy}
        if managed:
            handlers, authorize, _, _, _ = load_backend(config, store)
        else:
            spec = importlib.util.spec_from_file_location('synthetic_child_host', adapter)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            backend = module.build(str(root), store, 'r1')
            handlers = {name: task_manifest.ReportingHandler(h, root) for name, h in backend['handlers'].items()}
            authorize = lambda plan, task, wrapper: backend['authorize'](plan, task, wrapper.handler)
        child = handlers['verify_artifacts'].handler
        if with_result:
            helpers = {'produce_fixture': ArtifactHandler(root),
                       'verify_experiment_result': ResultValidationHandler(root, independent_verify)}
            handlers.update({name: task_manifest.ReportingHandler(h, root, independent_verify) for name, h in helpers.items()})
            base_authorize = authorize
            authorize = lambda plan, task, wrapper: (base_authorize(plan, task, wrapper)
                if wrapper.handler is child else wrapper.handler in helpers.values())
        if mode == 'denied':
            child.grant = False
        events, verify_calls = [], [0]
        original_lookup = task_manifest._prior_result_search
        original_documents = task_manifest.check_task_documents

        def lookup(*args, **kwargs):
            result = original_lookup(*args, **kwargs)
            if store.snapshot('r1')['state']['tasks']['T1']['status'] != 'doing':
                return result
            events.append('lookup')
            if mode in ('revoked', 'legacy-revoked'):
                child.grant = False
            elif mode == 'unavailable':
                child.policy_error = True
            elif mode == 'cancelled':
                store.cancel('r1', 'explicit synthetic cancellation', now=f.now[0])
            elif mode == 'lookup-task-mutated':
                child.last_task.setdefault('inputs', {})['unreviewed'] = 'changed'
                events.append('task-mutated')
            return result

        def verify(root, manifest, plan):
            value = independent_verify(root, manifest, plan)
            verify_calls[0] += 1
            if verify_calls[0] == 2 and mode == 'verifier-revoked':
                child.grant = False
                events.append('verifier-revoked')
            elif verify_calls[0] == 2 and mode == 'cached-revoked' and cached_phase[0]:
                child.grant = False
                events.append('cached-verifier-revoked')
            return value

        def mutate_on_authorize(plan, task):
            if child.policy_calls == 3:
                if mode == 'copy-mutated':
                    task.setdefault('inputs', {})['unreviewed'] = 'changed'
                    events.append('copy-mutated')
                elif mode == 'plan-mutated':
                    plan['tasks'][0].setdefault('inputs', {})['unreviewed'] = 'changed'
                    events.append('plan-mutated')
                elif mode == 'result-mutated':
                    raw = root / 'raw.json'
                    raw.write_bytes(raw.read_bytes() + b'\n')
                    events.append('result-mutated')
        child.on_authorize = mutate_on_authorize

        def documents(*args, **kwargs):
            value = original_documents(*args, **kwargs)
            if mode == 'binding-expiry' and child.policy_calls >= 3 and 'binding-expiry' not in events:
                f.now[0] += 6
                events.append('binding-expiry')
            return value

        handlers['verify_artifacts'].result_verifier = verify if with_result else None
        kwargs = {'plan_review_verifier': f.session.verify, 'clock': lambda: f.now[0], 'lease_seconds': 5}
        if managed:
            engine = ManagedEngine(config, store, handlers, authorize, result_verifier=verify if with_result else None, **kwargs)
        else:
            engine = Engine(store, handlers, authorize, project_root=root, allow_legacy=legacy, **kwargs)
        marker = root / 'child-effect.txt'
        cached_phase = [False]
        first_entries = None
        with patch.object(task_manifest, '_prior_result_search', side_effect=lookup), patch.object(task_manifest, 'check_task_documents', side_effect=documents):
            if with_result:
                for event, completed in [('fixture-produce', 'produce'), ('fixture-verify', 'verify')]:
                    upstream = engine.tick('r1', event)
                    self.assertEqual(upstream['tasks'][completed]['status'], 'done', upstream['tasks'][completed])
            state = engine.tick('r1', 'child-first')
            if mode == 'cached-revoked':
                first_entries = list(child.entries)
                self.assertEqual(len(first_entries), 1)
                self.assertEqual(marker.read_bytes(), b'actual child entry')
                child.entries.clear()
                marker.unlink()
                verify_calls[0] = 0
                cached_phase[0] = True
                f.now[0] = state['tasks']['T1']['next_at']
                state = engine.tick('r1', 'child-second')
        progress = json.loads((state_dir / 'progress.json').read_bytes()) if managed else None
        print('CHILD_ADMISSION_PROBE ' + json.dumps({'path': 'managed' if managed else 'portable',
            'mode': mode, 'events': events, 'entries': child.entries, 'first_entries': first_entries,
            'marker_hex': marker.read_bytes().hex() if marker.exists() else None,
            'policy_calls': child.policy_calls, 'policy_errors': child.policy_errors,
            'identities': child.identities, 'synthetic_review_requests': len(f.calls),
            'status': state['status'], 'attempts': state['tasks']['T1']['attempts'],
            'managed_reportable': progress['all_reportable'] if progress else None}, sort_keys=True))
        self.assertTrue(child.identities)
        self.assertTrue(all(child.identities))
        self.assertEqual(len(f.calls), 0 if legacy else 1)
        if mode in ('healthy', 'legacy-healthy'):
            self.assertEqual(child.policy_calls, 3, 'wrapped healthy path explicitly pays one fresh policy call')
            self.assertEqual(events, ['lookup'])
            self.assertEqual(len(child.entries), 1)
            self.assertTrue(child.entries[0]['current'])
            self.assertTrue(child.entries[0]['permitted'])
            self.assertEqual(marker.read_bytes(), b'actual child entry')
            self.assertTrue(child.last_task.get('prior_result_search'))
        else:
            self.assertEqual(child.entries, [], 'actual child must not enter before current authority and bindings')
            self.assertFalse(marker.exists())
            if mode == 'denied':
                self.assertEqual(events, [])
                self.assertEqual(state['tasks']['T1']['attempts'], 0)
            elif mode == 'cancelled':
                self.assertEqual(state['status'], 'cancelled')
            elif mode == 'unavailable':
                self.assertEqual(child.policy_errors, 1)
            elif mode == 'cached-revoked':
                self.assertEqual(events.count('lookup'), 1)
                self.assertIn('cached-verifier-revoked', events)
            elif mode in ('copy-mutated', 'plan-mutated', 'result-mutated', 'binding-expiry'):
                self.assertIn(mode, events)
            elif mode == 'lookup-task-mutated':
                self.assertIn('task-mutated', events)
            if mode in ('revoked', 'legacy-revoked', 'verifier-revoked', 'unavailable'):
                self.assertEqual(state['status'], 'blocked')
        self.assertNotEqual(state['status'], 'done')
        if progress:
            self.assertEqual(progress['run_id'], 'r1')
            self.assertFalse(progress['all_reportable'])


@unittest.skipIf(os.name == 'nt', 'managed tmux module requires Unix/fcntl; portable Engine cases run here')
class ManagedChildAuthority(BoundaryFixture, unittest.TestCase):
    def test_healthy(self): self.boundary('healthy', managed=True)
    def test_initial_denial(self): self.boundary('denied', managed=True)
    def test_lookup_cancellation(self): self.boundary('cancelled', managed=True)
    def test_lookup_revocation(self): self.boundary('revoked', managed=True)


class PortableChildAuthority(BoundaryFixture, unittest.TestCase):
    def test_healthy(self): self.boundary('healthy')
    def test_lookup_revocation(self): self.boundary('revoked')
    def test_policy_unavailable(self): self.boundary('unavailable')
    def test_verifier_revocation(self): self.boundary('verifier-revoked')
    def test_result_mutated_during_authorization(self): self.boundary('result-mutated')
    def test_child_copy_mutated_during_authorization(self): self.boundary('copy-mutated')
    def test_plan_mutated_during_authorization(self): self.boundary('plan-mutated')
    def test_claim_expires_during_binding_reads(self): self.boundary('binding-expiry')
    def test_legacy_derived_search(self): self.boundary('legacy-healthy')
    def test_legacy_revocation(self): self.boundary('legacy-revoked')
    def test_cached_lookup_verifier_revocation(self): self.boundary('cached-revoked')
    def test_lookup_changes_protected_task(self): self.boundary('lookup-task-mutated')


if __name__ == '__main__':
    unittest.main()
