"""Traversal-local schema reuse must preserve hydration and validity gates."""
import json
import sys
from contextlib import contextmanager
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import agent_runtime.project_memory as memory


class MemorySchemaTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.ledger = memory.MemoryLedger(Path(tmp.name), create=True)
        for name, deps in [('parent', []), ('a', ['parent']), ('b', ['parent']), ('leaf', ['a', 'b'])]:
            self.ledger.add(name, 'claim', name, 'synthetic', deps=deps, evidence='verified')

    def trace_check(self, refs):
        trace = []
        original = memory._read_entry
        def profile(frame, event, arg):
            if event == 'call' and frame.f_code is original.__code__:
                frame.f_locals['db'].set_trace_callback(trace.append)
        previous = sys.getprofile()
        try:
            sys.setprofile(profile)
            result = self.ledger.check(refs)
        finally:
            sys.setprofile(previous)
        return result, trace

    @staticmethod
    def schema_queries(trace):
        return [q for q in trace if 'FROM sqlite_master' in q]

    def test_one_lookup_present_and_absent_without_skipping_nodes(self):
        for present in (True, False):
            if not present:
                with self.ledger._connect(write=True) as db:
                    db.execute('DROP TABLE document_dependencies')
            values, trace = self.trace_check(['leaf', 'parent'])
            self.assertEqual([v['id'] for v in values], ['leaf', 'parent'])
            self.assertEqual(len(self.schema_queries(trace)), 1)
            reads = [q for q in trace if q.startswith('SELECT * FROM entries WHERE id=')]
            self.assertEqual([q.split("'")[1] for q in reads], ['leaf', 'a', 'parent', 'b'])

    def test_unknown_or_bad_scope_precedes_schema_lookup(self):
        with self.assertRaisesRegex(memory.MemoryError, 'unknown memory ID'):
            self.ledger.check(['missing'])
        with self.ledger._connect(write=True) as db:
            db.execute("UPDATE entries SET scope='broken',status='stale' WHERE id='leaf'")
        with self.assertRaises(json.JSONDecodeError):
            self.ledger.check(['leaf'])

    def test_get_override_keeps_original_calls_and_schema_queries(self):
        original = memory.MemoryLedger._get
        with patch.object(memory.MemoryLedger, '_get', wraps=original) as get:
            _, trace = self.trace_check(['leaf'])
        self.assertEqual([x.args[1] for x in get.call_args_list], ['leaf', 'a', 'parent', 'b'])
        self.assertEqual(len(self.schema_queries(trace)), 4)

    def test_check_override_is_not_bypassed(self):
        with patch.object(memory.MemoryLedger, '_check', return_value=['sentinel']) as check:
            self.assertEqual(self.ledger.check(['leaf']), ['sentinel'])
            self.assertEqual(check.call_args.args[1], ['leaf'])

    def test_instance_check_override_is_not_bypassed(self):
        self.ledger._check = lambda *args: ['instance sentinel']
        self.assertEqual(self.ledger.check(['leaf']), ['instance sentinel'])

    def test_instance_connect_override_keeps_uncached_schema_reads(self):
        original = self.ledger._connect
        trace = []
        @contextmanager
        def customized():
            with original() as db:
                db.set_trace_callback(trace.append)
                yield db
        self.ledger._connect = customized
        self.assertEqual(self.ledger.check(['leaf'])[0]['id'], 'leaf')
        self.assertEqual(len(self.schema_queries(trace)), 4)

    def test_replaced_global_row_factory_keeps_same_connection_ddl_behavior(self):
        original = memory.sqlite3.Row
        def custom_row(cursor, values):
            row = original(cursor, values)
            if (cursor.description[0][0] == 'id' and row[0] == 'a'):
                cursor.connection.execute('DROP TABLE IF EXISTS document_dependencies')
            return row
        with patch.object(memory.sqlite3, 'Row', custom_row):
            self.assertEqual(self.ledger.check(['leaf'])[0]['id'], 'leaf')

    def test_schema_changes_between_calls_and_direct_get_are_fresh(self):
        self.ledger.check(['leaf'])
        with self.ledger._connect(write=True) as db:
            db.execute('DROP TABLE document_dependencies')
        self.assertIsNone(self.ledger.check(['leaf'])[0]['document_refs'])
        with self.ledger._connect(write=True) as db:
            db.execute('CREATE TABLE document_dependencies(entry_id TEXT PRIMARY KEY,snapshot TEXT NOT NULL)')
            db.execute("INSERT INTO document_dependencies VALUES('parent','broken')")
        with self.assertRaises(json.JSONDecodeError):
            self.ledger.check(['leaf'])
        with self.ledger._connect(write=True) as db:
            self.assertIsNone(memory.MemoryLedger._get(db, 'a')['document_refs'])
            db.execute("INSERT INTO document_dependencies VALUES('a','broken')")
            with self.assertRaises(json.JSONDecodeError):
                memory.MemoryLedger._get(db, 'a')

    def test_direct_check_preserves_same_connection_ddl_between_nodes(self):
        original = memory._read_entry
        def read(db, ref, schema_state=None):
            entry = original(db, ref, schema_state)
            if ref == 'leaf':
                db.execute('DROP TABLE document_dependencies')
            return entry
        with self.ledger._connect(write=True) as db, patch.object(memory, '_read_entry', side_effect=read):
            self.assertEqual(memory.MemoryLedger._check(db, ['leaf'], self.ledger.root)[0]['id'], 'leaf')


if __name__ == '__main__':
    unittest.main()
