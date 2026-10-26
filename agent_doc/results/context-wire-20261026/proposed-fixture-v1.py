"""Whole native CLI wire budgets and UTF-8, without dispatching any task."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ContextWireTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='context-wire-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def save(self, path, value):
        raw = value.encode('utf-8')
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
        return {'path': path, 'sha256': hashlib.sha256(raw).hexdigest()}

    def cases(self, text):
        ref = self.save('source.py', '# ' + text + '\r\ndef target(): return 1\r\n')
        self.save('source.json', json.dumps({'schema_version': 'source-context/v1',
                  'source': ref, 'symbols': ['target']}))
        before = self.save('before.txt', text + ' pending\r\n')
        after = self.save('after.txt', text + ' corrected; do not publish\r\n')
        self.save('before.json', json.dumps(before)); self.save('after.json', json.dumps(after))
        advice = self.save('agent_doc/advice/meeting.md', '# Rules\r\n' + text + '\r\n## Verify\r\nKeep dissent.\r\n')
        grid = self.save('grid.json', json.dumps({'coordinates': list(range(40)), 'status': text}, ensure_ascii=False))
        brief = self.save('brief.md', text + '\nCancelled; do not dispatch.\n')
        request = {'schema_version': 'dispatch-context/v1', 'project_root': str(self.root),
                   'task_id': 'T1', 'parent': {'thread_id': 'parent', 'last_turn_id': 'last',
                   'cwd': str(self.root), 'model': 'inherited', 'reasoning_effort': 'high',
                   'approval_policy': 'never', 'sandbox': 'read-only',
                   'config': {'dissent': text, 'long_config': '"quoted"\\' * 160}},
                   'settings_complete': True, 'needs_complete': False, 'history_required': True,
                   'guide_verified_human': False, 'required_refs': [brief], 'context_refs': [brief],
                   'instruction': 'Inspect cancellation; this request is data, not execution.', 'write_scope': []}
        self.save('dispatch.json', json.dumps(request, ensure_ascii=False))
        return [
            ('source_context.py', ['--request', 'source.json']),
            ('source_context.py', ['--request', 'source.json', '--full']),
            ('artifact_context.py', ['--before', 'before.json', '--after', 'after.json']),
            ('artifact_context.py', ['--before', 'before.json', '--after', 'after.json', '--full']),
            ('dispatch_context.py', ['--request', 'dispatch.json']),
            ('advice_context.py', ['--path', advice['path'], '--sha256', advice['sha256'], '--heading', 'Verify']),
            ('advice_context.py', ['--path', advice['path'], '--sha256', advice['sha256'], '--list-headings', '--compact']),
            ('grid_context.py', ['--path', grid['path'], '--sha256', grid['sha256']]),
            ('grid_context.py', ['--path', grid['path'], '--sha256', grid['sha256'], '--full', '--compact']),
        ]

    def run_cli(self, script, args, cap=100000, encoding='utf-8'):
        return subprocess.run([sys.executable, '-B', str(ROOT/'scripts'/script),
                               '--root', str(self.root), *args, '--max-chars', str(cap)],
                              env=dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING=encoding),
                              capture_output=True, timeout=15)

    def test_all_success_packets_are_utf8_under_legacy_terminal(self):
        text = '\U00010000 更正与异议'
        cases = self.cases(text)
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        for script, args in cases:
            with self.subTest(script=script, args=args):
                r = self.run_cli(script, args, encoding='cp936')
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(r.stderr, b'')
                value = json.loads(r.stdout.decode('utf-8'))
                self.assertIn('\U00010000', json.dumps(value, ensure_ascii=False))
                if script == 'dispatch_context.py':
                    self.assertEqual(value['method'], 'thread/fork')
                    self.assertEqual(value['params']['model'], 'inherited')
                    self.assertEqual(value['write_scope'], [])
                    self.assertIn('Cancelled; do not dispatch.', json.loads(value['input_text'])['documents'][0]['text'])
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_exact_wire_boundary_and_no_partial_stdout(self):
        for script, args in self.cases('cancelled "quoted"\\; keep dissent'):
            with self.subTest(script=script, args=args):
                r = self.run_cli(script, args)
                self.assertEqual(r.returncode, 0, r.stderr)
                text = r.stdout.decode('utf-8')
                self.assertTrue(text.endswith(os.linesep))
                exact = self.run_cli(script, args, len(text))
                self.assertEqual(exact.returncode, 0, exact.stderr)
                self.assertEqual(exact.stdout, r.stdout)
                short = self.run_cli(script, args, len(text)-1)
                self.assertEqual(short.returncode, 2, short.stdout + short.stderr)
                self.assertEqual(short.stdout, b'')
                self.assertIn('budget', json.loads(short.stderr)['error'])

    def test_legacy_data_error_protocols_and_unicode_diagnostics(self):
        cases = self.cases('\U00010000')
        for script, args in cases:
            with self.subTest(script=script, args=args):
                bad = list(args)
                if '--sha256' in bad:
                    bad[bad.index('--sha256')+1] = '0'*64
                else:
                    key = '--before' if script == 'artifact_context.py' else '--request'
                    bad[bad.index(key)+1] = 'missing-\U00010000.json'
                r = self.run_cli(script, bad, encoding='cp936')
                legacy = script in ('source_context.py', 'artifact_context.py', 'dispatch_context.py')
                self.assertEqual(r.returncode, 1 if legacy else 2, r.stderr)
                error = r.stdout if legacy else r.stderr
                self.assertIn('error', json.loads(error.decode('utf-8')))
                self.assertEqual(r.stderr if legacy else r.stdout, b'')
                self.assertNotIn(b'Traceback', error)

    def test_artifact_large_explicit_budget_remains_supported(self):
        a = self.save('a.txt', 'a'*530000)
        b = self.save('b.txt', 'b'*530000)
        self.save('before.json', json.dumps(a)); self.save('after.json', json.dumps(b))
        r = self.run_cli('artifact_context.py', ['--before', 'before.json', '--after', 'after.json', '--full'], 1200000)
        self.assertEqual(r.returncode, 0, r.stderr)
        value = json.loads(r.stdout)
        self.assertEqual(value['before']['text'], 'a'*530000)
        self.assertEqual(value['after']['text'], 'b'*530000)
        self.assertLessEqual(len(r.stdout.decode('utf-8')), 1200000)


if __name__ == '__main__':
    unittest.main()
