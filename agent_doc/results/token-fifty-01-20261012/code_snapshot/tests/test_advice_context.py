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
