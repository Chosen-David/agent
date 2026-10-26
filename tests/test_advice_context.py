import hashlib,tempfile,unittest
from pathlib import Path
from agent_runtime.advice_context import advice_view
TEXT='# Meeting\nCommon rule: evidence remains pending.\n## OLD\nold proposal\n### Detail\nold discussion\n## VERIFY\nReject publishing pending results.\n```md\n## FAKE\n```suffix\n## ALSO_FAKE\n```\n## NEXT\nnew task\n'
class AdviceViewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.path=self.root/'agent_doc/advice/meeting.md';self.path.parent.mkdir(parents=True)
        self.path.write_bytes(TEXT.encode());self.sha=hashlib.sha256(self.path.read_bytes()).hexdigest()
    def view(self,**kwargs):return advice_view(self.root,'agent_doc/advice/meeting.md',['VERIFY'],self.sha,**kwargs)
    def test_exact_section_and_leading_rules(self):
        v=self.view();self.assertEqual(v['leading_text'],'# Meeting\nCommon rule: evidence remains pending.\n')
        section=v['selected_sections'][0];self.assertEqual(section['text'],''.join(TEXT.splitlines(keepends=True)[6:13]))
        self.assertEqual((section['start_line'],section['end_line']),(7,13));self.assertEqual(v['omitted_sections'],2)
    def test_multi_select_document_order(self):
        v=advice_view(self.root,'agent_doc/advice/meeting.md',['NEXT','OLD'],self.sha)
        self.assertEqual([s['heading'] for s in v['selected_sections']],['OLD','NEXT']);self.assertIn('### Detail',v['selected_sections'][0]['text'])
    def test_unknown_duplicate_and_budget(self):
        for headings in ([],['MISSING'],['VERIFY','VERIFY'],['FAKE']):
            with self.assertRaises(ValueError):advice_view(self.root,'agent_doc/advice/meeting.md',headings,self.sha)
        with self.assertRaises(ValueError):self.view(max_chars=1)
    def test_source_version_and_scope(self):
        with self.assertRaises(ValueError):advice_view(self.root,'agent_doc/guide/GUIDE.md',['VERIFY'],self.sha)
        self.path.write_bytes((TEXT+'changed').encode())
        with self.assertRaises(ValueError):self.view()
    def test_bad_layout_fails_closed(self):
        for text in (TEXT+'## VERIFY\nduplicate\n',TEXT+'```\nunclosed',TEXT+'# Another document\n'):
            self.path.write_bytes(text.encode());self.sha=hashlib.sha256(self.path.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):self.view()
    def test_crlf_is_preserved(self):
        self.path.write_bytes(TEXT.replace('\n','\r\n').encode());self.sha=hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.assertIn('\r\n',self.view()['selected_sections'][0]['text'])
    def test_html_comment_headings_never_cut_comment_boundaries(self):
        text=TEXT.replace('## OLD\nold proposal','<!--\n## OLD\nold proposal\n-->')
        self.path.write_bytes(text.encode());self.sha=hashlib.sha256(self.path.read_bytes()).hexdigest()
        with self.assertRaises(ValueError):self.view()

class AdvicePhysicalLineTests(unittest.TestCase):
    setUp = AdviceViewTests.setUp
    separators = ('\v', '\f', '\x1c', '\x1d', '\x1e', '\x85', '\u2028', '\u2029')

    def chunks(self, sep, ending, *, fake_fence=False):
        return ['# Meeting' + ending,
                'Cancellation stays' + sep + '## FAKE_LEADING' + ending,
                'Literal prefix' + sep + ('```md' if fake_fence else 'suffix') + ending,
                '## VERIFY' + ending,
                'Correction stays' + sep + '## FAKE_BODY' + ending,
                '## NEXT' + ending, 'Unselected topic']

    def test_headings_and_view_follow_physical_source_lines(self):
        from agent_runtime.advice_context import advice_headings
        for sep in self.separators:
            for ending, fake_fence in ((e, f) for e in ('\n', '\r\n', '\r') for f in (False, True)):
                with self.subTest(separator=repr(sep), ending=repr(ending), fake_fence=fake_fence):
                    chunks = self.chunks(sep, ending, fake_fence=fake_fence)
                    raw = ''.join(chunks).encode('utf-8')
                    self.path.write_bytes(raw)
                    sha = hashlib.sha256(raw).hexdigest()
                    headings = advice_headings(self.root, 'agent_doc/advice/meeting.md', sha)
                    self.assertEqual(headings['leading_text'], ''.join(chunks[:3]))
                    self.assertEqual(headings['topics'], [
                        {'heading': 'VERIFY', 'start_line': 4, 'end_line': 5},
                        {'heading': 'NEXT', 'start_line': 6, 'end_line': 7}])
                    view = advice_view(self.root, 'agent_doc/advice/meeting.md', ['VERIFY'], sha)
                    self.assertEqual(view['leading_text'], ''.join(chunks[:3]))
                    self.assertEqual(view['selected_sections'], [
                        {'heading': 'VERIFY', 'start_line': 4, 'end_line': 5,
                         'text': ''.join(chunks[3:5])}])
                    self.assertEqual(view['omitted_sections'], 1)
                    self.assertEqual(self.path.read_bytes(), raw)

    def test_actual_cli_headings_and_view_preserve_literal_constraints(self):
        import json, os, subprocess, sys
        for sep in self.separators:
            for discover in (False, True):
                with self.subTest(separator=repr(sep), discover=discover):
                    chunks = self.chunks(sep, '\r\n')
                    raw = ''.join(chunks).encode('utf-8')
                    self.path.write_bytes(raw)
                    command = [sys.executable, '-B', str(Path(__file__).resolve().parents[1] / 'scripts/advice_context.py'),
                               '--root', str(self.root), '--path', 'agent_doc/advice/meeting.md',
                               '--sha256', hashlib.sha256(raw).hexdigest(), '--compact']
                    command += ['--list-headings'] if discover else ['--heading', 'VERIFY']
                    completed = subprocess.run(command, capture_output=True, timeout=15,
                                               env=dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936'))
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    self.assertEqual(completed.stderr, b'')
                    view = json.loads(completed.stdout.decode('utf-8'))
                    self.assertEqual(view['leading_text'], ''.join(chunks[:3]))
                    if discover:
                        self.assertEqual(view['topics'], [
                            {'heading': 'VERIFY', 'start_line': 4, 'end_line': 5},
                            {'heading': 'NEXT', 'start_line': 6, 'end_line': 7}])
                    else:
                        self.assertEqual(view['selected_sections'], [
                            {'heading': 'VERIFY', 'start_line': 4, 'end_line': 5,
                             'text': ''.join(chunks[3:5])}])
                        self.assertEqual(view['omitted_sections'], 1)
                    self.assertEqual(self.path.read_bytes(), raw)
