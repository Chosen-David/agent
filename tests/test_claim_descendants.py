"""Invalidation reachability, input ownership and legacy custom-type behavior."""
from copy import deepcopy
import unittest

from agent_runtime.handoff_basis import _claim_descendants


def legacy(graph, bad):
    while True:
        expanded = bad | {cid for cid, c in graph.items() if set(c['depends_on']) & bad}
        if expanded == bad:
            return bad
        bad = expanded


class DescendantTests(unittest.TestCase):
    def test_deep_closure_excludes_unrelated_component_and_keeps_inputs(self):
        graph = {str(i): {'depends_on': [str(i-1)] if i else []} for i in range(128)}
        graph.update({f'u{i}': {'depends_on': []} for i in range(128)})
        original = deepcopy(graph)
        seeds = {'0', '30'}
        self.assertEqual(_claim_descendants(graph, seeds), {str(i) for i in range(128)})
        self.assertEqual(seeds, {'0', '30'})
        self.assertEqual(graph, original)

    def test_size_boundaries_reverse_order_tuple_parents_and_dense(self):
        for n in (0, 8, 63, 64, 65, 128):
            for dense in (False, True):
                graph = {str(i): {'depends_on': tuple(str(j) for j in
                         (range(i) if dense else ([i-1] if i else [])))}
                         for i in reversed(range(n))}
                seeds = {'0'} if n else set()
                with self.subTest(n=n, dense=dense):
                    self.assertEqual(_claim_descendants(graph, seeds), set(graph))
                    self.assertEqual(seeds, {'0'} if n else set())

    def test_custom_dependency_container_retains_legacy_operation_trace(self):
        class Traced(list):
            def __iter__(self):
                calls.append('iter')
                return super().__iter__()

            def __len__(self):
                calls.append('len')
                return super().__len__()

        graph = {str(i): {'depends_on': [str(i-1)] if i else []} for i in range(65)}
        graph['50']['depends_on'] = Traced(['49'])
        calls = []
        expected = legacy(graph, {'0'})
        expected_calls = list(calls)
        calls.clear()
        self.assertEqual(_claim_descendants(graph, {'0'}), expected)
        self.assertEqual(calls, expected_calls)


if __name__ == '__main__':
    unittest.main()
