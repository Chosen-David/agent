"""Directory scan failures must not become successful incomplete inventories."""
import errno
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.artifact_index import build_artifact_index
from agent_runtime.project_docs import DocumentError, snapshot_project_docs


class InventoryScanErrors(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='inventory-errors-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        (self.root / 'TASK.md').write_bytes(b'- [ ] [ONE] Keep declared evidence\n')
        self.advice = self.root / 'agent_doc' / 'advice'
        self.nested = self.advice / 'nested'
        self.nested.mkdir(parents=True)
        (self.advice / 'top.md').write_bytes(b'top\n')
        (self.nested / 'correction.md').write_bytes(b'corrected\n')
        self.before = self.contents()

    def contents(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob('*') if p.is_file()}

    def assert_scan_refused(self, target, consumer):
        original = os.scandir
        for code in (errno.EACCES, errno.EIO):
            calls = []

            def failing_scandir(path):
                if Path(path) == target:
                    calls.append(str(path))
                    raise OSError(code, 'injected directory scan failure', str(path))
                return original(path)

            with self.subTest(errno=code):
                try:
                    with patch('os.scandir', side_effect=failing_scandir):
                        with self.assertRaises(DocumentError) as caught:
                            consumer()
                    self.assertIsInstance(caught.exception.__cause__, OSError)
                    self.assertEqual(caught.exception.__cause__.errno, code)
                    self.assertEqual(caught.exception.__cause__.filename, str(target))
                finally:
                    self.assertEqual(calls, [str(target)])
                    self.assertEqual(self.contents(), self.before)

    def test_artifact_scan_root_error_refuses(self):
        self.assert_scan_refused(self.advice, lambda: build_artifact_index(
            self.root, directory='agent_doc/advice', required=['nested/correction.md']))

    def test_artifact_scan_nested_error_refuses(self):
        self.assert_scan_refused(self.nested, lambda: build_artifact_index(
            self.root, directory='agent_doc/advice', required=['nested/correction.md']))

    def test_document_snapshot_scan_root_error_refuses(self):
        self.assert_scan_refused(self.advice, lambda: snapshot_project_docs(self.root))

    def test_document_snapshot_scan_nested_error_refuses(self):
        self.assert_scan_refused(self.nested, lambda: snapshot_project_docs(self.root))

    def test_readable_inventory_and_snapshot_preserve_exact_evidence(self):
        expected = {f'agent_doc/advice/{name}': hashlib.sha256(data).hexdigest()
                    for name, data in [('top.md', b'top\n'),
                                       ('nested/correction.md', b'corrected\n')]}
        index = build_artifact_index(self.root, directory='agent_doc/advice',
                                    required={'nested/correction.md': expected[
                                        'agent_doc/advice/nested/correction.md']})
        self.assertEqual({p: v['sha256'] for p, v in index['files'].items()}, expected)
        self.assertEqual(index['count'], 2)
        self.assertEqual(index['required']['nested/correction.md'],
                         {'path': 'agent_doc/advice/nested/correction.md',
                          'present': True, 'match': True})
        snapshot = snapshot_project_docs(self.root)
        self.assertEqual(snapshot['advice'], expected)
        self.assertEqual(snapshot['guides'], {})
        self.assertEqual(self.contents(), self.before)

    def test_absent_optional_documents_remain_compatible(self):
        with tempfile.TemporaryDirectory(prefix='inventory-absent-') as directory:
            root = Path(directory)
            raw = b'- [ ] [ONE] Keep declared evidence\n'
            (root / 'TASK.md').write_bytes(raw)
            snapshot = snapshot_project_docs(root)
            self.assertEqual(snapshot['advice'], {})
            self.assertEqual(snapshot['guides'], {})
            self.assertEqual(snapshot['task_index']['sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(list(root.iterdir()), [root / 'TASK.md'])


if __name__ == '__main__':
    unittest.main()
