"""Actual result ranking must work on every supported Python interpreter."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from agent_runtime.result_store import ResultStore


class ResultSearchCompatTests(unittest.TestCase):
    def test_bounded_order_matches_full_sort_with_ties(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / 'evidence.txt'
            evidence.write_bytes(b'fixed historical evidence')
            ref = {'path': 'evidence.txt', 'sha256': hashlib.sha256(evidence.read_bytes()).hexdigest()}
            store = ResultStore(root)
            expected = []
            for n in reversed(range(25)):
                run_id = 'run-%02d' % n
                summary = 'alpha beta' if n % 3 == 0 else 'alpha' if n % 3 == 1 else 'unrelated'
                store.register_history(run_id, summary, [ref])
                if n % 3 != 2:
                    expected.append((2 if n % 3 == 0 else 1, run_id))
            result = store.search('alpha beta', limit=7)
            self.assertEqual(result['errors'], [])
            self.assertEqual(result['status'], 'candidates')
            self.assertTrue(result['partial'])
            self.assertEqual([(hit['score'], hit['run_id']) for hit in result['results']],
                             sorted(expected, key=lambda item: (-item[0], item[1]))[:7])
            empty = store.search('absent-query')
            self.assertEqual(empty['results'], [])
            self.assertEqual(empty['errors'], [])
            self.assertEqual(empty['status'], 'no_hits')
