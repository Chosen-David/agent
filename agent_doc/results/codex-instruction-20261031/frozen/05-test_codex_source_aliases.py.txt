import os
import json
from pathlib import Path
import unittest

from tests import test_codex_setup as fixtures


class CodexSourceAliasTests(unittest.TestCase):
    setUp = fixtures.CodexSetupTests.setUp
    git = fixtures.CodexSetupTests.git
    write = fixtures.CodexSetupTests.write
    commit = fixtures.CodexSetupTests.commit
    sync = fixtures.CodexSetupTests.sync

    def alias(self, name, target):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target)

    def assert_uninstalled(self):
        self.assertFalse(self.dest.exists())
        self.assertFalse(self.home.exists())
        self.assertFalse(self.state.exists())

    def test_committed_shared_files_install_as_exact_regular_bytes(self):
        targets = ['shared-references/policy.md', 'agent_runtime/helper.py',
                   'plugins/research-assistant/shared-scripts/helper.py']
        for i, target in enumerate(targets):
            self.write(target, '中文 shared\n')
            self.alias('skills/one/references/shared%d.md' % i,
                       os.path.relpath(self.repo / target, self.repo / 'skills/one/references'))
        self.alias('shared-references/chain.md', 'policy.md')
        self.alias('skills/two/chain.md', '../../shared-references/chain.md')
        self.commit()
        self.git('config', 'core.autocrlf', 'true')
        self.assertEqual(self.sync()['status'], 'configured')
        for i, target in enumerate(targets):
            path = self.dest / ('one/references/shared%d.md' % i)
            self.assertFalse(path.is_symlink())
            self.assertEqual(path.read_bytes(), self.git('show', 'HEAD:' + target))
        self.assertEqual((self.dest / 'two/chain.md').read_bytes(),
                         self.git('show', 'HEAD:shared-references/policy.md'))
        self.assertEqual(self.sync(check=True)['status'], 'configured')
        self.assertEqual(self.sync()['updated_files'], 0)

    def test_dirty_canonical_target_blocks_before_installation(self):
        self.write('shared-references/policy.md', 'committed\n')
        self.alias('skills/one/policy.md', '../../shared-references/policy.md')
        self.commit()
        self.write('shared-references/policy.md', 'uncommitted secret\n')
        with self.assertRaisesRegex(ValueError, 'source is dirty'):
            self.sync()
        self.assert_uninstalled()

    def test_unrelated_uncommitted_shared_file_is_not_installed(self):
        self.write('shared-references/policy.md', 'committed\n')
        self.alias('skills/one/policy.md', '../../shared-references/policy.md')
        self.commit()
        self.write('shared-references/unrelated.md', 'private unrelated\n')
        self.assertEqual(self.sync()['status'], 'configured')
        self.assertFalse((self.dest / 'one/unrelated.md').exists())

    def test_unsafe_alias_targets_fail_closed(self):
        path = self.repo / 'skills/one/bad.md'
        for target in ('/etc/passwd', '../../../../outside',
                       '..\\..\\shared-references\\policy.md', '../../config/role_registry.json'):
            with self.subTest(target=target):
                if path.is_symlink():
                    path.unlink()
                self.alias('skills/one/bad.md', target)
                self.commit()
                with self.assertRaisesRegex(ValueError, 'Symlink in committed skill|committed skill alias'):
                    self.sync()
                self.assert_uninstalled()

    def test_missing_directory_and_cyclic_targets_fail_closed(self):
        self.write('shared-references/directory/child.md', 'child\n')
        self.alias('shared-references/cycle-a.md', 'cycle-b.md')
        self.alias('shared-references/cycle-b.md', 'cycle-a.md')
        path = self.repo / 'skills/one/bad.md'
        for target in ('../../shared-references/missing.md',
                       '../../shared-references/directory', '../../shared-references/cycle-a.md'):
            with self.subTest(target=target):
                if path.is_symlink():
                    path.unlink()
                self.alias('skills/one/bad.md', target)
                self.commit()
                with self.assertRaisesRegex(ValueError, 'Symlink in committed skill|committed skill alias'):
                    self.sync()
                self.assert_uninstalled()

    def test_worktree_target_link_is_rejected_without_reading_external_bytes(self):
        self.write('shared-references/policy.md', 'committed\n')
        self.alias('skills/one/policy.md', '../../shared-references/policy.md')
        self.commit()
        outside = self.base / 'outside.md'
        outside.write_bytes(b'private outside')
        target = self.repo / 'shared-references/policy.md'
        target.unlink()
        target.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'source is dirty'):
            self.sync()
        self.assert_uninstalled()
        self.assertEqual(outside.read_bytes(), b'private outside')


    def test_gitlink_target_is_not_exported(self):
        revision = self.git('rev-parse', 'HEAD').decode().strip()
        self.alias('skills/one/bad.py', '../../agent_runtime/submodule.py')
        self.git('add', '-A')
        self.git('update-index', '--add', '--cacheinfo', '160000,' + revision + ',agent_runtime/submodule.py')
        self.git('commit', '-qm', 'gitlink fixture')
        with self.assertRaisesRegex(ValueError, 'committed skill alias'):
            self.sync()
        self.assert_uninstalled()

    def test_excessive_alias_chain_is_rejected(self):
        for i in range(40):
            self.alias('shared-references/chain%d.md' % i, 'chain%d.md' % (i + 1))
        self.write('shared-references/chain40.md', 'terminal\n')
        self.alias('skills/one/deep.md', '../../shared-references/chain0.md')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'committed skill alias'):
            self.sync()
        self.assert_uninstalled()


    def test_global_instruction_template_alias_remains_forbidden(self):
        template = self.repo / 'templates/codex_global_instructions.md'
        self.write('shared-references/template.md', template.read_text())
        template.unlink()
        template.symlink_to('../shared-references/template.md')
        self.commit()
        for overlap in (False, True):
            with self.subTest(registered_prefix_overlap=overlap):
                if overlap:
                    self.write('templates/SKILL.md', '---\nname: one\ndescription: Fixture\n---\nInstructions\n')
                    self.write('config/role_registry.json', json.dumps({'roles': [
                        {'id': 'one', 'skill': 'templates/SKILL.md'}]}))
                    self.commit()
                with self.assertRaisesRegex(ValueError, 'Symlink'):
                    self.sync()
                self.assert_uninstalled()


if __name__ == '__main__':
    unittest.main()
