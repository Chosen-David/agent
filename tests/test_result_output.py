"""Registry response budgets must not truncate records or reject successful writes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.result_store import ResultStore

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/result_store.py'


class ResultOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='results \U00010000 ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        raw = b'original artifact'
        (self.root / 'artifact.txt').write_bytes(raw)
        self.artifacts = [{'path': 'artifact.txt', 'sha256': hashlib.sha256(raw).hexdigest()}]
        self.store = ResultStore(self.root)

    def cli(self, *args, formatting=()):
        return subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root),
                               *formatting, *args], capture_output=True, timeout=20,
                              env=dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936'))

    def files(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def test_native_utf8_complete_formatting_and_exact_limits(self):
        self.store.register_history('one', 'needle \U00010000\r\n"quoted"', self.artifacts)
        for command in (('show', 'one'), ('search', 'needle')):
            before = self.files()
            values = []
            for formatting in ((), ('--pretty',), ('--compact',)):
                full = self.cli(*command, formatting=formatting)
                self.assertEqual(full.returncode, 0, full.stderr)
                self.assertEqual(full.stderr, b'')
                text = full.stdout.decode('utf-8')
                exact = self.cli(*command, '--max-chars', str(len(text)), formatting=formatting)
                self.assertEqual(exact.stdout, full.stdout)
                self.assertEqual(exact.returncode, 0, exact.stderr)
                failed = self.cli(*command, '--max-chars', str(len(text) - 1), formatting=formatting)
                self.assertEqual(failed.returncode, 2)
                self.assertEqual(failed.stdout, b'')
                self.assertIn('budget', json.loads(failed.stderr)['error'])
                values.append(json.loads(text))
            self.assertTrue(all(value == values[0] for value in values))
            self.assertEqual(self.files(), before)

    def test_large_search_refuses_without_echo_and_explicit_raise_is_lossless(self):
        summary = 'PRIVATE needle \U00010000 ' * 2000
        self.store.register_history('large', summary, self.artifacts)
        before = self.files()
        for command in (('search', 'needle'), ('show', 'large')):
            denied = self.cli(*command)
            self.assertEqual(denied.returncode, 2)
            self.assertEqual(denied.stdout, b'')
            self.assertNotIn(b'PRIVATE', denied.stderr)
            full = self.cli(*command, '--max-chars', '200000')
            self.assertEqual(full.returncode, 0, full.stderr)
            packet = json.loads(full.stdout)
            actual = packet['record']['summary'] if command[0] == 'show' else packet['results'][0]['summary']
            self.assertEqual(actual, summary)
        self.assertEqual(self.files(), before)

    def test_write_is_not_rejected_after_commit_by_read_display_cap(self):
        summary = 'w' * 21000
        record = self.root / 'input.json'
        record.write_text(json.dumps({'run_id': 'written', 'summary': summary,
                                      'artifacts': self.artifacts}), encoding='utf-8')
        result = self.cli('register-history', '--record', str(record))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.store.show('written')['record']['summary'], summary)


if __name__ == '__main__':
    unittest.main()
