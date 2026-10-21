"""Install and execute from only the documented product paths, without history."""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ProductProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='product 中文 profile ')
        cls.base = Path(cls.temp.name)
        cls.source = cls.base / 'workflow'
        # Test the actual staged candidate when developing, HEAD in a clean clone.
        tree = subprocess.check_output(['git', 'write-tree'], cwd=ROOT).decode().strip()
        readme = subprocess.check_output(['git', 'show', tree + ':README.md'], cwd=ROOT).decode('utf-8')
        command = re.search(r'^git -C agent sparse-checkout set (.+)$', readme, re.M)
        if command is None:
            cls.temp.cleanup()
            raise AssertionError('README must document the product dependency paths')
        selected = shlex.split(command[1])
        # Shared objects avoid copying historical evidence into another temp Git
        # pack; actual cone checkout rules decide exactly which files appear.
        subprocess.check_output(['git', 'clone', '--shared', '--no-checkout', '--config',
                                 'core.autocrlf=false', str(ROOT), str(cls.source)], stderr=subprocess.STDOUT)
        cls.git('sparse-checkout', 'set', '--cone', *selected)
        cls.git('read-tree', '--reset', '-u', tree)
        commit = cls.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                         '-c', 'commit.gpgsign=false', 'commit-tree', tree, '-p', 'HEAD',
                         '-m', 'Isolated product fixture').decode().strip()
        cls.git('update-ref', 'HEAD', commit)
        cls.product_bytes = sum(p.stat().st_size for p in cls.source.rglob('*')
                                if p.is_file() and '.git' not in p.relative_to(cls.source).parts)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @classmethod
    def git(cls, *args):
        return subprocess.check_output(['git', *args], cwd=cls.source, stderr=subprocess.STDOUT)

    def call(self, *args, cwd=None):
        env = dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936')
        run = subprocess.run([sys.executable, '-X', 'utf8=0', '-B', *map(str, args)],
                             cwd=cwd or self.source, env=env, capture_output=True, timeout=90)
        self.assertEqual(run.returncode, 0, run.stderr.decode('utf-8', errors='replace'))
        return json.loads(run.stdout.decode('utf-8'))

    def test_no_historical_project_or_bulk_documents_are_required(self):
        self.assertFalse((self.source / 'agent_doc').exists())
        self.assertFalse((self.source / 'tests').exists())
        self.assertLess(self.product_bytes, 32 * 1024 * 1024)
        self.assertEqual(self.git('status', '--porcelain'), b'')

    def test_claude_install_and_actual_role_preview(self):
        project = self.base / '新项目 space'
        self.assertEqual(self.call('setup.py', '--target', project, '--copy-skills')['status'], 'configured')
        self.assertEqual(self.call('setup.py', '--target', project, '--check')['status'], 'configured')
        self.assertEqual(self.call('scripts/run_role.py', '--project', project, '--role', 'research-write', '--dry-run')['transport'], 'native')
        self.assertEqual(list((project / 'agent_doc/guide').iterdir()), [])

    def test_codex_committed_install_check_and_repeat(self):
        args = ['scripts/setup_codex.py', '--repo', self.source, '--dest', self.base / 'user/skills',
                '--codex-home', self.base / 'user/codex', '--state', self.base / 'user/state']
        for extra in ([], ['--check'], []):
            self.assertEqual(self.call(*args, *extra)['status'], 'configured')

    def test_core_and_standalone_knowledge_entrypoints(self):
        self.call('-m', 'agent_runtime', '--db', self.base / 'runtime.sqlite', 'capabilities')
        skill = self.source / 'plugins/research-assistant/skills/model-with-knowledge'
        result = self.call('-I', skill / 'scripts/knowledge.py', '--root', skill / 'assets/knowledge', 'validate')
        self.assertTrue(result['valid'])
        self.assertGreater(result['entries'], 0)


if __name__ == '__main__':
    unittest.main()
