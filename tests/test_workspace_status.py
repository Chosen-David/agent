import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/workspace_status.py'


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.adapter = self.base / 'owner.py'
        self.adapter.write_text("from contextlib import contextmanager\n@contextmanager\ndef lease(repo, slot, task, run):\n yield task == 'task' and run == 'run'\n")
        self.repo = self.base / 'repo'
        subprocess.run(['git', 'init', '-q', self.repo], check=True)
        for name, content in [('src/value.py', 'answer=42'), ('tests/run.py',
                              "import runpy\nassert runpy.run_path('src/value.py')['answer']==42"),
                              ('dataset/data.txt', 'unused'), ('.gitignore', '*.ignored')]:
            path = self.repo / name
            path.parent.mkdir(exist_ok=True)
            path.write_text(content)
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'base')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', self.repo, *args])

    def cli(self, *args, repo=None, check=True):
        return subprocess.run([sys.executable, SCRIPT, '--repo', repo or self.repo, *args],
                              capture_output=True, text=True, check=check)

    def create(self, name, *args, source='current-task', check=True, repo=None):
        return self.cli('--intent', 'isolate', '--source', source, '--task', 'task', '--run', 'run',
                        '--create-local-slot', self.base / name, '--lease-adapter', self.adapter, *args, repo=repo, check=check)

    def test_history_and_resume_leave_registration_unchanged(self):
        before = self.git('worktree', 'list', '--porcelain')
        for _ in range(2):
            self.assertEqual(json.loads(self.cli('--intent', 'read').stdout)['action'], 'read-commit')
            self.assertEqual(json.loads(self.cli('--intent', 'develop', '--source',
                                                'current-task').stdout)['action'], 'reuse-current')
        self.assertEqual(before, self.git('worktree', 'list', '--porcelain'))

    def test_isolated_sparse_real_entry_and_missing_dependency(self):
        self.create('ok', '--sparse-dir', 'src', '--sparse-dir', 'tests',
                    '--require-file', 'tests/run.py', '--require-file', 'src/value.py')
        tree = self.base / 'ok/tree'
        subprocess.run([sys.executable, 'tests/run.py'], cwd=tree, check=True)
        self.assertFalse((tree / 'dataset/data.txt').exists())
        self.assertEqual(self.git('worktree', 'list').count(b'\n'), 2)
        nested = self.create('nested', repo=tree, check=False)
        self.assertEqual(nested.returncode, 2)
        self.assertFalse((self.base / 'nested').exists())
        bad = self.create('bad', '--sparse-dir', 'tests', '--require-file', 'src/value.py', check=False)
        self.assertEqual(bad.returncode, 2)
        self.assertIn('missing checkout dependency', bad.stderr)
        events = (self.base / 'bad/events.jsonl').read_text().splitlines()
        self.assertEqual(json.loads(events[-1])['action'], 'failed-pending')

    def test_host_unknown_and_dirty_workspace_retained(self):
        for source in ('host', 'unknown', 'user'):
            result = self.create('other', source=source, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertFalse((self.base / 'other').exists())
        (self.repo / 'private.ignored').write_bytes(b'keep')
        (self.repo / 'new').write_bytes(b'keep')
        self.assertEqual(self.create('dirty', check=False).returncode, 2)
        receipt = json.loads(self.cli('--intent', 'reclaim', '--source', 'current-task').stdout)
        self.assertEqual(receipt['action'], 'retain')
        self.assertIn('local changes, untracked or ignored files', receipt['reasons'])
        self.assertEqual((self.repo / 'private.ignored').read_bytes(), b'keep')

    def test_live_owner_conflict_never_creates_slot(self):
        self.adapter.write_text("from contextlib import nullcontext\ndef lease(*args): return nullcontext(False)")
        result = self.create('busy', check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn('active workspace conflict', result.stderr)
        self.assertFalse((self.base / 'busy').exists())

    def test_reclaim_candidate_rechecks_live_consumers_and_local_changes(self):
        self.create('owned')
        tree = self.base / 'owned/tree'
        args = ['--intent', 'reclaim', '--source', 'current-task', '--lease-adapter', self.adapter,
                '--task', 'task', '--run', 'run', '--merged-into', self.git('rev-parse', 'HEAD').decode().strip()]
        with self.adapter.open('a') as stream:
            stream.write("def release_facts(tree, task, run):\n return dict(owner_verified=True, active_processes=[], tasks=[], consumers=['evaluation'] if (tree.parent/'active').exists() else [], recovery_dependencies=[], locks=[])")
        self.assertEqual(json.loads(self.cli(*args, repo=tree).stdout)['action'], 'candidate-for-review')
        (tree.parent / 'active').touch()
        active = json.loads(self.cli(*args, repo=tree).stdout)
        self.assertEqual(active['action'], 'retain')
        self.assertIn('active or unknown consumers', active['reasons'])
        (tree / 'keep.ignored').touch()
        self.assertEqual(json.loads(self.cli(*args, repo=tree).stdout)['action'], 'retain')
        self.assertTrue((tree / 'keep.ignored').exists())

    def test_concurrent_slot_reservation_creates_one_checkout(self):
        command = [sys.executable, SCRIPT, '--repo', self.repo, '--intent', 'isolate', '--source',
                   'current-task', '--task', 'task', '--run', 'run', '--lease-adapter', self.adapter,
                   '--create-local-slot', self.base / 'race']
        jobs = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        for job in jobs:
            job.communicate(timeout=15)
        self.assertEqual(sorted(job.returncode for job in jobs), [0, 2])
        self.assertEqual(self.git('worktree', 'list').count(b'\n'), 2)
        events = (self.base / 'race/events.jsonl').read_text().splitlines()
        self.assertEqual([json.loads(line)['action'] for line in events], ['creating', 'created'])

    def test_gitfile_submodule_is_distinct_from_linked_worktree(self):
        parent = self.base / 'parent'
        subprocess.run(['git', 'init', '-q', parent], check=True)
        subprocess.run(['git', '-C', parent, '-c', 'protocol.file.allow=always', 'submodule', 'add',
                        '--quiet', str(self.repo), 'component'], check=True)
        child = parent / 'component'
        self.assertTrue((child / '.git').is_file())
        receipt = json.loads(self.cli('--intent', 'read', repo=child).stdout)
        self.assertFalse(receipt['linked'])
        self.assertEqual(receipt['root'], str(child))
