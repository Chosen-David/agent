"""Content reuse preserves JSON normalization and mutable-value isolation."""
import copy
import json
from pathlib import Path
import unittest

from agent_runtime.knowledge import KnowledgeStore


class ContentCopyTests(unittest.TestCase):
    def setUp(self):
        self.store = KnowledgeStore(Path(__file__).resolve().parents[1] / 'knowledge')
        self.kid = 'math.cauchy-schwarz'

    def test_body_reused_and_metadata_isolated(self):
        original = self.store.records[self.kid]
        result = self.store.get(self.kid)
        self.assertIs(result['content'], original['content'])
        result['assumptions'].append('changed')
        self.assertNotIn('changed', original['assumptions'])

    def test_json_value_and_order(self):
        original = self.store.records[self.kid]
        class Text(str):
            pass
        for body in ('', '中文😀', '\ud800', '\ud83d\ude00', Text('custom')):
            for pos in (0, 3, len(original)):
                with self.subTest(body=repr(body), pos=pos):
                    pairs = [(k,copy.deepcopy(v)) for k,v in original.items() if k != 'content']
                    pairs.insert(pos, ('content',body))
                    record = dict(pairs)
                    record['extra'] = {4: (1,2)}
                    self.store.records[self.kid] = record
                    expected = json.loads(json.dumps(record))
                    result = self.store.get(self.kid)
                    result.pop('knowledge_refs')
                    self.assertEqual(result,expected)
                    self.assertEqual(list(result),list(expected))

    def test_unsupported_metadata_errors(self):
        record = self.store.records[self.kid]
        record['extra'] = object()
        with self.assertRaises(TypeError):
            self.store.get(self.kid)
        record['extra'] = record
        with self.assertRaises(ValueError):
            self.store.get(self.kid)

    def test_non_string_outer_key_fallback(self):
        record = self.store.records[self.kid]
        record[1] = 'numeric'
        record['1'] = 'string'
        expected = json.loads(json.dumps(record))
        result = self.store.get(self.kid)
        result.pop('knowledge_refs')
        self.assertEqual(result,expected)
        self.assertEqual(list(result),list(expected))


if __name__ == '__main__':
    unittest.main()
