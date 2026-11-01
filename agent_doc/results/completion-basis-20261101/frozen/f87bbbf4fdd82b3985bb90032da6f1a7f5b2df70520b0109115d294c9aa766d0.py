"""Complete memory context closure without repeatedly walking deep ancestry."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from agent_runtime.handoff_basis import basis_context
from agent_runtime.project_memory import MemoryLedger, MemoryError, _read_entry


class MemoryContextClosureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.ledger = MemoryLedger(self.root, create=True)

    def seed(self, count=32):
        for i in range(count):
            self.ledger.add(f'm{i:03}', 'claim', f'complete content {i}', 'fixture',
                deps=[f'm{i-1:03}'] if i else [], evidence='verified')
        return {'input_version': 'v1', 'memory_refs': [f'm{count-1:03}'], 'artifacts': []}

    def test_complete_chain_does_not_rewalk_each_ancestor_generation(self):
        record = self.seed(); calls = []
        def profile(frame, event, arg):
            if event == 'call' and frame.f_code is _read_entry.__code__:
                calls.append(frame.f_locals['entry_id'])
        previous = sys.getprofile()
        try:
            sys.setprofile(profile)
            pack = basis_context(self.root, record, {}, max_chars=100000)
        finally:
            sys.setprofile(previous)
        entries = json.loads(pack['payload'])['memory_entries']
        self.assertEqual([e['id'] for e in entries], [f'm{i:03}' for i in range(32)])
        self.assertEqual([e['content'] for e in entries], [f'complete content {i}' for i in range(32)])
        self.assertLessEqual(len(calls), 5 * 32)

    def test_known_leaf_keeps_missing_ancestors_and_correction_blocks_reuse(self):
        record = self.seed(6)
        pack = basis_context(self.root, record, {}, known_memory_ids=['m005'], max_chars=100000)
        self.assertEqual([e['id'] for e in json.loads(pack['payload'])['memory_entries']], [f'm{i:03}' for i in range(5)])
        self.assertEqual(pack['reused_memory_ids'], ['m005'])
        self.ledger.correct('m000', 'v2', 'correction', 'user', 'changed')
        with self.assertRaises(MemoryError):
            basis_context(self.root, record, {}, known_memory_ids=['m005'], max_chars=100000)

    def test_check_still_returns_only_requested_roots_in_request_order(self):
        self.seed(5)
        self.assertEqual([e['id'] for e in self.ledger.check(['m004', 'm002'])], ['m004', 'm002'])

    def test_custom_public_check_keeps_observable_generation_calls(self):
        record = self.seed(4); seen = []; original = MemoryLedger.check
        def checked(ledger, refs):
            seen.append(list(refs)); return original(ledger, refs)
        with patch.object(MemoryLedger, 'check', checked):
            pack = basis_context(self.root, record, {}, max_chars=100000)
        self.assertEqual(len(json.loads(pack['payload'])['memory_entries']), 4)
        self.assertEqual(seen, [['m003'], ['m002'], ['m001'], ['m000']])

    def test_custom_walk_keeps_legacy_signature(self):
        record = self.seed(4)
        original = MemoryLedger._walk
        seen = []
        def walk(db, refs, root=None, schema_state=None):
            seen.append(list(refs))
            return original(db, refs, root, schema_state)
        with patch.object(MemoryLedger, '_walk', staticmethod(walk)):
            pack = basis_context(self.root, record, {}, max_chars=100000)
        self.assertEqual(len(json.loads(pack['payload'])['memory_entries']), 4)
        self.assertEqual(seen, [['m003'], ['m002'], ['m001'], ['m000']])

    def test_custom_row_factory_requests_legacy_path(self):
        import sqlite3
        with patch.object(sqlite3, 'Row', lambda cursor, row: row):
            self.assertIsNone(self.ledger._context_closure(['unused']))
