"""Scope order must not hide a shared-scope memory review signal."""
from pathlib import Path
import tempfile
import unittest

from agent_runtime.project_memory import MemoryLedger


class ReconcileScopeTests(unittest.TestCase):
    def test_all_scopes_are_checked_and_siblings_count_once(self):
        for scopes in (['first', 'shared'], ['shared', 'first']):
            with self.subTest(scopes=scopes), tempfile.TemporaryDirectory() as tmp:
                ledger = MemoryLedger(Path(tmp), create=True)
                ledger.add('old', 'observation', 'previous evidence', 'fixture', evidence='verified', scope=scopes)
                ledger.add('new', 'observation', 'new shared-scope evidence', 'fixture', evidence='verified', scope=['shared'])
                ledger.add('both', 'observation', 'new evidence with two scopes', 'fixture', evidence='verified',
                           scope=['first', 'shared'])
                ledger.add('other', 'observation', 'unrelated evidence', 'fixture', evidence='verified', scope=['other'])
                # Explicit timestamps avoid millisecond-resolution ordering races.
                with ledger._connect(write=True) as db:
                    db.execute("UPDATE entries SET created_at='2026-01-01T00:00:00Z' WHERE id='old'")
                    db.execute("UPDATE entries SET created_at='2026-01-02T00:00:00Z' WHERE id<>'old'")
                before = ledger.list('all')
                result = ledger.reconcile()
                counts = {row['id']: row['newer_sibling_count'] for row in result['potentially_obsolete']}
                self.assertEqual(counts, {'old': 2})
                self.assertEqual(ledger.list('all'), before)
                filtered = ledger.reconcile(scope='shared')
                self.assertEqual(filtered['potentially_obsolete'], result['potentially_obsolete'])
