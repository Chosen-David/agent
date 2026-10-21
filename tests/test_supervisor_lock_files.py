"""Actual supervisor entry points reject special lock files before side effects."""
import json
import fcntl
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.task_manifest import atomic_json, prepare
from agent_runtime.task_supervisor import _lock_file, worker


ROOT = Path(__file__).resolve().parents[1]
CHILD = '''
import json, os, sys
from pathlib import Path
from unittest.mock import patch
from agent_runtime.task_supervisor import start, worker
from agent_runtime.project_docs import guard_write_path
root = Path(sys.argv[1])
mode = sys.argv[2]
def guarded(path):
    target = guard_write_path(path)
    if len(sys.argv) > 3:
        target.unlink()
        os.mkfifo(target)
    return target
try:
    with patch('agent_runtime.task_supervisor.shutil.which', return_value='/fixture/tmux'), \\
         patch('agent_runtime.task_supervisor.Store', side_effect=AssertionError('DB reached')), \\
         patch('agent_runtime.task_supervisor.tmux', side_effect=AssertionError('tmux reached')), \\
         patch('agent_runtime.task_supervisor.guard_write_path', side_effect=guarded):
        if mode == 'launch':
            start(root / 'plan.json', root, root / 'run', allow_legacy=True)
        else:
            os.environ['TMUX'] = 'explicit-test-fixture'
            worker({'project_root': str(root), 'state_dir': str(root / 'run')})
except (OSError, ValueError) as exc:
    print(json.dumps({'rejected': type(exc).__name__, 'error': str(exc)}))
else:
    raise AssertionError('special lock accepted')
'''


@unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX special file fixtures required')
class SupervisorLockFileTests(unittest.TestCase):
    def test_special_locks_fail_promptly_at_real_entry_points(self):
        for mode in ('launch', 'worker'):
          for kind in ('fifo', 'directory', 'symlink', 'replaced-fifo'):
            with self.subTest(mode=mode, kind=kind), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                task = root / 'TASK.md'
                task.write_text('- [ ] [T1] Verify local artifact\n')
                plan = prepare(task, 'lock-fixture', 'manual', 'unit-test', review_required=False)
                plan['tasks'][0].update(action='verify_artifacts', done_when={'artifacts': []})
                atomic_json(root / 'plan.json', plan)
                state = root / 'run'
                state.mkdir()
                target = state / (mode + '.lock')
                if kind == 'fifo':
                    os.mkfifo(target)
                elif kind == 'directory':
                    target.mkdir()
                elif kind == 'symlink':
                    target.symlink_to(root / 'plan.json')
                else:
                    target.write_bytes(b'original-lock')
                try:
                    args = [sys.executable, '-c', CHILD, str(root), mode]
                    if kind == 'replaced-fifo':
                        args.append('replace-after-guard')
                    result = subprocess.run(args,
                                            cwd=ROOT, capture_output=True, text=True, timeout=2)
                except subprocess.TimeoutExpired:
                    self.fail(mode + ' FIFO lock blocked instead of rejecting input')
                self.assertEqual(result.returncode, 0, result.stderr)
                error = json.loads(result.stdout)['error']
                if kind in ('fifo', 'replaced-fifo'):
                    self.assertIn('regular file', error)
                self.assertEqual(list(state.iterdir()), [target])

    def test_normal_lock_keeps_inode_bytes_and_releases_after_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'normal.lock'
            target.write_bytes(b'existing-lock')
            inode = target.stat().st_ino
            with self.assertRaisesRegex(RuntimeError, 'body failed'):
                with _lock_file(target) as fd:
                    fcntl.flock(fd, fcntl.LOCK_EX)
                    raise RuntimeError('body failed')
            with _lock_file(target) as fd:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(target.stat().st_ino, inode)
            self.assertEqual(target.read_bytes(), b'existing-lock')

    def test_descriptor_closed_when_fstat_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'normal.lock'
            actual_open = os.open
            opened = []
            def observed_open(*args):
                fd = actual_open(*args)
                opened.append(fd)
                return fd
            with patch('agent_runtime.task_supervisor.os.open', side_effect=observed_open), \
                 patch('agent_runtime.task_supervisor.os.fstat', side_effect=OSError('fstat failed')):
                with self.assertRaisesRegex(OSError, 'fstat failed'):
                    with _lock_file(target):
                        self.fail('fstat failure entered critical section')
            self.assertEqual(len(opened), 1)
            with self.assertRaises(OSError):
                os.fstat(opened[0])

    def test_duplicate_worker_still_returns_zero_without_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / 'run'
            state.mkdir()
            with _lock_file(state / 'worker.lock') as fd:
                fcntl.flock(fd, fcntl.LOCK_EX)
                with patch.dict(os.environ, {'TMUX': 'explicit-test-fixture'}), \
                     patch('agent_runtime.task_supervisor.Store') as store:
                    self.assertEqual(worker({'project_root': str(root), 'state_dir': str(state)}), 0)
                store.assert_not_called()

    def test_process_exit_releases_shared_lock(self):
        code = '''
import fcntl, sys
from agent_runtime.task_supervisor import _lock_file
with _lock_file(sys.argv[1]) as fd:
    fcntl.flock(fd, fcntl.LOCK_EX)
    print('acquired', flush=True)
    sys.stdin.readline()
'''
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'normal.lock'
            child = subprocess.Popen([sys.executable, '-c', code, str(target)], cwd=ROOT,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True)
            try:
                import select
                self.assertTrue(select.select([child.stdout], [], [], 3)[0])
                self.assertEqual(child.stdout.readline().strip(), 'acquired')
                with _lock_file(target) as fd:
                    with self.assertRaises(BlockingIOError):
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                child.terminate()
                child.wait(timeout=3)
                with _lock_file(target) as fd:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=3)
                child.stdin.close()
                child.stdout.close()
                child.stderr.close()


if __name__ == '__main__':
    unittest.main()
