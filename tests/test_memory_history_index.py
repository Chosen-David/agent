"""Legacy migration, full audit history and implicit rowid ordering."""
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import sqlite3
import tempfile
import unittest

from agent_runtime.project_memory import MemoryError, MemoryLedger, main
from agent_runtime.project_docs import migrate


class HistoryIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = MemoryLedger(self.root, create=True)

    def columns(self):
        with sqlite3.connect(self.ledger.path) as db:
            return [r[2] for r in db.execute('PRAGMA index_info(memory_events_entry)')]

    def snapshot(self):
        with sqlite3.connect(self.ledger.path) as db:
            return {t: db.execute('SELECT * FROM ' + t + ' ORDER BY rowid').fetchall()
                    for t in ('entries', 'dependencies', 'document_dependencies',
                              'events', 'sqlite_sequence')}

    def legacy(self):
        self.ledger.add('a', 'claim', 'original', 'test', evidence='verified')
        self.ledger.add('b', 'claim', 'derived', 'test', deps=['a'], evidence='verified')
        self.ledger.correct('b', 'b2', 'revision', 'test', 'correction')
        (self.root / 'TASK.md').write_text('## 2026-10-16\n- [ ] [T1] Audit memory\n')
        docs = migrate(self.root, '2026-10-16')
        self.ledger.add('bound', 'claim', 'bound', 'test', evidence='verified', document_refs=docs)
        with sqlite3.connect(self.ledger.path) as db:
            db.execute('DROP INDEX IF EXISTS memory_events_entry')

    def test_fresh_index_has_entry_and_implicit_rowid_keys(self):
        self.assertEqual(self.columns(), ['entry_id'])
        with sqlite3.connect(self.ledger.path) as db:
            indexes = {r[1]: r for r in db.execute('PRAGMA index_list(events)')}
            self.assertEqual(indexes['memory_events_entry'][2], 0)
            self.assertEqual(indexes['memory_events_entry'][4], 0)
            info = db.execute('PRAGMA index_xinfo(memory_events_entry)').fetchall()
            self.assertEqual(info[1][1], -1)

    def test_legacy_read_and_idempotent_explicit_upgrade_preserve_all_rows(self):
        self.legacy()
        before = self.snapshot()
        self.assertTrue(before['document_dependencies'])
        physical = self.ledger.path.read_bytes()
        history = self.ledger.history('b')
        self.assertEqual(self.ledger.path.read_bytes(), physical)
        self.assertEqual(self.columns(), [])
        for _ in range(2):
            MemoryLedger(self.root, create=True)
            self.assertEqual(self.columns(), ['entry_id'])
            self.assertEqual(self.snapshot(), before)
            self.assertEqual(self.ledger.history('b'), history)

    def test_explicit_sequence_order_with_gaps_negative_ids_and_backwards_clocks(self):
        self.ledger.add('a', 'claim', 'a', 'test', evidence='verified')
        self.ledger.add('A', 'claim', 'other case', 'test', evidence='verified')
        with self.ledger._connect(write=True) as db:
            for seq, clock in [(31, '1900'), (-7, '2200'), (0, '2100'), (10, '1800')]:
                db.execute('INSERT INTO events(sequence,entry_id,action,reason,source,created_at) '
                           'VALUES(?,?,?,?,?,?)', (seq, 'a', 'fixture', 'reason', 'test', clock))
        result = self.ledger.history('a')
        self.assertEqual([r['sequence'] for r in result['events']], [-7, 0, 1, 10, 31])
        self.assertTrue(all(r['entry_id'] == 'a' for r in result['events']))
        self.assertEqual(len(self.ledger.history('A')['events']), 1)

    def test_failed_cli_add_can_upgrade_without_changing_business_history(self):
        self.legacy()
        before = self.snapshot()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            rc = main(['--root', str(self.root), 'add', '--id', 'a', '--kind', 'claim',
                       '--content', 'duplicate', '--source', 'test'])
        self.assertEqual(rc, 2)
        self.assertEqual(self.columns(), ['entry_id'])
        self.assertEqual(self.snapshot(), before)

    def test_unknown_same_named_index_is_preserved(self):
        with sqlite3.connect(self.ledger.path) as db:
            db.execute('DROP INDEX IF EXISTS memory_events_entry')
            db.execute('CREATE INDEX memory_events_entry ON events(action)')
        MemoryLedger(self.root, create=True)
        self.assertEqual(self.columns(), ['action'])
        self.assertEqual(self.ledger.list(), [])

    def test_same_named_table_failure_preserves_business_rows(self):
        self.legacy()
        with sqlite3.connect(self.ledger.path) as db:
            db.execute('CREATE TABLE memory_events_entry(marker TEXT)')
        before = self.snapshot()
        with self.assertRaises(MemoryError):
            MemoryLedger(self.root, create=True)
        self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()
