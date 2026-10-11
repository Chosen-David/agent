import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_runtime.maintenance_gate import MaintenanceGate, MaintenanceOutcome
from agent_runtime.maintenance_observer import maintenance_observer, read_bound


class ObserverTests(unittest.TestCase):
    def test_real_project_binding_and_quiet_trace(self):
        root = Path(__file__).resolve().parents[1]
        event = {'due': False, 'evidence': 'pending'}
        observe = maintenance_observer(root, 'bounded-test', [], lambda: event)
        calls = []
        gate = MaintenanceGate(lambda r: (calls.append(r), MaintenanceOutcome('handled'))[1],
                               observe, project_root=root, run_id='bounded-test', max_quiet_seconds=5, clock=lambda: 0)
        report = {'run_id': 'bounded-test', 'updated_at': 1}
        self.assertEqual(gate(report).status, 'handled')
        report['updated_at'] = 2
        self.assertEqual(gate(report).status, 'unchanged')
        event['due'] = True
        self.assertEqual(gate(report).status, 'handled')
        self.assertEqual(len(calls), 2)

    def test_required_files_missing_do_not_fall_back(self):
        with tempfile.TemporaryDirectory() as d:
            observe = maintenance_observer(Path(d).resolve(), 'test', [], lambda: {})
            with self.assertRaises(ValueError):
                observe()

    def test_file_reads_are_bounded_and_scoped(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve(); (root / 'data').write_bytes(b'abcdef')
            self.assertEqual(read_bound(root, 'data'), b'abcdef')
            for path in ('../data', '/data', 'a//b', 'a\\b', 'C:data'):
                with self.assertRaises(ValueError):
                    read_bound(root, path)
            with self.assertRaises(ValueError):
                read_bound(root, 'data', max_bytes=5)

    def test_ambiguous_and_unstable_events(self):
        root = Path(__file__).resolve().parents[1]
        with self.assertRaises(ValueError):
            maintenance_observer(root, 'test', ['agent_doc/task/TASK.md'], lambda: {})
        counter = iter([{'epoch': 1}, {'epoch': 2}])
        observe = maintenance_observer(root, 'test', [], lambda: next(counter))
        with self.assertRaises(ValueError):
            observe()
        with self.assertRaises(ValueError):
            maintenance_observer(root, 'test', [], lambda: {'x': float('nan')})()
        for events in ({1: 'stringified'}, {'x': (1, 2)}, {'x': 'a' * 65537}):
            with self.assertRaises(ValueError):
                maintenance_observer(root, 'test', [], lambda: events)()

    def test_all_advice_version_is_bound(self):
        root = Path(__file__).resolve().parents[1]
        with patch('agent_runtime.maintenance_observer.observe_advice', return_value=({}, {'v': 1})):
            first = maintenance_observer(root, 'test', [], lambda: {})()
        with patch('agent_runtime.maintenance_observer.observe_advice', return_value=({}, {'v': 2})):
            second = maintenance_observer(root, 'test', [], lambda: {})()
        self.assertNotEqual(first, second)
