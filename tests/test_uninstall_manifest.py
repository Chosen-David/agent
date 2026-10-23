"""Malformed ownership records must fail before any uninstall removal."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import setup


def snapshot(root):
    return {p.relative_to(root).as_posix(): ('link', str(p.readlink())) if p.is_symlink()
            else ('file', p.read_bytes()) for p in root.rglob('*') if p.is_symlink() or p.is_file()}


class UninstallManifestTests(unittest.TestCase):
    def fixture(self, root):
        setup.install(root, model_inventory=setup.EMPTY_INVENTORY)
        path = root / '.claude/agent-workflows/installation.json'
        return path, json.loads(path.read_text())

    def test_invalid_manifest_preserves_all_files_and_links(self):
        mutations = (
            lambda m: [],
            lambda m: {k: v for k, v in m.items() if k != 'files'},
            lambda m: {**m, 'files': []},
            lambda m: {**m, 'links': []},
            lambda m: {**m, 'links': {k: None for k in m['links']}},
            lambda m: {**m, 'skill_copies': None},
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                path, manifest = self.fixture(root)
                path.write_text(json.dumps(mutate(copy.deepcopy(manifest))))
                before = snapshot(root)
                with self.assertRaisesRegex(ValueError, 'invalid installation manifest'):
                    setup.uninstall(root)
                self.assertEqual(snapshot(root), before)

    def test_cli_reports_blocked_before_any_removal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path, manifest = self.fixture(root)
            manifest['links'] = []
            path.write_text(json.dumps(manifest))
            before = snapshot(root)
            result = subprocess.run([sys.executable, str(setup.REPO / 'setup.py'),
                                     '--target', str(root), '--uninstall'],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 2)
            self.assertIn('setup blocked: invalid installation manifest', result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            self.assertEqual(snapshot(root), before)
