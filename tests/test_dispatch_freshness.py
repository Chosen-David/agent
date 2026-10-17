"""Declared dependencies invalidated by pre-dispatch callbacks must block work."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime import task_manifest
from agent_runtime.core import Outcome
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.project_memory import MemoryLedger


class DispatchFreshnessTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.task = {'task_id': 'T1', 'report_path': 'report.json'}
        (self.root / 'report.json').write_text(json.dumps({
            'task_id': 'T1', 'summary': 'synthetic fixture',
            'data': [{'kind': 'synthetic', 'description': 'test only'}]}))

        class Handler:
            idempotent = True
            required_capabilities = ()
            calls = 0
            status = 'pending'

            def run(self, task, context):
                self.calls += 1
                return Outcome(self.status, 'fixture', [{'fixture': True}])

            def verify(self, task, evidence):
                return evidence == [{'fixture': True}]

        self.base = Handler()
        self.wrapper = task_manifest.ReportingHandler(self.base, self.root)

    def memory_change(self):
        ledger = MemoryLedger(self.root, create=True)
        ledger.add('intent-v1', 'intention', 'old intent', 'user:1',
                   evidence='user_confirmed')
        self.task['memory_refs'] = ['intent-v1']
        return lambda: ledger.correct('intent-v1', 'intent-v2', 'new intent',
                                      'user:2', 'user correction')

    def knowledge_change(self):
        corpus = self.root / 'knowledge'
        shutil.copytree(Path(__file__).resolve().parents[1] / 'knowledge', corpus)
        self.task['knowledge_refs'] = KnowledgeStore(corpus).get('math.topk-margin')['knowledge_refs']
        path = corpus / 'entries/math.topk-margin.md'
        return lambda: path.write_text(path.read_text() + '\nChanged premise.\n')

    def run_after_change(self, change, boundary):
        calls = []

        def invalidate():
            calls.append(boundary)
            change()

        if boundary == 'lookup':
            original = task_manifest._prior_result_search

            def lookup(*args, **kwargs):
                result = original(*args, **kwargs)
                invalidate()
                return result

            with patch.object(task_manifest, '_prior_result_search', side_effect=lookup):
                outcome = self.wrapper.run(self.task, None)
        else:
            class Context:
                def current(self):
                    invalidate()
                    return True

            outcome = self.wrapper.run(self.task, Context())
        self.assertEqual(calls, [boundary])
        self.assertEqual(self.base.calls, 0, 'invalidated inputs must block before handler work')
        self.assertEqual(outcome.status, 'blocked')
        self.assertIn('reconciliation', outcome.reason)

    def test_memory_corrected_during_lookup(self):
        self.run_after_change(self.memory_change(), 'lookup')

    def test_memory_corrected_during_current_callback(self):
        self.run_after_change(self.memory_change(), 'current')

    def test_knowledge_changed_during_lookup(self):
        self.run_after_change(self.knowledge_change(), 'lookup')

    def test_knowledge_changed_during_current_callback(self):
        self.run_after_change(self.knowledge_change(), 'current')

    def test_current_false_retains_claim_gate(self):
        class Context:
            def current(self):
                return False

        outcome = self.wrapper.run(self.task, Context())
        self.assertEqual(outcome.status, 'blocked')
        self.assertIn('claim no longer current', outcome.reason)
        self.assertEqual(self.base.calls, 0)

    def test_unchanged_memory_complete_and_verify(self):
        self.memory_change()  # Register an active reference without correcting it.
        self.base.status = 'complete'
        outcome = self.wrapper.run(self.task, None)
        self.assertEqual(outcome.status, 'complete')
        self.assertEqual(self.base.calls, 1)
        self.assertTrue(self.wrapper.verify(self.task, outcome.evidence))

    def test_empty_refs_do_not_require_stores(self):
        self.task.update(memory_refs=[], knowledge_refs=[])
        outcome = self.wrapper.run(self.task, None)
        self.assertEqual(outcome.status, 'pending')
        self.assertEqual(self.base.calls, 1)
        self.assertFalse((self.root / '.agent-memory').exists())


if __name__ == '__main__':
    unittest.main()
