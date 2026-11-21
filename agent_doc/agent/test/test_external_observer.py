import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.advice_context import advice_view
from agent_runtime.maintenance_observer import read_bound
from agent_runtime.task_context import task_view


class ExternalObserverTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.project = self.base / 'code'
        self.project.mkdir()
        self.docs = self.base / 'agent_doc/example'
        (self.docs / 'task').mkdir(parents=True)
        (self.docs / 'advice').mkdir()
        self.task = b'# Tasks\n\n## 2026-11-21\n\n- [ ] [FIX-01] Fix ([detail](task_details/FIX-01.md))\n'
        self.advice = b'# Review\n\n## Current\nCancellation remains binding.\n'
        (self.docs / 'task/TASK.md').write_bytes(self.task)
        (self.docs / 'advice/review.md').write_bytes(self.advice)
        self.addCleanup(patch.stopall)
        patch.dict(os.environ, {'AGENT_DOC_ROOT': str(self.docs)}).start()

    def assert_views(self):
        try:
            data = read_bound(self.project, 'agent_doc/task/TASK.md')
        except ValueError as exc:
            self.fail(f'authorized document tree refused: {exc}')
        self.assertEqual(data, self.task)
        view = task_view(self.project, ['FIX-01'], hashlib.sha256(self.task).hexdigest())
        self.assertEqual(view['text'].encode(), self.task)
        view = advice_view(self.project, 'agent_doc/advice/review.md', ['Current'],
                           hashlib.sha256(self.advice).hexdigest())
        self.assertIn('Cancellation remains binding.', view['selected_sections'][0]['text'])

    def test_external_views_ignore_local_decoy(self):
        local = self.project / 'agent_doc/task'
        local.mkdir(parents=True)
        (local / 'TASK.md').write_bytes(b'Old internal task')
        self.assert_views()
        self.assertEqual((local / 'TASK.md').read_bytes(), b'Old internal task')

    def test_existing_anchor_without_environment(self):
        os.environ.pop('AGENT_DOC_ROOT')
        (self.project / 'agent_doc').symlink_to(self.docs, target_is_directory=True)
        self.assert_views()
        self.assertTrue((self.project / 'agent_doc').is_symlink())

    def test_missing_external_does_not_fall_back(self):
        local = self.project / 'agent_doc/task'
        local.mkdir(parents=True)
        (local / 'TASK.md').write_bytes(self.task)
        os.environ['AGENT_DOC_ROOT'] = str(self.base / 'missing')
        with self.assertRaises(ValueError):
            read_bound(self.project, 'agent_doc/task/TASK.md')

    def test_limits_and_descendant_links_remain_rejected(self):
        with self.assertRaises(ValueError):
            read_bound(self.project, 'agent_doc/task/TASK.md', max_bytes=1)
        (self.docs / 'advice/link.md').symlink_to(self.docs / 'advice/review.md')
        with self.assertRaises(ValueError):
            read_bound(self.project, 'agent_doc/advice/link.md')
        (self.project / 'ordinary').write_bytes(b'code')
        self.assertEqual(read_bound(self.project, 'ordinary'), b'code')


if __name__ == '__main__':
    unittest.main()
