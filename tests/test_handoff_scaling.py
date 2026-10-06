"""Scaling regressions with an independent small-graph DFS oracle.
These program tests do not measure model success or certify scientific evidence.
"""
import copy
import hashlib
import importlib.util
import io
from pathlib import Path
import random
import tempfile
import tracemalloc
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('handoff_scaling', Path(__file__).resolve().parents[1] / 'scripts/validate_handoff.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def dfs_has_cycle(graph):
    # Different algorithm from production Kahn, only small generated graphs.
    gray, black = set(), set()
    def visit(node):
        if node in gray:
            return True
        if node in black:
            return False
        gray.add(node)
        for predecessor in graph[node]:
            if predecessor in graph and visit(predecessor):
                return True
        gray.remove(node)
        black.add(node)
        return False
    return any(visit(node) for node in graph)


class HandoffScalingTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / 'artifact').write_bytes(b'fixture')
        self.record = dict(schema_version=1, run_id='scale', role='code-organization',
                           input_version='fixed', status='completed', limitations=[],
                           artifacts=[dict(id='a', path='artifact', sha256=hashlib.sha256(b'fixture').hexdigest())],
                           checks=[dict(criterion='fixture', status='pass', artifact_ids=['a'])], tasks=[])

    def validate(self, graph):
        record = copy.deepcopy(self.record)
        record['tasks'] = [dict(task_id=node, status='done', evidence=['a'], depends_on=deps)
                           for node, deps in graph.items()]
        request = dict(schema_version=1, input_version='fixed', tasks=[dict(task_id=node) for node in graph])
        return M.validate(record, self.root, True, consumer_request=request)

    def test_random_graphs_against_independent_cycle_oracle(self):
        rng = random.Random(470381)
        cyclic = acyclic = 0
        for index in range(240):
            n = rng.randint(2, 28)
            nodes = [str(i) for i in range(n)]
            if index % 2:
                graph = {node: [dep for dep in nodes[:i] if rng.random() < .22]
                         for i, node in enumerate(nodes)}
            else:
                graph = {node: [dep for dep in nodes if rng.random() < .07] for node in nodes}
            # Edge multiplicity must not strand an otherwise removable node.
            for deps in graph.values():
                if deps and rng.random() < .5:
                    deps.extend(deps[:1] * 2)
            expected = dfs_has_cycle(graph)
            cyclic += expected
            acyclic += not expected
            with self.subTest(index=index):
                errors = self.validate(graph)
                self.assertEqual('task dependency cycle' in errors, expected)
                self.assertEqual(errors, ['task dependency cycle'] if expected else [])
        self.assertGreater(cyclic, 40)
        self.assertGreater(acyclic, 100)

    def test_unknown_and_duplicate_dependencies_keep_distinct_semantics(self):
        self.assertEqual(self.validate({'0': [], '1': ['0', '0', '0']}), [])
        self.assertEqual(self.validate({'0': ['absent', 'absent']}),
                         ['0: unknown dependency absent', '0: unknown dependency absent'])
        self.assertEqual(self.validate({'0': ['0', 'absent']}),
                         ['0: unknown dependency absent', 'task dependency cycle'])

    def test_long_chain_and_late_backedge_without_recursion(self):
        graph = {str(i): [str(i - 1)] if i else [] for i in range(10000)}
        self.assertEqual(self.validate(graph), [])
        graph['0'] = ['9999']
        self.assertEqual(self.validate(graph), ['task dependency cycle'])

    def test_stream_hash_empty_binary_and_chunk_boundaries(self):
        # hashlib over in-memory fixture is an independent digest oracle.
        rng = random.Random(92343)
        for size in (0, 1, 1024 * 1024 - 1, 1024 * 1024, 1024 * 1024 + 17, 3 * 1024 * 1024 + 9):
            with self.subTest(size=size):
                content = rng.randbytes(size)
                (self.root / 'artifact').write_bytes(content)
                record = copy.deepcopy(self.record)
                record['artifacts'][0]['sha256'] = hashlib.sha256(content).hexdigest()
                self.assertEqual(M.validate(record, self.root), [])
                record['artifacts'][0]['sha256'] = 'wrong'
                self.assertIn('artifact 0: sha256 mismatch', M.validate(record, self.root))

    def test_short_reads_continue_until_empty(self):
        class ShortReader(io.BytesIO):
            def read(self, size=-1):
                return super().read(min(size, 3))
        with patch.object(Path, 'open', return_value=ShortReader(b'fixture')) as opened:
            self.assertEqual(M.validate(self.record, self.root), [])
        opened.assert_called_once_with('rb')

    def test_midstream_read_error_rejected_and_file_closed(self):
        class FailingReader(io.BytesIO):
            def read(self, size=-1):
                if self.tell():
                    raise OSError('simulated I/O failure after successful read')
                return super().read(3)
        stream = FailingReader(b'fixture')
        with patch.object(Path, 'open', return_value=stream):
            self.assertIn('artifact 0: cannot read path (OSError)', M.validate(self.record, self.root))
        self.assertTrue(stream.closed)

    def test_large_file_python_allocation_is_bounded(self):
        # Start tracing after fixture generation; verifies validator allocation,
        # not process RSS. Threshold rejects former whole-file 8MiB loading.
        block = bytes(range(256)) * 4096
        digest = hashlib.sha256()
        with (self.root / 'artifact').open('wb') as stream:
            for _ in range(8):
                stream.write(block)
                digest.update(block)
        self.record['artifacts'][0]['sha256'] = digest.hexdigest()
        tracemalloc.start()
        try:
            errors = M.validate(self.record, self.root)
            peak = tracemalloc.get_traced_memory()[1]
        finally:
            tracemalloc.stop()
        self.assertEqual(errors, [])
        self.assertLess(peak, 3 * 1024 * 1024)

    def test_scope_and_dependency_state_still_rejected(self):
        record = copy.deepcopy(self.record)
        record['tasks'] = [dict(task_id='before', status='skipped', reason='producer wants skip'),
                           dict(task_id='after', status='done', evidence=['a'], depends_on=['before'])]
        request = dict(schema_version=1, input_version='fixed', tasks=[dict(task_id='before'), dict(task_id='after')])
        errors = M.validate(record, self.root, True, consumer_request=request)
        self.assertIn('before: skip not authorized by consumer', errors)
        self.assertIn('after: done before dependency before', errors)
        request['tasks'].append(dict(task_id='omitted'))
        self.assertIn('consumer task missing: omitted', M.validate(record, self.root, True, consumer_request=request))


if __name__ == '__main__':
    unittest.main()
