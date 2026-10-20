import tempfile
import unittest
from unittest.mock import patch
from agent_runtime import project_memory as m


class ClosureSchemaTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.ledger=m.MemoryLedger(tmp.name, create=True)
        self.ledger.add('a','claim','parent','fixture',evidence='verified')
        self.ledger.add('b','claim','child','fixture',deps=['a'],evidence='verified')

    def test_two_argument_helper(self):
        original=m._read_entry
        def helper(db, ref):
            return original(db,ref)
        with patch.object(m,'_read_entry',helper):
            self.assertEqual([x['id'] for x in self.ledger._context_closure(['b'])],['b','a'])

    def test_helper_ddl(self):
        original=m._read_entry
        def helper(db, ref, schema_state=None):
            value=original(db,ref,schema_state)
            if ref=='b':
                db.execute('DROP TABLE document_dependencies')
            return value
        with patch.object(m,'_read_entry',helper):
            self.assertEqual([x['id'] for x in self.ledger._context_closure(['b'])],['b','a'])

    def test_schema_fresh_between_calls(self):
        expected=self.ledger._context_closure(['b'])
        with self.ledger._connect(write=True) as db:
            db.execute('DROP TABLE document_dependencies')
        self.assertEqual(self.ledger._context_closure(['b']),expected)
        with self.ledger._connect(write=True) as db:
            db.execute('CREATE TABLE document_dependencies(entry_id TEXT PRIMARY KEY,snapshot TEXT NOT NULL)')
            db.execute("INSERT INTO document_dependencies VALUES('a','broken')")
        with self.assertRaises(ValueError):
            self.ledger._context_closure(['b'])
