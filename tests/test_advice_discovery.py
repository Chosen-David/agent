import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from agent_runtime.advice_context import advice_headings,advice_view


class AdviceDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.rel='agent_doc/advice/meeting.md';self.file=self.root/self.rel
        self.file.parent.mkdir(parents=True)
        self.write('# Meeting\nGlobal: do not publish pending data.\n## Old\n'+'history\n'*40+
                   '## Verify ###\nCancelled run; fix before review.\n~~~md\n## Fake\n~~~suffix\n## Also fake\n~~~\n## Next\nnext\n')
    def write(self,text):
        self.file.write_bytes(text.encode());self.sha=hashlib.sha256(self.file.read_bytes()).hexdigest()
    def discover(self,**kw):return advice_headings(self.root,self.rel,self.sha,**kw)
    def test_all_topics_and_exact_line_ranges(self):
        v=self.discover();self.assertEqual(v['leading_text'],'# Meeting\nGlobal: do not publish pending data.\n')
        self.assertEqual(v['topics'],[{'heading':'Old','start_line':3,'end_line':43},
                        {'heading':'Verify','start_line':44,'end_line':50},
                        {'heading':'Next','start_line':51,'end_line':52}])
        self.assertNotIn('Cancelled',json.dumps(v));self.assertIn('no assessment, closure or authority',v['scope'])
    def test_same_sha_selection_preserves_all_selected_bytes(self):
        v=self.discover();raw=self.file.read_bytes().decode().splitlines(keepends=True)
        for topic in v['topics']:
            selected=advice_view(self.root,self.rel,[topic['heading']],v['source']['sha256'])
            self.assertEqual(selected['selected_sections'][0]['text'],''.join(raw[topic['start_line']-1:topic['end_line']]))
            self.assertEqual(selected['leading_text'],v['leading_text'])
    def test_stale_discovery_never_selects_new_bytes(self):
        v=self.discover();self.write(self.file.read_text()+'new\n')
        with self.assertRaises(ValueError):advice_view(self.root,self.rel,['Verify'],v['source']['sha256'])
    def test_ambiguous_and_bad_layouts(self):
        for suffix in ('## Verify\nduplicate\n','```\nunclosed','<!-- comment -->\n','# New document\n'):
            self.write('# M\n## Verify\nbody\n'+suffix)
            with self.assertRaises(ValueError):self.discover()
    def test_empty_and_no_topics(self):
        for text in ('','# Text\nbody\n','```md\n## False\n```\n'):
            self.write(text)
            with self.assertRaises(ValueError):self.discover()
    def test_budget_is_fail_closed(self):
        for size in (1,0,True,1000001):
            with self.assertRaises(ValueError):self.discover(max_chars=size)
    def test_crlf_unicode_literal_titles(self):
        self.write('# 会议\r\n约束\r\n## 旧记录\r\n历史\r\n## 核验\r\n取消\r\n')
        v=self.discover();self.assertEqual(v['leading_text'],'# 会议\r\n约束\r\n')
        self.assertEqual([t['heading'] for t in v['topics']],['旧记录','核验'])
    def test_invalid_utf8_and_wrong_sha(self):
        with self.assertRaises(ValueError):advice_headings(self.root,self.rel,'0'*64)
        self.file.write_bytes(b'\xff');self.sha=hashlib.sha256(b'\xff').hexdigest()
        with self.assertRaises(UnicodeDecodeError):self.discover()
    def test_path_boundary(self):
        for path in ('agent_doc/guide/GUIDE.md','agent_doc/advice/../guide/GUIDE.md',str(self.file)):
            with self.assertRaises(ValueError):advice_headings(self.root,path,self.sha)
    def test_symlink_boundary(self):
        link=self.root/'agent_doc/advice/link.md'
        try:link.symlink_to(self.file)
        except OSError:self.skipTest('host cannot create symlinks')
        with self.assertRaises(ValueError):advice_headings(self.root,'agent_doc/advice/link.md',self.sha)
    def test_cli_discovery_and_legacy_selection(self):
        script=Path(__file__).resolve().parents[1]/'scripts/advice_context.py'
        args=[sys.executable,str(script),'--root',str(self.root),'--path',self.rel,'--sha256',self.sha,'--compact']
        d=subprocess.run([*args,'--list-headings'],capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(d.stdout),self.discover())
        v=subprocess.run([*args,'--heading','Verify'],capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(v.stdout),advice_view(self.root,self.rel,['Verify'],self.sha))
        invalid=subprocess.run([*args,'--list-headings','--heading','Verify'],capture_output=True)
        self.assertEqual(invalid.returncode,2)
    def test_max_topic_bound(self):
        self.write('# M\n'+''.join(f'## T{i}\nbody\n' for i in range(129)))
        with self.assertRaises(ValueError):self.discover()
    def test_selection_title_limit_is_supported(self):
        title='A'*256;self.write('# M\n## '+title+'\nbody\n')
        v=self.discover();self.assertEqual(v['topics'][0]['heading'],title)
        self.assertIn('body',advice_view(self.root,self.rel,[title],self.sha)['selected_sections'][0]['text'])
    def test_overlong_title_refuses_incomplete_discovery(self):
        self.write('# M\n## '+('A'*257)+'\nbody\n## VALID\ntext\n')
        with self.assertRaises(ValueError):self.discover()
        self.assertIn('text',advice_view(self.root,self.rel,['VALID'],self.sha)['selected_sections'][0]['text'])
