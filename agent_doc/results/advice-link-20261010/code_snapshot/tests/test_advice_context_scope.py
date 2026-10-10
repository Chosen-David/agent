"""Public CPU fixtures for task-scoped references, not model quality tests."""
import copy
from pathlib import Path
import tempfile
import unittest

from agent_runtime import project_docs as docs
from agent_runtime.task_manifest import prepare, validate_contract


class AdviceContextScopeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        docs.initialize_project_docs(self.root)
        index = '# Tasks\n\n## 2026-10-09\n'
        for tid in ('A', 'B', 'C'):
            index += f'- [ ] [{tid}] Task {tid} ([detail](task_details/{tid}.md))\n'
            docs.atomic_write(self.root, f'agent_doc/task/task_details/{tid}.md',
                              f'# {tid}\n\nTask-ID: {tid}\nDate: 2026-10-09\n\n## Plan\nScope {tid}\n\n## Progress\n'.encode())
        docs.atomic_write(self.root, docs.CANONICAL_TASK, index.encode())
        # Synthetic human input exists only inside this temporary project.
        (self.root / 'agent_doc/guide/policy.md').write_text('Synthetic preserve-evidence policy.\n')
        for name in ('a', 'b', 'shared', 'deferred'):
            docs.atomic_write(self.root, f'agent_doc/advice/{name}.md', f'Synthetic {name}\n'.encode())
        self.plan = prepare(self.root / docs.CANONICAL_TASK, 'scope-fixture', 'auto',
                            'Synthetic CPU fixture only', review_required=False)
        self.snapshot = self.plan['project_documents']
        reviews = [{'path': path, 'sha256': sha, 'origin': 'owner_authored',
                    'authorization_reference': 'Synthetic fixture input', 'task_refs': ['A', 'B', 'C'],
                    'disposition': 'applied', 'reason': 'Retain synthetic source bytes.'}
                   for path, sha in self.snapshot['guides'].items()]
        docs.bind_guide_reviews(self.plan, reviews)
        self.assessments = []
        for name, tasks, action in (('a', ['A'], 'adopt'), ('b', ['B'], 'adapt'),
                                    ('shared', ['A', 'B'], 'adapt'), ('deferred', ['C'], 'defer')):
            path = f'agent_doc/advice/{name}.md'
            self.assessments.append({'path': path, 'sha256': self.snapshot['advice'][path],
                                     'task_refs': tasks, 'disposition': action,
                                     'reason': 'Synthetic applicability decision.',
                                     'guide_alignment': 'compatible'})
        docs.bind_advice(self.plan, self.assessments)

    def task(self, tid):
        return next(t for t in self.plan['tasks'] if t['task_id'] == tid)

    def test_scoped_sources_and_full_global_coverage(self):
        validate_contract(self.plan, self.root)
        self.assertEqual(set(self.snapshot['advice']),
                         {f'agent_doc/advice/{n}.md' for n in ('a', 'b', 'shared', 'deferred')})
        for tid, names in (('A', ('a', 'shared')), ('B', ('b', 'shared')), ('C', ())):
            refs = self.task(tid)['document_refs']
            self.assertEqual(set(refs['advice']), {f'agent_doc/advice/{n}.md' for n in names})
            self.assertEqual(refs['advice'], refs['adopted_advice'])
            self.assertEqual(set(refs['task_details']), {tid})
            self.assertEqual(refs['guides'], self.snapshot['guides'])
            self.assertEqual(refs['guide_reviews'], self.plan['guide_reviews'])
            docs.check_task_documents(self.root, self.task(tid))
        with self.assertRaisesRegex(ValueError, 'unassessed advice'):
            docs.bind_advice(copy.deepcopy(self.plan), self.assessments[:-1])

    def test_multi_requirement_union_and_detached_copy(self):
        original = copy.deepcopy(self.snapshot)
        self.snapshot['future_field'] = {'constraints': ['keep']}
        refs = docs.task_document_refs(self.snapshot, ['A', 'B'], self.assessments,
                                      self.plan['guide_reviews'])
        self.assertEqual(set(refs['advice']), {f'agent_doc/advice/{n}.md' for n in ('a', 'b', 'shared')})
        self.assertEqual(set(refs['task_details']), {'A', 'B'})
        refs['future_field']['constraints'].clear()
        refs['guides'].clear()
        refs['guide_reviews'][0]['task_refs'].clear()
        self.assertEqual(self.snapshot['future_field']['constraints'], ['keep'])
        self.assertEqual(self.snapshot['guides'], original['guides'])
        self.assertEqual(self.plan['guide_reviews'][0]['task_refs'], ['A', 'B', 'C'])

    def test_adopted_and_adapted_edits_rejected(self):
        for name, tid in (('a', 'A'), ('b', 'B')):
            with self.subTest(name=name):
                path = self.root / f'agent_doc/advice/{name}.md'
                old = path.read_bytes(); path.write_bytes(old + b'Changed\n')
                with self.assertRaisesRegex(ValueError, 'adopted_advice'):
                    docs.check_task_documents(self.root, self.task(tid))
                with self.assertRaises(ValueError): validate_contract(self.plan, self.root)
                path.write_bytes(old)

    def test_sibling_source_is_not_this_workers_dependency(self):
        (self.root / 'agent_doc/advice/b.md').write_text('Edited sibling proposal\n')
        docs.check_task_documents(self.root, self.task('A'))
        with self.assertRaises(ValueError): docs.check_task_documents(self.root, self.task('B'))
        # Global plan remains bound to every adopted source.
        with self.assertRaises(ValueError): validate_contract(self.plan, self.root)

    def test_deferred_rejected_and_new_sources_remain_nonbinding(self):
        for action in ('defer', 'reject'):
            with self.subTest(action=action):
                self.assessments[-1]['disposition'] = action
                docs.bind_advice(self.plan, self.assessments)
                (self.root / 'agent_doc/advice/deferred.md').write_text('Changed nonbinding source\n')
                (self.root / 'agent_doc/advice/new.md').write_text('New unassessed source\n')
                validate_contract(self.plan, self.root)
                docs.check_task_documents(self.root, self.task('C'))

    def test_any_guide_set_or_bytes_change_still_blocks(self):
        guide = self.root / 'agent_doc/guide/policy.md'
        old = guide.read_bytes()
        for action in ('edit', 'add', 'delete', 'rename'):
            with self.subTest(action=action):
                extra = guide.with_name('other.md')
                if action == 'edit': guide.write_bytes(old + b'Changed\n')
                elif action == 'add': extra.write_bytes(b'New guide\n')
                elif action == 'delete': guide.unlink()
                else: guide.rename(extra)
                with self.assertRaises(ValueError): docs.check_task_documents(self.root, self.task('C'))
                with self.assertRaises(ValueError): validate_contract(self.plan, self.root)
                if extra.exists(): extra.unlink()
                guide.write_bytes(old)

    def test_old_broad_node_requires_explicit_replan(self):
        old = copy.deepcopy(self.plan)
        for task in old['tasks']:
            task['document_refs']['advice'] = copy.deepcopy(self.snapshot['advice'])
        with self.assertRaisesRegex(ValueError, 'task document dependencies'):
            validate_contract(old, self.root)
        validate_contract(self.plan, self.root)


if __name__ == '__main__':
    unittest.main()
