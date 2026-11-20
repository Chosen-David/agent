import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.project_docs import (
    DocumentError, atomic_write, guard_write_path, initialize_project_docs, task_navigation,
)
from agent_runtime.result_store import ResultStore
from agent_runtime.task_manifest import prepare, validate_contract


def artifact(docs):
    raw = b'prior data'
    (docs / 'results/raw.txt').write_bytes(raw)
    return [{'path': 'agent_doc/results/raw.txt', 'sha256': hashlib.sha256(raw).hexdigest()}]


class ExternalProjectDocsTest(unittest.TestCase):
    def test_external_root_keeps_project_and_registry_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / 'code'
            docs = Path(temp) / 'documents'
            project.mkdir()
            with patch.dict(os.environ, {'AGENT_DOC_ROOT': str(docs)}):
                initialize_project_docs(project)
                (docs / 'task/TASK.md').write_text(
                    '## 2026-11-20\n\n- [ ] [T1] Check ([detail](task_details/T1.md))\n'
                )
                (docs / 'task/task_details/T1.md').write_text(
                    '# Check\nTask-ID: T1\nDate: 2026-11-20\n\n## Plan\n\nCheck.\n\n## Progress\n'
                )
                self.assertEqual(task_navigation(project)['task_index'], 'agent_doc/task/TASK.md')
                self.assertTrue((docs / 'task/TASK.md').is_file())
                self.assertFalse(os.path.lexists(project / 'agent_doc'))
                with self.assertRaisesRegex(DocumentError, 'bound code project'):
                    guard_write_path(docs / 'results/out.json')
                alias = Path(temp) / 'doc-alias'
                alias.symlink_to(docs, target_is_directory=True)
                with self.assertRaisesRegex(DocumentError, 'bound code project'):
                    guard_write_path(alias / 'task/TASK.md')
                unbound = Path(temp) / 'unbound'
                unbound.mkdir()
                (unbound / 'agent_doc').symlink_to(docs, target_is_directory=True)
                with self.assertRaisesRegex(DocumentError, 'bound code project'):
                    guard_write_path(unbound / 'agent_doc/task/TASK.md')
                logical = project / 'agent_doc/results/out.json'
                with self.assertRaisesRegex(DocumentError, 'bound code project'):
                    guard_write_path(logical)
                (project / '.git').mkdir()
                self.assertEqual(guard_write_path(logical), docs / 'results/out.json')
                with self.assertRaisesRegex(DocumentError, 'traversal'):
                    guard_write_path(logical / '..' / 'another.json')
                plan = prepare(docs / 'task/TASK.md', 'run', 'auto', 'test',
                               project_root=project)
                self.assertEqual(plan['task_source']['path'], str(project / 'agent_doc/task/TASK.md'))
                store = ResultStore(project)
                entry = store.register_history('prior', 'External evidence', artifact(docs))
                self.assertEqual(entry['record_ref']['path'], 'agent_doc/results/prior/record.json')
                self.assertEqual(store.show('prior')['record']['summary'], 'External evidence')
                with self.assertRaises(DocumentError):
                    atomic_write(project, docs / 'guide/human.md', b'blocked')
                with self.assertRaisesRegex(DocumentError, 'traversal'):
                    atomic_write(project, 'agent_doc/results/../../code.py', b'blocked')

    def test_directory_link_is_an_anchor_but_child_redirects_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / 'code'
            docs = Path(temp) / 'documents'
            project.mkdir()
            docs.mkdir()
            (project / 'agent_doc').symlink_to(docs, target_is_directory=True)
            with patch.dict(os.environ, {'AGENT_DOC_ROOT': ''}):
                initialize_project_docs(project)
                ResultStore(project).register_history('prior', 'External evidence', artifact(docs))
                (docs / 'task/redirect').symlink_to(Path(temp), target_is_directory=True)
                with self.assertRaises(DocumentError):
                    atomic_write(project, 'agent_doc/task/redirect/file.md', b'blocked')
                self.assertFalse((Path(temp) / 'file.md').exists())
                with self.assertRaisesRegex(DocumentError, 'bound code project|symlinks'):
                    guard_write_path(docs / 'task/redirect/file.md')
                with self.assertRaisesRegex(DocumentError, 'bound code project'):
                    guard_write_path(docs / 'task/TASK.md')
                with self.assertRaises(DocumentError):
                    guard_write_path(docs / 'guide/human.md')
                alias = Path(temp) / 'other'
                alias.symlink_to(docs / 'guide', target_is_directory=True)
                with self.assertRaises(DocumentError):
                    guard_write_path(alias / 'human.md')

    def test_overlapping_checkout_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            with patch.dict(os.environ, {'AGENT_DOC_ROOT': str(project / 'src')}):
                with self.assertRaisesRegex(DocumentError, 'separate'):
                    initialize_project_docs(project)
                self.assertFalse((project / 'src').exists())

    def test_existing_plan_and_record_survive_relocation(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / 'code'
            project.mkdir()
            local = project / 'agent_doc'
            outside = Path(temp) / 'documents'
            (local / 'task/task_details').mkdir(parents=True)
            (local / 'results').mkdir()
            (local / 'task/TASK.md').write_text(
                '## 2026-11-20\n\n- [ ] [T1] Check ([detail](task_details/T1.md))\n'
            )
            (local / 'task/task_details/T1.md').write_text(
                '# Check\nTask-ID: T1\nDate: 2026-11-20\n\n## Plan\n\nCheck.\n\n## Progress\n'
            )
            with patch.dict(os.environ, {'AGENT_DOC_ROOT': ''}):
                plan = prepare(project, 'run', 'auto', 'test')
                record = ResultStore(project).register_history('historical', 'Saved', artifact(local))
                before = validate_contract(plan, project)
            local.rename(outside)
            with patch.dict(os.environ, {'AGENT_DOC_ROOT': str(outside)}):
                self.assertEqual(validate_contract(plan, project), before)
                self.assertEqual(ResultStore(project).show('historical'), record)
