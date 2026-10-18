"""Empty lexical queries keep validation and avoid document tokenization."""
from pathlib import Path
import unittest
from unittest.mock import patch

from agent_runtime import knowledge

ROOT = Path(__file__).resolve().parents[1]


class EmptyQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = knowledge.KnowledgeStore(ROOT / 'knowledge')

    def test_empty_terms_skip_document_tokenization(self):
        for query in ('!!!', '🙂', 'Ω'):
            for options in ({}, {'limit': 20, 'include_unpublished': True},
                            {'domain': 'physics', 'structure': 'missing'}):
                with self.subTest(query=query, options=options):
                    with patch.object(knowledge, '_terms', wraps=knowledge._terms) as tokenize:
                        result = self.store.search(query, **options)
                    self.assertEqual(result, {
                        'schema_version': 1, 'snapshot': self.store.snapshot,
                        'backend': 'files-lexical-v1', 'applicability': 'unchecked',
                        'results': []})
                    self.assertEqual(tokenize.call_count, 1)
                    result['results'].append('mutated')
                    self.assertEqual(self.store.search(query)['results'], [])

    def test_validation_precedes_fast_return(self):
        for query in ('', ' ', None, [], '!' * 2001):
            with self.subTest(query=query), self.assertRaises(knowledge.KnowledgeError):
                self.store.search(query)
        for limit in (0, 21, True, None, 1.5):
            with self.subTest(limit=limit), self.assertRaises(knowledge.KnowledgeError):
                self.store.search('!!!', limit=limit)

    def test_nfkc_and_cjk_are_not_empty(self):
        for query in ('ｌｏｗ ｒａｎｋ', '量纲'):
            self.assertTrue(self.store.search(query)['results'])


if __name__ == '__main__':
    unittest.main()
