"""Independent callback-boundary probes; no guide files created or altered."""
from pathlib import Path
import tempfile
import unittest
from agent_runtime import task_manifest
from agent_runtime.core import Outcome
from agent_runtime.project_docs import snapshot_project_docs

class IndependentDocumentCases(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.index = self.root / 'TASK.md'
        self.index.write_text('- [ ] [R1] Initial task\n')
        self.task = {'task_id': 'R1'}
        class Counter:
            idempotent = True
            required_capabilities = ()
            calls = 0
            def run(counter, task, context):
                counter.calls += 1
                return Outcome('pending', 'independent counter')
        self.counter = Counter()
        self.wrapper = task_manifest.ReportingHandler(self.counter, self.root)

    def invoke(self, mutate, current=True):
        class Context:
            def current(context):
                mutate()
                return current
        return self.wrapper.run(self.task, Context())

    def test_false_current_keeps_priority_even_with_deleted_document(self):
        self.task['document_refs'] = snapshot_project_docs(self.root)
        result = self.invoke(self.index.unlink, False)
        self.assertEqual(self.counter.calls, 0)
        self.assertEqual(result.status, 'blocked')
        self.assertEqual(result.reason, 'claim no longer current after prior-result lookup')

    def test_legacy_file_without_declared_refs_keeps_compatibility(self):
        result = self.invoke(lambda: self.index.write_text('- [ ] [R1] Changed task\n'))
        self.assertEqual(result.status, 'pending')
        self.assertEqual(self.counter.calls, 1)

    def test_adopted_advice_change_stops_handler(self):
        advice = self.root / 'agent_doc/advice/proposal.md'
        advice.parent.mkdir(parents=True)
        advice.write_text('Accepted input v1\n')
        refs = snapshot_project_docs(self.root)
        refs['adopted_advice'] = dict(refs['advice'])
        self.task['document_refs'] = refs
        result = self.invoke(lambda: advice.write_text('Accepted input v2\n'))
        self.assertEqual(self.counter.calls, 0)
        self.assertEqual(result.status, 'blocked')
        self.assertIn('pre-dispatch', result.reason)
        self.assertIn('adopted_advice', result.reason)

    def test_unadopted_advice_change_remains_allowed(self):
        advice = self.root / 'agent_doc/advice/proposal.md'
        advice.parent.mkdir(parents=True)
        advice.write_text('Unadopted input v1\n')
        self.task['document_refs'] = snapshot_project_docs(self.root)
        result = self.invoke(lambda: advice.write_text('Unadopted input v2\n'))
        self.assertEqual(self.counter.calls, 1)
        self.assertEqual(result.status, 'pending')

    def test_canonical_detail_deleted_stops_handler(self):
        self.index.unlink()
        detail = self.root / 'agent_doc/task/task_details/R1.md'
        detail.parent.mkdir(parents=True)
        (detail.parent.parent / 'TASK.md').write_text('## 2026-10-18\n- [ ] [R1] Task ([detail](task_details/R1.md))\n')
        detail.write_text('Task-ID: R1\nDate: 2026-10-18\n\n## Plan\nInitial input\n\n## Progress\n')
        self.task.update(document_refs=snapshot_project_docs(self.root), task_refs=['R1'])
        result = self.invoke(detail.unlink)
        self.assertEqual(self.counter.calls, 0)
        self.assertEqual(result.status, 'blocked')
        self.assertIn('pre-dispatch', result.reason)
        self.assertIn('detail/index mismatch', result.reason)

    def test_bound_legacy_invalid_utf8_stops_handler(self):
        self.task['document_refs'] = snapshot_project_docs(self.root)
        result = self.invoke(lambda: self.index.write_bytes(b'\xff'))
        self.assertEqual(self.counter.calls, 0)
        self.assertEqual(result.status, 'blocked')
        self.assertIn('pre-dispatch', result.reason)
