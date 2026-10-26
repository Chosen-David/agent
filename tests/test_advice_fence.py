"""Literal advice sections use the existing top-level fence grammar."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.advice_context import advice_headings, advice_view
from agent_runtime.project_docs import outside_fences


class AdviceFenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.path = 'agent_doc/advice/meeting.md'
        self.file = self.root / self.path
        self.file.parent.mkdir(parents=True)

    def bind(self, chunks):
        self.raw = ''.join(chunks).encode('utf-8')
        self.file.write_bytes(self.raw)
        self.sha = hashlib.sha256(self.raw).hexdigest()

    def assert_topics(self, chunks, expected, selected):
        self.bind(chunks)
        heading = advice_headings(self.root, self.path, self.sha)
        self.assertEqual(heading['topics'], expected)
        self.assertEqual(heading['leading_text'], chunks[0])
        view = advice_view(self.root, self.path, [selected], self.sha)
        chosen = next(t for t in expected if t['heading'] == selected)
        self.assertEqual(view['selected_sections'], [dict(
            chosen, text=''.join(chunks[chosen['start_line']-1:chosen['end_line']]))])
        self.assertEqual(view['omitted_sections'], len(expected)-1)
        self.assertEqual(view['source'], {'path': self.path, 'sha256': self.sha})
        self.assertEqual(view['leading_text'], chunks[0])
        self.assertEqual(self.file.read_bytes(), self.raw)

    def test_non_fence_prefixes_do_not_hide_correction(self):
        for ending in ('\n', '\r\n', '\r'):
            for token in ('```', '~~~'):
                for prefix in ('    ', '\t', '\u00a0', '\u2028'):
                    with self.subTest(ending=repr(ending), token=token, prefix=repr(prefix)):
                        chunks = [s+ending for s in ('# Meeting', '## OLD', '',
                            prefix+token, '## CANCEL', 'Cancel old approval.', '',
                            prefix+token, '## NEXT', 'Next step')]
                        self.assert_topics(chunks, [
                            {'heading': 'OLD', 'start_line': 2, 'end_line': 4},
                            {'heading': 'CANCEL', 'start_line': 5, 'end_line': 8},
                            {'heading': 'NEXT', 'start_line': 9, 'end_line': 10}], 'CANCEL')

    def test_backtick_in_info_does_not_open_fence(self):
        chunks = [s+'\n' for s in ('# Meeting', '## OLD', '```bad`info',
            '## CANCEL', 'Correction.', '```bad`info', '## NEXT', 'Next')]
        self.assert_topics(chunks, [
            {'heading': 'OLD', 'start_line': 2, 'end_line': 3},
            {'heading': 'CANCEL', 'start_line': 4, 'end_line': 6},
            {'heading': 'NEXT', 'start_line': 7, 'end_line': 8}], 'CANCEL')

    def test_valid_fences_and_invalid_closers_keep_examples_hidden(self):
        for token in ('```', '~~~'):
            for indent in range(4):
                for invalid in ('    '+token, '\t'+token, token+'\u00a0',
                                token+'suffix', token[:2], '~~~' if token=='```' else '```'):
                    with self.subTest(token=token, indent=indent, invalid=repr(invalid)):
                        chunks = [s+'\r\n' for s in ('# Meeting', '## VERIFY',
                            ' '*indent+token+'md', '## FAKE', invalid, '## HIDDEN',
                            '   '+token+'`' if token=='```' else '   '+token+'~',
                            '## NEXT', 'Next')]
                        self.assert_topics(chunks, [
                            {'heading': 'VERIFY', 'start_line': 2, 'end_line': 7},
                            {'heading': 'NEXT', 'start_line': 8, 'end_line': 9}], 'VERIFY')

    def test_invalid_only_closer_requires_full_source(self):
        for close in ('    ```', '\t```', '```\u00a0', '```suffix', '~~'):
            with self.subTest(close=repr(close)):
                self.bind([s+'\n' for s in ('# Meeting', '## VERIFY', '```', close, '## FAKE')])
                with self.assertRaisesRegex(ValueError, 'unterminated code fence'):
                    advice_headings(self.root, self.path, self.sha)
                with self.assertRaisesRegex(ValueError, 'unterminated code fence'):
                    advice_view(self.root, self.path, ['VERIFY'], self.sha)
                self.assertEqual(self.file.read_bytes(), self.raw)

    def test_existing_outside_fences_offsets_are_unchanged(self):
        text = '## Plan\r\n```bad`info\r\nA\r\n  ~~~md\r\n## FAKE\r\n~~~\r\n## Progress'
        self.assertEqual(list(outside_fences(text)), [
            (0, 9, '## Plan'), (22, 25, 'A'), (48, 59, '## Progress')])

    def test_actual_cli_exposes_correction(self):
        chunks = [s+'\r\n' for s in ('# Meeting', '## OLD', '', '    ```',
                    '## CANCEL', '取消旧批准。', '', '    ```', '## NEXT', 'Next')]
        self.bind(chunks)
        base = [sys.executable, '-B', str(Path(__file__).resolve().parents[1]/'scripts/advice_context.py'),
                '--root', str(self.root), '--path', self.path, '--sha256', self.sha, '--compact']
        for discover in (True, False):
            with self.subTest(discover=discover):
                command = base + (['--list-headings'] if discover else ['--heading', 'CANCEL'])
                run = subprocess.run(command, capture_output=True, timeout=15,
                    env=dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936'))
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(run.stderr, b'')
                value = json.loads(run.stdout.decode('utf-8'))
                if discover:
                    self.assertEqual([t['heading'] for t in value['topics']], ['OLD', 'CANCEL', 'NEXT'])
                else:
                    self.assertEqual(value['selected_sections'], [{
                        'heading': 'CANCEL', 'start_line': 5, 'end_line': 8, 'text': ''.join(chunks[4:8])}])
                self.assertEqual(self.file.read_bytes(), self.raw)
