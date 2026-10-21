"""Real native CLI character budgets and Unicode; source values remain complete."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ContextCliOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='context \U00010000 ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def source(self, path, text):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(text.encode('utf-8'))
        return hashlib.sha256(file.read_bytes()).hexdigest()

    def cli(self, script, args, cap=1000000, compact=False):
        return subprocess.run([sys.executable, str(ROOT / 'scripts' / script),
                               '--root', str(self.root), *args, '--max-chars', str(cap),
                               *(['--compact'] if compact else [])], capture_output=True,
                              env=dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936'), timeout=20)

    def boundary(self, script, args):
        values = []
        for compact in (False, True):
            full = self.cli(script, args, compact=compact)
            self.assertEqual(full.returncode, 0, full.stderr)
            self.assertEqual(full.stderr, b'')
            text = full.stdout.decode('utf-8')
            self.assertTrue(text.endswith(os.linesep))
            cap = len(text)
            exact = self.cli(script, args, cap, compact)
            self.assertEqual(exact.returncode, 0, exact.stderr)
            self.assertEqual(exact.stdout, full.stdout)
            short = self.cli(script, args, cap - 1, compact)
            self.assertEqual(short.returncode, 2)
            self.assertEqual(short.stdout, b'')
            self.assertIn('budget', json.loads(short.stderr)['error'])
            values.append(json.loads(text))
        self.assertEqual(*values)
        return values[0]

    def test_task_complete_packet_and_native_newline(self):
        text = '# Rules \U00010000\r\n## 2026-10-21\r\n- [ ] [T1] Fix "quoted" output ([detail](task_details/T1.md))\r\n'
        sha = self.source('agent_doc/task/TASK.md', text)
        packet = self.boundary('task_context.py', ['--task-id', 'T1', '--sha256', sha])
        self.assertEqual(packet['text'], text)
        before = (self.root / 'agent_doc/task/TASK.md').read_bytes()
        failed = self.cli('task_context.py', ['--task-id', 'MISSING', '--sha256', sha])
        self.assertEqual(failed.returncode, 2)
        self.assertEqual(failed.stdout, b'')
        self.assertEqual((self.root / 'agent_doc/task/TASK.md').read_bytes(), before)

    def test_records_keep_physical_lines_and_global_dependencies(self):
        text = '{"rule":"global \U00010000"}\r\n{"history":0}\n{"current":"cancelled\\nnow"}'
        sha = self.source('records.ndjson', text)
        packet = self.boundary('record_context.py', ['--path', 'records.ndjson', '--sha256', sha,
                                                    '--line', '3', '--global-line', '1'])
        self.assertEqual([r['line'] for r in packet['records']], [1, 3])
        self.assertEqual(packet['records'][0]['text'], text.splitlines(keepends=True)[0])
        self.assertEqual(packet['omitted_records'], 1)

    def test_log_encodings_restore_exact_lines_with_complete_packet_limits(self):
        from agent_runtime.log_context import restore_log_lines
        text = 'header \U00010000\r\nERROR "quoted"\r\ntail\r\n'
        sha = self.source('run.log', text)
        args = ['--path', 'run.log', '--sha256', sha, '--head', '3', '--tail', '0']
        for encoding in ('lines', 'chunks', 'runs'):
            with self.subTest(encoding=encoding):
                packet = self.boundary('log_context.py', [*args, '--encoding', encoding])
                self.assertEqual(''.join(row['text'] for row in restore_log_lines(packet)), text)
        bad = self.cli('log_context.py', ['--path', 'run.log', '--sha256', '0' * 64])
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, b'')
        self.assertNotIn(b'Traceback', bad.stderr)

    def test_reference_full_and_prefix_transport_respect_display_budget(self):
        from agent_runtime.reference_context import restore_reference_view
        prefix = 'agent_doc/results/long-independent-evidence-run/'
        data = {'references': [{'path': prefix + f'part-{n}.json', 'sha256': str(n) * 64}
                               for n in range(8)],
                'current': {'status': 'cancelled', 'text': '\U00010000\u2028"quoted"'}}
        sha = self.source('refs.json', json.dumps(data, ensure_ascii=False))
        for extra in ([], ['--full']):
            packet = self.boundary('reference_context.py', ['--path', 'refs.json', '--sha256', sha, *extra])
            self.assertEqual(restore_reference_view(self.root, json.dumps(packet, ensure_ascii=False),
                                                   'refs.json', sha), data)


if __name__ == '__main__':
    unittest.main()
