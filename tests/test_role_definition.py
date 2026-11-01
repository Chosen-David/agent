"""Revalidate Skill text after setup check; no model/role process is involved.

The previous native/adapter launch tests are retained in Git at 2fd48652.
The new entry reads the same bounded regular UTF-8 source for the current main.
"""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


loader = module('single_skill_loader', ROOT / 'scripts/load_skill.py')


class SkillDefinitionTests(unittest.TestCase):
    def fixture(self, copy=True):
        temp = tempfile.TemporaryDirectory(prefix='skill 中文 boundary ')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name).resolve()
        installer = loader.bootstrap()
        installer.install(root, copy_skills=copy)
        return root, installer

    def test_healthy_copy_and_declared_link(self):
        for copy in (True, False):
            with self.subTest(copy=copy):
                root, installer = self.fixture(copy)
                with patch.object(loader, 'bootstrap', return_value=installer):
                    result = loader.load_skill(root, 'research-write')
                self.assertFalse(result['launched'])
                self.assertEqual(result['execution_mode'], 'single-main')
                self.assertIn('单主 Agent', result['content'])

    def late_change(self, change):
        root, installer = self.fixture()
        original = installer.check
        path = root / '.claude/skills/research-write/SKILL.md'
        def check(target):
            result = original(target)
            self.assertEqual(result['errors'], [])
            change(path)
            return result
        with patch.object(installer, 'check', side_effect=check), patch.object(loader, 'bootstrap', return_value=installer):
            with self.assertRaises((OSError, ValueError)):
                loader.load_skill(root, 'research-write')

    def test_changed_text_after_check_is_not_returned(self):
        self.late_change(lambda path: path.write_text('changed Skill', encoding='utf-8'))

    def test_installed_orchestrator_policy_link_resolves_in_project(self):
        root, _ = self.fixture()
        entry = root / '.claude/agent-workflows/orchestrator.md'
        self.assertIn('](single_main_workflow.md)', entry.read_text(encoding='utf-8'))
        policy = entry.parent / 'single_main_workflow.md'
        self.assertIn('不要 spawn/delegate', policy.read_text(encoding='utf-8'))

    def test_invalid_utf8_after_check_is_refused(self):
        self.late_change(lambda path: path.write_bytes(b'\xff'))

    def test_oversized_text_after_check_is_refused(self):
        self.late_change(lambda path: path.write_bytes(b'x' * (16 * 1024 * 1024 + 1)))

    @unittest.skipUnless(hasattr(os, 'symlink'), 'symlink unavailable')
    def test_redirected_skill_after_check_is_refused(self):
        def redirect(path):
            outside = path.parent.parent / 'different.md'
            outside.write_bytes(path.read_bytes())
            path.unlink()
            try:
                path.symlink_to(outside)
            except OSError as exc:
                self.skipTest('symlink creation unavailable: ' + str(exc))
        self.late_change(redirect)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO requires POSIX')
    def test_fifo_after_check_is_refused_without_blocking(self):
        def fifo(path):
            path.unlink()
            os.mkfifo(path)
        self.late_change(fifo)

    def test_unknown_skill_does_not_fall_back_to_an_agent(self):
        root, installer = self.fixture()
        with patch.object(loader, 'bootstrap', return_value=installer):
            for name in ('planner-main', 'review-main', '../research-write'):
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'unknown Skill'):
                    loader.load_skill(root, name)

    @unittest.skipIf(os.name == 'nt', 'declared Unix Skill link path')
    def test_changed_skill_root_link_after_check_is_refused(self):
        root, installer = self.fixture(copy=False)
        original = installer.check
        path = root / '.claude/skills/research-write'
        def check(target):
            result = original(target)
            self.assertEqual(result['errors'], [])
            path.unlink()
            path.symlink_to(root / '.claude/skills/research-review', target_is_directory=True)
            return result
        with patch.object(installer, 'check', side_effect=check), patch.object(loader, 'bootstrap', return_value=installer):
            with self.assertRaisesRegex(ValueError, 'link changed'):
                loader.load_skill(root, 'research-write')


if __name__ == '__main__':
    unittest.main()
