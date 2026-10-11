import tempfile
from pathlib import Path
import unittest
from agent_runtime.maintenance_gate import MaintenanceGate, MaintenanceOutcome


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = str(Path(self.tmp.name).resolve())
        self.now = 0
        self.events = {'advice_sha': 'v1', 'due': False}
        self.report = {'run_id': 'r', 'updated_at': 1, 'source_error': None,
                       'requirements': [{'status': 'blocked', 'reason': 'wait', 'next_at': 30}]}
        self.calls = []

    def gate(self, callback=None, observer=None):
        def handle(report):
            self.calls.append(report)
            return MaintenanceOutcome('handled')
        return MaintenanceGate(callback or handle,
            observer or (lambda: {'project_root': self.root, 'run_id': 'r', 'events': self.events}),
            project_root=self.root, run_id='r', max_quiet_seconds=10, clock=lambda: self.now)

    def test_only_acknowledged_unchanged_is_skipped(self):
        gate = self.gate()
        self.assertEqual(gate(self.report).status, 'handled')
        self.report['updated_at'] = 2
        self.assertEqual(gate(self.report).status, 'unchanged')
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.gate()(self.report).status, 'handled')

    def test_semantics_external_events_and_due_wake(self):
        gate = self.gate()
        gate(self.report)
        self.events['advice_sha'] = 'v2'; gate(self.report)
        self.events['due'] = True; gate(self.report)
        self.report['source_error'] = 'stale evidence'; gate(self.report)
        self.report['requirements'][0]['next_at'] = 31; gate(self.report)
        self.assertEqual(len(self.calls), 5)

    def test_expiry_boundary_clock_rollback_and_restart(self):
        gate = self.gate(); gate(self.report)
        self.now = 9.99; self.assertEqual(gate(self.report).status, 'unchanged')
        self.now = 10; gate(self.report)
        self.now = 1; gate(self.report)
        self.assertEqual(len(self.calls), 3)

    def test_pending_none_and_exception_never_ack(self):
        for result in (None, MaintenanceOutcome('pending'), MaintenanceOutcome('unchanged')):
            calls = []
            gate = self.gate(lambda r: calls.append(r) or result)
            gate(self.report); gate(self.report)
            self.assertEqual(len(calls), 2)
        def fail(r):
            self.calls.append(r); raise RuntimeError('failed')
        gate = self.gate(fail)
        for _ in range(2):
            with self.assertRaisesRegex(RuntimeError, 'failed'): gate(self.report)
        self.assertEqual(len(self.calls), 2)

    def test_race_and_failed_refresh_do_not_reuse_old_ack(self):
        def handle(r):
            self.calls.append(r); self.events['advice_sha'] += 'x'
            return MaintenanceOutcome('handled')
        gate = self.gate(handle); gate(self.report); gate(self.report)
        self.assertEqual(len(self.calls), 2)
        gate = self.gate(); gate(self.report)
        self.now = 10
        gate.maintain = lambda r: MaintenanceOutcome('pending')
        gate(self.report); self.now = 11
        self.assertEqual(gate(self.report).status, 'pending')

    def test_binding_errors_bad_json_and_budget(self):
        for external in ({}, {'project_root': self.root, 'run_id': 'wrong', 'events': {}},
                         {'project_root': self.root+'x', 'run_id': 'r', 'events': {}}):
            with self.assertRaises(ValueError): self.gate(observer=lambda: external)(self.report)
        for value in (float('nan'), float('inf'), object(), (1, 2), {1: 'x'}, 'x'*65536):
            self.events['bad'] = value
            with self.assertRaises(ValueError): self.gate()(self.report)
        self.assertFalse(self.calls)

    def test_nested_timestamp_and_reentrancy_preserved(self):
        gate = self.gate(); gate(self.report)
        self.report['requirements'][0]['updated_at'] = 1; gate(self.report)
        self.assertEqual(len(self.calls), 2)
        def recursive(report): return gate(report)
        gate.maintain = recursive; self.now = 20
        with self.assertRaisesRegex(RuntimeError, 'in flight'): gate(self.report)
        gate.maintain = lambda r: MaintenanceOutcome('handled')
        self.assertEqual(gate(self.report).status, 'handled')

    def test_configuration_clock_and_observer_failure(self):
        for limit in (True, 0, -1, float('nan')):
            with self.assertRaises(ValueError):
                MaintenanceGate(lambda r: None, lambda: {}, project_root=self.root,
                                run_id='r', max_quiet_seconds=limit)
        gate = self.gate(); self.now = float('inf')
        with self.assertRaises(ValueError): gate(self.report)
        self.now = 0
        def unavailable(): raise OSError('unreadable')
        gate = self.gate(observer=unavailable)
        with self.assertRaises(OSError): gate(self.report)
        self.assertFalse(self.calls)

    def test_observer_failure_invalidates_prior_ack(self):
        gate = self.gate(); gate(self.report)
        observer = gate.observe
        def fail(): raise OSError('lost checkpoint')
        gate.observe = fail
        with self.assertRaises(OSError): gate(self.report)
        gate.observe = observer
        self.assertEqual(gate(self.report).status, 'handled')
        self.assertEqual(len(self.calls), 2)
        self.now = float('nan')
        with self.assertRaises(ValueError): gate(self.report)
        self.now = 0
        self.assertEqual(gate(self.report).status, 'handled')
        self.assertEqual(len(self.calls), 3)

    def test_node_character_and_recursion_budgets(self):
        for value in ([None]*8193, ['x'*100]*1000, 1 << 300000):
            self.events['large'] = value
            with self.assertRaises(ValueError): self.gate()(self.report)
        self.events.clear(); self.events['cycle'] = self.events
        with self.assertRaises(ValueError): self.gate()(self.report)
        self.assertFalse(self.calls)


if __name__ == '__main__': unittest.main()
