"""Navigation must not hide updates, dependencies, or oversized metadata."""
from contextlib import closing, redirect_stdout, redirect_stderr
import hashlib
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.project_memory import MemoryError, MemoryLedger, main


class MemoryIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = MemoryLedger(self.root, create=True)

    def seed(self, count=9):
        for i in range(count):
            self.ledger.add(f'm{i:02}', 'claim', ('事实\n😀 ' * 150) + str(i), 'fixture:用户原话',
                            deps=[f'm{i-1:02}'] if i else [], scope=['T1', 'T10'], evidence='verified')
        with self.ledger._connect(write=True) as db:
            db.execute("UPDATE entries SET created_at='2026-10-20'")

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(['--root', str(self.root), *args])
        return code, out.getvalue(), err.getvalue()

    def test_pages_recover_exact_order_metadata_and_bodies(self):
        self.seed()
        full = self.ledger.list()
        rows, cursor, snapshot = [], None, None
        while True:
            page = self.ledger.index(limit=2, after_id=cursor, expected_snapshot=snapshot)
            snapshot = page['snapshot']
            rows += page['entries']
            cursor = page['next_after_id']
            self.assertEqual(page['partial'], cursor is not None)
            if cursor is None:
                break
        self.assertEqual([r['id'] for r in rows], [r['id'] for r in full])
        for expected, row in zip(full, rows):
            self.assertNotIn('content', row)
            for key, value in expected.items():
                if key != 'content':
                    self.assertEqual(row[key], value)
            self.assertEqual(row['content_sha256'], hashlib.sha256(expected['content'].encode()).hexdigest())
            self.assertEqual(row['content_chars'], len(expected['content']))
            recalled = self.ledger.check([row['id']])[0]
            self.assertEqual(recalled, expected)
            raw = json.dumps(recalled, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
            self.assertEqual(row['entry_sha256'], hashlib.sha256(raw.encode()).hexdigest())

    def test_correction_rejects_cursor_and_current_check_rejects_stale(self):
        self.seed()
        page = self.ledger.index(limit=1)
        self.ledger.correct('m00', 'v2', 'corrected', 'user', 'changed')
        with self.assertRaisesRegex(MemoryError, 'changed'):
            self.ledger.index(after_id=page['next_after_id'], expected_snapshot=page['snapshot'])
        with self.assertRaises(MemoryError):
            self.ledger.check(['m01'])
        all_ = self.ledger.index('all', limit=100)
        statuses = {r['id']: r['status'] for r in all_['entries']}
        self.assertEqual(statuses['m00'], 'superseded')
        self.assertEqual(statuses['m01'], 'stale')

    def test_snapshot_binds_hidden_body_metadata_query_and_project(self):
        self.seed(3)
        page = self.ledger.index(limit=1)
        kwargs = dict(after_id=page['next_after_id'], expected_snapshot=page['snapshot'])
        for field, replacement in [('content', 'same ID changed body'), ('source', 'changed-source')]:
            with self.subTest(field=field):
                old = self.ledger.list()[2][field]
                with self.ledger._connect(write=True) as db:
                    db.execute(f'UPDATE entries SET {field}=? WHERE id=?', (replacement, 'm02'))
                with self.assertRaisesRegex(MemoryError, 'changed'):
                    self.ledger.index(**kwargs)
                with self.ledger._connect(write=True) as db:
                    db.execute(f'UPDATE entries SET {field}=? WHERE id=?', (old, 'm02'))
        for options in ({'scope': 'T1'}, {'status': 'all'}):
            with self.assertRaisesRegex(MemoryError, 'changed'):
                self.ledger.index(**kwargs, **options)
        other = self.root / 'other'; other.mkdir()
        second = MemoryLedger(other, create=True)
        with closing(sqlite3.connect(second.path)) as dst, closing(sqlite3.connect(self.ledger.path)) as src:
            src.backup(dst)
        with self.assertRaisesRegex(MemoryError, 'changed'):
            second.index(**kwargs)

    def test_addition_acceptance_and_removal_change_snapshot(self):
        self.seed(2)
        page = self.ledger.index(limit=1)
        self.ledger.add('new', 'claim', 'pending', 'fixture', evidence='candidate')
        # Candidate outside active filter does not alter the selected snapshot.
        self.assertEqual(self.ledger.index()['snapshot'], page['snapshot'])
        self.ledger.accept('new', 'accepted', 'fixture-review', 'fixture only')
        with self.assertRaises(MemoryError):
            self.ledger.index(expected_snapshot=page['snapshot'])
        page = self.ledger.index(limit=1)
        with self.ledger._connect(write=True) as db:
            db.execute("DELETE FROM events WHERE entry_id='accepted'")
            db.execute("DELETE FROM entries WHERE id='accepted'")
        with self.assertRaises(MemoryError):
            self.ledger.index(expected_snapshot=page['snapshot'])

    def test_exact_scope_and_legacy_schema(self):
        self.seed(2)
        self.assertEqual(self.ledger.index(scope='T')['entries'], [])
        with self.ledger._connect(write=True) as db:
            db.execute('DROP TABLE document_dependencies')
        self.assertEqual([r['id'] for r in self.ledger.index(scope='T1')['entries']], ['m00', 'm01'])

    def test_empty_and_end_cursor(self):
        page = self.ledger.index()
        self.assertEqual(page['total_entries'], 0)
        self.assertFalse(page['partial'])
        self.assertIsNone(page['next_after_id'])
        self.seed(1)
        page = self.ledger.index()
        end = self.ledger.index(after_id='m00', expected_snapshot=page['snapshot'])
        self.assertEqual(end['entries'], [])
        self.assertFalse(end['partial'])

    def test_strict_cursor_and_budget_controls(self):
        self.seed(2)
        snapshot = self.ledger.index()['snapshot']
        for options in ({'limit': True}, {'limit': 0}, {'limit': 101}, {'max_chars': False},
                        {'max_chars': 255}, {'max_chars': 200001}, {'expected_snapshot': 'bad'},
                        {'after_id': 'm00'}, {'after_id': 1, 'expected_snapshot': snapshot},
                        {'after_id': 'missing', 'expected_snapshot': snapshot}, {'scope': []}):
            with self.subTest(options=options), self.assertRaises(MemoryError):
                self.ledger.index(**options)
        with self.assertRaisesRegex(MemoryError, 'exceeds budget'):
            self.ledger.index(max_chars=256)

    def test_budget_counts_full_cli_packet_and_never_splits_entry(self):
        self.seed(7)
        def native(*args):
            result = subprocess.run([sys.executable, '-m', 'agent_runtime.project_memory',
                                     '--root', str(self.root), 'index', *args],
                                    capture_output=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, b'')
            return result.stdout.decode('utf-8')  # Preserve native CRLF, never universal-newline conversion.
        text = native('--limit', '1')
        self.assertTrue(text.endswith(os.linesep))
        cap = len(text)
        bounded = native('--max-chars', str(cap))
        self.assertLessEqual(len(bounded), cap)
        page = json.loads(bounded)
        self.assertEqual(len(page['entries']), 1)
        self.assertEqual(page['next_after_id'], 'm00')
        self.assertEqual(self.cli('index', '--max-chars', str(cap-1))[0], 2)
        self.assertEqual(self.ledger.list()[0]['content'], self.ledger.check(['m00'])[0]['content'])

    def test_index_propagates_corrupt_excluded_metadata(self):
        self.seed(2)
        with self.ledger._connect(write=True) as db:
            db.execute("UPDATE entries SET status='candidate',scope='invalid' WHERE id='m01'")
        with self.assertRaises(json.JSONDecodeError):
            self.ledger.index()

    def test_storage_observes_existing_pages_without_business_changes(self):
        self.seed()
        before = {p.name: p.read_bytes() for p in self.ledger.path.parent.iterdir() if p.is_file()}
        state = self.ledger.storage()
        self.assertEqual(state['logical_bytes'], state['page_count'] * state['page_size_bytes'])
        self.assertEqual(state['freelist_bytes'], state['free_pages'] * state['page_size_bytes'])
        self.assertEqual(state['entries_by_status'], {'active': 9})
        self.assertIn('memory_events_entry', state['indexes'])
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.ledger.path.parent.iterdir() if p.is_file()})
        self.assertEqual(self.cli('storage')[0], 0)

    def test_read_commands_do_not_initialize_missing_ledger(self):
        other = self.root / 'missing'; other.mkdir()
        ledger = MemoryLedger(other)
        for method in (ledger.index, ledger.storage):
            with self.assertRaises(MemoryError):
                method()
        self.assertFalse(ledger.path.parent.exists())


if __name__ == '__main__':
    unittest.main()
