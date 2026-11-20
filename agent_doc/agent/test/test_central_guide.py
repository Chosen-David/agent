import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

from agent_runtime.project_docs import DocumentError, assert_ai_writable, guard_write_path, initialize_project_docs


class CentralGuideTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '.git').mkdir()
        self.project = self.root / 'agent_doc' / 'ProjectA'
        self.guide = self.project / 'guide'
        self.guide.mkdir(parents=True)
        self.source = self.guide / 'GUIDE.md'
        self.source.write_bytes(b'human requirements\n')

    def test_direct_and_rebased_guide_writes_are_rejected(self):
        for root in (self.root, self.project, self.guide):
            with self.subTest(root=root):
                with self.assertRaises(DocumentError):
                    assert_ai_writable(root, self.source)
        with self.assertRaises(DocumentError):
            guard_write_path(self.source)

    def test_project_parent_cannot_be_removed(self):
        with self.assertRaises(DocumentError):
            assert_ai_writable(self.root, self.project)

    def test_hard_link_alias_cannot_be_written(self):
        alias = self.root / 'alias.md'
        os.link(self.source, alias)
        with self.assertRaises(DocumentError):
            guard_write_path(alias)
        self.assertEqual(self.source.read_bytes(), b'human requirements\n')

    def test_task_writes_remain_available(self):
        path = self.project / 'task' / 'TASK.md'
        self.assertEqual(assert_ai_writable(self.root, path), path)
        self.assertEqual(guard_write_path(path), path)

    def test_bootstrap_cannot_rebase_into_central_guide(self):
        with self.assertRaises(DocumentError):
            initialize_project_docs(self.guide)
        spec = importlib.util.spec_from_file_location('central_guide_setup', Path(__file__).resolve().parents[3] / 'setup.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with self.assertRaises(ValueError):
            module.installation_root(self.guide)
        self.assertFalse((self.guide / 'agent_doc').exists())

    def test_rebased_project_hard_link_is_rejected(self):
        alias = self.project / 'alias.md'
        os.link(self.source, alias)
        with self.assertRaises(DocumentError):
            assert_ai_writable(self.project, alias)
