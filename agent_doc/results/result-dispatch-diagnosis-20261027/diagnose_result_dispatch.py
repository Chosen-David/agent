"""Negative correctness diagnosis; not production or test-discovery code."""
from pathlib import Path
import sys
repository = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(repository), str(repository / 'tests')]
sys.argv = [sys.argv[0], '-v']
import json
import tempfile
import unittest
from unittest.mock import patch
from agent_runtime import task_manifest
from agent_runtime.core import Outcome
from agent_runtime.result_validation import inspect_result
from test_result_validation import make_fixture, independent_verify


class ResultDispatchDiagnosis(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        contract = make_fixture(self.root)
        self.assertEqual(inspect_result(self.root, contract, independent_verify)['status'],
                         'usable-with-scope')
        self.task = {'task_id': 'consume', 'required_result_refs': [contract]}

        class Handler:
            calls = 0
            idempotent = True
            required_capabilities = ()

            def run(self, task, context):
                self.calls += 1
                return Outcome('pending', 'work already started', [])

        self.handler = Handler()
        self.wrapper = task_manifest.ReportingHandler(self.handler, self.root, independent_verify)

    def corrupt_result(self):
        p = self.root / 'raw.json'
        p.write_bytes(p.read_bytes() + b'\n')

    def assert_blocked_before_work(self, outcome):
        print(json.dumps({'case': self.id(), 'status': outcome.status,
                          'reason': outcome.reason, 'handler_calls': self.handler.calls}), flush=True)
        self.assertEqual(outcome.status, 'blocked')
        self.assertEqual(self.handler.calls, 0, 'post-work rejection cannot undo handler work')

    def test_result_changed_during_real_lookup_blocks_before_work(self):
        original = task_manifest._prior_result_search
        events = []

        def lookup(*args, **kwargs):
            value = original(*args, **kwargs)
            self.corrupt_result()
            events.append('lookup-result-changed')
            return value

        with patch.object(task_manifest, '_prior_result_search', side_effect=lookup):
            outcome = self.wrapper.run(self.task, None)
        self.assertEqual(events, ['lookup-result-changed'])
        self.assertIn('post-action document/result reconciliation', outcome.reason)
        self.assert_blocked_before_work(outcome)

    def test_result_changed_during_current_blocks_before_work(self):
        owner = self
        events = []

        class Context:
            def current(self):
                owner.corrupt_result()
                events.append('current-result-changed')
                return True

        outcome = self.wrapper.run(self.task, Context())
        self.assertEqual(events, ['current-result-changed'])
        self.assertIn('post-action document/result reconciliation', outcome.reason)
        self.assert_blocked_before_work(outcome)

    def test_unchanged_result_allows_one_pending_handler(self):
        outcome = self.wrapper.run(self.task, None)
        self.assertEqual((outcome.status, self.handler.calls), ('pending', 1))

    def test_noncurrent_claim_blocks_handler(self):
        class Context:
            def current(self):
                return False

        outcome = self.wrapper.run(self.task, Context())
        self.assert_blocked_before_work(outcome)
        self.assertIn('claim no longer current', outcome.reason)


if __name__ == '__main__':
    unittest.main()
