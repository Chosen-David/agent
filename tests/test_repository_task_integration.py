"""Exercise the maintained checkout, not just synthetic document examples."""
import copy
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

from agent_runtime.project_docs import check_document_refs, parse_requirements, snapshot_project_docs, split_detail
from agent_runtime.task_context import task_view
from agent_runtime.task_manifest import prepare, validate_contract

ROOT = Path(__file__).resolve().parents[1]


class RepositoryTaskIntegrationTests(unittest.TestCase):
    def test_repository_snapshot_has_every_indexed_detail(self):
        source = ROOT / 'agent_doc/task/TASK.md'
        items = parse_requirements(source.read_text(), canonical=True)
        snapshot = snapshot_project_docs(ROOT)
        self.assertEqual(set(snapshot['task_details']), {item['id'] for item in items})
        self.assertEqual(snapshot['task_index']['sha256'], hashlib.sha256(source.read_bytes()).hexdigest())

    def test_repository_draft_keeps_complete_scope_and_review_gate(self):
        # Retrieval is tested separately; this check exercises real project docs.
        with patch('agent_runtime.task_manifest._prior_result_search', return_value={'test_only': True}):
            draft = prepare(ROOT, 'repository-document-check', 'manual', 'read-only regression')
        ids = {item['id'] for item in parse_requirements(
            (ROOT / 'agent_doc/task/TASK.md').read_text(), canonical=True)}
        self.assertEqual({task['task_id'] for task in draft['tasks']}, ids)
        self.assertEqual(set(draft['project_documents']['task_details']), ids)
        self.assertEqual(draft['plan_review']['schema_version'], 'main-plan-review/v1')
        self.assertTrue(all(task['action'] == 'configure_host_action' for task in draft['tasks']))
        self.assertEqual(draft['advice_assessments'], [])
        self.assertEqual(draft['guide_reviews'], [])
        with self.assertRaisesRegex(ValueError, 'human guide review required'):
            validate_contract(draft, ROOT)

    def test_current_snapshot_rejects_old_bindings_but_not_progress(self):
        snapshot = snapshot_project_docs(ROOT)
        for field in ('task_index', 'task_details'):
            stale = copy.deepcopy(snapshot)
            ref = stale[field] if field == 'task_index' else next(iter(stale[field].values()))
            ref['sha256'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'reconcile and version'):
                check_document_refs(ROOT, stale)
        for ref in snapshot['task_details'].values():
            text = (ROOT / ref['path']).read_text().replace('\r\n', '\n')
            plan, _ = split_detail(text)
            changed_plan, _ = split_detail(text + '\nProgress append probe.\n')
            self.assertEqual(plan, changed_plan)

    def test_repository_task_view_remains_navigation_only(self):
        source = ROOT / 'agent_doc/task/TASK.md'
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        items = parse_requirements(source.read_text(), canonical=True)
        selected = items[0]['id']
        view = task_view(ROOT, [selected], digest, max_chars=1000000)
        self.assertEqual(view['selected_task_ids'], [selected])
        self.assertEqual(view['omitted_task_rows'], len(items) - 1)
        self.assertIn('no global clearance', view['scope'])
        for ids, sha in ((['NO-SUCH-REPOSITORY-TASK'], digest), ([selected], '0' * 64)):
            with self.assertRaises(ValueError):
                task_view(ROOT, ids, sha)


if __name__ == '__main__':
    unittest.main()
