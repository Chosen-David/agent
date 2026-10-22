"""Doctor control flow; mocked discovery/tmux do not establish live access."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import setup


class SetupDoctorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='doctor setup ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        env = patch.dict(os.environ, {}, clear=True)
        env.start()
        self.addCleanup(env.stop)

    def test_uninstalled_no_gateway_reports_needs_setup(self):
        with patch('subprocess.run') as run:
            report = setup.doctor(self.root)
        run.assert_not_called()
        self.assertEqual(report['status'], 'needs_setup')
        self.assertTrue(report['errors'])
        self.assertFalse(report['doctor']['in_tmux'])
        self.assertFalse((self.root / '.claude').exists())

    def test_all_fallback_discovery_unavailable(self):
        setup.install(self.root, model_inventory=setup.EMPTY_INVENTORY)
        initial = {'model_routing': {'routes': {'writer': {'fallback': True}}},
                   'errors': ['fixture needs setup'], 'status': 'needs_setup'}
        with patch.object(setup, 'check', return_value=initial), patch.object(
                setup, '_auto_discover_inventory', return_value=None) as discover:
            report = setup.doctor(self.root)
        discover.assert_called_once_with(self.root)
        self.assertEqual(report['errors'], ['fixture needs setup'])
        self.assertEqual(report['doctor']['fixes_applied'], [])

    def test_nonfallback_inventory_skips_discovery(self):
        initial = {'model_routing': {'routes': {'writer': {'fallback': False}}}}
        with patch.object(setup, 'check', return_value=initial), patch.object(
                setup, '_auto_discover_inventory') as discover:
            report = setup.doctor(self.root)
        discover.assert_not_called()
        self.assertFalse(report['doctor']['in_tmux'])

    def test_tmux_control_flow_preserves_arguments_and_failure_report(self):
        for code in (0, 1):
            with self.subTest(returncode=code), patch.dict(os.environ, {'TMUX': 'fixture'}), patch(
                    'subprocess.run', return_value=subprocess.CompletedProcess([], code, '', 'fixture failure')) as run:
                report = setup.doctor(self.root)
            run.assert_called_once_with(
                ['tmux', 'source-file', str(setup.REPO / 'agent_runtime/tmux.conf')],
                capture_output=True, text=True, timeout=5, check=False)
            self.assertTrue(report['doctor']['in_tmux'])
            message = report['doctor']['fixes_applied'][0]
            self.assertIn('Applied tmux.conf' if code == 0 else 'tmux source-file failed: fixture failure', message)

    def test_installed_no_gateway_lifecycle_preserves_user_prose(self):
        claude = self.root / 'CLAUDE.md'
        claude.write_text('User prose\n', encoding='utf-8')
        setup.install(self.root, model_inventory=setup.EMPTY_INVENTORY)
        manifest = self.root / '.claude/agent-workflows/installation.json'
        original_manifest = manifest.read_bytes()
        installed_claude = claude.read_bytes()
        report = setup.doctor(self.root)
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['status'], 'configured')
        self.assertEqual(manifest.read_bytes(), original_manifest)
        self.assertEqual(claude.read_bytes(), installed_claude)
        self.assertEqual(setup.check(self.root)['errors'], [])
        self.assertEqual(setup.uninstall(self.root)['status'], 'uninstalled')
        self.assertTrue(claude.read_text(encoding='utf-8').startswith('User prose\n'))
        self.assertNotIn(setup.BEGIN, claude.read_text(encoding='utf-8'))

    def test_cli_uninstalled_returns_health_json(self):
        result = subprocess.run([sys.executable, str(setup.REPO / 'setup.py'),
                                 '--target', str(self.root), '--doctor'],
                                capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, '')
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'needs_setup')
        self.assertFalse(report['doctor']['in_tmux'])
        self.assertFalse((self.root / '.claude').exists())


if __name__ == '__main__':
    unittest.main()
