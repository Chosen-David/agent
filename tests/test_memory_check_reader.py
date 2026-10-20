"""Public check must preserve legacy custom-reader semantics."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import agent_runtime.project_memory as memory


class PublicCheckReaderTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.ledger = memory.MemoryLedger(Path(tmp.name), create=True)
        self.ledger.add('parent', 'claim', 'parent', 'synthetic', evidence='verified')
        self.ledger.add('leaf', 'claim', 'leaf', 'synthetic', deps=['parent'], evidence='verified')

    def test_two_argument_reader_keeps_call_contract(self):
        original = memory._read_entry
        calls = []
        def read(db, ref):
            calls.append(ref)
            return original(db, ref)
        with patch.object(memory, '_read_entry', read):
            result = self.ledger.check(['leaf'])
        self.assertEqual(result[0]['id'], 'leaf')
        self.assertEqual(calls, ['leaf', 'parent'])

    def test_reader_ddl_between_nodes_observes_fresh_schema(self):
        original = memory._read_entry
        states = []
        def read(db, ref, schema_state=None):
            states.append(schema_state)
            entry = original(db, ref, schema_state)
            if ref == 'leaf':
                db.execute('DROP TABLE document_dependencies')
            return entry
        with patch.object(memory, '_read_entry', read):
            result = self.ledger.check(['leaf'])
        self.assertEqual(result[0]['id'], 'leaf')
        self.assertEqual(states, [None, None])


if __name__ == '__main__':
    unittest.main()
