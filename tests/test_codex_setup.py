import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.setup_codex import synchronize


class CodexSetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.repo = self.base/'repo'
        self.repo.mkdir()
        self.dest, self.state, self.home = self.base/'skills', self.base/'state', self.base/'codex'
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        for name in ['one', 'two']:
            self.write('skills/'+name+'/SKILL.md', '---\nname: '+name+'\ndescription: Fixture\n---\nInstructions\n')
        self.write('skills/one/old.txt', 'original')
        self.write('config/role_registry.json', json.dumps({'roles': [
            {'id': name, 'skill': 'skills/'+name+'/SKILL.md'} for name in ['one', 'two']]}))
        self.write('templates/codex_global_instructions.md',
                   '<!-- chosen-agent:begin -->\n{{REPOSITORY}}\n<!-- chosen-agent:end -->\n')
        self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.repo, stderr=subprocess.STDOUT)

    def write(self, relative, data):
        p = self.repo/relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data, encoding='utf-8')

    def commit(self):
        self.git('add', '-A')
        self.git('commit', '-qm', 'fixture')

    def sync(self, **kwargs):
        return synchronize(self.repo, self.dest, self.state, self.home, **kwargs)

    def test_install_idempotence_check_and_preserve_global_preferences(self):
        self.home.mkdir()
        (self.home/'AGENTS.md').write_bytes(b'Existing preference\r\n')
        self.assertEqual(self.sync()['skills'], 2)
        self.sync()
        self.assertEqual(self.sync(check=True)['status'], 'configured')
        text = (self.home/'AGENTS.md').read_bytes()
        self.assertTrue(text.startswith(b'Existing preference\r\n'))
        self.assertEqual(text.count(b'<!-- chosen-agent:begin -->'), 1)
        (self.dest/'one/__pycache__').mkdir()
        (self.dest/'one/__pycache__/runtime.pyc').write_bytes(b'cache')
        self.sync(check=True)

    def test_foreign_collision_and_exact_explicit_adoption(self):
        (self.dest/'one').mkdir(parents=True)
        (self.dest/'one/SKILL.md').write_bytes(b'user skill')
        with self.assertRaisesRegex(ValueError, 'Unowned'):
            self.sync()
        self.assertFalse(self.home.exists())
        with self.assertRaisesRegex(ValueError, 'Unowned'):
            self.sync(adopt=True)
        for source in self.git('ls-tree', '-r', '--name-only', 'HEAD', 'skills').decode().splitlines():
            p = self.dest/source.removeprefix('skills/')
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(self.git('show', 'HEAD:'+source))
        self.sync(adopt=True)
        self.sync(check=True)

    def test_archive_matches_git_blob_when_host_uses_crlf(self):
        self.git('config', 'core.autocrlf', 'true')
        self.sync()
        self.assertEqual((self.dest/'one/SKILL.md').read_bytes(), self.git('show', 'HEAD:skills/one/SKILL.md'))
        self.assertNotIn(b'\r\n', (self.dest/'one/SKILL.md').read_bytes())

    def test_published_update_removes_only_unchanged_owned_file_and_backs_up(self):
        self.sync()
        old = (self.dest/'one/SKILL.md').read_bytes()
        (self.repo/'skills/one/old.txt').unlink()
        self.write('skills/one/SKILL.md', old.decode()+'Updated\n')
        self.write('skills/two/new.txt', 'new API')
        self.commit()
        self.sync()
        self.assertFalse((self.dest/'one/old.txt').exists())
        self.assertEqual((self.dest/'two/new.txt').read_text(), 'new API')
        self.assertTrue(any(p.read_bytes() == old for p in (self.state/'backups').rglob('SKILL.md')))
        self.sync(check=True)

    def test_local_edit_prevents_entire_update(self):
        self.sync()
        (self.dest/'one/old.txt').write_text('private edit')
        self.write('skills/two/new.txt', 'should not install')
        self.commit()
        before = (self.home/'AGENTS.md').read_bytes()
        with self.assertRaisesRegex(ValueError, 'Locally changed'):
            self.sync()
        self.assertFalse((self.dest/'two/new.txt').exists())
        self.assertEqual((self.dest/'one/old.txt').read_text(), 'private edit')
        self.assertEqual((self.home/'AGENTS.md').read_bytes(), before)

    def test_managed_instruction_edit_is_preserved(self):
        self.sync()
        p = self.home/'AGENTS.md'
        p.write_bytes(p.read_bytes().replace(b'<!-- chosen-agent:end -->', b'Custom\n<!-- chosen-agent:end -->'))
        before = p.read_bytes()
        with self.assertRaisesRegex(ValueError, 'instructions were edited'):
            self.sync()
        self.assertEqual(p.read_bytes(), before)

    def test_symlink_escape_and_extra_user_file_are_rejected(self):
        self.sync()
        (self.dest/'two/user.txt').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'Locally changed'):
            self.sync()
        (self.dest/'two/user.txt').unlink()
        outside = self.base/'outside.txt'
        outside.write_text('private')
        try:
            os.symlink(outside, self.dest/'two/escape.txt')
        except OSError:
            self.skipTest('Host does not permit creating fixture symlinks')
        with self.assertRaisesRegex(ValueError, 'Linked'):
            self.sync()
        self.assertEqual(outside.read_text(), 'private')

    def test_dirty_source_shadowed_instructions_and_stale_revision(self):
        self.sync()
        self.write('skills/one/extra.txt', 'uncommitted')
        with self.assertRaisesRegex(ValueError, 'source is dirty'):
            self.sync()
        self.commit()
        with self.assertRaisesRegex(ValueError, 'stale'):
            self.sync(check=True)
        self.sync()
        (self.home/'AGENTS.override.md').write_text('override')
        with self.assertRaisesRegex(ValueError, 'shadows'):
            self.sync()

    def test_interrupted_write_retains_backup_and_blocks_replay(self):
        self.sync()
        original = (self.state/'installation.json').read_bytes()
        self.write('skills/one/old.txt', 'next version')
        self.commit()
        from scripts.setup_codex import atomic
        def fail(path, data):
            if path == self.dest/'one/old.txt':
                raise OSError('fixture I/O failure')
            return atomic(path, data)
        with patch('scripts.setup_codex.atomic', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'fixture'):
                self.sync()
        self.assertTrue((self.state/'pending.json').is_file())
        self.assertEqual((self.state/'installation.json').read_bytes(), original)
        self.assertTrue(any(p.read_text() == 'original' for p in (self.state/'backups').rglob('old.txt')))
        with self.assertRaisesRegex(ValueError, 'Interrupted'):
            self.sync()


if __name__ == '__main__':
    unittest.main()
