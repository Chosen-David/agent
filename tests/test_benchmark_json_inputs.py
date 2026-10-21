"""Formal benchmark CLIs reject unsafe configs before producing evidence."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BenchmarkJSONInputTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='benchmark-json-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.baseline = self.root / 'baseline.py'
        self.baseline.write_text('class Mailbox: pass\n')

    def commands(self, source, output):
        return [
            [sys.executable, str(ROOT / 'scripts/bench_memory_check.py'),
             '--config', str(source), '--output', str(output)],
            [sys.executable, str(ROOT / 'scripts/bench_memory_retrieval.py'),
             '--config', str(source), '--output', str(output)],
            [sys.executable, str(ROOT / 'scripts/benchmark_communication_usage.py'),
             '--plan', str(source), '--baseline', str(self.baseline), '--out', str(output)],
        ]

    def assert_invalid(self, source, *, name, indexes=range(3)):
        for index in indexes:
            command = self.commands(source, self.root / f'{name}-{index}.json')[index]
            output = Path(command[-1])
            with self.subTest(name=name, script=Path(command[1]).name):
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                        timeout=5, env={**os.environ, 'PYTHONPATH': str(ROOT)})
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(result.stderr, '')
                self.assertEqual(json.loads(result.stdout)['status'], 'invalid')
                self.assertFalse(output.exists())
                self.assertFalse(output.with_name(output.stem + '-summary.json').exists())

    def test_individually_legal_fields_cannot_multiply_into_unbounded_work(self):
        source = self.root / 'aggregate.json'
        cases = [
            (0, {'baseline': 'a' * 40, 'fixtures': [{'id': 'huge', 'shape': 'chain',
                  'nodes': 1_000_000, 'content_bytes': 1024, 'roots': [999999]}],
                 'measurement': {'seed': 1, 'wall_pairs': 1, 'traced_pairs': 1,
                                 'warmup_each': 0}}),
            (1, {'baseline_revision': 'a' * 40, 'baseline_source_sha256': 'b' * 64,
                 'seed': 1, 'repeats': 1, 'cases': [{'name': 'huge', 'entries': 1_000_000,
                 'active': 1_000_000, 'content_bytes': 1024, 'match_every': 1,
                 'scope': None}]}),
            (2, {'scope': 'bounded synthetic fixture', 'matrix': {'backlog': [1_000_000],
                 'fanout': [100_000], 'byte_budget': [True], 'repeats': 1, 'warmups': 0,
                 'summary_chars': 1, 'arms': ['baseline', 'indexed_scan', 'candidate'],
                 'seed': 1}}),
        ]
        for index, value in cases:
            with self.subTest(script=index):
                source.write_text(json.dumps(value))
                before = source.read_bytes()
                self.assert_invalid(source, name='aggregate-' + str(index), indexes=[index])
                self.assertEqual(source.read_bytes(), before)

    def test_regular_invalid_inputs_are_readonly_and_structured(self):
        source = self.root / 'config.json'
        payloads = {
            'utf16': '{}'.encode('utf-16'),
            'duplicate': b'{"x":1,"x":2}',
            'overflow': b'{"x":1e400}',
            'deep': ('{"x":' + '[' * 300 + '0' + ']' * 300 + '}').encode(),
            'oversized': b' ' * (2 * 1024 * 1024 + 1),
            'top-list': b'[]',
            'null': b'null',
            'empty-object': b'{}',
            'wrong-nested': b'{"baseline":[],"baseline_revision":[],"scope":"x","matrix":[]}',
        }
        for name, raw in payloads.items():
            source.write_bytes(raw)
            before = source.read_bytes()
            self.assert_invalid(source, name=name)
            self.assertEqual(source.read_bytes(), before)

    def test_fifo_directory_and_final_symlink_do_not_block_or_write(self):
        source = self.root / 'special-input'
        target = self.root / 'target.json'
        target.write_text('{}')
        kinds = ['directory', 'symlink'] + (['fifo'] if hasattr(os, 'mkfifo') else [])
        for kind in kinds:
            with self.subTest(kind=kind):
                if source.exists() or source.is_symlink():
                    if source.is_dir() and not source.is_symlink():
                        source.rmdir()
                    else:
                        source.unlink()
                if kind == 'directory':
                    source.mkdir()
                elif kind == 'symlink':
                    source.symlink_to(target)
                else:
                    os.mkfifo(source)
                self.assert_invalid(source, name=kind)
                if source.is_dir() and not source.is_symlink():
                    source.rmdir()
                else:
                    source.unlink()


if __name__ == '__main__':
    unittest.main()
