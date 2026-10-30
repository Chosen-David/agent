"""Unreadable late ownership inputs must not leave a partly removed install."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import setup
from agent_runtime.external_json import DEFAULT_JSON_LIMIT
from tests import test_setup_text as installed_text_tests


class UninstallTextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='uninstall text ')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name).resolve() / 'project'
        self.project.mkdir()
        setup.install(self.project, model_inventory=setup.EMPTY_INVENTORY)
        self.manifest = self.project / '.claude/agent-workflows/installation.json'
        files = json.loads(self.manifest.read_text(encoding='utf-8'))['files']
        self.relative = list(files)[-1]
        self.late = self.project / self.relative
        self.assertGreater(len(files), 1)
        self.assertTrue((self.project / list(files)[0]).is_file())

    def snapshot(self):
        return installed_text_tests.SetupTextTests.snapshot(self)

    def blocked_cli(self):
        before = self.snapshot()
        env = dict(os.environ)
        for key in ('ANTHROPIC_BASE_URL', 'TMUX'):
            env.pop(key, None)
        result = subprocess.run(
            [sys.executable, '-B', str(setup.REPO / 'setup.py'),
             '--target', str(self.project), '--uninstall'],
            cwd=self.temp.name, env=env, capture_output=True,
            encoding='utf-8', timeout=20)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertIn('setup blocked:', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_late_invalid_utf8_preserves_complete_install(self):
        self.late.write_bytes(b'\xff invalid local edit')
        self.blocked_cli()

    def test_late_oversize_text_preserves_complete_install(self):
        self.late.write_bytes(b'x' * (DEFAULT_JSON_LIMIT + 1))
        self.blocked_cli()

    def test_late_read_error_preserves_complete_install(self):
        original = setup._installed_text
        before = self.snapshot()

        def unreadable(target, relative):
            if relative == self.relative:
                raise PermissionError('injected unreadable late text')
            return original(target, relative)

        with patch.object(setup, '_installed_text', side_effect=unreadable):
            with self.assertRaisesRegex(PermissionError, 'injected unreadable late text'):
                setup.uninstall(self.project)
        self.assertEqual(self.snapshot(), before)

    def test_valid_local_edits_and_unowned_data_survive_uninstall(self):
        self.late.write_bytes(b'locally edited agent\n')
        note = self.project / 'notes.txt'
        note.write_bytes(b'keep user data\r\n')
        result = setup.uninstall(self.project)
        self.assertEqual(result['status'], 'uninstalled')
        self.assertIn(self.relative, result['preserved_local_edits'])
        self.assertEqual(self.late.read_bytes(), b'locally edited agent\n')
        self.assertEqual(note.read_bytes(), b'keep user data\r\n')
        self.assertFalse(self.manifest.exists())

    def test_ownership_is_rechecked_after_preflight(self):
        original = setup._installed_text
        reads = []

        def changed_after_read(target, relative):
            text = original(target, relative)
            if relative == self.relative:
                reads.append(text)
                if len(reads) == 1:
                    self.late.write_bytes(b'new concurrent edit\n')
            return text

        with patch.object(setup, '_installed_text', side_effect=changed_after_read):
            result = setup.uninstall(self.project)
        self.assertEqual(result['status'], 'uninstalled')
        self.assertIn(self.relative, result['preserved_local_edits'])
        self.assertEqual(self.late.read_bytes(), b'new concurrent edit\n')
        self.assertEqual(len(reads), 2)


if __name__ == '__main__':
    unittest.main()
