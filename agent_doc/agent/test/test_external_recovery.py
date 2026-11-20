import hashlib
import importlib.util
import json
import sys
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from agent_runtime.codex_host import CodexHost

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('external_recovery_runner', ROOT / 'scripts/project_test.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ExternalRecoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / 'code'
        self.root.mkdir()
        self.docs = self.base / 'agent_doc/example'
        (self.docs / 'guide').mkdir(parents=True)
        (self.docs / 'guide/GUIDE.md').write_text('human requirement')
        (self.docs / 'test/T1').mkdir(parents=True)
        (self.docs / 'test/T1/check.py').write_text('assert True\n')
        environment = patch.dict(os.environ, {'AGENT_DOC_ROOT': str(self.docs)})
        environment.start()
        self.addCleanup(environment.stop)

    def host(self):
        host = CodexHost.__new__(CodexHost)
        host.root = self.root
        host.workflow = self.base / 'agent'
        host.project = 'example'
        host.task_id = 'T1'
        host.context_paths = ()
        host.write_paths = ()
        host.model_selection = None
        host.flow_class = lambda *args: SimpleNamespace(state={})
        return host

    def test_context_includes_external_guide_and_task_tests(self):
        packet = self.host()._context()
        self.assertEqual(packet['files']['agent_doc/guide/GUIDE.md']['content'], 'human requirement')
        self.assertIn('assert True', ''.join(packet['acceptance_tests'].values()))
        self.assertFalse((self.root / 'agent_doc').exists())

    def test_context_rejects_redirected_external_guide(self):
        guide = self.docs / 'guide/GUIDE.md'
        guide.unlink()
        guide.symlink_to(self.base / 'outside')
        (self.base / 'outside').write_text('outside')
        with self.assertRaises(ValueError):
            self.host()._context()

    def test_controller_hash_is_checked_in_bound_external_tree(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        task = self.docs / 'task/task_details/T1.md'
        task.parent.mkdir(parents=True)
        task.write_bytes(b'controller progress')
        refs = {'agent_doc/task/task_details/T1.md': hashlib.sha256(task.read_bytes()).hexdigest()}
        self.assertEqual(runner.source_manifest(self.root, exclude_owned=refs), {})
        subprocess.run(['git', '-C', str(self.root), 'config', 'user.email', 'fixture@example.invalid'], check=True)
        subprocess.run(['git', '-C', str(self.root), 'config', 'user.name', 'Fixture'], check=True)
        subprocess.run(['git', '-C', str(self.root), 'commit', '--allow-empty', '-qm', 'fixture'], check=True)
        subprocess.run(['git', '-C', str(self.root), 'remote', 'add', 'origin', 'https://example.invalid/example.git'], check=True)
        manifest = {'version': 1, 'origin': 'https://example.invalid/example.git', 'checks': [
            {'id': 'check', 'kind': 'python', 'path': 'check.py', 'timeout_seconds': 10, 'requirement': 'external task acceptance'}]}
        (self.docs / 'test/T1/suite.json').write_text(json.dumps(manifest))
        command = [sys.executable, str(ROOT / 'scripts/project_test.py'), '--workflow-root', str(self.base / 'agent'),
            '--project', 'example', '--target', str(self.root), '--task', 'T1', '--controller-documents-json', json.dumps(refs)]
        output = self.base / 'evidence'
        result = subprocess.run([*command, '--output', str(output)], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads((output / 'report.json').read_text())['status'], 'pass')
        task.write_bytes(b'external edit')
        rejected = subprocess.run([*command, '--output', str(self.base / 'rejected')], capture_output=True, text=True, timeout=30)
        self.assertEqual(rejected.returncode, 2, rejected.stdout + rejected.stderr)
        with self.assertRaisesRegex(ValueError, 'controller document changed'):
            runner.source_manifest(self.root, exclude_owned=refs)

    def test_context_uses_existing_anchor_without_environment(self):
        (self.root / 'agent_doc').symlink_to(self.docs, target_is_directory=True)
        with patch.dict(os.environ, {'AGENT_DOC_ROOT': ''}):
            packet = self.host()._context()
        self.assertEqual(packet['files']['agent_doc/guide/GUIDE.md']['content'], 'human requirement')
        self.assertTrue(packet['acceptance_tests'])
