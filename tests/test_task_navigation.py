"""Summary-first task navigation digest; derived fields are non-authoritative."""
import json
from pathlib import Path
import tempfile
import unittest

from agent_runtime.project_docs import DocumentError, document_delta, snapshot_project_docs, task_navigation

DETAIL = '''# [T1] Build a widget

Task-ID: T1
Date: 2026-10-07
Status: doing
Owner: main-ai

## Plan

### 摘要

- Build the widget; code done, now verifying; next: sub-agent W1.

### 目标与验收

- 用户要求与来源：assemble the widget.

### 沙箱 / 写入范围

- 唯一作者与允许写入路径：agent_doc/task/task_details/T1.md

### 实现方法

- 方案：weld then polish.

## Progress

### 进度与证据

- 2026-10-07 wired the widget.

### 阻塞与下一步

- Waiting on independent verify.
'''


class TaskNavigationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='task-navigation-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        details = self.root / 'agent_doc/task/task_details'
        details.mkdir(parents=True)
        (self.root / 'agent_doc/task/TASK.md').write_text(
            '# Project tasks\n\n## 2026-10-07\n\n'
            '- [ ] [T1] Build a widget ([详情](task_details/T1.md))\n')
        (details / 'T1.md').write_text(DETAIL)

    def test_digest_carries_index_and_derived_fields_not_plan_bodies(self):
        nav = task_navigation(self.root)
        self.assertEqual(nav['schema_version'], 'task-navigation/v1')
        self.assertEqual(nav['task_index'], 'agent_doc/task/TASK.md')
        self.assertEqual(len(nav['tasks']), 1)
        task = nav['tasks'][0]
        self.assertEqual(task['id'], 'T1')
        self.assertEqual(task['title'], 'Build a widget')
        self.assertEqual(task['date'], '2026-10-07')
        self.assertFalse(task['checked'])
        self.assertEqual(task['status'], 'doing')
        self.assertEqual(task['owner'], 'main-ai')
        self.assertIn('Build the widget', task['summary'])
        # The digest stops at the next plan heading; other plan bodies stay out.
        self.assertNotIn('目标与验收', task['summary'])
        self.assertNotIn('实现方法', task['summary'])
        self.assertIn('Waiting on independent verify', task['progress_tail'])

    def test_missing_summary_is_none_and_budget_fails_closed(self):
        detail = self.root / 'agent_doc/task/task_details/T1.md'
        detail.write_text(DETAIL.replace('### 摘要\n\n- Build the widget; code done, now verifying; next: sub-agent W1.\n\n', ''))
        self.assertIsNone(task_navigation(self.root)['tasks'][0]['summary'])
        with self.assertRaisesRegex(DocumentError, 'character budget'):
            task_navigation(self.root, max_chars=20)

    def test_missing_status_and_owner_are_none_for_legacy_details(self):
        detail = self.root / 'agent_doc/task/task_details/T1.md'
        detail.write_text(DETAIL.replace('Status: doing\n', '').replace('Owner: main-ai\n', ''))
        task = task_navigation(self.root)['tasks'][0]
        self.assertIsNone(task['status'])
        self.assertIsNone(task['owner'])

    def test_identity_mismatch_and_ambiguous_status_are_rejected(self):
        detail = self.root / 'agent_doc/task/task_details/T1.md'
        detail.write_text(DETAIL.replace('Task-ID: T1', 'Task-ID: T2'))
        with self.assertRaisesRegex(DocumentError, 'identity/date'):
            task_navigation(self.root)
        detail.write_text(DETAIL.replace('Status: doing', 'Status: doing\nStatus: blocked'))
        with self.assertRaisesRegex(DocumentError, 'multiple Status'):
            task_navigation(self.root)

    def test_legacy_index_without_canonical_links_is_rejected(self):
        (self.root / 'agent_doc/task/TASK.md').write_text('- [ ] [T1] plain row\n')
        with self.assertRaisesRegex(DocumentError, 'canonical TASK.md'):
            task_navigation(self.root)

    def test_progress_tail_is_bounded(self):
        detail = self.root / 'agent_doc/task/task_details/T1.md'
        detail.write_text(DETAIL.replace(
            '- Waiting on independent verify.',
            '- Waiting on independent verify.\n' + '- detail ' * 200))
        tail = task_navigation(self.root, progress_tail_chars=80)['tasks'][0]['progress_tail']
        self.assertLessEqual(len(tail), 80 + len('…(earlier progress omitted)…\n'))
        self.assertIn('…(earlier progress omitted)…', tail)


class DocumentDeltaTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='document-delta-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        details = self.root / 'agent_doc/task/task_details'
        details.mkdir(parents=True)
        (self.root / 'agent_doc/task/TASK.md').write_text(
            '# Project tasks\n\n## 2026-10-07\n\n'
            '- [ ] [T1] Build a widget ([详情](task_details/T1.md))\n')
        (details / 'T1.md').write_text(DETAIL)

    def base(self):
        return {'schema_version': 'project-documents/v1', 'layout': 'canonical',
                'task_index': {'path': 'agent_doc/task/TASK.md', 'sha256': 'i'},
                'task_details': {'T1': {'path': 'task_details/T1.md', 'sha256': 'd'}},
                'guides': {'agent_doc/guide/GUIDE.md': 'g'},
                'advice': {'agent_doc/advice/a.md': 'a'},
                'adopted_advice': {}}

    def test_unchanged_snapshot_reports_no_change(self):
        base = self.base()
        delta = document_delta(base, base)
        self.assertFalse(delta['any_changed'])
        self.assertFalse(delta['layout']['changed'])
        self.assertFalse(delta['task_index_changed'])

    def test_added_removed_changed_are_symmetric(self):
        base = self.base()
        next_snapshot = json.loads(json.dumps(base))
        next_snapshot['task_details']['T2'] = {'path': 'task_details/T2.md', 'sha256': 'd2'}
        next_snapshot['task_details']['T1']['sha256'] = 'd-now'
        next_snapshot['guides']['agent_doc/guide/GUIDE.md'] = 'g-now'
        del next_snapshot['advice']['agent_doc/advice/a.md']
        next_snapshot['adopted_advice'] = {'agent_doc/advice/a.md': 'a'}
        delta = document_delta(next_snapshot, base)
        self.assertTrue(delta['any_changed'])
        self.assertEqual(delta['task_details']['added'], ['T2'])
        self.assertEqual(delta['task_details']['changed'], ['T1'])
        self.assertEqual(delta['guides']['changed'], ['agent_doc/guide/GUIDE.md'])
        self.assertEqual(delta['advice']['removed'], ['agent_doc/advice/a.md'])
        self.assertEqual(delta['adopted_advice']['added'], ['agent_doc/advice/a.md'])
        # Symmetry: the same entries appear when diffing in the reverse direction.
        reverse = document_delta(base, next_snapshot)
        self.assertEqual(reverse['task_details']['removed'], ['T2'])
        self.assertEqual(reverse['guides']['changed'], ['agent_doc/guide/GUIDE.md'])

    def test_non_snapshot_input_is_rejected(self):
        base = self.base()
        with self.assertRaisesRegex(DocumentError, 'project-documents/v1'):
            document_delta({'schema_version': 'other'}, base)
        with self.assertRaisesRegex(DocumentError, 'two project-documents/v1'):
            document_delta(base, 'not-a-dict')

    def test_integration_with_real_snapshot_reports_guide_change(self):
        base = snapshot_project_docs(self.root)
        guide = self.root / 'agent_doc/guide'
        guide.mkdir()
        (guide / 'GUIDE.md').write_text('# Human guide\n', encoding='utf-8')
        delta = document_delta(snapshot_project_docs(self.root), base)
        self.assertTrue(delta['any_changed'])
        self.assertEqual(delta['guides']['added'], ['agent_doc/guide/GUIDE.md'])


if __name__ == '__main__':
    unittest.main()
