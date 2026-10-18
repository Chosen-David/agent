"""Exact index-state parity, batch boundaries, and statement-count regression."""
import sqlite3
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from agent_runtime import knowledge_index as index
from scripts.benchmark_knowledge_index import corpus, logical, transition


class BatchIndexTests(unittest.TestCase):
    def test_delete_statements_are_bounded_by_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'index.db'
            store = corpus(129)
            index.build_index(store, db)
            statements = []
            connect = index._connect
            def traced(*args, **kwargs):
                con = connect(*args, **kwargs)
                con.set_trace_callback(statements.append)
                return con
            with patch.object(index, '_connect', traced):
                result = index.build_index(transition(store, 'all'), db)
            deletes = [sql for sql in statements if sql.startswith('DELETE FROM docs WHERE')]
            self.assertEqual(result['updated'], 129)
            self.assertEqual(len(deletes), 2)
            with sqlite3.connect(db) as con:
                self.assertEqual(con.execute('SELECT count(*) FROM docs').fetchone()[0], 129)

    def test_multiple_batches_rollback_and_empty_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'index.db'
            store = corpus(257)
            index.build_index(store, db)
            before = logical(db)
            with patch.object(index, 'sections', side_effect=RuntimeError('interrupted')):
                with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                    index.build_index(transition(store, 'all'), db)
            self.assertEqual(logical(db), before)
            empty = transition(store, 'delete')
            self.assertEqual(index.build_index(empty, db)['removed'], 257)
            self.assertEqual(index.build_index(empty, db)['updated'], 0)
            self.assertEqual(logical(db)['docs'], [])
            self.assertEqual(logical(db)['chunks'], [])


if __name__ == '__main__':
    unittest.main()
