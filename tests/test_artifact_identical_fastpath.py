"""Identical content skips matching without changing transport or validation."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_runtime.artifact_context import compare_artifacts, restore_comparison


class IdenticalFastpathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def save(self, name, text):
        data = text.encode()
        (self.root / name).write_bytes(data)
        return {'path': name, 'sha256': hashlib.sha256(data).hexdigest()}

    def test_identical_bypasses_matcher_for_all_selection_modes(self):
        for text in ('', 'unchanged\n' * 2048, '取消\r\n预算保持\n'):
            a = self.save('a', text)
            b = self.save('b', text)
            for reuse in (False, True):
                for counter in (None, lambda wire: len(wire)):
                    with patch('agent_runtime.artifact_context.SequenceMatcher',
                               side_effect=AssertionError('redundant matching')):
                        result = compare_artifacts(self.root, a, b, multi_edit=True,
                                                   reuse_identical=reuse,
                                                   token_counter=counter, max_chars=200000)
                    self.assertEqual(restore_comparison(self.root, result, a, b),
                                     (text, text))

    def test_changed_content_still_uses_matcher(self):
        from difflib import SequenceMatcher
        a = self.save('a', 'original\n' * 10)
        b = self.save('b', 'changed\n' + 'original\n' * 9)
        with patch('agent_runtime.artifact_context.SequenceMatcher',
                   wraps=SequenceMatcher) as matcher:
            result = compare_artifacts(self.root, a, b, multi_edit=True)
        matcher.assert_called_once()
        self.assertEqual(restore_comparison(self.root, result, a, b),
                         ('original\n' * 10, 'changed\n' + 'original\n' * 9))

    def test_equal_expected_hashes_do_not_bypass_current_source_read(self):
        a = self.save('a', 'unchanged\n')
        b = self.save('b', 'unchanged\n')
        (self.root / 'b').write_text('mutated\n')
        with self.assertRaisesRegex(ValueError, 'stale'):
            compare_artifacts(self.root, a, b, multi_edit=True, reuse_identical=True)


if __name__ == '__main__':
    unittest.main()
