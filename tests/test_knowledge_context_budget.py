"""Complete bundles that cannot fit need not be materialized."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.knowledge import KnowledgeStore

ROOT = Path(__file__).resolve().parents[1]


def corpus(root, count=21, shape='chain'):
    entries = root / 'entries'
    entries.mkdir(parents=True)
    template = json.loads((ROOT/'knowledge/entries/math.cauchy-schwarz.json').read_text())
    for i in range(count):
        deps = ([i-1] if i else []) if shape == 'chain' else (list(range(i)) if i == count-1 else [])
        data = dict(template, id=f'test.node-{i:04d}', title=f'Node {i}',
                    requires=[{'id': f'test.node-{j:04d}', 'version': 1} for j in deps], relations=[])
        (entries/f"{data['id']}.json").write_text(json.dumps(data))
        (entries/f"{data['id']}.md").write_text('Synthetic complete prerequisite bundle.\n')


def hits(store, *ids):
    return {'snapshot': store.snapshot, 'backend': 'files-lexical-v1',
            'results': [{'id': kid} for kid in ids]}


class ContextBudgetTests(unittest.TestCase):
    def test_rejected_bundle_only_loads_seed_and_later_seed_can_fit(self):
        for shape in ('chain', 'fanout'):
            with self.subTest(shape=shape), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                corpus(root, shape=shape)
                store = KnowledgeStore(root)
                with patch.object(store, 'get', wraps=store.get) as get:
                    packet = store.context(hits(store, 'test.node-0020', 'test.node-0000'),
                                           max_entries=20, include_related=False)
                self.assertEqual(get.call_count, 3)  # rejected seed; fitting seed; its payload
                self.assertEqual([d['id'] for d in packet['entries']], ['test.node-0000'])
                self.assertEqual(packet['skipped'], [{'id': 'test.node-0020',
                    'reason': 'complete prerequisite bundle exceeds context budget',
                    'selection_reason': 'retrieved'}])
                self.assertTrue(store.check_refs(packet['knowledge_refs'])['valid'])

    def test_exact_count_boundary_and_character_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus(root, 20)
            store = KnowledgeStore(root)
            request = hits(store, 'test.node-0019')
            accepted = store.context(request, max_entries=20, max_chars=200000, include_related=False)
            self.assertEqual(len(accepted['entries']), 20)
            self.assertEqual(accepted['status'], 'ready')
            cost = accepted['budget']['used_chars']
            exact = store.context(request, max_entries=20, max_chars=cost, include_related=False)
            self.assertEqual(len(exact['entries']), 20)
            short = store.context(request, max_entries=20, max_chars=cost-1, include_related=False)
            self.assertEqual(short['entries'], [])
            for entry_budget, char_budget in ((19, 200000), (20, 1)):
                packet = store.context(request, max_entries=entry_budget,
                                       max_chars=char_budget, include_related=False)
                self.assertEqual(packet['status'], 'partial')
                self.assertEqual(packet['entries'], [])
                self.assertEqual(packet['budget']['used_chars'], 0)

    def test_already_selected_dependencies_not_double_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus(root, 20)
            store = KnowledgeStore(root)
            packet = store.context(hits(store, 'test.node-0009', 'test.node-0019', 'test.node-0019'),
                                   max_entries=20, max_chars=200000, include_related=False)
            self.assertEqual(len(packet['entries']), 20)
            self.assertEqual(packet['skipped'], [])

    def test_duplicate_skipped_seeds_remain_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus(root, 21)
            store = KnowledgeStore(root)
            packet = store.context(hits(store, 'test.node-0020', 'test.node-0020'),
                                   max_entries=20, include_related=False)
            self.assertEqual(len(packet['skipped']), 2)
            self.assertEqual(packet['skipped'][0], packet['skipped'][1])


if __name__ == '__main__':
    unittest.main()
