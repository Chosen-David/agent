"""Completion must not accept basis invalidated by a late verifier callback."""
import hashlib
import unittest
from agent_runtime.core import ArtifactHandler
from agent_runtime.project_memory import MemoryLedger, MemoryError
from agent_runtime.task_manifest import ReportingHandler, atomic_json, result_report
from tests.test_result_validation import make_fixture, independent_verify
from tests import test_handoff_basis as basis_fixture


class CompletionBasisTests(unittest.TestCase):
    def case(self, mutation):
        f = basis_fixture.BasisTests(); f.setUp(); self.addCleanup(f.doCleanups)
        root = f.root
        contract = make_fixture(root)
        artifact = root / 'completion.txt'; artifact.write_bytes(b'completed artifact')
        task = dict(task_id='consumer', report_path='completion-report.json',
            memory_refs=['derived-v1'], knowledge_root='corpus', knowledge_refs=f.refs,
            required_result_refs=[contract], done_when={'artifacts': [dict(path=artifact.name,
                sha256=hashlib.sha256(artifact.read_bytes()).hexdigest())]})
        atomic_json(root / task['report_path'], dict(task_id='consumer', summary='fixture completion',
            data=[dict(kind='synthetic', description='Finite arithmetic and current basis fixture')]))
        state = dict(after_child=False, callbacks=0, mutations=0, child_verifications=0)
        class Child(ArtifactHandler):
            def verify(self, task, evidence):
                value = super().verify(task, evidence)
                state['child_verifications'] += 1
                state['after_child'] = True
                return value
        def verifier(root, manifest, plan):
            state['callbacks'] += 1
            review = independent_verify(root, manifest, plan)
            if state['after_child'] and not state['mutations']:
                if mutation == 'root':
                    f.memory.correct('derived-v1', 'derived-v2', 'New conclusion', 'fixture:user', 'corrected')
                elif mutation == 'ancestor':
                    f.memory.correct('input-v1', 'input-v2', 'New input', 'fixture:user', 'corrected')
                elif mutation == 'knowledge':
                    path = root / 'corpus/entries/math.topk-margin.md'
                    path.write_bytes(path.read_bytes() + b'\nExplicit correction.\n')
                elif mutation == 'unrelated':
                    f.memory.add('unrelated-v1', 'claim', 'Not referenced', 'fixture', evidence='verified')
                    f.memory.correct('unrelated-v1', 'unrelated-v2', 'Corrected unrelated', 'fixture:user', 'corrected')
                elif mutation != 'none':
                    raise AssertionError('unknown fixture mode')
                state['mutations'] += 1
            return review
        child = Child(root)
        handler = ReportingHandler(child, root, verifier)
        original_artifact = artifact.read_bytes()
        original_report = (root / task['report_path']).read_bytes()
        evidence = child.run(task, None).evidence
        _, report_proof = result_report(root, task, verifier)
        accepted = handler.verify(task, evidence + [dict(task_report=report_proof)])
        self.assertEqual(state['callbacks'], 3)
        self.assertEqual(state['child_verifications'], 1)
        self.assertEqual(state['mutations'], 1)
        self.assertEqual(artifact.read_bytes(), original_artifact)
        self.assertEqual((root / task['report_path']).read_bytes(), original_report)
        if mutation in ('root', 'ancestor'):
            with self.assertRaises(MemoryError): MemoryLedger(root).check(['derived-v1'])
        return accepted

    def test_late_root_correction_rejects_old_completion(self):
        self.assertFalse(self.case('root'))

    def test_late_ancestor_correction_rejects_derived_completion(self):
        self.assertFalse(self.case('ancestor'))

    def test_late_knowledge_change_rejects_old_completion(self):
        self.assertFalse(self.case('knowledge'))

    def test_unchanged_basis_preserves_valid_completion(self):
        self.assertTrue(self.case('none'))

    def test_unrelated_correction_preserves_valid_completion(self):
        self.assertTrue(self.case('unrelated'))
