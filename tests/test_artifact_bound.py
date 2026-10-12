import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from difflib import SequenceMatcher
from agent_runtime.artifact_context import compare_artifacts, restore_comparison


class ArtifactBoundTests(unittest.TestCase):
    def test_repeated_multiline_deletion_skips_nonwinning_matcher(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            texts = ('x\n' * 2048, 'x\n' * 2046)
            refs = []
            for name, text in zip(('old', 'new'), texts):
                (root / name).write_text(text)
                refs.append({'path': name, 'sha256': hashlib.sha256(text.encode()).hexdigest()})
            with patch('agent_runtime.artifact_context.SequenceMatcher',
                       side_effect=AssertionError('dominated matcher')):
                packet = compare_artifacts(root, *refs, multi_edit=True, max_chars=100000)
            self.assertEqual(restore_comparison(root, packet, *refs), texts)
            # A custom counter can prefer an otherwise longer codec.
            with patch('agent_runtime.artifact_context.SequenceMatcher', wraps=SequenceMatcher) as matcher:
                counted = compare_artifacts(root, *refs, multi_edit=True, max_chars=100000,
                    token_counter=lambda wire: 0 if '"representation":"edits"' in wire else 1)
            matcher.assert_called_once()
            self.assertEqual(counted['after']['representation'], 'edits')
            self.assertEqual(restore_comparison(root, counted, *refs), texts)
