"""Legacy migration preserves the same literal task set and source blocks."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.project_docs import migrate, parse_requirements, snapshot_project_docs


class MigrationFenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.counter = 0

    def source(self, text):
        self.counter += 1
        root = self.base / str(self.counter)
        root.mkdir()
        raw = text.encode('utf-8')
        (root / 'TASK.md').write_bytes(raw)
        return root, raw

    @staticmethod
    def inventory(root):
        return {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}

    def assert_migrated(self, root, raw, expected, snapshot):
        sha = hashlib.sha256(raw).hexdigest()
        archive = root / f'agent_doc/task/legacy/TASK.{sha}.md'
        self.assertEqual(archive.read_bytes(), raw)
        pointer = (root / 'TASK.md').read_bytes()
        self.assertNotIn(b'- [ ]', pointer)
        self.assertIn(b'agent_doc/task/TASK.md', pointer)
        index = root / 'agent_doc/task/TASK.md'
        items = parse_requirements(index.read_bytes().decode(), canonical=True)
        self.assertEqual([(t['id'], t['date']) for t in items], [(i, d) for i, d, _ in expected])
        self.assertEqual(set(snapshot['task_details']), {i for i, _, _ in expected})
        self.assertEqual(snapshot['task_index']['sha256'], hashlib.sha256(index.read_bytes()).hexdigest())
        for identity, date, block in expected:
            detail = (root / f'agent_doc/task/task_details/{identity}.md').read_bytes().decode()
            self.assertIn(f'Task-ID: {identity}\nDate: {date}\n', detail)
            preserved = detail.split('### Preserved implementation and evidence\n\n', 1)[1]
            preserved = preserved.split('\n\n### Historical context\n\n', 1)[0]
            self.assertEqual(preserved, block)
            self.assertIn(f'Source SHA256: {sha}', detail)
        self.assertEqual(list((root / 'agent_doc/guide').iterdir()), [])

    @staticmethod
    def invalid_fixture(marker, ending):
        lines = ['## 2026-10-27', '- [ ] [KEEP] Keep', 'Keep evidence.', '', marker,
                 '- [ ] [CORRECT] Correction', 'Correction evidence.', marker,
                 '- [ ] [NEXT] Next', 'Next evidence.']
        text = ending.join(lines) + ending
        normalize = lambda xs: ending.join(xs).replace('\r\n', '\n')
        expected = [('KEEP', '2026-10-27', normalize(lines[1:5])),
                    ('CORRECT', '2026-10-27', normalize(lines[5:8])),
                    ('NEXT', '2026-10-27', normalize(lines[8:]))]
        return text, expected

    def test_invalid_openers_do_not_remove_migration_rows(self):
        for ending in ('\n', '\r\n', '\r'):
            for marker in ('    ```', '\t```', '\u00a0```', '\u2028```',
                           '    ~~~', '\t~~~', '\u00a0~~~', '\u2028~~~', '```bad`info'):
                with self.subTest(ending=repr(ending), marker=repr(marker)):
                    text, expected = self.invalid_fixture(marker, ending)
                    root, raw = self.source(text)
                    snapshot = migrate(root, '2026-10-26')
                    self.assert_migrated(root, raw, expected, snapshot)

    def test_invalid_closers_keep_example_dates_and_evidence_in_real_block(self):
        for token in ('```', '~~~'):
            for indent in range(4):
                for invalid in ('    ' + token, '\t' + token, token + '\u00a0', token + 'suffix',
                                token[:2], '~~~' if token == '```' else '```'):
                    with self.subTest(token=token, indent=indent, invalid=repr(invalid)):
                        lines = ['## 2026-10-27', '- [ ] [KEEP] Keep', 'Before example.',
                                 ' ' * indent + token + 'md', invalid, '## 2099-01-01',
                                 '- [ ] [FAKE] Example only', 'Example evidence stays here.',
                                 '   ' + token + token[0] + ' \t', 'After example.',
                                 '- [ ] [NEXT] Next', 'Next evidence.']
                        root, raw = self.source('\n'.join(lines) + '\n')
                        expected = [('KEEP', '2026-10-27', '\n'.join(lines[1:10])),
                                    ('NEXT', '2026-10-27', '\n'.join(lines[10:]))]
                        snapshot = migrate(root, '2026-10-26')
                        self.assert_migrated(root, raw, expected, snapshot)

    def test_unclosed_fence_keeps_complete_original_block_to_eof(self):
        for token in ('```', '~~~'):
            for invalid in ('    ' + token, '\t' + token, token + '\u00a0', token + 'suffix'):
                with self.subTest(token=token, invalid=repr(invalid)):
                    lines = ['## 2026-10-27', '- [ ] [KEEP] Keep', token, invalid,
                             '- [ ] [FAKE] Example only', 'Evidence at EOF']
                    root, raw = self.source('\n'.join(lines))
                    self.assert_migrated(root, raw, [('KEEP', '2026-10-27', '\n'.join(lines[1:]))],
                                         migrate(root, '2026-10-26'))

    def test_normal_dates_and_default_date_remain_unchanged(self):
        root, raw = self.source('- [ ] [KEEP] Keep\nKeep evidence.\n## 2026-10-27\n'
                                '- [ ] [NEXT] Next\nNext evidence.\n')
        expected = [('KEEP', '2026-10-26', '- [ ] [KEEP] Keep\nKeep evidence.'),
                    ('NEXT', '2026-10-27', '- [ ] [NEXT] Next\nNext evidence.')]
        self.assert_migrated(root, raw, expected, migrate(root, '2026-10-26'))

    def test_idempotence_conflicts_and_invalid_source_stay_fail_closed(self):
        text = '## 2026-10-27\n- [ ] [KEEP] Keep\nKeep evidence.\n'
        root, raw = self.source(text)
        snapshot = migrate(root, '2026-10-26')
        before = self.inventory(root)
        self.assertEqual(migrate(root, '2026-10-28'), snapshot)
        self.assertEqual(self.inventory(root), before)
        conflict, _ = self.source(text)
        detail = conflict / 'agent_doc/task/task_details/KEEP.md'
        detail.parent.mkdir(parents=True)
        detail.write_bytes(b'Existing user detail must remain unchanged.\n')
        before = self.inventory(conflict)
        with self.assertRaises(ValueError):
            migrate(conflict, '2026-10-26')
        self.assertEqual(self.inventory(conflict), before)
        for invalid in ('- [ ] [KEEP] One\n- [ ] [KEEP] Two\n', '- [ ] no identity\n'):
            with self.subTest(invalid=invalid):
                invalid_root, _ = self.source(invalid)
                before = self.inventory(invalid_root)
                with self.assertRaises(ValueError):
                    migrate(invalid_root, '2026-10-26')
                self.assertEqual(self.inventory(invalid_root), before)

    def test_actual_portable_migration_cli_preserves_required_blocks(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/project_docs.py'
        for marker in ('    ```', '\u00a0~~~', '```bad`info'):
            with self.subTest(marker=repr(marker)):
                text, expected = self.invalid_fixture(marker, '\n')
                root, raw = self.source(text)
                run = subprocess.run([sys.executable, '-B', str(script), '--root', str(root),
                                      'migrate', '--date', '2026-10-26'], capture_output=True, timeout=15,
                    env=dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936'))
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(run.stderr, b'')
                snapshot = json.loads(run.stdout.decode('utf-8'))
                self.assert_migrated(root, raw, expected, snapshot)
                self.assertEqual(snapshot_project_docs(root), snapshot)
