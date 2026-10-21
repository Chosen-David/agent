"""First-use and owned-copy lifecycle, without model calls or real user profiles."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('portable_setup', ROOT / 'setup.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class PortableSetup(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='agent 中文 project ')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.target = self.root / '项目 space'
        role, source, description = setup.catalog()[0]
        self.source = self.root / 'source'
        shutil.copytree(source, self.source)
        self.relative = '.claude/skills/' + role['id']
        catalog = patch.object(setup, 'catalog', return_value=[(role, self.source, description)])
        catalog.start()
        self.addCleanup(catalog.stop)

    def test_copy_repeat_update_and_uninstall(self):
        with patch.object(Path, 'symlink_to', side_effect=OSError('no symlink privilege')):
            self.assertEqual(setup.install(self.target, copy_skills=True)['status'], 'configured')
            manifest = self.target / '.claude/agent-workflows/installation.json'
            before = manifest.read_bytes()
            setup.install(self.target)
            self.assertEqual(before, manifest.read_bytes())
            (self.source / 'new.md').write_text('中文\n', encoding='utf-8')
            self.assertEqual(setup.check(self.target)['status'], 'needs_setup')
            setup.install(self.target)
            self.assertEqual((self.target / self.relative / 'new.md').read_bytes(), (self.source / 'new.md').read_bytes())
            self.assertEqual(setup.check(self.target)['skill_storage'], 'copy')
            setup.uninstall(self.target)
        self.assertFalse((self.target / self.relative).exists())
        self.assertTrue((self.target / 'agent_doc/task/TASK.md').is_file())

    def test_changed_copy_and_foreign_empty_directory_preserved(self):
        for modification in ('edit', 'directory'):
            target = self.root / modification
            setup.install(target, copy_skills=True)
            skill = target / self.relative
            if modification == 'edit':
                (skill / 'SKILL.md').write_text('用户修改', encoding='utf-8')
            else:
                (skill / 'my-empty-directory').mkdir()
            before = (target / 'CLAUDE.md').read_bytes()
            with self.assertRaisesRegex(ValueError, 'locally edited skill'):
                setup.install(target)
            self.assertEqual(before, (target / 'CLAUDE.md').read_bytes())
            self.assertEqual(setup.check(target)['status'], 'needs_setup')
            self.assertIn(self.relative, setup.uninstall(target)['preserved_local_edits'])
            self.assertTrue(skill.is_dir())

    def test_non_utf8_cli_install_check_repeat_uninstall(self):
        env = dict(os.environ, PYTHONIOENCODING='cp936', PYTHONUTF8='0')
        # The CLI loads its own full catalog; no in-process mocks leak into it.
        for flags in (['--copy-skills'], ['--check'], [], ['--uninstall']):
            run = subprocess.run([sys.executable, '-X', 'utf8=0', str(ROOT / 'setup.py'),
                                  '--target', str(self.target), *flags], env=env, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr.decode('utf-8', errors='replace'))
            data = json.loads(run.stdout.decode('utf-8'))
            self.assertEqual(data['status'], 'uninstalled' if flags == ['--uninstall'] else 'configured')

    def test_simple_entry_loads_orchestration_only_on_demand(self):
        self.assertNotIn('@.claude/agent-workflows/orchestrator.md', setup.block())
        self.assertIn('`.claude/agent-workflows/orchestrator.md`', setup.block())
        self.assertIn('简单、目标明确的任务直接完成', setup.block())


if __name__ == '__main__':
    unittest.main()
