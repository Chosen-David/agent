"""Real SQLite initialization and legacy-ledger index compatibility."""
from contextlib import redirect_stdout
import io
from pathlib import Path
import sqlite3
import tempfile
import unittest

from agent_runtime.project_memory import MemoryLedger, main


class ReverseIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = MemoryLedger(self.root, create=True)

    def snapshot(self):
        with sqlite3.connect(self.ledger.path) as db:
            return {t: db.execute('SELECT * FROM ' + t + ' ORDER BY rowid').fetchall()
                    for t in ('entries', 'dependencies', 'document_dependencies',
                              'events', 'sqlite_sequence')}

    def index_columns(self):
        with sqlite3.connect(self.ledger.path) as db:
            return [r[2] for r in db.execute('PRAGMA index_info(memory_dependencies_parent)')]

    def legacy(self):
        self.ledger.add('a', 'claim', 'old', 'test', evidence='verified')
        self.ledger.add('b', 'claim', 'derived', 'test', deps=['a'], evidence='verified')
        self.ledger.correct('b', 'b2', 'revised', 'test', 'correction')
        with sqlite3.connect(self.ledger.path) as db:
            db.execute('DROP INDEX IF EXISTS memory_dependencies_parent')

    def test_new_database_has_nonunique_parent_child_index(self):
        self.assertEqual(self.index_columns(), ['parent', 'child'])
        with sqlite3.connect(self.ledger.path) as db:
            indexes = {r[1]: r for r in db.execute('PRAGMA index_list(dependencies)')}
            self.assertEqual(indexes['memory_dependencies_parent'][2], 0)
            self.assertEqual(indexes['memory_dependencies_parent'][4], 0)
            self.assertTrue(any(r[3] == 'pk' for r in indexes.values()))

    def test_legacy_reads_do_not_migrate_and_explicit_upgrade_is_idempotent(self):
        self.legacy()
        before = self.snapshot()
        schema = self.ledger.path.read_bytes()
        self.assertEqual([r['id'] for r in MemoryLedger(self.root).impact('a')], ['b'])
        self.assertEqual(self.ledger.path.read_bytes(), schema)
        self.assertEqual(self.index_columns(), [])
        for _ in range(2):
            MemoryLedger(self.root, create=True)
            self.assertEqual(self.index_columns(), ['parent', 'child'])
            self.assertEqual(self.snapshot(), before)

    def test_cli_add_uses_existing_initialization_upgrade(self):
        self.legacy()
        before = self.snapshot()
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(['--root', str(self.root), 'add', '--id', 'c',
                                   '--kind', 'claim', '--content', 'new', '--source', 'test']), 0)
        self.assertEqual(self.index_columns(), ['parent', 'child'])
        after = self.snapshot()
        for table in ('dependencies', 'document_dependencies'):
            self.assertEqual(after[table], before[table])
        self.assertEqual(after['entries'][:-1], before['entries'])
        self.assertEqual(after['events'][:-1], before['events'])

    def test_unknown_same_named_index_is_not_rebuilt(self):
        with sqlite3.connect(self.ledger.path) as db:
            db.execute('DROP INDEX IF EXISTS memory_dependencies_parent')
            db.execute('CREATE INDEX memory_dependencies_parent ON dependencies(child)')
        MemoryLedger(self.root, create=True)
        self.assertEqual(self.index_columns(), ['child'])
        # IF NOT EXISTS preserves unknown schema objects; no speed guarantee here.
        self.assertEqual(self.ledger.list(), [])


if __name__ == '__main__':
    unittest.main()
