"""Stored JSON depth failures are local to a record, not the entire search."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.result_store import METADATA_LIMIT, ResultStore, SCHEMA


class ResultSearchDepthTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='result-depth-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.store = ResultStore(self.root)

    def write(self, run_id, data):
        path = self.root / 'agent_doc/results' / run_id / 'record.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def good(self, run_id='good'):
        return self.write(run_id, json.dumps({
            'schema_version': SCHEMA, 'run_id': run_id,
            'origin': 'historical-external-reference', 'summary': 'needle',
            'registered_at': '2026-10-20T00:00:00+00:00', 'context': {},
            'validation_at_registration': {'status': 'unknown'},
        }).encode())

    def deep(self, kind='list', run_id='bad'):
        # CPython's C JSON decoder limit can exceed getrecursionlimit().
        depth = 10000
        left, right = ('[', ']') if kind == 'list' else ('{"x":', '}')
        data = ('{"payload":' + left * depth + '0' + right * depth + '}').encode()
        self.assertLess(len(data), METADATA_LIMIT)
        return self.write(run_id, data)

    def assert_isolated(self, result, bad, expected):
        self.assertEqual([hit['run_id'] for hit in result['results']], expected)
        self.assertEqual([error['run_id'] for error in result['errors']], bad)
        self.assertTrue(all('recursion' in error['error'].lower() for error in result['errors']))
        self.assertEqual(result['status'], 'candidates' if expected else 'incomplete')
        self.assertTrue(all(hit['applicability'] == 'unchecked' for hit in result['results']))

    def test_deep_records_do_not_hide_good_neighbor_or_modify_files(self):
        paths = [self.deep('list', 'a-bad'), self.good('middle'), self.deep('dict', 'z-bad')]
        before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
        self.assert_isolated(self.store.search('needle'), ['a-bad', 'z-bad'], ['middle'])
        self.assert_isolated(self.store.search('unmatched'), ['a-bad', 'z-bad'], [])
        self.assertEqual(before, [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths])

    def test_only_deep_records_are_incomplete_not_no_hits(self):
        self.deep()
        self.assert_isolated(self.store.search('needle'), ['bad'], [])

    def test_cli_returns_structured_results_with_deep_record(self):
        self.good()
        self.deep('dict')
        script = Path(__file__).resolve().parents[1] / 'scripts/result_store.py'
        for flags in ([], ['-O']):
            with self.subTest(flags=flags):
                result = subprocess.run([sys.executable, *flags, str(script), '--root', str(self.root),
                                         'search', 'needle'], capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assert_isolated(json.loads(result.stdout), ['bad'], ['good'])

    def test_direct_show_still_raises_recursion_error(self):
        path = self.deep()
        with self.assertRaises(RecursionError) as original:
            json.loads(path.read_bytes())
        with self.assertRaises(RecursionError) as caught:
            self.store.show('bad')
        self.assertEqual(str(caught.exception), str(original.exception))
        self.assertIsInstance(caught.exception.__cause__, RecursionError)
        self.assertEqual(str(caught.exception.__cause__), str(original.exception))

    def test_invalid_caller_context_is_not_a_record_error(self):
        nested = 0
        for _ in range(10000):
            nested = [nested]
        with self.assertRaises(RecursionError):
            self.store.search('needle', context={'artifacts': {'deep': nested}})

    def test_custom_show_recursion_error_is_not_swallowed(self):
        self.good()
        error = RecursionError('custom show failure')
        with patch.object(self.store, 'show', side_effect=error):
            with self.assertRaises(RecursionError) as caught:
                self.store.search('needle')
        self.assertIs(caught.exception, error)

    def test_unrelated_errors_are_not_swallowed(self):
        self.good()
        for error in (RuntimeError('unexpected'), SystemExit(7)):
            with self.subTest(error=type(error).__name__):
                with patch.object(self.store, 'show', side_effect=error):
                    with self.assertRaises(type(error)) as caught:
                        self.store.search('needle')
                self.assertIs(caught.exception, error)


if __name__ == '__main__':
    unittest.main()
