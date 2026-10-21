"""Unified artifact index: classification, required checks and symmetric diff."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from agent_runtime.artifact_index import build_artifact_index, diff_artifact_index
from agent_runtime.project_docs import DocumentError


class ArtifactIndexTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='artifact-index-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.run = self.root / '.agent-runs' / 'run-1'
        self.run.mkdir(parents=True)
        (self.run / 'launch.json').write_text('{}')
        (self.run / 'receipt.json').write_text('{}')
        (self.run / 'supervisor.log').write_text('line\n')
        (self.run / 'artifact.py').write_text('x = 1\n')
        (self.run / 'unknown.bin').write_bytes(b'\x00\x01')

    def test_classifies_known_layout_and_unknown_files(self):
        index = build_artifact_index(self.root, directory='.agent-runs/run-1')
        self.assertEqual(index['schema_version'], 'artifact-index/v1')
        files = index['files']
        self.assertEqual(files['.agent-runs/run-1/launch.json']['category'], 'state')
        self.assertTrue(files['.agent-runs/run-1/launch.json']['mutable'])
        self.assertEqual(files['.agent-runs/run-1/receipt.json']['category'], 'delivery')
        self.assertFalse(files['.agent-runs/run-1/receipt.json']['mutable'])
        self.assertEqual(files['.agent-runs/run-1/supervisor.log']['category'], 'log')
        self.assertEqual(files['.agent-runs/run-1/artifact.py']['category'], 'source')
        self.assertEqual(files['.agent-runs/run-1/unknown.bin']['category'], 'other')
        self.assertIsNone(files['.agent-runs/run-1/unknown.bin']['mutable'])
        self.assertEqual(index['count'], 5)

    def test_required_paths_report_present_missing_match_mismatch(self):
        expected_sha = hashlib.sha256(b'{}').hexdigest()
        index = build_artifact_index(
            self.root, directory='.agent-runs/run-1',
            required={'launch.json': expected_sha, 'receipt.json': '0' * 64,
                      'absent.txt': None})
        self.assertEqual(index['required']['launch.json'],
                         {'path': '.agent-runs/run-1/launch.json', 'present': True, 'match': True})
        self.assertEqual(index['required']['receipt.json'],
                         {'path': '.agent-runs/run-1/receipt.json', 'present': True, 'match': False})
        self.assertEqual(index['required']['absent.txt'],
                         {'path': '.agent-runs/run-1/absent.txt', 'present': False})

    def test_symlinked_file_and_directory_are_rejected(self):
        (self.root / 'outside.txt').write_text('x')
        (self.run / 'link.txt').symlink_to(self.root / 'outside.txt')
        with self.assertRaisesRegex(DocumentError, 'symlink'):
            build_artifact_index(self.root, directory='.agent-runs/run-1')
        (self.run / 'link.txt').unlink()
        outside_dir = self.root / 'outside'
        outside_dir.mkdir()
        (self.run / 'linkdir').symlink_to(outside_dir, target_is_directory=True)
        with self.assertRaisesRegex(DocumentError, 'symlink'):
            build_artifact_index(self.root, directory='.agent-runs/run-1')

    def test_directory_outside_root_and_missing_directory_are_rejected(self):
        with self.assertRaisesRegex(DocumentError, 'does not exist'):
            build_artifact_index(self.root, directory='nope')
        with self.assertRaisesRegex(DocumentError, 'under the project root'):
            build_artifact_index(self.run, directory='..')

    def test_entry_bound_fails_closed(self):
        with self.assertRaisesRegex(DocumentError, 'exceeds 2 file entries'):
            build_artifact_index(self.root, directory='.agent-runs/run-1', max_entries=2)

    def test_required_argument_must_be_paths_or_mapping(self):
        with self.assertRaisesRegex(DocumentError, 'required must be'):
            build_artifact_index(self.root, directory='.agent-runs/run-1', required=5)


class ArtifactIndexDiffTests(unittest.TestCase):
    def index(self):
        temporary = tempfile.TemporaryDirectory(prefix='artifact-diff-')
        self.addCleanup(temporary.cleanup)
        return temporary.name

    def make(self, root):
        run = Path(root) / 'run'
        run.mkdir(parents=True, exist_ok=True)
        return build_artifact_index(Path(root), directory='run')

    def test_unchanged_index_reports_no_change(self):
        root = self.index()
        base = self.make(root)
        self.assertFalse(diff_artifact_index(base, base)['any_changed'])

    def test_added_removed_changed_are_symmetric(self):
        root = self.index()
        run = Path(root) / 'run'
        run.mkdir(parents=True, exist_ok=True)
        (run / 'launch.json').write_text('{}')
        base = self.make(root)
        (run / 'new.txt').write_text('new')
        (run / 'launch.json').write_text('changed')
        current = self.make(root)
        delta = diff_artifact_index(current, base)
        self.assertTrue(delta['any_changed'])
        self.assertIn('run/new.txt', delta['added'])
        self.assertIn('run/launch.json', delta['changed'])
        reverse = diff_artifact_index(base, current)
        self.assertEqual(reverse['removed'], delta['added'])
        self.assertEqual(reverse['changed'], delta['changed'])

    def test_non_index_input_is_rejected(self):
        with self.assertRaisesRegex(DocumentError, 'artifact-index/v1'):
            diff_artifact_index({'schema_version': 'other'}, {})
        with self.assertRaisesRegex(DocumentError, 'two artifact-index/v1'):
            diff_artifact_index({'schema_version': 'artifact-index/v1'}, 'not-a-dict')


if __name__ == '__main__':
    unittest.main()
