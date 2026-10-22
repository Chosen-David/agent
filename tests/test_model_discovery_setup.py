"""Installer discovery ownership; process fixtures do not test a live gateway."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

import setup


def inventory(model='fixture-model'):
    return {'schema_version': 1, 'models': [{'provider': 'fixture', 'model': model,
            'available': True, 'capabilities': ['tools'], 'transport': 'native'}]}


class ModelDiscoverySetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='discovery setup ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixed = self.root / '.claude/agent-workflows/_discovery_tmp.json'
        self.outputs = []
        self.env = patch.dict(os.environ, {'ANTHROPIC_BASE_URL': 'https://fixture.invalid'}, clear=True)
        self.env.start(); self.addCleanup(self.env.stop)

    def succeed(self, command, **kwargs):
        path = Path(command[command.index('--output') + 1])
        self.outputs.append(path)
        path.write_text(json.dumps(inventory()))
        return subprocess.CompletedProcess(command, 0, '', '')

    def sentinel(self):
        self.fixed.parent.mkdir(parents=True, exist_ok=True)
        self.fixed.write_bytes(b'user-owned file: preserve exactly\n')
        return self.fixed.read_bytes()

    def test_absent_gateway_preserves_existing_same_named_file(self):
        original = self.sentinel()
        with patch.dict(os.environ, {}, clear=True), patch('subprocess.run') as run:
            self.assertIsNone(setup._auto_discover_inventory(self.root))
        run.assert_not_called()
        self.assertEqual(self.fixed.read_bytes(), original)

    def test_first_discovery_has_output_parent_and_cleans_own_files(self):
        self.assertFalse(self.fixed.parent.exists())
        with patch('subprocess.run', side_effect=self.succeed):
            self.assertEqual(setup._auto_discover_inventory(self.root), inventory())
        self.assertFalse(self.fixed.parent.exists())
        self.assertEqual(len(self.outputs), 1)
        self.assertFalse(self.outputs[0].exists())
        self.assertFalse(self.outputs[0].parent.exists())

    def test_success_does_not_overwrite_or_unlink_existing_file(self):
        original = self.sentinel()
        with patch('subprocess.run', side_effect=self.succeed):
            self.assertEqual(setup._auto_discover_inventory(self.root), inventory())
        self.assertEqual(self.fixed.read_bytes(), original)

    def test_timeout_falls_back_without_touching_project_file(self):
        original = self.sentinel()
        def timeout(command, **kwargs):
            self.outputs.append(Path(command[command.index('--output') + 1]))
            raise subprocess.TimeoutExpired(command, kwargs['timeout'])
        with patch('subprocess.run', side_effect=timeout):
            self.assertIsNone(setup._auto_discover_inventory(self.root))
        self.assertEqual(self.fixed.read_bytes(), original)
        self.assertFalse(self.outputs[0].parent.exists())

    def test_failure_and_bad_json_clean_only_owned_paths(self):
        original = self.sentinel()
        for code, data in ((1, 'partial'), (0, '{bad json')):
            def fail(command, **kwargs):
                path = Path(command[command.index('--output') + 1]); self.outputs.append(path)
                path.write_text(data)
                return subprocess.CompletedProcess(command, code, '', 'fixture failure')
            with self.subTest(code=code), patch('subprocess.run', side_effect=fail):
                self.assertIsNone(setup._auto_discover_inventory(self.root))
                self.assertEqual(self.fixed.read_bytes(), original)
                self.assertFalse(self.outputs[-1].parent.exists())

    def test_concurrent_calls_have_distinct_result_paths(self):
        self.fixed.parent.mkdir(parents=True)
        barrier = threading.Barrier(2)
        def respond(command, **kwargs):
            path = Path(command[command.index('--output') + 1])
            self.outputs.append(path)
            path.write_text(json.dumps(inventory(threading.current_thread().name)))
            barrier.wait(timeout=5)
            return subprocess.CompletedProcess(command, 0, '', '')
        def call():
            expected = threading.current_thread().name
            actual = setup._auto_discover_inventory(self.root)
            self.assertEqual(actual, inventory(expected))
        with patch('subprocess.run', side_effect=respond), ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(call) for _ in range(2)]
            for future in futures:
                future.result(timeout=10)
        self.assertEqual(len(set(self.outputs)), 2)
        self.assertTrue(all(not p.parent.exists() for p in self.outputs))

    def test_real_install_consumes_discovery_without_precreating_claude(self):
        real_run = subprocess.run
        def run(command, **kwargs):
            if '--output' in command:
                return self.succeed(command, **kwargs)
            return real_run(command, **kwargs)
        with patch('subprocess.run', side_effect=run):
            self.assertEqual(setup.install(self.root)['status'], 'configured')
        manifest = json.loads((self.root / '.claude/agent-workflows/installation.json').read_text())
        self.assertEqual(manifest['model_inventory'], inventory())
        self.assertEqual(setup.check(self.root)['status'], 'configured')
        self.assertTrue(all(not p.exists() for p in self.outputs))
        setup.uninstall(self.root)


if __name__ == '__main__':
    unittest.main()
