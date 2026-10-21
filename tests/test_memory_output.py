"""Actual UTF-8 CLI output stays complete and bounded without changing the ledger."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.project_memory import MemoryLedger


class MemoryOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='memory \U00010000 ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = MemoryLedger(self.root, create=True)

    def cli(self, *args, formatting=()):
        return subprocess.run([sys.executable, '-m', 'agent_runtime.project_memory',
                               '--root', str(self.root), *formatting, *args],
                              capture_output=True, timeout=20,
                              env=dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936'))

    def files(self):
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.ledger.path.parent.iterdir() if p.is_file()}

    def seed(self, count=1, content='memory \U00010000\r\n"quoted"', dependent=False):
        for n in range(count):
            self.ledger.add(f'm{n}', 'observation', content, 'fixture:source',
                            deps=['m0'] if dependent and n else [], scope=['T1'], evidence='verified')

    def test_utf8_default_compact_pretty_and_exact_character_limits(self):
        self.seed(2)
        for command in (('list',), ('check', 'm0', 'm1'), ('history', 'm0'), ('impact', 'm0')):
            with self.subTest(command=command):
                before = self.files()
                full = self.cli(*command)
                self.assertEqual(full.returncode, 0, full.stderr)
                self.assertEqual(full.stderr, b'')
                text = full.stdout.decode('utf-8')
                self.assertTrue(text.endswith(os.linesep))
                self.assertEqual(text, json.dumps(json.loads(text), ensure_ascii=False,
                                                 separators=(',', ':')) + os.linesep)
                exact = self.cli(*command, '--max-chars', str(max(256, len(text))))
                self.assertEqual(exact.stdout, full.stdout)
                self.assertEqual(exact.returncode, 0, exact.stderr)
                if len(text) > 256:
                    failed = self.cli(*command, '--max-chars', str(len(text) - 1))
                    self.assertEqual(failed.returncode, 2)
                    self.assertEqual(failed.stdout, b'')
                    self.assertIn('exceeds max_chars', json.loads(failed.stderr)['error'])
                pretty = self.cli(*command, formatting=('--pretty',))
                self.assertEqual(pretty.returncode, 0, pretty.stderr)
                self.assertEqual(json.loads(pretty.stdout), json.loads(full.stdout))
                pretty_chars = len(pretty.stdout.decode('utf-8'))
                if pretty_chars > 256:
                    exact_pretty = self.cli(*command, '--max-chars', str(pretty_chars),
                                            formatting=('--pretty',))
                    self.assertEqual(exact_pretty.stdout, pretty.stdout)
                    short_pretty = self.cli(*command, '--max-chars', str(pretty_chars - 1),
                                            formatting=('--pretty',))
                    self.assertEqual(short_pretty.returncode, 2)
                    self.assertEqual(short_pretty.stdout, b'')
                self.assertEqual(self.cli(*command, formatting=('--compact',)).stdout, full.stdout)
                self.assertEqual(self.files(), before)

    def test_large_responses_refuse_before_stdout_and_explicit_raise_is_lossless(self):
        secret = 'PRIVATE-NOT-FOR-ERROR-' + '\U00010000' * 1500
        self.seed(14, secret, dependent=True)
        with self.ledger._connect(write=True) as db:
            for n in range(14):
                db.execute('INSERT INTO events(entry_id,action,source,reason) VALUES (?,?,?,?)',
                           ('m0', 'fixture', 'fixture:source', secret))
        for command in (('list',), ('check', *[f'm{n}' for n in range(14)]),
                        ('history', 'm0'), ('impact', 'm0')):
            with self.subTest(command=command):
                before = self.files()
                failed = self.cli(*command)
                self.assertEqual(failed.returncode, 2, failed.stderr)
                self.assertEqual(failed.stdout, b'')
                self.assertNotIn(b'PRIVATE-NOT-FOR-ERROR', failed.stderr)
                result = self.cli(*command, '--max-chars', '200000')
                self.assertEqual(result.returncode, 0, result.stderr)
                expected = (self.ledger.list() if command[0] == 'list' else
                            self.ledger.check(command[1:]) if command[0] == 'check' else
                            self.ledger.history('m0') if command[0] == 'history' else
                            self.ledger.impact('m0'))
                self.assertEqual(json.loads(result.stdout), expected)
                self.assertEqual(self.files(), before)
        self.assertEqual(len(json.loads(self.cli('index', '--limit', '1').stdout)['entries']), 1)

    def test_invalid_budget_and_ledger_failures_preserve_storage(self):
        self.seed()
        for cap in ('255', '200001', '-1'):
            before = self.files()
            result = self.cli('list', '--max-chars', cap)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, b'')
            self.assertEqual(self.files(), before)
        self.ledger.correct('m0', 'm-new', 'revised', 'fixture:correction', 'superseded')
        before = self.files()
        stale = self.cli('check', 'm0')
        self.assertEqual(stale.returncode, 2)
        self.assertEqual(stale.stdout, b'')
        self.assertIn('superseded', json.loads(stale.stderr)['error'])
        self.assertEqual(self.files(), before)
        with self.ledger._connect(write=True) as db:
            db.execute('DROP TABLE dependencies')
        before = self.files()
        self.assertEqual(self.cli('list').returncode, 2)
        self.assertEqual(self.files(), before)
        self.ledger.path.write_bytes(b'not a database')
        before = self.files()
        broken = self.cli('list')
        self.assertEqual(broken.returncode, 2)
        self.assertEqual(broken.stdout, b'')
        self.assertEqual(self.files(), before)

    def test_missing_ledger_is_not_initialized_by_read(self):
        missing = self.root / 'missing-project'
        result = subprocess.run([sys.executable, '-m', 'agent_runtime.project_memory',
                                 '--root', str(missing), 'list'], capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b'')
        self.assertFalse(missing.exists())

    def test_large_write_is_successful_and_not_rejected_after_commit(self):
        content = 'w' * 21000
        result = self.cli('add', '--id', 'large', '--kind', 'observation',
                          '--content', content, '--source', 'fixture:write', '--evidence', 'verified')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['content'], content)
        self.assertEqual(self.ledger.check(['large'])[0]['content'], content)


if __name__ == '__main__':
    unittest.main()
