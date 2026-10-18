"""Exact excerpt ordering and no repeated per-section lexical tokenization."""
from collections import Counter
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime import knowledge_index as index
from agent_runtime.knowledge import _terms
from scripts.benchmark_knowledge_index import corpus, digest, snapshot


class ExcerptSelectionTests(unittest.TestCase):
    def search(self, content, query='memory retrieval', **kwargs):
        store = corpus(1)
        record = next(iter(store.records.values()))
        record.update(content=content, aliases=['zqxalias'], title='Fixture')
        record['sha256'] = digest(content)
        snapshot(store)
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'search.db'
            index.build_index(store, db)
            with patch.object(index, '_terms', wraps=_terms) as tokenize:
                result = index.indexed_search(store, db, query, **kwargs)
            calls = Counter(call.args[0] for call in tokenize.call_args_list)
        return record, result, calls

    def test_each_section_tokenized_once(self):
        record, result, calls = self.search('# One\nmemory retrieval uniquea\n# Two\nmemory uniqueb\n')
        self.assertEqual(len(result['results'][0]['sections']), 2)
        for node in index.sections(record):
            self.assertEqual(calls[node['text'] + ' ' + node['title']], 1)

    def test_exact_reference_with_ties_unicode_fences_and_lengths(self):
        rng = random.Random(22)
        cases = ['', 'memory', '# A\nother', '# ＭＥＭＯＲＹ\n量纲 单位\n',
                 'intro memory\n```md\n# hidden\n```\n# Tail\nretrieval\n',
                 '# Long\n' + 'memory ' * 512]
        for count in (1, 2, 3, 16, 256):
            cases.append(''.join(f'# Section {i}\n' + rng.choice(
                ['memory retrieval', 'memory', 'other', '量纲 单位']) + '\n' for i in range(count)))
        for content in cases:
            for query in ('memory retrieval', '量纲 单位', 'zqxalias', '!!!'):
                with self.subTest(length=len(content), query=query):
                    record, result, _ = self.search(content, query)
                    terms = _terms(query)
                    ranked = sorted(index.sections(record), key=lambda n: (
                        -len(terms & _terms(n['text'] + ' ' + n['title'])), n['start_line']))
                    expected = [{k: n[k] for k in ('node', 'title', 'start_line', 'end_line')}
                                | {'excerpt': n['text'][:900]} for n in ranked[:2]
                                if terms & _terms(n['text'] + ' ' + n['title'])]
                    if result['results']:
                        self.assertEqual(result['results'][0]['sections'], expected)
                    else:
                        self.assertEqual(expected, [])


if __name__ == '__main__':
    unittest.main()
