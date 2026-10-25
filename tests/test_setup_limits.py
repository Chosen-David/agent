"""Copied-skill resource policy and installer ownership boundaries."""
import importlib.util
import hashlib
import shutil
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import NamedTuple
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('limited_setup', os.environ.get('AGENT_SETUP_BASELINE', ROOT / 'setup.py'))
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
setup.REPO = ROOT


class Limits(NamedTuple):
    max_entries: int = 100000
    max_bytes: int = 268435456
    max_file_bytes: int = 33554432
    max_depth: int = 64


class SetupLimits(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.target = self.base / 'project'
        catalog = []
        for i, (role, _, description) in enumerate(setup.catalog()[:2]):
            source = self.base / ('source' + str(i))
            source.mkdir()
            (source / 'SKILL.md').write_bytes(b'abcd')
            catalog.append((role, source, description))
        self.catalog = catalog
        self.source = catalog[0][1]
        self.relative = '.claude/skills/' + catalog[0][0]['id']
        catalog_patch = patch.object(setup, 'catalog', return_value=catalog)
        catalog_patch.start()
        self.addCleanup(catalog_patch.stop)

    def limits(self, **kw):
        return getattr(setup, 'SkillCopyLimits', Limits)(**kw)

    def call(self, operation, *args, limits=None, **kw):
        # Original entry points have no policy keyword; this adapter adds no guard.
        if hasattr(setup, 'SkillCopyLimits') and limits is not None:
            kw['skill_limits'] = limits
        return operation(*args, **kw)

    def install(self, limits=None):
        return self.call(setup.install, self.target, limits=limits, copy_skills=True,
                         model_inventory=setup.EMPTY_INVENTORY)

    def snapshot(self, root, limits=None, **kw):
        return self.call(setup.skill_snapshot, root, limits=limits, **kw)

    def files(self):
        if not self.target.exists():
            return {}
        return {p.relative_to(self.target).as_posix(): p.read_bytes()
                for p in self.target.rglob('*') if p.is_file()}

    def test_single_file_policy_refuses_before_install_writes(self):
        with self.assertRaisesRegex(ValueError, 'file bytes'):
            self.install(self.limits(max_file_bytes=3))
        self.assertFalse(self.target.exists())

    def test_later_skill_aggregate_bytes_refuses_all_writes(self):
        with self.assertRaisesRegex(ValueError, 'total bytes'):
            self.install(self.limits(max_bytes=7))
        self.assertFalse(self.target.exists())

    def test_later_skill_aggregate_entries_refuses_all_writes(self):
        with self.assertRaisesRegex(ValueError, 'entries'):
            self.install(self.limits(max_entries=1))
        self.assertFalse(self.target.exists())

    def test_uninstall_resource_refusal_retains_manifest_and_all_files(self):
        self.install()
        before = self.files()
        with self.assertRaisesRegex(ValueError, 'total bytes'):
            self.call(setup.uninstall, self.target, limits=self.limits(max_bytes=7))
        self.assertEqual(self.files(), before)
        self.assertEqual(self.call(setup.uninstall, self.target, limits=self.limits(max_bytes=8))['preserved_local_edits'], [])

    def test_deep_source_refuses_before_install_writes(self):
        (self.source / 'one/two').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'depth'):
            self.install(self.limits(max_depth=1))
        self.assertFalse(self.target.exists())

    def test_check_reports_resource_reason(self):
        self.install()
        report = self.call(setup.check, self.target, limits=self.limits(max_bytes=7))
        self.assertEqual(report['status'], 'needs_setup')
        self.assertTrue(any('total bytes' in x for x in report['errors']))

    def test_exact_phase_limits_do_not_double_charge_and_reinstall(self):
        limits = self.limits(max_bytes=8, max_file_bytes=4, max_entries=2)
        self.assertEqual(self.install(limits)['status'], 'configured')
        before = self.files()
        self.assertEqual(self.install(limits)['status'], 'configured')
        self.assertEqual(self.files(), before)
        self.assertEqual(self.call(setup.check, self.target, limits=limits)['status'], 'configured')
        self.assertEqual(self.call(setup.uninstall, self.target, limits=limits)['preserved_local_edits'], [])

    def test_copy_time_limits_cleanup_and_no_old_replacement(self):
        self.install()
        skill = self.target / self.relative
        before_skill = setup.skill_snapshot(skill)
        manifest = self.target / '.claude/agent-workflows/installation.json'
        before_manifest = manifest.read_bytes()
        (self.source / 'SKILL.md').write_bytes(b'efgh')
        copier = setup.copy_skill
        for mode in ('file', 'depth', 'entries', 'alias'):
            with self.subTest(mode=mode):
                budgets = []
                def changed(source, staged, **kw):
                    self.assertEqual(Path(source), self.source)
                    budgets.append(kw['budget'])
                    if mode == 'file':
                        (self.source / 'SKILL.md').write_bytes(b'too large')
                    elif mode == 'depth':
                        (self.source / 'one/two').mkdir(parents=True)
                    elif mode == 'entries':
                        for name in ('x', 'y', 'z'):
                            (self.source / name).write_bytes(b'')
                    else:
                        (self.source / 'SKILL.md').unlink()
                        (self.source / 'SKILL.md').symlink_to(self.base / 'large')
                        (self.base / 'large').write_bytes(b'too large')
                    try:
                        return copier(source, staged, **kw)
                    finally:
                        if (self.source / 'SKILL.md').is_symlink():
                            (self.source / 'SKILL.md').unlink()
                        (self.source / 'SKILL.md').write_bytes(b'efgh')
                        shutil.rmtree(self.source / 'one', ignore_errors=True)
                        for name in ('x', 'y', 'z'):
                            (self.source / name).unlink(missing_ok=True)
                with patch.object(setup, 'copy_skill', side_effect=changed) as invoked:
                    reason = {'file': 'file bytes', 'depth': 'depth', 'entries': 'entries', 'alias': 'file bytes'}[mode]
                    with self.assertRaisesRegex(setup.SkillCopyLimitError, reason):
                        self.install(self.limits(max_bytes=8, max_file_bytes=4, max_depth=1,
                                                 max_entries=2 if mode == 'entries' else 16))
                self.assertEqual(invoked.call_count, 1)
                self.assertLessEqual(budgets[0].accepted_bytes, 8)
                self.assertLessEqual(budgets[0].read_bytes, 9)
                self.assertLessEqual(budgets[0].written_bytes, 8)
                self.assertEqual(setup.skill_snapshot(skill), before_skill)
                self.assertEqual(manifest.read_bytes(), before_manifest)
                self.assertEqual(list(skill.parent.glob('.skill-*')), [])
        self.assertEqual(self.install()['status'], 'configured')

    def test_legacy_129_depth_preserved(self):
        # Independently build the legacy fingerprint format for this ordinary tree.
        self.install()
        skill = self.target / self.relative
        deep = skill
        for _ in range(129):
            deep = deep / 'd'
            deep.mkdir()
        manifest = self.target / '.claude/agent-workflows/installation.json'
        data = json.loads(manifest.read_text())
        data['skill_copies'][self.relative] = {
            item.relative_to(skill).as_posix() + ('/' if item.is_dir() else ''):
            '' if item.is_dir() else hashlib.sha256(item.read_bytes()).hexdigest()
            for item in skill.rglob('*')}
        manifest.write_text(json.dumps(data))
        before = self.files()
        for operation in (setup.install, setup.uninstall):
            with self.subTest(operation=operation.__name__):
                with self.assertRaisesRegex(setup.SkillCopyLimitError, 'depth'):
                    self.call(operation, self.target, limits=self.limits(max_depth=128))
                self.assertEqual(self.files(), before)
                self.assertTrue(deep.is_dir())
        self.assertEqual(self.call(setup.check, self.target, limits=self.limits(max_depth=128))['status'], 'needs_setup')

    def test_limits_invalid_before_any_io(self):
        for operation in (setup.install, setup.check, setup.uninstall, setup.discover, setup.doctor):
            for policy in (self.limits(max_entries=True), self.limits(max_bytes=0), self.limits(max_depth=129)):
                with self.subTest(operation=operation.__name__, policy=policy), patch.object(setup, 'installation_root', side_effect=AssertionError('IO before valid policy')):
                    with self.assertRaises(ValueError):
                        self.call(operation, self.target, limits=policy)

    def test_copy_growth_after_fstat_cleans_owned_stage(self):
        self.install()
        skill = self.target / self.relative
        manifest = self.target / '.claude/agent-workflows/installation.json'
        before_skill, before_manifest = setup.skill_snapshot(skill), manifest.read_bytes()
        payload = self.source / 'SKILL.md'
        payload.write_bytes(b'efgh')
        copier, real_fstat = setup.copy_skill, os.fstat
        budgets = []
        def copying(source, staged, **kw):
            budgets.append(kw['budget'])
            def grow(fd):
                info = real_fstat(fd)
                payload.write_bytes(b'efghXYZ')
                return info
            try:
                with patch.object(setup.os, 'fstat', side_effect=grow):
                    return copier(source, staged, **kw)
            finally:
                payload.write_bytes(b'efgh')
        with patch.object(setup, 'copy_skill', side_effect=copying) as invoked:
            with self.assertRaisesRegex(setup.SkillCopyLimitError, 'file bytes'):
                self.install(self.limits(max_bytes=8, max_file_bytes=4))
        self.assertEqual(invoked.call_count, 1)
        self.assertEqual((budgets[0].accepted_bytes, budgets[0].read_bytes, budgets[0].written_bytes), (0, 5, 0))
        self.assertEqual(setup.skill_snapshot(skill), before_skill)
        self.assertEqual(manifest.read_bytes(), before_manifest)
        self.assertEqual(list(skill.parent.glob('.skill-*')), [])

    def test_directory_alias_retarget_during_copy_is_bounded(self):
        small, large = self.base / 'small', self.base / 'large'
        small.mkdir()
        large.mkdir()
        (small / 'payload').write_bytes(b'abcd')
        (large / 'payload').write_bytes(b'12345678')
        alias = self.source / 'alias'
        alias.symlink_to(small, target_is_directory=True)
        self.install()
        before_skill = setup.skill_snapshot(self.target / self.relative)
        manifest = self.target / '.claude/agent-workflows/installation.json'
        before_manifest = manifest.read_bytes()
        (self.source / 'SKILL.md').write_bytes(b'efgh')
        copier = setup.copy_skill
        def copying(source, staged, **kw):
            self.assertEqual(Path(source), self.source)
            alias.unlink()
            alias.symlink_to(large, target_is_directory=True)
            try:
                return copier(source, staged, **kw)
            finally:
                alias.unlink()
                alias.symlink_to(small, target_is_directory=True)
        with patch.object(setup, 'copy_skill', side_effect=copying) as invoked:
            with self.assertRaisesRegex(setup.SkillCopyLimitError, 'file bytes'):
                self.install(self.limits(max_bytes=12, max_file_bytes=4))
        self.assertEqual(invoked.call_count, 1)
        self.assertEqual(setup.skill_snapshot(self.target / self.relative), before_skill)
        self.assertEqual(manifest.read_bytes(), before_manifest)
        self.assertEqual(list((self.target / self.relative).parent.glob('.skill-*')), [])

    def test_supported_legacy_larger_copy_requires_explicit_policy_and_preserves_edits(self):
        self.install()
        before = self.files()
        with self.assertRaisesRegex(setup.SkillCopyLimitError, 'file bytes'):
            self.install(self.limits(max_file_bytes=3))
        self.assertEqual(self.files(), before)
        self.assertEqual(self.install(self.limits(max_file_bytes=4))['status'], 'configured')
        payload = self.target / self.relative / 'SKILL.md'
        payload.write_bytes(b'edit')
        with self.assertRaisesRegex(ValueError, 'locally edited skill'):
            self.install(self.limits(max_file_bytes=4))
        self.assertEqual(payload.read_bytes(), b'edit')
        self.assertIn(self.relative, self.call(setup.uninstall, self.target, limits=self.limits(max_file_bytes=4))['preserved_local_edits'])
        self.assertEqual(payload.read_bytes(), b'edit')

    def test_discover_and_doctor_propagate_policy(self):
        limits = self.limits(max_bytes=7)
        with patch.object(setup.subprocess, 'run') as run, patch.object(setup, 'load_json', return_value=setup.EMPTY_INVENTORY), patch.object(setup, 'install', return_value={}) as installing:
            run.return_value.returncode = 0
            setup.discover(self.target, skill_limits=limits)
        self.assertEqual(installing.call_args.kwargs['skill_limits'], limits)
        with patch.object(setup, 'check', return_value={'status': 'configured', 'model_routing': {}}) as checking, patch.object(setup.shutil, 'which', return_value=None):
            setup.doctor(self.target, skill_limits=limits)
        self.assertEqual(checking.call_args.kwargs['skill_limits'], limits)

    def test_cli_flags_and_invalid_policy(self):
        for flags in (['--skill-max-depth', '129'], ['--skill-max-bytes', '0']):
            result = subprocess.run([sys.executable, str(ROOT / 'setup.py'), '--target', str(self.target), *flags], capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertFalse(self.target.exists())
        result = subprocess.run([sys.executable, str(ROOT / 'setup.py'), '--help'], capture_output=True, text=True, timeout=20)
        for name in ('entries', 'bytes', 'file-bytes', 'depth'):
            self.assertIn('--skill-max-' + name, result.stdout)


core = setup

class SkillStreamLimits(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.source = self.base / 'source'
        self.source.mkdir()

    def limits(self, **kw):
        return core.SkillCopyLimits(**kw)

    def test_content_reference_empty_alias_ignore_and_copy(self):
        (self.source / 'a').write_bytes(b'abc')
        (self.source / 'empty').mkdir()
        (self.source / '.DS_Store').write_bytes(b'ignored')
        external = self.base / 'external'
        external.mkdir()
        (external / 'z').write_bytes(b'xy')
        (self.source / 'one').symlink_to(external, target_is_directory=True)
        (self.source / 'two').symlink_to(external, target_is_directory=True)
        expected = {'a': hashlib.sha256(b'abc').hexdigest(), 'empty/': '',
                    'one/': '', 'one/z': hashlib.sha256(b'xy').hexdigest(),
                    'two/': '', 'two/z': hashlib.sha256(b'xy').hexdigest()}
        budget = core.SkillBudget()
        self.assertEqual(core.skill_snapshot(self.source, follow_directory_links=True, budget=budget), expected)
        self.assertEqual((budget.entries, budget.accepted_bytes, budget.read_bytes), (7, 7, 7))
        copied = core.SkillBudget()
        destination = self.base / 'new'
        core.copy_skill(self.source, destination, budget=copied)
        self.assertEqual((copied.entries, copied.accepted_bytes, copied.read_bytes, copied.written_bytes), (7, 7, 7, 7))
        self.assertEqual(core.skill_snapshot(destination), expected)
        self.assertFalse((destination / 'one').is_symlink())
        self.assertFalse((destination / '.DS_Store').exists())
        with self.assertRaisesRegex(ValueError, 'directory symbolic link'):
            core.skill_snapshot(self.source)

    def test_file_boundary_and_metadata_refusal_without_content_read(self):
        (self.source / 'a').write_bytes(b'abcd')
        self.assertEqual(core.skill_snapshot(self.source, skill_limits=self.limits(max_file_bytes=4)),
                         {'a': hashlib.sha256(b'abcd').hexdigest()})
        with patch.object(core.os, 'read', side_effect=AssertionError('body read before metadata refusal')):
            with self.assertRaisesRegex(core.SkillCopyLimitError, 'file bytes'):
                core.skill_snapshot(self.source, skill_limits=self.limits(max_file_bytes=3))
        (self.source / 'a').unlink()
        sparse = self.source / 'sparse'
        with sparse.open('wb') as stream:
            stream.truncate(1048576)
        with patch.object(core.os, 'read', side_effect=AssertionError('sparse read')):
            with self.assertRaises(core.SkillCopyLimitError):
                core.skill_snapshot(self.source, skill_limits=self.limits(max_file_bytes=3))

    def test_growth_sentinel_and_latched_budget_no_more_reads(self):
        payload = self.source / 'a'
        payload.write_bytes(b'abcd')
        budget = core.SkillBudget(self.limits(max_bytes=4, max_file_bytes=4))
        real_fstat = os.fstat
        def grow(fd):
            info = real_fstat(fd)
            payload.write_bytes(b'abcdef')
            return info
        with patch.object(core.os, 'fstat', side_effect=grow):
            with self.assertRaises(core.SkillCopyLimitError):
                core.skill_snapshot(self.source, budget=budget)
        self.assertEqual((budget.accepted_bytes, budget.read_bytes, budget.written_bytes), (0, 5, 0))
        error = budget.error
        with patch.object(core.os, 'scandir', side_effect=AssertionError('enumerated after failure')), \
             patch.object(core.os, 'open', side_effect=AssertionError('opened after failure')):
            with self.assertRaises(core.SkillCopyLimitError) as caught:
                core.skill_snapshot(self.source, budget=budget)
        self.assertIs(caught.exception, error)

    def test_copy_growth_never_writes_sentinel(self):
        payload = self.source / 'a'
        payload.write_bytes(b'abcd')
        budget = core.SkillBudget(self.limits(max_bytes=4, max_file_bytes=4))
        real_fstat = os.fstat
        def grow(fd):
            info = real_fstat(fd)
            payload.write_bytes(b'abcdef')
            return info
        with patch.object(core.os, 'fstat', side_effect=grow):
            with self.assertRaises(core.SkillCopyLimitError):
                core.copy_skill(self.source, self.base / 'new', budget=budget)
        self.assertEqual((self.base / 'new/a').read_bytes(), b'')
        self.assertEqual((budget.read_bytes, budget.written_bytes), (5, 0))

    def test_entries_include_ignored_and_aggregate_roots(self):
        (self.source / 'a').write_bytes(b'a')
        (self.source / '.DS_Store').write_bytes(b'x')
        self.assertEqual(len(core.skill_snapshot(self.source, skill_limits=self.limits(max_entries=2))), 1)
        with self.assertRaisesRegex(core.SkillCopyLimitError, 'entries'):
            core.skill_snapshot(self.source, skill_limits=self.limits(max_entries=1))
        budget = core.SkillBudget(self.limits(max_entries=3))
        core.skill_snapshot(self.source, budget=budget)
        with self.assertRaisesRegex(core.SkillCopyLimitError, 'entries'):
            core.skill_snapshot(self.source, budget=budget)
        self.assertEqual(budget.entries, 3)

    def test_aggregate_bytes_does_not_reset_between_roots(self):
        (self.source / 'a').write_bytes(b'abcd')
        budget = core.SkillBudget(self.limits(max_bytes=7))
        core.skill_snapshot(self.source, budget=budget)
        with self.assertRaisesRegex(core.SkillCopyLimitError, 'total bytes'):
            core.skill_snapshot(self.source, budget=budget)
        self.assertEqual((budget.accepted_bytes, budget.read_bytes), (4, 4))

    def test_depth_boundary_and_bad_policy(self):
        (self.source / 'one').mkdir()
        core.skill_snapshot(self.source, skill_limits=self.limits(max_depth=1))
        (self.source / 'one/two').mkdir()
        with self.assertRaisesRegex(core.SkillCopyLimitError, 'depth'):
            core.skill_snapshot(self.source, skill_limits=self.limits(max_depth=1))
        for limits in (self.limits(max_entries=True), self.limits(max_bytes=0), self.limits(max_depth=129)):
            with self.subTest(limits=limits), patch.object(core.os, 'scandir', side_effect=AssertionError('invalid policy IO')):
                with self.assertRaises(ValueError):
                    core.skill_snapshot(self.source, skill_limits=limits)

    def test_finite_alias_fanout_and_cycle(self):
        external = self.base / 'leaf'
        external.mkdir()
        (external / 'x').write_bytes(b'x')
        for i in range(6):
            (self.source / str(i)).symlink_to(external, target_is_directory=True)
        full = core.skill_snapshot(self.source, follow_directory_links=True)
        self.assertEqual(len(full), 12)
        with self.assertRaisesRegex(core.SkillCopyLimitError, 'entries'):
            core.skill_snapshot(self.source, follow_directory_links=True, skill_limits=self.limits(max_entries=10))
        (external / 'cycle').symlink_to(self.source, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'cyclic directory'):
            core.skill_snapshot(self.source, follow_directory_links=True)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX FIFO required')
    def test_regular_to_fifo_swap_at_open_is_nonblocking(self):
        payload = self.source / 'a'
        payload.write_bytes(b'x')
        real_open = os.open
        def swap(path, flags, *a, **kw):
            payload.unlink()
            os.mkfifo(payload)
            return real_open(path, flags, *a, **kw)
        with patch.object(core.os, 'open', side_effect=swap):
            with self.assertRaisesRegex(ValueError, 'unsupported skill entry'):
                core.skill_snapshot(self.source)

    def test_file_descriptor_closed_after_read_error(self):
        payload = self.source / 'a'
        payload.write_bytes(b'x')
        real_open, descriptors = os.open, []
        def opened(*args, **kw):
            fd = real_open(*args, **kw)
            descriptors.append(fd)
            return fd
        with patch.object(core.os, 'open', side_effect=opened), patch.object(core.os, 'read', side_effect=OSError('injected read failure')):
            with self.assertRaisesRegex(OSError, 'injected read failure'):
                core.skill_snapshot(self.source)
        self.assertEqual(len(descriptors), 1)
        import errno
        with self.assertRaises(OSError) as caught:
            os.fstat(descriptors[0])
        self.assertEqual(caught.exception.errno, errno.EBADF)

    def test_explicit_limits_and_budget_must_agree_before_io(self):
        strict = core.SkillCopyLimits(max_file_bytes=3)
        for operation in (core.skill_snapshot, core.copy_skill):
            args = [self.source] if operation is core.skill_snapshot else [self.source, self.base / 'stage']
            with self.subTest(operation=operation.__name__), patch.object(core.os, 'scandir', side_effect=AssertionError('enumerated')), patch.object(core.os, 'open', side_effect=AssertionError('opened')), patch.object(Path, 'mkdir', side_effect=AssertionError('created')):
                with self.assertRaisesRegex(ValueError, 'differ from shared budget'):
                    operation(*args, skill_limits=strict, budget=core.SkillBudget(core.SkillCopyLimits(max_file_bytes=4)))
        self.assertFalse((self.base / 'stage').exists())



if __name__ == '__main__':
    unittest.main()
