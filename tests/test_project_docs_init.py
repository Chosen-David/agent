"""Actual explicit-project bootstrap boundaries; no human guide fixtures authored."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.project_docs import (
    CANONICAL_TASK, DocumentError, initialize_project_docs, snapshot_project_docs,
)

REPO = Path(__file__).resolve().parents[1]


class ProjectDocumentInitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = self.base / 'ProjectA'
        self.project.mkdir()

    def test_projects_are_separate_from_each_other_and_workflow_repository(self):
        source = (REPO / CANONICAL_TASK).read_bytes()
        second = self.base / 'ProjectB'
        second.mkdir()
        for target in (self.project, second):
            result = initialize_project_docs(target)
            self.assertEqual(result['project_root'], str(target.resolve()))
            self.assertNotEqual((target / CANONICAL_TASK).read_bytes(), source)
            self.assertFalse(list((target / 'doc/task/task_details').iterdir()))
            self.assertFalse(list((target / 'doc/guide').iterdir()))
            self.assertTrue((target / 'doc/results').is_dir())
            with self.assertRaises(DocumentError):
                snapshot_project_docs(target)  # Empty index is not dispatch-ready.
        (self.project / 'doc/advice/only-A.md').write_text('A', encoding='utf-8')
        self.assertFalse((second / 'doc/advice/only-A.md').exists())
        self.assertEqual((REPO / CANONICAL_TASK).read_bytes(), source)

    def test_idempotent_and_preserves_all_existing_project_files(self):
        initialize_project_docs(self.project)
        files = [self.project / CANONICAL_TASK, self.project / 'doc/task/task_details/A.md',
                 self.project / 'doc/advice/A.md', self.project / 'doc/results/existing.json']
        for index, path in enumerate(files):
            path.write_bytes(f'existing-{index}\r\n'.encode())
        before = [(p.read_bytes(), p.stat().st_mtime_ns) for p in files]
        self.assertEqual(initialize_project_docs(self.project)['created'], [])
        self.assertEqual(before, [(p.read_bytes(), p.stat().st_mtime_ns) for p in files])
        self.assertFalse(list((self.project / 'doc/guide').iterdir()))

    def test_directory_conflict_is_preflighted_before_any_new_documents(self):
        (self.project / 'doc').mkdir()
        (self.project / 'doc/results').write_bytes(b'preserve')
        with self.assertRaises(DocumentError):
            initialize_project_docs(self.project)
        self.assertEqual([p.name for p in (self.project / 'doc').iterdir()], ['results'])
        self.assertEqual((self.project / 'doc/results').read_bytes(), b'preserve')

    def test_legacy_task_requires_explicit_migration(self):
        (self.project / 'TASK.md').write_bytes(b'- [ ] [OLD] Existing task\n')
        with self.assertRaisesRegex(DocumentError, 'migrate'):
            initialize_project_docs(self.project)
        self.assertFalse((self.project / 'doc').exists())

    def test_two_active_task_indexes_rejected_without_changes(self):
        initialize_project_docs(self.project)
        (self.project / 'TASK.md').write_bytes(b'- [ ] [OLD] Existing task\n')
        before = (self.project / CANONICAL_TASK).read_bytes()
        with self.assertRaisesRegex(DocumentError, 'dual active'):
            initialize_project_docs(self.project)
        self.assertEqual(before, (self.project / CANONICAL_TASK).read_bytes())

    def test_guide_subtree_cannot_be_reinterpreted_as_a_project(self):
        target = self.project / 'DoC/GuIdE/nested'
        target.mkdir(parents=True)
        with self.assertRaisesRegex(DocumentError, 'human-only'):
            initialize_project_docs(target)
        self.assertFalse(list(target.iterdir()))

    def test_nonexistent_root_does_not_create_a_project(self):
        target = self.base / 'typo'
        with self.assertRaises(DocumentError):
            initialize_project_docs(target)
        self.assertFalse(target.exists())

    def test_cli_explicit_root_wins_over_source_working_directory(self):
        script = REPO / 'scripts/project_docs.py'
        before = (REPO / CANONICAL_TASK).read_bytes()
        result = subprocess.run([sys.executable, str(script), '--root', str(self.project), 'init'],
                                cwd=REPO, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout)['project_root'], str(self.project.resolve()))
        self.assertEqual((REPO / CANONICAL_TASK).read_bytes(), before)
        missing = subprocess.run([sys.executable, str(script), 'init'], cwd=REPO,
                                 capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(missing.returncode, 2)
        self.assertIn('--root', missing.stderr)

    def test_symlinked_document_directory_is_refused_before_writes(self):
        outside = self.base / 'outside'
        outside.mkdir()
        (self.project / 'doc').mkdir()
        try:
            (self.project / 'doc/advice').symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest('symlink creation unavailable')
        with self.assertRaises(DocumentError):
            initialize_project_docs(self.project)
        self.assertFalse(list(outside.iterdir()))
        self.assertFalse((self.project / 'doc/task').exists())


if __name__ == '__main__':
    unittest.main()
