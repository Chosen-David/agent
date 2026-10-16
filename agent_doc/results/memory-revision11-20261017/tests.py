"""Correction dependency validation uses the public memory error contract."""
import sqlite3
import tempfile
import unittest
from agent_runtime.project_memory import MemoryError, MemoryLedger


class MemoryRevisionInputTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.ledger = MemoryLedger(tmp.name, create=True)
        self.ledger.add('old', 'claim', 'old', 'fixture', evidence='verified')
        self.ledger.add('child', 'claim', 'child', 'fixture', deps=['old'], evidence='verified')
        self.ledger.add('unrelated', 'observation', 'raw', 'fixture', evidence='verified')

    def rows(self):
        with sqlite3.connect(self.ledger.path) as db:
            return {table: db.execute('SELECT * FROM ' + table + ' ORDER BY rowid').fetchall()
                    for table in ('entries', 'dependencies', 'events', 'document_dependencies')}

    def test_malformed_dependencies_raise_memory_error_without_writes(self):
        for deps in (None, 1, [[]], [{}], ['child', {}]):
            with self.subTest(deps=deps):
                before = self.rows()
                with self.assertRaisesRegex(MemoryError, 'unique stable IDs'):
                    self.ledger.correct('old', 'new', 'new', 'user', 'reason', deps=deps)
                self.assertEqual(self.rows(), before)

    def test_valid_list_and_tuple_dependencies_correct_and_invalidate(self):
        for index, container in enumerate((list, tuple)):
            old_id = 'root' + str(index)
            child_id = 'dependent' + str(index)
            new_id = 'revision' + str(index)
            self.ledger.add(old_id, 'claim', 'old', 'fixture', evidence='verified')
            self.ledger.add(child_id, 'claim', 'derived', 'fixture', deps=[old_id], evidence='verified')
            result = self.ledger.correct(old_id, new_id, 'changed', 'user', 'reason',
                                         deps=container(['unrelated']))
            self.assertEqual(result['revision']['deps'], ['unrelated'])
            self.assertEqual(result['affected'], [child_id])
            self.assertEqual(self.ledger.history(child_id)['entry']['status'], 'stale')

    def test_duplicate_missing_and_invalidated_dependencies_still_rejected(self):
        for deps in (['unrelated', 'unrelated'], ['missing'], ['old'], ['child']):
            with self.subTest(deps=deps):
                before = self.rows()
                with self.assertRaises(MemoryError):
                    self.ledger.correct('old', 'new', 'new', 'user', 'reason', deps=deps)
                self.assertEqual(self.rows(), before)

    def test_candidate_acceptance_preserves_dependency_and_content(self):
        self.ledger.add('candidate', 'claim', 'candidate text', 'fixture', deps=['unrelated'])
        result = self.ledger.accept('candidate', 'accepted', 'review', 'verified')
        self.assertEqual(result['revision']['content'], 'candidate text')
        self.assertEqual(result['revision']['deps'], ['unrelated'])
        self.assertEqual(self.ledger.check(['accepted'])[0]['evidence'], 'verified')
