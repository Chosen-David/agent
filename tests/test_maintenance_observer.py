import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agent_runtime.maintenance_gate import MaintenanceGate, MaintenanceOutcome
from agent_runtime.maintenance_observer import maintenance_observer, read_bound


class ObserverTests(unittest.TestCase):
    def maintained_root(self):
        root = Path(__file__).resolve().parents[1]
        if not (root / 'agent_doc/guide/GUIDE.md').is_file():
            self.skipTest('maintained-checkout integration needs an existing human guide; never create one')
        return root

    def test_real_project_binding_and_quiet_trace(self):
        root = self.maintained_root()
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

    def test_small_file_does_not_read_the_entire_budget(self):
        import os
        original = os.fdopen
        reads = []

        def tracked(*args, **kwargs):
            stream = original(*args, **kwargs)
            proxy = MagicMock(wraps=stream)
            proxy.__enter__.return_value = proxy
            proxy.__exit__.side_effect = lambda *exc: stream.close()
            proxy.read.side_effect = lambda size: (reads.append(size), stream.read(size))[1]
            return proxy

        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / 'data').write_bytes(b'abcdef')
            with patch('agent_runtime.maintenance_observer.os.fdopen', side_effect=tracked):
                self.assertEqual(read_bound(root, 'data'), b'abcdef')
            self.assertEqual(reads, [7])

    def test_nonseekable_regular_adapter_retains_full_bounded_read(self):
        import os
        original = os.fdopen
        reads = []

        class Stream:
            def __init__(self, *args, **kwargs):
                self.raw = original(*args, **kwargs)
            def __enter__(self):
                return self
            def __exit__(self, *exc):
                self.raw.close()
            def fileno(self):
                return self.raw.fileno()
            def seekable(self):
                return False
            def seek(self, *args):
                raise AssertionError('must not seek')
            def read(self, size):
                reads.append(size)
                return self.raw.read(size)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / 'data').write_bytes(b'abcdef')
            with patch('agent_runtime.maintenance_observer.os.fdopen', Stream):
                self.assertEqual(read_bound(root, 'data', max_bytes=8), b'abcdef')
                from types import SimpleNamespace
                with patch('agent_runtime.maintenance_observer.os.fstat',
                           return_value=SimpleNamespace(st_size=2, st_mode=0o100600)):
                    with self.assertRaisesRegex(ValueError, 'source exceeds budget'):
                        read_bound(root, 'data', max_bytes=5)
            self.assertEqual(reads, [9, 6])

    def test_size_snapshot_growth_keeps_complete_read_and_bound(self):
        import os
        from types import SimpleNamespace
        original = os.fstat

        def smaller(fd):
            info = original(fd)
            return SimpleNamespace(st_size=2, st_mode=info.st_mode)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            (root / 'data').write_bytes(b'abcdef')
            with patch('agent_runtime.maintenance_observer.os.fstat', side_effect=smaller):
                self.assertEqual(read_bound(root, 'data', max_bytes=6), b'abcdef')
                with self.assertRaisesRegex(ValueError, 'source exceeds budget'):
                    read_bound(root, 'data', max_bytes=5)
            for data in (b'', b'x', b'123456'):
                (root / 'data').write_bytes(data)
                self.assertEqual(read_bound(root, 'data', max_bytes=6), data)

    def test_ambiguous_and_unstable_events(self):
        root = self.maintained_root()
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
        root = self.maintained_root()
        with patch('agent_runtime.maintenance_observer.observe_advice', return_value=({}, {'v': 1})):
            first = maintenance_observer(root, 'test', [], lambda: {})()
        with patch('agent_runtime.maintenance_observer.observe_advice', return_value=({}, {'v': 2})):
            second = maintenance_observer(root, 'test', [], lambda: {})()
        self.assertNotEqual(first, second)
