"""Publication and rollback preserve competing targets and recoverable originals."""
import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.test_setup import setup, ROOT


def identity(path):
    stat = path.stat()
    return stat.st_dev, stat.st_ino


def publication_hook(target, interleave):
    publisher = getattr(setup, '_publish_skill', None)
    original = publisher or Path.rename
    def call(source, destination):
        if Path(destination) == target and Path(source).name in ('new', 'ready'):
            interleave(Path(source))
        return original(source, destination)
    return (patch.object(setup, '_publish_skill', call) if publisher is not None
            else patch.object(Path, 'rename', call))


class SetupPublicationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.addCleanup(patch.stopall)
        patch.dict(os.environ, {'ANTHROPIC_BASE_URL': ''}).start()

    def fixture(self, name):
        base = self.base / name
        base.mkdir()
        source, target = base / 'source', base / 'installed'
        source.mkdir(); target.mkdir()
        (source / 'SKILL.md').write_text('# New skill\n', encoding='utf-8')
        (target / 'SKILL.md').write_text('# Original owned skill\n', encoding='utf-8')
        return base, source, target

    def claims(self, *, fault):
        for kind in ('empty', 'nonempty', 'file'):
            with self.subTest(kind=kind):
                base, source, target = self.fixture(kind)
                previous, expected = setup.skill_snapshot(target), setup.skill_snapshot(source)
                original_id, claim_id, calls = identity(target), [], []
                def interleave(ready):
                    calls.append(ready)
                    self.assertFalse(target.exists())
                    if kind == 'file':
                        target.write_bytes(b'claimant')
                    else:
                        target.mkdir()
                        if kind == 'nonempty':
                            (target / 'claimed.txt').write_bytes(b'claimant')
                    claim_id.append(identity(target))
                    if fault:
                        raise OSError(errno.EIO, 'controlled publication fault')
                error = None
                with publication_hook(target, interleave):
                    try:
                        setup.replace_skill_copy(target, source, previous, expected)
                    except (OSError, ValueError) as exc:
                        error = exc
                self.assertEqual(len(calls), 1)
                self.assertIsNotNone(error)
                self.assertEqual(identity(target), claim_id[0])
                if kind == 'file':
                    self.assertEqual(target.read_bytes(), b'claimant')
                else:
                    self.assertEqual(sorted(p.name for p in target.iterdir()),
                                     ['claimed.txt'] if kind == 'nonempty' else [])
                    if kind == 'nonempty':
                        self.assertEqual((target / 'claimed.txt').read_bytes(), b'claimant')
                self.assertEqual(type(error).__name__, 'SkillCopyRecoveryError')
                backup = error.recovery_path
                self.assertEqual(backup.parent.parent, base)
                self.assertEqual(identity(backup), original_id)
                self.assertEqual(setup.skill_snapshot(backup), previous)
                self.assertEqual((backup.parent / 'ready' / 'SKILL.md').read_text(encoding='utf-8'),
                                 '# New skill\n')
                self.assertEqual(list(base.glob('.skill-*')), [backup.parent])
                self.assertIn(str(backup), str(error))
                if fault:
                    self.assertEqual(error.publication_error.errno, errno.EIO)

    def test_publication_claims_preserve_owner_and_recoverable_backup(self):
        self.claims(fault=False)

    def test_rollback_claims_preserve_owner_and_recoverable_backup(self):
        self.claims(fault=True)

    def test_normal_replacement_cleans_stage(self):
        base, source, target = self.fixture('normal')
        setup.replace_skill_copy(target, source, setup.skill_snapshot(target), setup.skill_snapshot(source))
        self.assertEqual((target / 'SKILL.md').read_text(encoding='utf-8'), '# New skill\n')
        self.assertEqual(list(base.glob('.skill-*')), [])

    def test_uncontended_error_restores_original_and_cleans_stage(self):
        base, source, target = self.fixture('fault')
        previous, original_id = setup.skill_snapshot(target), identity(target)
        def fail(ready):
            raise OSError(errno.EIO, 'controlled publication fault')
        with publication_hook(target, fail), self.assertRaises(OSError) as caught:
            setup.replace_skill_copy(target, source, previous, setup.skill_snapshot(source))
        self.assertEqual(caught.exception.errno, errno.EIO)
        self.assertEqual(identity(target), original_id)
        self.assertEqual(setup.skill_snapshot(target), previous)
        self.assertEqual(list(base.glob('.skill-*')), [])

    def test_capability_failure_precedes_original_move(self):
        if not hasattr(setup, '_publish_skill'):
            self.skipTest('baseline lacks explicit native capability preflight')
        base, source, target = self.fixture('capability')
        previous, original_id = setup.skill_snapshot(target), identity(target)
        with patch.object(setup, '_publish_skill', side_effect=OSError(errno.ENOSYS, 'unavailable')), \
             self.assertRaises(OSError):
            setup.replace_skill_copy(target, source, previous, setup.skill_snapshot(source))
        self.assertEqual(identity(target), original_id)
        self.assertEqual(setup.skill_snapshot(target), previous)
        self.assertEqual(list(base.glob('.skill-*')), [])

    def test_actual_installer_conflict_recovery_retry_and_uninstall(self):
        role, _, description = setup.catalog()[0]
        source = self.base / 'source'
        source.mkdir()
        (source / 'SKILL.md').write_text('# Version one\n', encoding='utf-8')
        project = self.base / 'project'
        project.mkdir()
        with patch.object(setup, 'catalog', return_value=[(role, source, description)]):
            self.assertEqual(setup.install(project, model_inventory=setup.EMPTY_INVENTORY,
                                           copy_skills=True)['status'], 'configured')
            target = project / '.claude/skills' / role['id']
            manifest = project / '.claude/agent-workflows/installation.json'
            before_manifest = manifest.read_bytes()
            original_id = identity(target)
            (source / 'SKILL.md').write_text('# Version two\n', encoding='utf-8')
            claim_id, calls = [], []
            def claim(ready):
                calls.append(ready); target.mkdir(); claim_id.append(identity(target))
            error = None
            with publication_hook(target, claim):
                try:
                    setup.install(project, model_inventory=setup.EMPTY_INVENTORY, copy_skills=True)
                except (OSError, ValueError) as exc:
                    error = exc
            self.assertEqual(len(calls), 1)
            self.assertIsNotNone(error)
            self.assertEqual(identity(target), claim_id[0])
            self.assertEqual(list(target.iterdir()), [])
            self.assertEqual(manifest.read_bytes(), before_manifest)
            self.assertEqual(setup.check(project)['status'], 'needs_setup')
            backup = error.recovery_path
            self.assertEqual(identity(backup), original_id)
            self.assertEqual((backup / 'SKILL.md').read_text(encoding='utf-8'), '# Version one\n')
            # Recovery here operates only on this test's known empty claimant.
            target.rmdir(); backup.rename(target)
            import shutil
            shutil.rmtree(backup.parent)
            self.assertEqual(setup.install(project, model_inventory=setup.EMPTY_INVENTORY,
                                           copy_skills=True)['status'], 'configured')
            self.assertEqual(setup.check(project)['status'], 'configured')
            self.assertEqual(setup.uninstall(project)['status'], 'uninstalled')

    def test_actual_cli_full_catalog_copy_lifecycle(self):
        project = self.base / 'cli-project'
        project.mkdir()
        inventory = self.base / 'inventory.json'
        inventory.write_text(json.dumps(setup.EMPTY_INVENTORY), encoding='utf-8')
        base = [sys.executable, str(ROOT / 'setup.py'), '--target', str(project)]
        for flags, status in [(['--copy-skills', '--model-inventory', str(inventory)], 'configured'),
                              (['--check'], 'configured'),
                              (['--copy-skills', '--model-inventory', str(inventory)], 'configured'),
                              (['--uninstall'], 'uninstalled')]:
            run = subprocess.run(base + flags, capture_output=True, encoding='utf-8', timeout=30,
                                 cwd=self.base, env=dict(os.environ, ANTHROPIC_BASE_URL=''))
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertEqual(json.loads(run.stdout)['status'], status)


if __name__ == '__main__':
    unittest.main()
