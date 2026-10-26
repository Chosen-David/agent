"""Whole native CLI wire budgets and UTF-8, without dispatching any task."""
import hashlib
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

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
        self.expected = {'text': text, 'source': ref, 'before': before, 'after': after,
                         'advice': advice, 'grid': grid, 'request': copy.deepcopy(request)}
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

    def snapshot(self):
        return {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def assert_packet(self, script, args, value):
        e = self.expected
        if script != 'dispatch_context.py':
            self.assertEqual(value['project_root'], str(self.root))
        if script == 'source_context.py':
            text = (self.root/'source.py').read_bytes().decode('utf-8')
            self.assertEqual(value['source'], e['source'])
            self.assertEqual(value['requested_symbols'], ['target'])
            self.assertEqual(value['chunks'], [{'start_line': 1, 'end_line': 2, 'text': text}])
        elif script == 'artifact_context.py':
            from agent_runtime.artifact_context import restore_comparison
            expected = tuple((self.root/ref['path']).read_bytes().decode('utf-8')
                             for ref in (e['before'], e['after']))
            self.assertEqual(restore_comparison(self.root, value, e['before'], e['after']), expected)
        elif script == 'advice_context.py':
            self.assertEqual(value['source'], e['advice'])
            self.assertEqual(value['leading_text'], '# Rules\r\n' + e['text'] + '\r\n')
            if '--list-headings' in args:
                self.assertEqual(value['topics'], [{'heading': 'Verify', 'start_line': 3, 'end_line': 4}])
                self.assertNotIn('selected_sections', value)
            else:
                self.assertEqual(value['selected_sections'], [{'heading': 'Verify', 'start_line': 3,
                                 'end_line': 4, 'text': '## Verify\r\nKeep dissent.\r\n'}])
                self.assertEqual(value['omitted_sections'], 0)
        elif script == 'grid_context.py':
            from agent_runtime.grid_context import restore_grid_view
            restored = restore_grid_view(self.root, json.dumps(value, ensure_ascii=False),
                                         e['grid']['path'], e['grid']['sha256'])
            self.assertEqual(restored, {'coordinates': list(range(40)), 'status': e['text']})
        elif script == 'dispatch_context.py':
            request = e['request']; parent = request['parent']
            self.assertEqual(value['method'], 'thread/fork')
            self.assertEqual(value['params'], {'cwd': str(self.root), 'model': parent['model'],
                             'approvalPolicy': parent['approval_policy'], 'sandbox': parent['sandbox'],
                             'ephemeral': False, 'config': dict(parent['config'], model_reasoning_effort='high'),
                             'threadId': 'parent', 'lastTurnId': 'last', 'excludeTurns': True})
            self.assertEqual(value['write_scope'], [])
            self.assertEqual(value['source_dependencies'], request['context_refs'])
            packet = json.loads(value['input_text'])
            self.assertEqual(packet, {'schema_version': 'subtask-context/v1', 'project_root': str(self.root),
                             'task_id': 'T1', 'instruction': request['instruction'], 'guide_verified_human': False,
                             'write_scope': [], 'documents': [{**ref, 'text':
                             (self.root/ref['path']).read_bytes().decode('utf-8')} for ref in request['context_refs']]})

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
                self.assert_packet(script, args, value)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_exact_wire_boundary_and_no_partial_stdout(self):
        for script, args in self.cases('cancelled "quoted"\\; keep dissent'):
            with self.subTest(script=script, args=args):
                before = self.snapshot()
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
                self.assertEqual(before, self.snapshot())

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
                before = self.snapshot()
                r = self.run_cli(script, bad, encoding='cp936')
                legacy = script in ('source_context.py', 'artifact_context.py', 'dispatch_context.py')
                self.assertEqual(r.returncode, 1 if legacy else 2, r.stderr)
                error = r.stdout if legacy else r.stderr
                self.assertIn('error', json.loads(error.decode('utf-8')))
                self.assertEqual(r.stderr if legacy else r.stdout, b'')
                self.assertNotIn(b'Traceback', error)
                self.assertEqual(before, self.snapshot())

    def test_dispatch_main_never_launches_a_process(self):
        from scripts.dispatch_context import main
        self.cases('cancelled; preserve dissent')
        before = self.snapshot()
        out = io.StringIO()
        with contextlib.redirect_stdout(out), patch('subprocess.Popen', side_effect=AssertionError('unexpected launch')):
            self.assertEqual(main(['--root', str(self.root), '--request', 'dispatch.json']), 0)
        self.assert_packet('dispatch_context.py', [], json.loads(out.getvalue()))
        self.assertEqual(before, self.snapshot())

    def test_artifact_counter_filters_native_newline_before_selection(self):
        from scripts.artifact_context import main
        from agent_runtime.artifact_context import compare_artifacts, restore_comparison
        old = 'unchanged '*150 + '\nold\n' + 'tail '*150
        new = old.replace('\nold\n', '\nnew\n')
        a = self.save('before.txt', old); b = self.save('after.txt', new)
        self.save('before.json', json.dumps(a)); self.save('after.json', json.dumps(b))
        full = compare_artifacts(self.root, a, b, full=True)
        cap = len(json.dumps(full, ensure_ascii=False, separators=(',', ':')))
        def counter(wire):
            return 0 if json.loads(wire)['after']['representation'] == 'full' else 1
        before = self.snapshot()
        for budget in (cap, 1):
            out = io.StringIO(); err = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), patch(
                    'agent_runtime.handoff_basis.make_token_counter', return_value=counter):
                rc = main(['--root', str(self.root), '--before', 'before.json', '--after', 'after.json',
                           '--encoding', 'controlled-counter', '--max-chars', str(budget)])
            if budget == cap:
                self.assertEqual(rc, 0, err.getvalue())
                self.assertLessEqual(len(out.getvalue()) + out.getvalue().count('\n')*(len(os.linesep)-1), cap)
                value = json.loads(out.getvalue())
                self.assertEqual(value['after']['representation'], 'splice')
                self.assertEqual(restore_comparison(self.root, value, a, b), (old, new))
            else:
                self.assertEqual(rc, 2)
                self.assertEqual(out.getvalue(), '')
                self.assertIn('budget', json.loads(err.getvalue())['error'])
        self.assertEqual(before, self.snapshot())

    def test_shared_output_ceiling_defaults_and_explicit_limits(self):
        from agent_runtime.context_serialization import render_cli_context
        with self.assertRaises(ValueError):
            render_cli_context({}, max_chars=1000001)
        for ceiling in (True, False, 0, -1, '1000000', None, 16*1024*1024+1):
            with self.subTest(ceiling=ceiling), self.assertRaises(ValueError):
                render_cli_context({}, max_chars_limit=ceiling)
        self.assertEqual(json.loads(render_cli_context({}, max_chars=1000001,
                                   max_chars_limit=16*1024*1024)), {})

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
