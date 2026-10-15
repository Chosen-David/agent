"""Request-local reuse must not weaken memory or document validity gates."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.project_memory import MemoryError, MemoryLedger


class MemoryCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = MemoryLedger(self.root, create=True)
        for name, deps in (('parent', []), ('a', ['parent']), ('b', ['parent']),
                           ('leaf', ['a', 'b'])):
            self.ledger.add(name, 'claim', name, 'synthetic', deps=deps, evidence='verified')

    def test_each_root_is_hydrated_once_including_dependency_first_roots(self):
        expected = [self.ledger.history(ref)['entry'] for ref in ('leaf', 'parent', 'a')]
        with patch.object(MemoryLedger, '_get', wraps=MemoryLedger._get) as get:
            actual = self.ledger.check(['leaf', 'parent', 'a'])
        self.assertEqual(actual, expected)
        self.assertEqual([c.args[1] for c in get.call_args_list], ['leaf', 'a', 'parent', 'b'])

    def test_returned_objects_are_fresh_on_every_call(self):
        actual = self.ledger.check(['leaf'])
        actual[0]['content'] = 'caller mutation'
        actual[0]['deps'].clear()
        actual[0]['scope'].append('changed')
        again = self.ledger.check(('leaf',))
        self.assertEqual(again[0]['content'], 'leaf')
        self.assertEqual(again[0]['deps'], ['a', 'b'])
        self.assertEqual(again[0]['scope'], [])

    def test_correction_between_calls_rechecks_ancestors(self):
        self.ledger.check(['leaf'])
        self.ledger.correct('parent', 'parent2', 'corrected', 'user', 'fixture correction')
        with self.assertRaisesRegex(MemoryError, 'stale'):
            self.ledger.check(['leaf'])
        self.assertEqual(self.ledger.check(['parent2'])[0]['content'], 'corrected')

    def test_document_binding_is_revalidated_every_call(self):
        from agent_runtime.project_docs import migrate, snapshot_project_docs
        (self.root / 'TASK.md').write_text('## 2026-10-16\n- [ ] [T1] Original task\n')
        snapshot = migrate(self.root, '2026-10-16')
        self.ledger.add('bound', 'claim', 'bound claim', 'synthetic', evidence='verified',
                        document_refs=snapshot)
        self.ledger.check(['bound'])
        # Only an AI-owned task fixture changes; human guide paths stay untouched.
        task = self.root / 'agent_doc/task/TASK.md'
        task.write_text(task.read_text().replace('Original task', 'Changed task'))
        with self.assertRaisesRegex(MemoryError, 'document dependencies'):
            self.ledger.check(['bound'])
        self.assertEqual(self.ledger.check(['parent'])[0]['id'], 'parent')

    def test_failed_traversal_is_not_cached(self):
        original = MemoryLedger._get
        def fail(db, ref):
            if ref == 'parent':
                raise MemoryError('injected ancestor failure')
            return original(db, ref)
        with patch.object(MemoryLedger, '_get', side_effect=fail):
            with self.assertRaisesRegex(MemoryError, 'injected ancestor'):
                self.ledger.check(['leaf'])
        self.assertEqual(self.ledger.check(['leaf'])[0]['id'], 'leaf')

    def test_legacy_schema_and_missing_dependency_schema(self):
        with self.ledger._connect(write=True) as db:
            db.execute('DROP TABLE document_dependencies')
        self.assertIsNone(self.ledger.check(['leaf'])[0]['document_refs'])
        with self.ledger._connect(write=True) as db:
            db.execute('DROP TABLE dependencies')
        with self.assertRaisesRegex(MemoryError, 'no such table: dependencies'):
            self.ledger.check(['leaf'])

    def test_deep_chain_does_not_depend_on_python_recursion_limit(self):
        # Bulk-load a valid synthetic history; timing add() would test a
        # different operation and repeat validation of every partial chain.
        with self.ledger._connect(write=True) as db:
            for i in range(1200):
                name = f'deep{i:04d}'
                db.execute('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',
                           (name, 'claim', 'payload', 'synthetic', '[]',
                            'verified', 'active', '2026-10-16'))
                if i:
                    db.execute('INSERT INTO dependencies VALUES(?,?)',
                               (name, f'deep{i-1:04d}'))
        self.assertEqual(self.ledger.check(['deep1199'])[0]['id'], 'deep1199')

    def test_first_error_keeps_lazy_depth_first_order(self):
        with self.ledger._connect(write=True) as db:
            db.execute("UPDATE entries SET status='stale' WHERE id IN ('parent','b')")
        with patch.object(MemoryLedger, '_get', wraps=MemoryLedger._get) as get:
            with self.assertRaisesRegex(MemoryError, 'memory parent is stale'):
                self.ledger.check(['leaf', 'b'])
        self.assertEqual([c.args[1] for c in get.call_args_list], ['leaf', 'a', 'parent'])


if __name__ == '__main__':
    unittest.main()
