"""Global instruction input bounds and preflight replacement regressions."""
import json
import multiprocessing
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from scripts import setup_codex
from tests import test_codex_setup as fixtures

LIMIT = 16 * 1024 * 1024


def fifo_race(queue, repo, dest, state, home, phase):
    target = Path(home) / 'AGENTS.md'
    real_is_file = Path.is_file
    real_merge = setup_codex.merge_instructions
    replaced = False

    def swap():
        nonlocal replaced
        if not replaced:
            target.unlink()
            os.mkfifo(target)
            replaced = True

    def is_file(path):
        result = real_is_file(path)
        if phase == 'preflight' and path == target and result:
            swap()
        return result

    def merge(current, block):
        result = real_merge(current, block)
        if phase == 'locked-recheck':
            swap()
        return result

    try:
        with patch.object(Path, 'is_file', is_file), patch.object(setup_codex, 'merge_instructions', merge):
            setup_codex.synchronize(repo, dest, state, home)
    except BaseException as exc:
        queue.put(('error', type(exc).__name__, str(exc)))
    else:
        queue.put(('accepted', None, None))


class CodexInstructionReadTests(unittest.TestCase):
    setUp = fixtures.CodexSetupTests.setUp
    git = fixtures.CodexSetupTests.git
    write = fixtures.CodexSetupTests.write
    commit = fixtures.CodexSetupTests.commit
    sync = fixtures.CodexSetupTests.sync

    def assert_no_installed_files(self):
        self.assertFalse(self.dest.exists())
        for name in ('pending.json', 'installation.json', 'sync.lock', 'backups'):
            self.assertFalse((self.state / name).exists(), name)

    def test_oversize_global_instructions_cli_rejected_without_changes(self):
        self.home.mkdir()
        target = self.home / 'AGENTS.md'
        data = b'x' * (LIMIT + 1)
        target.write_bytes(data)
        command = [sys.executable, str(Path(setup_codex.__file__)), '--repo', str(self.repo),
                   '--dest', str(self.dest), '--state', str(self.state), '--codex-home', str(self.home)]
        for check in (False, True):
            with self.subTest(check=check):
                result = subprocess.run(command + (['--check'] if check else []),
                                        capture_output=True, text=True, timeout=8)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertEqual(json.loads(result.stdout)['status'], 'blocked')
                self.assertIn('bound', result.stdout)
                self.assertNotIn('Traceback', result.stderr)
                self.assertEqual(target.read_bytes(), data)
                self.assert_no_installed_files()

    def test_merged_instructions_limit_checked_before_writes(self):
        self.home.mkdir()
        target = self.home / 'AGENTS.md'
        data = b'x' * LIMIT
        target.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'bound'):
            self.sync()
        self.assertEqual(target.read_bytes(), data)
        self.assert_no_installed_files()

    def test_exact_limit_existing_instructions_remain_valid(self):
        self.sync()
        target = self.home / 'AGENTS.md'
        original = target.read_bytes()
        data = b'x' * (LIMIT - len(original)) + original
        target.write_bytes(data)
        self.assertEqual(self.sync(check=True)['status'], 'configured')
        self.sync()
        self.assertEqual(target.read_bytes(), data)
        self.assertFalse((self.state / 'pending.json').exists())

    def test_missing_and_binary_crlf_preferences_preserved(self):
        self.sync()
        self.assertEqual(self.sync(check=True)['status'], 'configured')
        target = self.home / 'AGENTS.md'
        preferences = b'outside preferences\xff\r\n'
        target.write_bytes(preferences + target.read_bytes())
        self.sync()
        self.assertTrue(target.read_bytes().startswith(preferences))
        self.assertEqual(self.sync(check=True)['status'], 'configured')

    def assert_fifo_race_rejected(self, phase):
        self.home.mkdir()
        target = self.home / 'AGENTS.md'
        target.write_bytes(b'preferences\r\n')
        context = multiprocessing.get_context('spawn')
        queue = context.Queue()
        process = context.Process(target=fifo_race,
                                  args=(queue, self.repo, self.dest, self.state, self.home, phase))
        process.start()
        process.join(3)
        if process.is_alive():
            process.terminate()
            process.join(3)
            if process.is_alive():
                self.fail('owned race child did not stop after termination')
            self.fail('global instruction FIFO replacement blocked synchronization')
        self.assertEqual(process.exitcode, 0)
        outcome = queue.get(timeout=1)
        self.assertEqual(outcome[0], 'error', outcome)
        self.assertEqual(outcome[1], 'ValueError', outcome)
        self.assertIn('regular', outcome[2])
        self.assert_no_installed_files()
        import stat
        self.assertTrue(stat.S_ISFIFO(target.stat().st_mode))
        queue.close()
        queue.join_thread()

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO requires POSIX')
    def test_fifo_replacement_after_type_check_is_nonblocking(self):
        self.assert_fifo_race_rejected('preflight')

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO requires POSIX')
    def test_fifo_replacement_before_locked_recheck_is_nonblocking(self):
        self.assert_fifo_race_rejected('locked-recheck')

    @unittest.skipUnless(os.name == 'posix', 'controlled symlink race requires POSIX')
    def test_symlink_replacement_after_type_check_is_rejected(self):
        self.home.mkdir()
        target = self.home / 'AGENTS.md'
        target.write_bytes(b'preferences')
        external = self.base / 'external.txt'
        external.write_bytes(b'external preferences')
        real = Path.is_file
        replaced = False

        def is_file(path):
            nonlocal replaced
            result = real(path)
            if path == target and result and not replaced:
                target.unlink()
                target.symlink_to(external)
                replaced = True
            return result

        with patch.object(Path, 'is_file', is_file):
            with self.assertRaisesRegex(ValueError, 'Linked'):
                self.sync()
        self.assertTrue(target.is_symlink())
        self.assertEqual(external.read_bytes(), b'external preferences')
        self.assert_no_installed_files()
