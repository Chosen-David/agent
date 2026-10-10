import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.source_context import source_context, physical_lines


class SourceContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.addCleanup(self.temp.cleanup)

    def request(self, text, symbols=None):
        raw = text.encode('utf-8')
        (self.root / 'code.py').write_bytes(raw)
        return {'schema_version': 'source-context/v1',
                'source': {'path': 'code.py', 'sha256': hashlib.sha256(raw).hexdigest()},
                'symbols': symbols or ['target']}

    def test_exact_unicode_crlf_closure_comments_and_nondefs(self):
        text = ('# 中文 header\r\nimport math\r\nLIMIT = 3\r\n'
                'def helper(x):\r\n    return x + LIMIT\r\n'
                '# 中间注释\r\ndef target(x):\r\n    return helper(x)\r\n'
                'def irrelevant():\r\n' + '    # unused filler\r\n' * 24 + '    return 0\r\n'
                '# 尾注释\r\n')
        request = self.request(text)
        view = source_context(self.root, request)
        self.assertEqual(view['mode'], 'focused')
        self.assertEqual(view['omitted_symbols'], ['irrelevant'])
        lines = text.splitlines(keepends=True)
        retained = []
        for chunk in view['chunks']:
            expected = ''.join(lines[chunk['start_line'] - 1:chunk['end_line']])
            self.assertEqual(chunk['text'], expected)
            retained.append(expected)
        joined = ''.join(retained)
        self.assertIn('return helper(x)\r\n', joined)
        self.assertIn('return x + LIMIT\r\n', joined)
        self.assertIn('# 尾注释\r\n', joined)
        self.assertNotIn('def irrelevant', joined)
        full = source_context(self.root, request, full=True)
        self.assertEqual(full['chunks'][0]['text'], text)

    def test_declaration_effects_classes_annotations_and_async_dependencies(self):
        text = ('def registry(fn): return fn\n'
                '@registry\ndef decorated(): return target()\n'
                'def default_effect(x=make()): return 1\n'
                'def annotated(x: Target): return 2\n'
                'class Target:\n    VALUE = 3\n'
                'async def helper(): return Target.VALUE\n'
                'def target(): return helper()\n'
                'def unused():\n' + '    # unused\n' * 30 + '    return 4\n')
        view = source_context(self.root, self.request(text))
        self.assertEqual(view['omitted_symbols'], ['unused'])
        joined = ''.join(x['text'] for x in view['chunks'])
        for declaration in ('@registry', 'def registry', 'make()', 'x: Target',
                            'class Target', 'async def helper'):
            self.assertIn(declaration, joined)

    def test_dynamic_namespace_alias_attribute_and_star_fallback(self):
        for code in ('def target(): return globals()["missing"]()\n',
                     'import builtins as b\ndef target(): return b.eval("missing()")\n',
                     'from builtins import eval as run\ndef target(): return run("missing()")\n',
                     'from other import *\ndef target(): return 1\n',
                     'def target(): return target.__globals__["unused"]()\n',
                     'import sys\ndef target(): return sys.modules[__name__].__dict__["unused"]()\n',
                     'def target(): return __builtins__["eval"]("unused()")\n'):
            text = code + 'def unused():\n' + '    # unused\n' * 30 + '    return 4\n'
            with self.subTest(code=code):
                view = source_context(self.root, self.request(text))
                self.assertEqual(view['mode'], 'full')
                self.assertEqual(view['chunks'][0]['text'], text)

    def test_python_physical_lines_do_not_split_unicode_string_separators(self):
        for newline in ('\n', '\r\n', '\r'):
            text = newline.join(['HEADER = "a\u2028b\u2029c\x85d\x0be"',
                                 'def helper(): return HEADER',
                                 'def target(): return helper()',
                                 'def unused():', *['    # unused'] * 25, '    return 0',
                                 '# trailing\u2028comment', ''])
            view = source_context(self.root, self.request(text))
            self.assertEqual(view['mode'], 'focused')
            expected = newline.join(['HEADER = "a\u2028b\u2029c\x85d\x0be"',
                                     'def helper(): return HEADER',
                                     'def target(): return helper()',
                                     '# trailing\u2028comment', ''])
            self.assertEqual(''.join(x['text'] for x in view['chunks']), expected)
            lines = physical_lines(text)
            for chunk in view['chunks']:
                self.assertEqual(chunk['text'], ''.join(lines[chunk['start_line']-1:chunk['end_line']]))

    def test_ambiguous_syntax_no_smaller_view_and_missing_target(self):
        for text in ('def target(): return 1\n', 'def target(): return 1\ndef target(): return 2\n',
                     'def target( syntax error\n'):
            view = source_context(self.root, self.request(text))
            self.assertEqual(view['mode'], 'full')
            self.assertEqual(view['chunks'][0]['text'], text)
        with self.assertRaisesRegex(ValueError, 'absent'):
            source_context(self.root, self.request('def other(): return 1\n'))

    def test_stale_cross_root_contract_flags_and_budget_reject(self):
        req = self.request('def target(): return 1\n')
        for update in ({'symbols': []}, {'symbols': ['target', 'target']},
                       {'symbols': ['target.method']}, {'extra': True}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                source_context(self.root, dict(req, **update))
        with self.assertRaises(ValueError):
            source_context(self.root, req, full=1)
        with self.assertRaises(ValueError):
            source_context(self.root, req, max_chars=10)
        bad = dict(req, source=dict(req['source'], path='../code.py'))
        with self.assertRaises(ValueError):
            source_context(self.root, bad)
        (self.root / 'code.py').write_text('def target(): return 2\n')
        with self.assertRaises(ValueError):
            source_context(self.root, req)

    def test_actual_cli_readonly_and_same_whole_source(self):
        text = 'def target(): return 1\ndef unused():\n' + '    # unused\n' * 25 + '    return 0\n'
        req = self.request(text)
        path = self.root / 'request.json'
        path.write_text(json.dumps(req), encoding='utf-8')
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        script = Path(__file__).resolve().parents[1] / 'scripts/source_context.py'
        p = subprocess.run([sys.executable, str(script), '--root', str(self.root),
                            '--request', 'request.json'], capture_output=True, text=True,
                           encoding='utf-8', timeout=15)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout), source_context(self.root, req))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})


if __name__ == '__main__':
    unittest.main()
