"""Memory retrieval parity against the original eager-hydration algorithm."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

from agent_runtime.project_memory import MemoryError, MemoryLedger


def eager(ledger, status='active', scope=None):
    if status not in ('active', 'candidate', 'stale', 'superseded', 'all'):
        raise MemoryError('unknown status')
    with ledger._connect() as db:
        ids = db.execute('SELECT id FROM entries ORDER BY created_at,id').fetchall()
        values = [ledger._get(db, row[0]) for row in ids]
        return [v for v in values if (status == 'all' or v['status'] == status)
                and (scope is None or scope in v['scope'])]


class MemoryRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ledger = MemoryLedger(Path(self.tmp.name), create=True)
        for i, status in enumerate(('active', 'candidate', 'stale', 'superseded') * 4):
            self.ledger.add(f'm{15-i:02}', 'claim', f'body-{i}', 'fixture',
                            scope=['T1', 'T10'] if i % 2 else ['T2'], evidence='verified')
            with self.ledger._connect(write=True) as db:
                db.execute('UPDATE entries SET status=?,created_at=? WHERE id=?',
                           (status, '2026-10-15', f'm{15-i:02}'))

    def test_complete_packets_and_exact_scope_order(self):
        for status in ('active', 'candidate', 'stale', 'superseded', 'all'):
            for scope in (None, 'T1', 'T10', 'T', '', 1, ['T1']):
                with self.subTest(status=status, scope=scope):
                    self.assertEqual(self.ledger.list(status, scope), eager(self.ledger, status, scope))

    def test_excluded_corruption_still_fails(self):
        depth = sys.getrecursionlimit() + 10
        for payload in ('not-json', b'"\xff"', '[' * depth + '0' + ']' * depth):
            with self.subTest(payload_type=type(payload).__name__):
                with self.ledger._connect(write=True) as db:
                    db.execute('UPDATE entries SET scope=? WHERE id=?', (payload, 'm14'))
                errors = []
                outputs = []
                for call in (eager, lambda ledger: ledger.list()):
                    try:
                        outputs.append(call(self.ledger))
                    except Exception as exc:
                        errors.append((type(exc), str(exc)))
                if errors:
                    self.assertEqual(len(errors), 2)
                    self.assertEqual(errors[0], errors[1])
                else:
                    # Python builds differ in whether deeply nested JSON is
                    # accepted. Preserve either outcome rather than inventing
                    # a fixed decoder depth limit.
                    self.assertEqual(outputs[0], outputs[1])
        with self.ledger._connect(write=True) as db:
            db.execute('UPDATE entries SET scope=? WHERE id=?', ('[]', 'm14'))
            db.execute('INSERT INTO document_dependencies VALUES(?,?)', ('m14', 'bad-json'))
        for call in (eager, lambda ledger: ledger.list()):
            with self.assertRaises(json.JSONDecodeError):
                call(self.ledger)

    def test_legacy_database_and_subclasses(self):
        with self.ledger._connect(write=True) as db:
            db.execute('DROP TABLE document_dependencies')
        self.assertEqual(self.ledger.list(), eager(self.ledger))
        class Child(MemoryLedger):
            pass
        child = Child(self.tmp.name)
        self.assertEqual(child.list(), eager(child))

    def test_correction_acceptance_and_document_packets(self):
        self.ledger.add('candidate', 'claim', 'new', 'source', evidence='candidate')
        self.ledger.accept('candidate', 'accepted', 'review', 'actual fixture review')
        self.ledger.add('derived', 'claim', 'child', 'source', deps=['accepted'], evidence='verified')
        self.ledger.correct('accepted', 'corrected', 'correct', 'user', 'changed')
        with self.ledger._connect(write=True) as db:
            db.execute('INSERT INTO document_dependencies VALUES(?,?)', ('m15', '{"fixture":1}'))
        for status in ('active', 'candidate', 'stale', 'superseded', 'all'):
            self.assertEqual(self.ledger.list(status), eager(self.ledger, status))

    def test_invalid_status_precedes_missing_database(self):
        self.ledger.path.unlink()
        with self.assertRaisesRegex(MemoryError, 'unknown status'):
            self.ledger.list('invalid')

    def test_missing_dependency_table_is_not_hidden_by_empty_selection(self):
        with self.ledger._connect(write=True) as db:
            db.execute("UPDATE entries SET status='candidate'")
            db.execute('DROP TABLE dependencies')
        for call in (eager, lambda ledger: ledger.list()):
            with self.assertRaisesRegex(MemoryError, 'no such table: dependencies'):
                call(self.ledger)

    def test_empty_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = MemoryLedger(directory, create=True)
            self.assertEqual(ledger.list(), [])

    def test_decoder_failure_does_not_hold_read_lock(self):
        with self.ledger._connect(write=True) as db:
            db.execute("UPDATE entries SET scope='bad-json' WHERE id='m14'")
        failure = None
        try:
            self.ledger.list()
        except json.JSONDecodeError as exc:
            failure = exc  # Keep the traceback and its locals alive during write.
        self.assertIsNotNone(failure)
        with self.ledger._connect(write=True) as db:
            db.execute("UPDATE entries SET scope='[]' WHERE id='m14'")
        self.assertEqual(self.ledger.list(), eager(self.ledger))


if __name__ == '__main__':
    unittest.main()
