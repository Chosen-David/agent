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

    def test_source_directory_aliases_copy_full_logical_contents(self):
        external = self.root / 'external'
        external.mkdir()
        (external / 'payload.md').write_text('outside source 中文', encoding='utf-8')
        nested = self.source / 'nested'
        nested.mkdir()
        (nested / 'local.md').write_text('inside source', encoding='utf-8')
        (self.source / 'internal').symlink_to(nested, target_is_directory=True)
        for name in ('external', 'second-alias'):
            (self.source / name).symlink_to(external, target_is_directory=True)
        empty = self.root / 'empty'
        empty.mkdir()
        (self.source / 'empty-alias').symlink_to(empty, target_is_directory=True)
        (external / 'nested-alias').symlink_to(nested, target_is_directory=True)
        self.assertEqual(setup.install(self.target, copy_skills=True)['status'], 'configured')
        skill = self.target / self.relative
        self.assertFalse((skill / 'external').is_symlink())
        self.assertEqual((skill / 'external/payload.md').read_bytes(), (external / 'payload.md').read_bytes())
        self.assertEqual((skill / 'internal/local.md').read_bytes(), (nested / 'local.md').read_bytes())
        self.assertTrue((skill / 'empty-alias').is_dir())
        self.assertEqual((skill / 'external/nested-alias/local.md').read_bytes(),
                         (nested / 'local.md').read_bytes())
        manifest_path = self.target / '.claude/agent-workflows/installation.json'
        before = manifest_path.read_bytes()
        copies = json.loads(before)['skill_copies'][self.relative]
        self.assertEqual(copies['external/payload.md'], copies['second-alias/payload.md'])
        setup.install(self.target)
        self.assertEqual(before, manifest_path.read_bytes())
        for operation in ('edit', 'add', 'delete'):
            with self.subTest(operation=operation):
                if operation == 'edit':
                    (external / 'payload.md').write_text('updated 中文', encoding='utf-8')
                elif operation == 'add':
                    (external / 'added.md').write_text('new child', encoding='utf-8')
                else:
                    (external / 'payload.md').unlink()
                self.assertEqual(setup.check(self.target)['status'], 'needs_setup')
                self.assertEqual(setup.install(self.target)['status'], 'configured')
                self.assertEqual(setup.skill_snapshot(skill),
                                 json.loads(manifest_path.read_bytes())['skill_copies'][self.relative])
                for name in ('external', 'second-alias'):
                    self.assertEqual((skill / name / 'payload.md').exists(),
                                     (external / 'payload.md').exists())
        self.assertEqual(setup.uninstall(self.target)['preserved_local_edits'], [])
        self.assertTrue((external / 'added.md').is_file())
        self.assertFalse(skill.exists())

    def test_source_directory_cycle_rejected_before_copy_or_writes(self):
        nested = self.source / 'nested'
        nested.mkdir()
        for destination in (self.source, nested):
            with self.subTest(destination=destination.name):
                alias = nested / 'cycle'
                alias.symlink_to(destination, target_is_directory=True)
                try:
                    with patch.object(setup.shutil, 'copytree', side_effect=AssertionError('cycle reached copy')):
                        with self.assertRaisesRegex(ValueError, 'cyclic directory'):
                            setup.install(self.target, copy_skills=True)
                    self.assertFalse(self.target.exists())
                finally:
                    alias.unlink()

    def test_installed_empty_directory_replaced_with_alias_is_preserved(self):
        (self.source / 'empty').mkdir()
        for nonempty in (False, True):
            with self.subTest(nonempty=nonempty):
                target = self.root / ('edited-' + str(nonempty))
                setup.install(target, copy_skills=True)
                installed = target / self.relative / 'empty'
                installed.rmdir()
                external = self.root / ('external-' + str(nonempty))
                external.mkdir()
                if nonempty:
                    (external / 'keep.md').write_text('human', encoding='utf-8')
                installed.symlink_to(external, target_is_directory=True)
                before = (target / '.claude/agent-workflows/installation.json').read_bytes()
                self.assertEqual(setup.check(target)['status'], 'needs_setup')
                with self.assertRaisesRegex(ValueError, 'directory symbolic link'):
                    setup.install(target)
                self.assertEqual(before, (target / '.claude/agent-workflows/installation.json').read_bytes())
                report = setup.uninstall(target)
                self.assertIn(self.relative, report['preserved_local_edits'])
                self.assertTrue(installed.is_symlink())
                self.assertTrue((target / self.relative / 'SKILL.md').is_file())
                self.assertTrue(external.is_dir())
                if nonempty:
                    self.assertEqual((external / 'keep.md').read_text(encoding='utf-8'), 'human')

    def test_cycle_in_later_skill_refuses_all_writes(self):
        role, _, description = setup.catalog()[0]
        later = self.root / 'later-skill'
        later.mkdir()
        (later / 'SKILL.md').write_text('later', encoding='utf-8')
        later_role = dict(role, id='code-organization')
        entries = [(role, self.source, description), (later_role, later, description)]
        with patch.object(setup, 'catalog', return_value=entries):
            setup.install(self.target, copy_skills=True)
            def snapshot():
                return sorted((p.relative_to(self.target).as_posix(),
                               ('link', str(p.readlink())) if p.is_symlink() else
                               ('file', p.read_bytes()) if p.is_file() else ('directory',))
                              for p in self.target.rglob('*'))
            before = snapshot()
            (self.source / 'new.md').write_text('valid but not to publish yet', encoding='utf-8')
            (later / 'cycle').symlink_to(later, target_is_directory=True)
            for target in (self.target, self.root / 'fresh'):
                with self.subTest(target=target.name):
                    with patch.object(setup.shutil, 'copytree', side_effect=AssertionError('cycle reached copy')):
                        with self.assertRaisesRegex(ValueError, 'cyclic directory'):
                            setup.install(target, copy_skills=True)
            self.assertEqual(before, snapshot())
            self.assertFalse((self.root / 'fresh').exists())

    def test_empty_source_alias_legacy_manifest_and_link_mode(self):
        empty = self.root / 'empty'
        empty.mkdir()
        (self.source / 'empty-alias').symlink_to(empty, target_is_directory=True)
        setup.install(self.target, copy_skills=True)
        manifest_path = self.target / '.claude/agent-workflows/installation.json'
        manifest = json.loads(manifest_path.read_bytes())
        # Old rglob fingerprint and copied-tree fingerprint coincide for empty aliases.
        manifest['skill_copies'][self.relative] = setup.skill_snapshot(self.target / self.relative)
        manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        self.assertEqual(setup.check(self.target)['status'], 'configured')
        self.assertEqual(setup.install(self.target)['status'], 'configured')
        link_target = self.root / 'linked'
        self.assertEqual(setup.install(link_target)['status'], 'configured')
        installed = link_target / self.relative
        self.assertEqual(installed.is_symlink(), os.name != 'nt')
        if os.name == 'nt':
            installed_manifest = json.loads(
                (link_target / '.claude/agent-workflows/installation.json').read_bytes())
            self.assertEqual(installed_manifest['skill_copies'][self.relative],
                             setup.skill_snapshot(installed))
        else:
            self.assertEqual(installed.resolve(), self.source.resolve())
        self.assertEqual(setup.install(link_target, copy_skills=True)['status'], 'configured')
        self.assertEqual(installed.is_symlink(), os.name != 'nt')
        self.assertEqual(setup.check(link_target)['status'], 'configured')
        self.assertEqual(setup.uninstall(link_target)['preserved_local_edits'], [])
        self.assertTrue((self.source / 'empty-alias').is_symlink())
        self.assertTrue(empty.is_dir())

    def test_file_alias_and_ignored_directory_alias_lifecycle(self):
        canonical = self.root / 'canonical.md'
        canonical.write_text('canonical 中文', encoding='utf-8')
        (self.source / 'reference.md').symlink_to(canonical)
        (self.source / '__pycache__').symlink_to(self.source, target_is_directory=True)
        (self.source / 'ignored.pyc').symlink_to(self.source, target_is_directory=True)
        (self.source / '.DS_Store').symlink_to(self.source, target_is_directory=True)
        nested = self.source / 'normal'
        nested.mkdir()
        for name in ('ignored.pyc', '.DS_Store'):
            ignored = nested / name
            ignored.mkdir()
            (ignored / 'hidden.md').write_text('ignored subtree', encoding='utf-8')
        self.assertEqual(setup.install(self.target, copy_skills=True)['status'], 'configured')
        installed = self.target / self.relative / 'reference.md'
        self.assertFalse(installed.is_symlink())
        self.assertEqual(installed.read_bytes(), canonical.read_bytes())
        self.assertFalse((self.target / self.relative / '__pycache__').exists())
        self.assertEqual(list((self.target / self.relative / 'normal').iterdir()), [])
        canonical.write_text('updated 中文', encoding='utf-8')
        self.assertEqual(setup.check(self.target)['status'], 'needs_setup')
        self.assertEqual(setup.install(self.target)['status'], 'configured')
        self.assertEqual(installed.read_bytes(), canonical.read_bytes())
        self.assertEqual(setup.uninstall(self.target)['preserved_local_edits'], [])
        self.assertTrue(canonical.is_file())

    def test_copy_stage_drift_preserves_owned_generation(self):
        payload = self.source / 'SKILL.md'
        original = payload.read_bytes()
        copier = shutil.copytree
        for established in (False, True):
            with self.subTest(established=established):
                payload.write_bytes(original)
                target = self.root / ('update' if established else 'fresh')
                skill = target / self.relative
                manifest = target / '.claude/agent-workflows/installation.json'
                if established:
                    setup.install(target, copy_skills=True)
                previous = setup.skill_snapshot(skill) if established else None
                manifest_before = manifest.read_bytes() if established else None
                expected = original + b'\nselected update\n'
                payload.write_bytes(expected)
                calls = []

                def changing_copy(source, staged, *args, **kwargs):
                    if Path(source) != self.source:
                        return copier(source, staged, *args, **kwargs)
                    payload.write_bytes(expected + b'intermediate bytes\n')
                    try:
                        calls.append(str(staged))
                        return copier(source, staged, *args, **kwargs)
                    finally:
                        payload.write_bytes(expected)

                with patch.object(setup.shutil, 'copytree', side_effect=changing_copy):
                    with self.assertRaisesRegex(ValueError, 'source changed during copy'):
                        setup.install(target, copy_skills=True)
                self.assertEqual(len(calls), 1)
                if established:
                    self.assertEqual(setup.skill_snapshot(skill), previous)
                    self.assertEqual(manifest.read_bytes(), manifest_before)
                else:
                    self.assertFalse(skill.exists())
                    self.assertFalse(manifest.exists())
                self.assertEqual(list(skill.parent.glob('.skill-*')), [])
                self.assertEqual(setup.install(target, copy_skills=True)['status'], 'configured')
                self.assertEqual((skill / 'SKILL.md').read_bytes(), expected)
                before = manifest.read_bytes()
                setup.install(target)
                self.assertEqual(manifest.read_bytes(), before)
                self.assertEqual(setup.uninstall(target)['preserved_local_edits'], [])

    def test_copy_stage_alias_subtree_edit_add_delete_rejected(self):
        external = self.root / 'external-stage'
        external.mkdir()
        child = external / 'child.md'
        (self.source / 'alias-stage').symlink_to(external, target_is_directory=True)
        copier = shutil.copytree
        for operation in ('edit', 'add', 'delete'):
            with self.subTest(operation=operation):
                child.write_bytes(b'original')
                target = self.root / operation
                setup.install(target, copy_skills=True)
                skill = target / self.relative
                before = setup.skill_snapshot(skill)
                manifest = target / '.claude/agent-workflows/installation.json'
                manifest_before = manifest.read_bytes()
                marker = self.source / ('update-' + operation + '.md')
                marker.write_bytes(b'selected update')

                def changing_copy(source, staged, *args, **kwargs):
                    if Path(source) != self.source:
                        return copier(source, staged, *args, **kwargs)
                    added = external / 'added.md'
                    if operation == 'edit':
                        child.write_bytes(b'intermediate')
                    elif operation == 'add':
                        added.write_bytes(b'intermediate')
                    else:
                        child.unlink()
                    try:
                        return copier(source, staged, *args, **kwargs)
                    finally:
                        child.write_bytes(b'original')
                        added.unlink(missing_ok=True)

                with patch.object(setup.shutil, 'copytree', side_effect=changing_copy):
                    with self.assertRaisesRegex(ValueError, 'source changed during copy'):
                        setup.install(target, copy_skills=True)
                self.assertEqual(setup.skill_snapshot(skill), before)
                self.assertEqual(manifest.read_bytes(), manifest_before)
                self.assertEqual(setup.install(target)['status'], 'configured')

    def test_copy_stage_ignored_change_and_restored_source_are_coherent(self):
        payload = self.source / 'SKILL.md'
        original = payload.read_bytes()
        copier = shutil.copytree

        def coherent_copy(source, staged, *args, **kwargs):
            if Path(source) == self.source:
                payload.write_bytes(original + b'transient before copy')
                payload.write_bytes(original)
                (self.source / '.DS_Store').write_bytes(b'ignored')
            return copier(source, staged, *args, **kwargs)

        with patch.object(setup.shutil, 'copytree', side_effect=coherent_copy):
            self.assertEqual(setup.install(self.target, copy_skills=True)['status'], 'configured')
        self.assertEqual((self.target / self.relative / 'SKILL.md').read_bytes(), original)
        self.assertFalse((self.target / self.relative / '.DS_Store').exists())

    def test_copy_stage_invalid_or_mismatched_tree_never_moves_destination(self):
        setup.install(self.target, copy_skills=True)
        skill = self.target / self.relative
        previous = setup.skill_snapshot(skill)
        expected = setup.skill_snapshot(self.source, follow_directory_links=True)
        copier = shutil.copytree
        for mode in ('copy-error', 'invalid', 'mismatch'):
            with self.subTest(mode=mode):
                def invalid_copy(source, staged, *args, **kwargs):
                    if mode == 'copy-error':
                        raise OSError('injected copy failure')
                    result = copier(source, staged, *args, **kwargs)
                    if mode == 'invalid':
                        (Path(staged) / 'unexpected-alias').symlink_to(self.source, target_is_directory=True)
                    else:
                        (Path(staged) / 'SKILL.md').write_bytes(b'mismatched stage')
                    return result

                with patch.object(setup.shutil, 'copytree', side_effect=invalid_copy), \
                     patch.object(Path, 'rename', side_effect=AssertionError('destination moved')):
                    with self.assertRaises((ValueError, OSError)):
                        setup.replace_skill_copy(skill, self.source, previous, expected)
                self.assertEqual(setup.skill_snapshot(skill), previous)
                self.assertEqual(list(skill.parent.glob('.skill-*')), [])

    def test_copy_stage_publish_failure_restores_previous_copy(self):
        setup.install(self.target, copy_skills=True)
        skill = self.target / self.relative
        previous = setup.skill_snapshot(skill)
        (self.source / 'update.md').write_bytes(b'new generation')
        expected = setup.skill_snapshot(self.source, follow_directory_links=True)
        rename = Path.rename

        def fail_publish(path, target):
            if path.name == 'new' and Path(target) == skill:
                raise OSError('injected publish failure')
            return rename(path, target)

        with patch.object(Path, 'rename', new=fail_publish):
            with self.assertRaisesRegex(OSError, 'publish failure'):
                setup.replace_skill_copy(skill, self.source, previous, expected)
        self.assertEqual(setup.skill_snapshot(skill), previous)
        setup.replace_skill_copy(skill, self.source, previous, expected)
        self.assertEqual(setup.skill_snapshot(skill), expected)

    def test_simple_entry_loads_orchestration_only_on_demand(self):
        self.assertNotIn('@.claude/agent-workflows/orchestrator.md', setup.block())
        self.assertIn('`.claude/agent-workflows/orchestrator.md`', setup.block())
        self.assertIn('简单、目标明确的任务直接完成', setup.block())


if __name__ == '__main__':
    unittest.main()
