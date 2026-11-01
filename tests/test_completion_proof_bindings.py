"""Late result callbacks must not invalidate previously accepted proof bindings."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from agent_runtime.core import ArtifactHandler
from agent_runtime.result_store import ResultStore, result_context
from agent_runtime.task_manifest import ReportingHandler, atomic_json, result_report
from tests.test_result_validation import make_fixture, independent_verify, ref


class CompletionProofTests(unittest.TestCase):
    def fixture(self, mode):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        root = Path(temporary.name).resolve()
        first = make_fixture(root)
        second = dict(first, result_id='cpu-result-2', manifest_path='manifest-2.json')
        manifest = json.loads((root / 'manifest.json').read_bytes())
        second_manifest = dict(manifest, result_id=second['result_id'])
        atomic_json(root / second['manifest_path'], second_manifest)
        note = root / 'earlier-review.txt'; note.write_bytes(b'original reviewer observation')
        artifact = root / 'completion.txt'; artifact.write_bytes(b'completed fixture')
        task = dict(task_id='consume', report_path='completion-report.json',
            required_result_refs=[first, second], done_when={'artifacts': [
                dict(path=artifact.name, sha256=hashlib.sha256(artifact.read_bytes()).hexdigest())]})
        if mode == 'reuse':
            registered = ResultStore(root).register(first, historical=True)
            task['required_result_refs'] = [second]
            task['result_reuse'] = dict(run_id=manifest['run_id'],
                record_sha256=registered['record_ref']['sha256'], query='square sums',
                context=result_context(manifest), explicit_reproduction=False, new_claim=False)
        atomic_json(root / task['report_path'], dict(task_id='consume', summary='fixture completion',
            data=[dict(kind='synthetic', description='Bounded arithmetic correctness fixture')]))
        original_report = (root / task['report_path']).read_bytes()
        original_artifact = artifact.read_bytes()
        state = dict(armed=mode == 'report', calls=0, changes=0, verified=0)
        earlier_id = second['result_id'] if mode == 'reuse' else first['result_id']
        later_id = first['result_id'] if mode == 'reuse' else second['result_id']
        def verifier(root, manifest, plan):
            state['calls'] += 1
            review = independent_verify(root, manifest, plan)
            source = first if manifest['result_id'] == first['result_id'] else second
            review['manifest_sha256'] = ref(root, source['manifest_path'])['sha256']
            if manifest['result_id'] == earlier_id:
                review['checks']['implementation']['evidence'].append(ref(root, note.name))
            if state['armed'] and not state['changes'] and manifest['result_id'] == later_id:
                target = root / 'unreferenced.txt' if mode == 'unrelated' else note
                if mode != 'unchanged': target.write_bytes(b'corrected reviewer observation')
                state['changes'] += 1
            return review
        class Child(ArtifactHandler):
            def verify(self, task, evidence):
                accepted = super().verify(task, evidence)
                state['verified'] += 1; state['armed'] = True
                return accepted
        child = Child(root)
        wrapper = ReportingHandler(child, root, verifier)
        def unchanged_bytes():
            self.assertEqual((root / task['report_path']).read_bytes(), original_report)
            self.assertEqual(artifact.read_bytes(), original_artifact)
        return root, task, verifier, child, wrapper, state, note, unchanged_bytes

    def test_report_rejects_proof_invalidated_by_later_result_callback(self):
        root, task, verifier, _, _, state, note, unchanged = self.fixture('report')
        try:
            with self.assertRaisesRegex(ValueError, r'^stale artifact: earlier-review\.txt$'):
                result_report(root, task, verifier)
        finally:
            self.assertEqual((state['calls'], state['changes']), (2, 1))
            self.assertEqual(note.read_bytes(), b'corrected reviewer observation')
            unchanged()

    def completion(self, mode):
        root, task, verifier, child, wrapper, state, note, unchanged = self.fixture(mode)
        evidence = child.run(task, None).evidence
        _, proof = result_report(root, task, verifier)
        accepted = wrapper.verify(task, evidence + [dict(task_report=proof)])
        self.assertEqual((state['calls'], state['changes'], state['verified']), (6, 1, 1))
        if mode in ('required', 'reuse'):
            self.assertEqual(note.read_bytes(), b'corrected reviewer observation')
        else:
            self.assertEqual(note.read_bytes(), b'original reviewer observation')
        unchanged()
        return accepted

    def test_completion_rejects_later_required_result_callback_change(self):
        self.assertFalse(self.completion('required'))

    def test_completion_rejects_later_reuse_callback_change(self):
        self.assertFalse(self.completion('reuse'))

    def test_unchanged_result_proofs_preserve_completion(self):
        self.assertTrue(self.completion('unchanged'))

    def test_unreferenced_correction_preserves_completion(self):
        self.assertTrue(self.completion('unrelated'))
