"""Navigation keeps exact selection without cloning unused record payloads."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.knowledge import KnowledgeStore
from tests.test_knowledge_context_budget import corpus, hits

ROOT = Path(__file__).resolve().parents[1]


class MetadataNavigationTests(unittest.TestCase):
    def test_related_does_not_serialize_payload(self):
        store = KnowledgeStore(ROOT / 'knowledge')
        expected = store.related('math.topk-margin')
        with patch('agent_runtime.knowledge.json.dumps', side_effect=AssertionError('payload copied')):
            self.assertEqual(store.related('math.topk-margin'), expected)

    def test_rejected_seed_does_not_serialize_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus(Path(tmp), 21)
            store = KnowledgeStore(tmp)
            request = hits(store, 'test.node-0020')
            with patch('agent_runtime.knowledge.json.dumps', side_effect=AssertionError('payload copied')):
                result = store.context(request, max_entries=20, include_related=False)
            self.assertEqual(result['entries'], [])
            self.assertEqual(len(result['skipped']), 1)

    def test_final_payload_remains_isolated(self):
        store = KnowledgeStore(ROOT / 'knowledge')
        request = hits(store, 'math.cauchy-schwarz')
        before = json.dumps(store.records, sort_keys=True)
        expected = store.context(request, include_related=False)
        actual = store.context(request, include_related=False)
        actual['entries'][0]['sources'][0]['url'] = 'changed'
        actual['entries'][0]['assumptions'].append('changed')
        self.assertEqual(json.dumps(store.records, sort_keys=True), before)
        self.assertEqual(store.context(request, include_related=False), expected)

    def test_custom_get_hook_remains_observable(self):
        store = KnowledgeStore(ROOT / 'knowledge')
        with patch.object(store, 'get', wraps=store.get) as get:
            store.related('math.cauchy-schwarz')
            get.assert_called_once_with('math.cauchy-schwarz')


if __name__ == '__main__':
    unittest.main()
