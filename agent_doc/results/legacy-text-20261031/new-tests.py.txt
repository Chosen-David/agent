"""Legacy TASK pointer reads use the installed-text boundary before mutation."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from tests import test_setup_text as fixture
from agent_runtime.external_json import DEFAULT_JSON_LIMIT

setup = fixture.setup

RACE = '''
import json, os, sys
from pathlib import Path
from unittest.mock import patch
import setup
target, mode = Path(sys.argv[1]), sys.argv[2]
legacy = target / 'TASK.md'
external = target.parent / 'external-pointer.txt'
external.write_bytes(b'External pointer\\n')
original = Path.is_file
changed = False
def is_file(path):
    global changed
    if path == legacy and not changed:
        changed = True
        legacy.unlink()
        if mode == 'fifo':
            os.mkfifo(legacy)
        else:
            try:
                legacy.symlink_to(external)
            except OSError as exc:
                legacy.write_bytes(b'Legacy pointer\\n')
                print(json.dumps({'skip': type(exc).__name__}))
                raise SystemExit(0)
        return True
    return original(path)
with patch.object(Path, 'is_file', is_file):
    try:
        setup.install(target, model_inventory=setup.EMPTY_INVENTORY)
    except ValueError as exc:
        print(json.dumps({'blocked': True, 'reason': str(exc), 'changed': changed}))
    else:
        print(json.dumps({'blocked': False, 'changed': changed}))
'''


class LegacyTaskTextTests(unittest.TestCase):
    setUp = fixture.SetupTextTests.setUp
    snapshot = fixture.SetupTextTests.snapshot
    cli = fixture.SetupTextTests.cli

    def test_oversize_legacy_pointer_refused_before_mutation(self):
        legacy = self.project / 'TASK.md'
        with legacy.open('wb') as stream:
            stream.truncate(DEFAULT_JSON_LIMIT + 1)
        before = self.snapshot()
        for command in [(), ('--check',), ('--doctor',)]:
            with self.subTest(command=command):
                self.cli(command, 2)
                self.assertEqual(self.snapshot(), before)

    def test_exact_byte_bound_pointer_remains_accepted(self):
        legacy = self.project / 'TASK.md'
        legacy.write_bytes(b' ' * DEFAULT_JSON_LIMIT)
        before = self.snapshot()
        self.cli(('--check',), 0)
        self.assertEqual(self.snapshot(), before)

    def race(self, mode):
        legacy = self.project / 'TASK.md'
        legacy.write_bytes(b'Legacy pointer\n')
        before = self.snapshot()
        try:
            result = subprocess.run(
                [sys.executable, '-B', '-c', RACE, str(self.project), mode],
                cwd=setup.REPO, env=self.env, capture_output=True,
                encoding='utf-8', errors='strict', timeout=3)
        except subprocess.TimeoutExpired:
            self.fail('legacy pointer replacement blocked the installer')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        value = json.loads(result.stdout)
        if 'skip' in value:
            self.skipTest('file symlink unavailable: ' + value['skip'])
        self.assertTrue(value['changed'])
        self.assertTrue(value['blocked'], value)
        after = self.snapshot()
        before.pop('TASK.md')
        after.pop('TASK.md')
        self.assertEqual(after, before)
        self.assertEqual((self.root / 'external-pointer.txt').read_bytes(), b'External pointer\n')

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO requires POSIX')
    def test_fifo_replacement_after_type_check_is_refused(self):
        self.race('fifo')

    def test_link_replacement_after_type_check_is_refused(self):
        self.race('link')

    def test_valid_pointer_newlines_and_lifecycle_preserved(self):
        legacy = self.project / 'TASK.md'
        canonical = self.project / 'agent_doc/task/TASK.md'
        canonical_bytes = canonical.read_bytes()
        for newline in (b'\r\n', b'\r'):
            with self.subTest(newline=newline):
                setup.install(self.project, model_inventory=setup.EMPTY_INVENTORY)
                pointer = '旧任务导航\nSee agent_doc/task/TASK.md.\n'.encode().replace(b'\n', newline)
                legacy.write_bytes(pointer)
                self.cli((), 0)
                self.cli(('--check',), 0)
                self.cli(('--doctor',), 0)
                self.cli(('--uninstall',), 0)
                self.assertEqual(legacy.read_bytes(), pointer)
                self.assertEqual(canonical.read_bytes(), canonical_bytes)

    def test_second_active_task_list_remains_refused(self):
        (self.project / 'TASK.md').write_bytes(b'- [ ] [OLD-1] old task\r\n')
        before = self.snapshot()
        for command in [(), ('--check',), ('--doctor',)]:
            with self.subTest(command=command):
                self.cli(command, 2)
                self.assertEqual(self.snapshot(), before)

    def test_legacy_without_canonical_still_requires_migration(self):
        (self.project / 'agent_doc/task/TASK.md').unlink()
        (self.project / 'TASK.md').write_bytes(b'Legacy pointer\n')
        before = self.snapshot()
        for command in [(), ('--check',), ('--doctor',)]:
            with self.subTest(command=command):
                self.cli(command, 2)
                self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()
