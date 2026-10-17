"""Independent dispatch boundary checks; temporary projects, no model service."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = next(parent for parent in Path(__file__).resolve().parents
            if (parent / 'agent_runtime/task_manifest.py').is_file())
sys.path.insert(0, str(ROOT))
from agent_runtime import task_manifest as tm
from agent_runtime.core import Outcome
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.project_memory import MemoryLedger


class ExtraChecks(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.task = {'task_id': 'extra', 'report_path': 'report.json'}
        (self.root / 'report.json').write_text(json.dumps({
            'task_id': 'extra', 'summary': 'independent synthetic fixture',
            'data': [{'kind': 'synthetic', 'description': 'boundary check'}]}))

        class Handler:
            idempotent = True
            required_capabilities = ()
            calls = 0
            status = 'pending'
            def run(self, task, context):
                self.calls += 1
                return Outcome(self.status, 'extra', [{'extra': True}])
            def verify(self, task, evidence):
                return evidence == [{'extra': True}]

        self.handler = Handler()
        self.wrapper = tm.ReportingHandler(self.handler, self.root)

    def memory(self):
        ledger = MemoryLedger(self.root, create=True)
        ledger.add('old', 'intention', 'old', 'owner:1', evidence='user_confirmed')
        self.task['memory_refs'] = ['old']
        return ledger

    @staticmethod
    def context(callback, current=True):
        class Context:
            idempotency_key = 'same-dispatch-key'
            def current(self):
                callback()
                return current
        return Context()

    def test_unchanged_knowledge_complete_and_verified_twice(self):
        corpus = self.root / 'knowledge'
        shutil.copytree(ROOT / 'knowledge', corpus)
        self.task['knowledge_refs'] = KnowledgeStore(corpus).get('math.topk-margin')['knowledge_refs']
        self.handler.status = 'complete'
        for _ in range(2):
            result = self.wrapper.run(self.task, self.context(lambda: None))
            self.assertEqual(result.status, 'complete')
            self.assertTrue(self.wrapper.verify(self.task, result.evidence))
        self.assertEqual(self.handler.calls, 2)

    def test_cached_lookup_does_not_bypass_later_current_correction(self):
        ledger = self.memory()
        original = tm._prior_result_search
        with patch.object(tm, '_prior_result_search', wraps=original) as lookup:
            result = self.wrapper.run(self.task, self.context(lambda: None))
            self.assertEqual(result.status, 'pending')
            def change():
                ledger.correct('old', 'new', 'new', 'owner:2', 'corrected')
            result = self.wrapper.run(self.task, self.context(change))
            self.assertEqual(lookup.call_count, 1)
        self.assertEqual(self.handler.calls, 1)
        self.assertEqual(result.status, 'blocked')
        self.assertIn('pre-dispatch', result.reason)

    def test_memory_database_deleted_by_current_blocks_before_work(self):
        ledger = self.memory()
        result = self.wrapper.run(self.task, self.context(lambda: ledger.path.unlink()))
        self.assertEqual(result.status, 'blocked')
        self.assertIn('pre-dispatch', result.reason)
        self.assertEqual(self.handler.calls, 0)

    def test_current_false_retains_priority_even_after_correction(self):
        ledger = self.memory()
        def change():
            ledger.correct('old', 'new', 'new', 'owner:2', 'corrected')
        result = self.wrapper.run(self.task, self.context(change, current=False))
        self.assertEqual(result.status, 'blocked')
        self.assertEqual(result.reason, 'claim no longer current after prior-result lookup')
        self.assertEqual(self.handler.calls, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
