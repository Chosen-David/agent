"""Memory CLI file decoding errors stay structured; internal errors stay visible."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.project_memory import MemoryLedger, main
from agent_runtime.project_docs import migrate, snapshot_project_docs


class MemoryCliInputTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = MemoryLedger(self.root, create=True)
        self.ledger.add('old', 'claim', 'original', 'test', evidence='verified')
        self.file = self.root / 'snapshot.json'

    def rows(self):
        with sqlite3.connect(self.ledger.path) as db:
            return {t: db.execute('SELECT * FROM ' + t + ' ORDER BY rowid').fetchall()
                    for t in ('entries', 'dependencies', 'document_dependencies', 'events', 'sqlite_sequence')}

    def args(self, command):
        if command == 'add':
            rest = ['add', '--id', 'new', '--kind', 'claim', '--content', 'new', '--source', 'test']
        else:
            rest = ['correct', '--id', 'old', '--new-id', 'new', '--content', 'new', '--source', 'test', '--reason', 'correct']
        return ['--root', str(self.root), *rest, '--document-refs', str(self.file)]

    def test_bad_external_snapshot_is_structured_and_preserves_business_state(self):
        for command in ('add', 'correct'):
            for payload in (b'{broken', b'\xff', b'', b'{"a":}'):
                with self.subTest(command=command, payload=payload):
                    self.file.write_bytes(payload)
                    before = self.rows()
                    out, err = io.StringIO(), io.StringIO()
                    with redirect_stdout(out), redirect_stderr(err):
                        code = main(self.args(command))
                    self.assertEqual(code, 2)
                    self.assertEqual(out.getvalue(), '')
                    self.assertIsInstance(json.loads(err.getvalue())['error'], str)
                    self.assertNotIn('Traceback', err.getvalue())
                    self.assertEqual(self.rows(), before)

    def test_valid_bound_snapshot_add_and_correct(self):
        (self.root / 'TASK.md').write_text('## 2026-10-16\n- [ ] [T1] Audit memory\n')
        migrate(self.root, '2026-10-16')
        self.file.write_text(json.dumps(snapshot_project_docs(self.root)))
        for command in ('add', 'correct'):
            if command == 'correct':
                args = self.args(command)
                args[args.index('--new-id') + 1] = 'revision'
            else:
                args = self.args(command)
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = main(args)
            self.assertEqual(code, 0)
            self.assertEqual(err.getvalue(), '')
            self.assertTrue(json.loads(out.getvalue()))
        self.assertEqual(self.ledger.history('old')['entry']['status'], 'superseded')

    def test_internal_json_decode_error_not_relabelled_as_input_error(self):
        self.file.write_text('{}')
        error = json.JSONDecodeError('internal corrupted ledger', '', 0)
        with patch.object(MemoryLedger, 'add', side_effect=error):
            with self.assertRaises(json.JSONDecodeError):
                main(self.args('add'))

    def test_missing_snapshot_file_stays_structured(self):
        before = self.rows()
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(self.args('correct'))
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), '')
        self.assertIn('error', json.loads(err.getvalue()))
        self.assertEqual(self.rows(), before)

    def test_first_add_invalid_file_preserves_initialization_order(self):
        fresh = self.root / 'fresh'
        fresh.mkdir()
        self.file.write_bytes(b'{broken')
        args = self.args('add')
        args[1] = str(fresh)
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(args)
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), '')
        self.assertIn('error', json.loads(err.getvalue()))
        ledger = MemoryLedger(fresh)
        self.assertEqual(ledger.list('all'), [])
        with sqlite3.connect(ledger.path) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM events').fetchone()[0], 0)
            self.assertTrue(db.execute("SELECT 1 FROM sqlite_master WHERE name='memory_events_entry'").fetchone())
