"""Reconcile must not combine active rows with later correction metadata."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.project_memory import MemoryLedger


class ReconcileSnapshotTests(unittest.TestCase):
    def test_correction_during_hydration_keeps_one_read_snapshot(self):
        self._check_snapshot(MemoryLedger)

    def test_inherited_list_keeps_one_read_snapshot(self):
        class InheritedLedger(MemoryLedger):
            pass
        self._check_snapshot(InheritedLedger)

    def _check_snapshot(self, ledger_type):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = ledger_type(Path(tmp), create=True)
            ledger.add('old', 'observation', 'old input', 'fixture', evidence='verified')
            ledger.add('derived', 'claim', 'derived input', 'fixture',
                       deps=['old'], evidence='verified')
            # WAL lets the independent writer commit during a pinned read.
            with sqlite3.connect(ledger.path) as db:
                self.assertEqual(db.execute('PRAGMA journal_mode=WAL').fetchone()[0], 'wal')
            original = MemoryLedger._get
            corrected = []

            def interleave(db, entry_id):
                value = original(db, entry_id)
                if not corrected:
                    corrected.append(True)
                    ledger.correct('old', 'new', 'corrected input', 'fixture', 'input correction')
                return value

            with patch.object(MemoryLedger, '_get', staticmethod(interleave)):
                observed = ledger.reconcile()
            self.assertEqual(corrected, [True])
            self.assertEqual((observed['active_total'], observed['flagged_total']), (2, 0))
            current = ledger.reconcile()
            self.assertEqual((current['active_total'], current['flagged_total']), (1, 0))
            self.assertEqual(ledger.history('old')['entry']['status'], 'superseded')
            self.assertEqual(ledger.history('derived')['entry']['status'], 'stale')

    def test_custom_list_preserves_subclass_and_instance_overrides(self):
        calls = []

        class CustomLedger(MemoryLedger):
            def list(self, status='active', scope=None):
                calls.append((status, scope))
                return []

        with tempfile.TemporaryDirectory() as tmp:
            ledger = CustomLedger(Path(tmp), create=True)
            ledger.add('entry', 'observation', 'input', 'fixture', evidence='verified')
            result = ledger.reconcile('topic')
            self.assertEqual(calls, [('active', 'topic')])
            self.assertEqual(result['active_total'], 0)
            self.assertIn('custom list snapshot consistency unchecked', result['scope'])
            calls.clear()
            ledger.list = lambda status, scope: calls.append((status, scope)) or []
            self.assertEqual(ledger.reconcile()['active_total'], 0)
            self.assertEqual(calls, [('active', None)])

    def test_list_bound_to_another_ledger_is_not_bypassed(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = MemoryLedger(Path(tmp) / 'first', create=True)
            other = MemoryLedger(Path(tmp) / 'second', create=True)
            other.add('entry', 'observation', 'input', 'fixture', evidence='verified')
            ledger.list = other.list
            result = ledger.reconcile()
            self.assertEqual(result['active_total'], 1)
            self.assertIn('custom list snapshot consistency unchecked', result['scope'])
