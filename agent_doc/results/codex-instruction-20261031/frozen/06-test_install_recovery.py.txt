"""Offline discovery-to-install recovery; subprocess fixtures are not live services."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import setup


def inventory():
    policy = setup.load_json(setup.REPO / 'config/role_model_policy.json')
    return {'schema_version': 1, 'models': [{**policy['models']['opus'],
            'available': True, 'transport': 'native', 'capabilities': ['tools', 'vision']}]}


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*')
            if p.is_file() and not p.is_symlink()}


class InstallRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='install recovery ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.outputs = []
        self.commands = []
        env = patch.dict(os.environ, {}, clear=True)
        env.start()
        self.addCleanup(env.stop)
        self.real_run = subprocess.run

    def discovered(self, command, **kwargs):
        if '--output' not in command:
            return self.real_run(command, **kwargs)
        output = Path(command[command.index('--output') + 1])
        self.outputs.append(output)
        self.commands.append((command, kwargs))
        output.write_text(json.dumps(inventory()), encoding='utf-8')
        return subprocess.CompletedProcess(command, 0, '', '')

    def sentinel(self):
        path = self.root / '.claude/agent-workflows/model_inventory.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'user inventory: preserve exactly\n')
        return path

    def install_empty(self, **kwargs):
        setup.install(self.root, model_inventory=setup.EMPTY_INVENTORY, **kwargs)

    def test_explicit_discovery_first_install_and_owned_cleanup(self):
        with patch('subprocess.run', side_effect=self.discovered):
            report = setup.discover(self.root)
        self.assertEqual(report['errors'], [])
        manifest = setup.load_json(self.root / '.claude/agent-workflows/installation.json')
        self.assertEqual(manifest['model_inventory'], inventory())
        self.assertFalse((self.root / '.claude/agent-workflows/model_inventory.json').exists())
        self.assertTrue(self.outputs)
        self.assertTrue(all(not p.parent.exists() for p in self.outputs))
        self.assertEqual(self.commands[0][1]['timeout'], 30)

    def test_explicit_discovery_preserves_user_inventory_on_success(self):
        sentinel = self.sentinel()
        before = sentinel.read_bytes()
        with patch('subprocess.run', side_effect=self.discovered):
            setup.discover(self.root)
        self.assertEqual(sentinel.read_bytes(), before)
        self.assertFalse(self.outputs[0].parent.exists())

    def test_explicit_discovery_installer_conflict_preserves_user_inventory(self):
        sentinel = self.sentinel()
        before = snapshot(self.root)
        with patch('subprocess.run', side_effect=self.discovered), patch.object(
                setup, 'install', side_effect=ValueError('fixture installation conflict')):
            with self.assertRaisesRegex(ValueError, 'fixture installation conflict'):
                setup.discover(self.root)
        self.assertEqual(snapshot(self.root), before)
        self.assertTrue(sentinel.exists())
        self.assertFalse(self.outputs[0].parent.exists())

    def test_explicit_discovery_errors_clean_owned_output(self):
        self.sentinel()
        before = snapshot(self.root)
        for kind in ('timeout', 'nonzero', 'json', 'schema'):
            with self.subTest(kind=kind):
                def failure(command, **kwargs):
                    output = Path(command[command.index('--output') + 1])
                    self.outputs.append(output)
                    output.write_text('{}' if kind == 'schema' else 'partial', encoding='utf-8')
                    if kind == 'timeout':
                        raise subprocess.TimeoutExpired(command, kwargs.get('timeout', 30))
                    return subprocess.CompletedProcess(command, int(kind == 'nonzero'), '', 'fixture error')
                with patch('subprocess.run', side_effect=failure), patch.object(setup, 'install') as install:
                    with self.assertRaises(ValueError):
                        setup.discover(self.root)
                install.assert_not_called()
                self.assertEqual(snapshot(self.root), before)
                self.assertFalse(self.outputs[-1].parent.exists())

    def test_doctor_updates_manifest_report_and_repeat_lifecycle(self):
        self.install_empty()
        sentinel = self.sentinel()
        before = sentinel.read_bytes()
        with patch.object(setup, '_auto_discover_inventory', return_value=inventory()) as discover:
            report = setup.doctor(self.root)
        discover.assert_called_once_with(self.root)
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['model_routing']['routes']['research-write']['model'], 'claude-opus-5-5')
        self.assertTrue(report['doctor']['needs_restart'])
        manifest = setup.load_json(self.root / '.claude/agent-workflows/installation.json')
        self.assertEqual(manifest['model_inventory'], inventory())
        for name, fingerprint in manifest['files'].items():
            self.assertEqual(setup.sha((self.root / name).read_text(encoding='utf-8')), fingerprint)
        self.assertEqual(sentinel.read_bytes(), before)
        self.assertEqual(setup.check(self.root)['errors'], [])
        with patch.object(setup, '_auto_discover_inventory') as discover:
            second = setup.doctor(self.root)
            self.assertEqual(second['errors'], [])
            self.assertFalse(second['doctor']['needs_restart'])
        discover.assert_not_called()
        self.assertEqual(setup.install(self.root)['errors'], [])
        result = setup.uninstall(self.root)
        self.assertEqual(result['preserved_local_edits'], [])
        self.assertFalse((self.root / '.claude/agents/agent-research-write.md').exists())
        self.assertEqual(sentinel.read_bytes(), before)

    def test_doctor_preserves_nonmodel_local_edits(self):
        self.install_empty()
        orchestrator = self.root / '.claude/agent-workflows/orchestrator.md'
        claude = self.root / 'CLAUDE.md'
        orchestrator.write_text('user orchestrator\n', encoding='utf-8')
        claude.write_text(claude.read_text(encoding='utf-8') + '\nUser project prose\n', encoding='utf-8')
        before = (orchestrator.read_bytes(), claude.read_bytes())
        with patch.object(setup, '_auto_discover_inventory', return_value=inventory()):
            report = setup.doctor(self.root)
        self.assertEqual((orchestrator.read_bytes(), claude.read_bytes()), before)
        self.assertEqual(report['model_routing']['routes']['research-write']['model'], 'claude-opus-5-5')
        self.assertEqual(report['errors'], ['missing/stale managed file: .claude/agent-workflows/orchestrator.md'])

    def test_doctor_model_conflicts_reject_before_any_write(self):
        self.install_empty()
        original = snapshot(self.root)
        for relative in ('.claude/agent-workflows/model-policy.json',
                         '.claude/agent-workflows/model-routing.json',
                         '.claude/agents/agent-research-write.md'):
            path = self.root / relative
            saved = path.read_bytes()
            path.write_bytes(b'user-edited model file\n')
            before = snapshot(self.root)
            with self.subTest(path=relative), patch.object(setup, '_auto_discover_inventory', return_value=inventory()):
                with self.assertRaisesRegex(ValueError, 'locally edited|preserving'):
                    setup.doctor(self.root)
                self.assertEqual(snapshot(self.root), before)
            # Restore the entire fixture after an old implementation's partial writes.
            for name, content in original.items():
                (self.root / name).write_bytes(content)
            path.write_bytes(saved)
            orphan = self.root / '.claude/agent-workflows/model_inventory.json'
            if str(orphan.relative_to(self.root)) not in original and orphan.exists():
                orphan.unlink()

    def test_doctor_rejects_foreign_manifest_identity(self):
        self.install_empty()
        path = self.root / '.claude/agent-workflows/installation.json'
        original = path.read_bytes()
        for field, value in (('repository', '/another/checkout'), ('project_root', '/another/project')):
            data = json.loads(original)
            data[field] = value
            path.write_text(json.dumps(data), encoding='utf-8')
            before = snapshot(self.root)
            with self.subTest(field=field), patch.object(setup, '_auto_discover_inventory', return_value=inventory()):
                with self.assertRaisesRegex(ValueError, 'different|another'):
                    setup.doctor(self.root)
                self.assertEqual(snapshot(self.root), before)
            for name, content in before.items():
                (self.root / name).write_bytes(content)
            path.write_bytes(original)

    def test_doctor_without_manifest_does_not_install_or_discover(self):
        with patch.object(setup, '_auto_discover_inventory', return_value=inventory()) as discover:
            report = setup.doctor(self.root)
        discover.assert_not_called()
        self.assertEqual(report['status'], 'needs_setup')
        self.assertFalse((self.root / '.claude').exists())

    def test_doctor_symlink_conflict_preflight_preserves_earlier_files(self):
        self.install_empty()
        guide = self.root / 'agent_doc/guide/GUIDE.md'
        # Fixture only: never points at or modifies the repository's human guide.
        guide.write_bytes(b'fixture human guide')
        policy = self.root / '.claude/agent-workflows/model-policy.json'
        policy.unlink()
        policy.symlink_to(guide)
        before = snapshot(self.root)
        with patch.object(setup, '_auto_discover_inventory', return_value=inventory()):
            with self.assertRaises(ValueError):
                setup.doctor(self.root)
        self.assertEqual(snapshot(self.root), before)
        self.assertTrue(policy.is_symlink())
        self.assertEqual(guide.read_bytes(), b'fixture human guide')

    def test_doctor_rejects_invalid_or_missing_file_ownership(self):
        self.install_empty()
        path = self.root / '.claude/agent-workflows/installation.json'
        original = setup.load_json(path)
        for kind in ('mapping', 'fingerprint', 'missing'):
            with self.subTest(kind=kind):
                data = json.loads(json.dumps(original))
                if kind == 'mapping':
                    data['files'] = []
                elif kind == 'fingerprint':
                    data['files']['.claude/agents/agent-research-write.md'] = 123
                else:
                    del data['files']['.claude/agents/agent-research-write.md']
                path.write_text(json.dumps(data), encoding='utf-8')
                before = snapshot(self.root)
                with patch.object(setup, '_auto_discover_inventory', return_value=inventory()):
                    with self.assertRaisesRegex(ValueError, 'manifest|ownership'):
                        setup.doctor(self.root)
                self.assertEqual(snapshot(self.root), before)

    def test_doctor_restores_missing_file_only_with_ownership(self):
        self.install_empty()
        path = self.root / '.claude/agents/agent-research-write.md'
        path.unlink()
        with patch.object(setup, '_auto_discover_inventory', return_value=inventory()):
            report = setup.doctor(self.root)
        self.assertEqual(report['errors'], [])
        self.assertIn('model: "claude-opus-5-5"', path.read_text(encoding='utf-8'))
        self.assertEqual(setup.install(self.root)['errors'], [])

    def test_doctor_rejects_invalid_discovered_inventory_before_writes(self):
        self.install_empty()
        before = snapshot(self.root)
        with patch.object(setup, '_auto_discover_inventory', return_value={'schema_version': 999, 'models': []}):
            with self.assertRaises(ValueError):
                setup.doctor(self.root)
        self.assertEqual(snapshot(self.root), before)

    def test_nonobject_manifest_check_and_offline_doctor_report_without_writes(self):
        self.install_empty()
        path = self.root / '.claude/agent-workflows/installation.json'
        for value in ([], None, 42):
            with self.subTest(value=value):
                path.write_text(json.dumps(value), encoding='utf-8')
                before = snapshot(self.root)
                report = setup.check(self.root)
                self.assertEqual(report['status'], 'needs_setup')
                self.assertIn('installation manifest missing/invalid', report['errors'])
                report = setup.doctor(self.root)
                self.assertEqual(report['status'], 'needs_setup')
                self.assertIn('installation manifest missing/invalid', report['errors'])
                self.assertEqual(snapshot(self.root), before)

    def test_nonobject_manifest_with_discovery_rejects_before_writes(self):
        self.install_empty()
        path = self.root / '.claude/agent-workflows/installation.json'
        for value in ([], None, 42):
            with self.subTest(value=value):
                path.write_text(json.dumps(value), encoding='utf-8')
                before = snapshot(self.root)
                with patch.object(setup, '_auto_discover_inventory', return_value=inventory()):
                    with self.assertRaisesRegex(ValueError, 'invalid installation manifest'):
                        setup.doctor(self.root)
                self.assertEqual(snapshot(self.root), before)

    def test_doctor_preserves_copy_manifest_and_unknown_metadata(self):
        self.install_empty(copy_skills=True)
        path = self.root / '.claude/agent-workflows/installation.json'
        data = setup.load_json(path)
        data['host_note'] = {'fixture': 'retain'}
        path.write_text(json.dumps(data), encoding='utf-8')
        with patch.object(setup, '_auto_discover_inventory', return_value=inventory()):
            report = setup.doctor(self.root)
        current = setup.load_json(path)
        self.assertEqual(current['host_note'], data['host_note'])
        self.assertEqual(current['skill_copies'], data['skill_copies'])
        self.assertEqual(report['errors'], [])
        self.assertEqual(setup.check(self.root)['errors'], [])


if __name__ == '__main__':
    unittest.main()
