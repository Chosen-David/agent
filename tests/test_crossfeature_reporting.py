"""Regression for a review-discovered case disappearing from the denominator."""
import importlib.util
from pathlib import Path
import unittest


class ReportingTests(unittest.TestCase):
    def test_unexpected_outcome_counts_as_failure(self):
        path = Path(__file__).resolve().parents[1] / 'evals/crossfeature/runtime_execute.py'
        spec = importlib.util.spec_from_file_location('crossfeature_runtime_report', path)
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        cases = [{'outcome': value} for value in ('pass', 'known_gap', 'unexpected_rejection', 'not_run')]
        actual = runner.summarize(cases)
        self.assertEqual(actual, {'pass': 1, 'fail': 1, 'not_run': 1, 'known_gap': 1})
        self.assertEqual(sum(actual.values()), len(cases))


if __name__ == '__main__':
    unittest.main()
