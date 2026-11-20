import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('external_setup', ROOT / 'setup.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class ExternalSetupTests(unittest.TestCase):
    def test_install_check_uninstall_preserve_external_documents(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            project = base / 'code'
            project.mkdir()
            docs = base / 'agent_doc' / 'code'
            with patch.dict(os.environ, {'AGENT_DOC_ROOT': str(docs)}):
                self.assertEqual(setup.install(project)['status'], 'configured')
                self.assertTrue((docs / 'task/TASK.md').is_file())
                self.assertFalse((project / 'agent_doc').exists())
                guide = docs / 'guide/GUIDE.md'
                guide.write_bytes(b'human requirements\r\n')
                before = (docs / 'task/TASK.md').read_bytes()
                self.assertEqual(setup.check(project)['status'], 'configured')
                setup.uninstall(project)
                self.assertEqual(guide.read_bytes(), b'human requirements\r\n')
                self.assertEqual((docs / 'task/TASK.md').read_bytes(), before)

    def test_existing_local_index_requires_reconciliation(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            project = base / 'code'
            (project / 'agent_doc/task').mkdir(parents=True)
            local = project / 'agent_doc/task/TASK.md'
            local.write_bytes(b'existing authoritative task')
            docs = base / 'agent_doc/code'
            with patch.dict(os.environ, {'AGENT_DOC_ROOT': str(docs)}):
                with self.assertRaises(ValueError):
                    setup.install(project)
            self.assertEqual(local.read_bytes(), b'existing authoritative task')
            self.assertFalse(docs.exists())
            self.assertFalse((project / '.claude').exists())

    def test_check_reports_missing_external_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            project = base / 'code'
            project.mkdir()
            docs = base / 'agent_doc/code'
            with patch.dict(os.environ, {'AGENT_DOC_ROOT': str(docs)}):
                setup.install(project)
                (docs / 'advice').rmdir()
                report = setup.check(project)
                self.assertEqual(report['status'], 'needs_setup')
                self.assertTrue(any(str(docs / 'advice') in error for error in report['errors']))

    def test_other_linked_task_index_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            project = base / 'code'
            project.mkdir()
            previous = base / 'previous'
            (previous / 'task').mkdir(parents=True)
            (previous / 'task/TASK.md').write_bytes(b'previous task')
            (project / 'agent_doc').symlink_to(previous, target_is_directory=True)
            docs = base / 'agent_doc/code'
            with patch.dict(os.environ, {'AGENT_DOC_ROOT': str(docs)}):
                with self.assertRaises(ValueError):
                    setup.install(project)
            self.assertFalse(docs.exists())
