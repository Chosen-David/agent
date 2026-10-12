"""Localized one-line changes avoid a non-winning byte-only matcher call."""
import hashlib
import tempfile
import unittest
from difflib import SequenceMatcher
from pathlib import Path
from unittest.mock import patch

from agent_runtime.artifact_context import compare_artifacts, restore_comparison


class LocalizedDiffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def save(self, name, text):
        raw = text.encode()
        (self.root / name).write_bytes(raw)
        return {'path': name, 'sha256': hashlib.sha256(raw).hexdigest()}

    def test_unique_single_line_bypasses_matcher_in_byte_mode(self):
        edge = 'same recurring status line\n'
        before = edge * 1024 + 'Status: old\n' + edge * 1023
        after = edge * 1024 + 'Status: new\n' + edge * 1023
        refs = self.save('old', before), self.save('new', after)
        with patch('agent_runtime.artifact_context.SequenceMatcher',
                   side_effect=AssertionError('non-winning matcher call')):
            value = compare_artifacts(self.root, *refs, multi_edit=True,
                                      max_chars=200000)
        self.assertEqual(value['after']['representation'], 'splice')
        self.assertEqual(restore_comparison(self.root, value, *refs),
                         (before, after))

    def test_token_counter_keeps_complete_codec_set(self):
        before = 'same\n' * 100 + 'Status: old\n' + 'same\n' * 100
        after = 'same\n' * 100 + 'Status: new\n' + 'same\n' * 100
        refs = self.save('old', before), self.save('new', after)
        with patch('agent_runtime.artifact_context.SequenceMatcher',
                   wraps=SequenceMatcher) as matcher:
            value = compare_artifacts(self.root, *refs, multi_edit=True,
                                      token_counter=lambda wire: len(wire),
                                      max_chars=200000)
        matcher.assert_called_once()
        self.assertEqual(restore_comparison(self.root, value, *refs),
                         (before, after))

    def test_disabled_or_full_modes_do_not_probe_fast_path(self):
        before = 'same\n' * 20 + 'Status: old\n'
        after = 'same\n' * 20 + 'Status: new\n'
        refs = self.save('old', before), self.save('new', after)
        with patch('agent_runtime.artifact_context._unique_single_splice',
                   side_effect=AssertionError('irrelevant fast-path probe')):
            for kwargs in ({}, {'full': True, 'multi_edit': True}):
                value = compare_artifacts(self.root, *refs, **kwargs)
                self.assertEqual(restore_comparison(self.root, value, *refs),
                                 (before, after))

    def test_nonunique_change_keeps_original_matcher(self):
        prefix = ''.join(f'prefix {i}\r\n' for i in range(50))
        suffix = ''.join(f'suffix {i}\n' for i in range(50))
        before = prefix + 'old one\nold two\n' + suffix
        # Keep the insert above the serialized-size lower-bound fast path,
        # so this fixture still verifies the necessary matcher fallback.
        after = prefix + 'new one with a longer payload\nnew two with a longer payload\n' + suffix
        refs = self.save('old', before), self.save('new', after)
        with patch('agent_runtime.artifact_context.SequenceMatcher',
                   wraps=SequenceMatcher) as matcher:
            value = compare_artifacts(self.root, *refs, multi_edit=True,
                                      max_chars=200000)
        matcher.assert_called_once()
        self.assertEqual(restore_comparison(self.root, value, *refs),
                         (before, after))

    def test_insert_delete_and_crlf_boundaries(self):
        pairs = [
            ('head\r\n' * 40 + 'tail\n' * 40,
             'head\r\n' * 40 + 'inserted\r\n' + 'tail\n' * 40),
            ('head\r\n' * 40 + 'deleted\r\n' + 'tail\n' * 40,
             'head\r\n' * 40 + 'tail\n' * 40),
            ('same\n' * 40 + '甲\r\n乙\n' + 'same\n' * 40,
             'same\n' * 40 + '龙\r\n' + 'same\n' * 40),
        ]
        for index, (before, after) in enumerate(pairs):
            refs = self.save(f'old-{index}', before), self.save(f'new-{index}', after)
            value = compare_artifacts(self.root, *refs, multi_edit=True,
                                      max_chars=200000)
            self.assertEqual(restore_comparison(self.root, value, *refs),
                             (before, after))


if __name__ == '__main__':
    unittest.main()
