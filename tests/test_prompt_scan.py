"""Exact line-start semantics, including non-LF Unicode separators."""
import itertools
import unittest
from agent_runtime import prompt_context as pc


class PromptScanTests(unittest.TestCase):
    def test_marker_positions_match_original_predicate(self):
        separators = ('', '\n', '\r', '\r\n', '\x85', '\u2028', '\u2029', '\0', '🙂', ' ')
        for prefix, middle in itertools.product(separators, repeat=2):
            text = prefix + pc.MARKER + middle + pc.MARKER + '\n```\n'
            expected = [i for i in range(len(text)) if text.startswith(pc.MARKER, i)
                        and (i == 0 or text[i - 1] == '\n')]
            actual = list(pc.re.finditer('^' + pc.re.escape(pc.MARKER), text, pc.re.MULTILINE))
            self.assertEqual([m.start() for m in actual], expected)

    def test_scope_boundaries(self):
        for newline in ('\n', '\r\n'):
            text = '```text' + newline + pc.MARKER + '\npolicy\n```\n'
            start = text.index(pc.MARKER)
            self.assertEqual(pc._span(text), (start, start + len(pc.MARKER + '\npolicy')))
        for prefix in ('```text\r', '```text\u2028', '```text\u2029',
                       '```text\x85', '```text\ninline ', '~~~markdown\n```text\n',
                       '<!--\n```text\n'):
            self.assertIsNone(pc._span(prefix + pc.MARKER + '\npolicy\n```\n'))
        valid = '```text\n' + pc.MARKER + '\npolicy\n```\n'
        self.assertIsNone(pc._span(valid + pc.MARKER + '\n'))

    def test_scan_does_not_use_python_character_loop(self):
        class Observed(str):
            def startswith(self, *args, **kwargs):
                raise AssertionError('per-character Python startswith remains')
        text = Observed('```text\n' + pc.MARKER + '\npolicy\n```\n')
        self.assertIsNotNone(pc._span(text))
