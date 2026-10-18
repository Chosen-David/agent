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
from agent_runtime.project_docs import snapshot_project_docs


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

    def bind_documents(self, canonical=False):
        if canonical:
            index = self.root / 'agent_doc/task/TASK.md'
            detail = self.root / 'agent_doc/task/task_details/T1.md'
            detail.parent.mkdir(parents=True)
            index.write_text('# Tasks\n\n## 2026-10-18\n\n'
                             '- [ ] [T1] Work ([details](task_details/T1.md))\n')
            detail.write_text('# T1\n\nTask-ID: T1\nDate: 2026-10-18\n\n'
                              '## Plan\n\nOriginal requirement.\n\n## Progress\n')
            self.task['task_refs'] = ['T1']
        else:
            index = self.root / 'TASK.md'
            index.write_text('- [ ] [T1] Original requirement\n')
            detail = None
        self.task['document_refs'] = snapshot_project_docs(self.root)
        return index, detail

    def test_legacy_task_changed_during_current_callback(self):
        index, _ = self.bind_documents()
        self.run_after_change(lambda: index.write_text('- [ ] [T1] Changed requirement\n'),
                              'current')

    def test_legacy_task_deleted_during_current_callback(self):
        index, _ = self.bind_documents()
        self.run_after_change(index.unlink, 'current')

    def test_canonical_index_changed_during_current_callback(self):
        index, _ = self.bind_documents(canonical=True)
        self.run_after_change(lambda: index.write_text(index.read_text().replace('Work', 'New work')),
                              'current')

    def test_canonical_plan_changed_during_current_callback(self):
        _, detail = self.bind_documents(canonical=True)
        self.run_after_change(lambda: detail.write_text(detail.read_text().replace('Original', 'New')),
                              'current')

    def test_progress_append_during_current_callback_remains_allowed(self):
        _, detail = self.bind_documents(canonical=True)

        class Context:
            def current(self):
                with detail.open('a') as stream:
                    stream.write('\nObserved progress only.\n')
                return True

        outcome = self.wrapper.run(self.task, Context())
        self.assertEqual(outcome.status, 'pending')
        self.assertEqual(self.base.calls, 1)

    def assert_unchanged_documents_complete(self, canonical):
        self.bind_documents(canonical=canonical)
        self.base.status = 'complete'
        outcome = self.wrapper.run(self.task, None)
        self.assertEqual(outcome.status, 'complete')
        self.assertEqual(self.base.calls, 1)
        self.assertTrue(self.wrapper.verify(self.task, outcome.evidence))

    def test_unchanged_legacy_documents_complete_and_verify(self):
        self.assert_unchanged_documents_complete(False)

    def test_unchanged_canonical_documents_complete_and_verify(self):
        self.assert_unchanged_documents_complete(True)

    def test_cached_lookup_still_rechecks_documents_after_current(self):
        index, _ = self.bind_documents()
        outcome = self.wrapper.run(self.task, None)
        self.assertEqual(outcome.status, 'pending')
        self.assertEqual(self.base.calls, 1)
        self.base.calls = 0
        with patch.object(task_manifest, '_prior_result_search',
                          side_effect=AssertionError('cached lookup must not rerun')):
            self.run_after_change(lambda: index.write_text('- [ ] [T1] Changed requirement\n'),
                                  'current')


if __name__ == '__main__':
    unittest.main()
