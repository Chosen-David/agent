import hashlib,json,tempfile,unittest,subprocess,sys
from pathlib import Path
from copy import deepcopy
from agent_runtime.text_dictionary import text_view,restore_text_view,_lines
from agent_runtime.reference_context import _wire

class TextDictionaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()
        self.text='pending; metric_unit=tokens; publication blocked\r\n'+''.join(f'Issue-{i}: dissent retained\r\n'+('exact evidence required '*20)+'\r\n' for i in range(16))+'EOF cancelled'
        self.sha=self.save(self.text)
    def save(self,text):
        raw=text.encode();(self.root/'meeting.md').write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()
    def view(self,**kw):return text_view(self.root,'meeting.md',self.sha,**kw)
    def restore(self,v,**kw):return restore_text_view(self.root,_wire(v),'meeting.md',self.sha,**kw)
    def test_nonconsecutive_exact_sharing_and_full(self):
        v=self.view();self.assertEqual(v['encoding'],'dictionary')
        self.assertLess(len(_wire(v)),len(_wire(self.view(full=True))))
        self.assertEqual(self.restore(v),self.text);self.assertEqual(self.restore(self.view(full=True)),self.text)
        self.assertEqual((self.root/'meeting.md').read_bytes(),self.text.encode())
        self.assertEqual(v['order'].count(2),16)
    def test_physical_lf_only_cr_unicode_separators_blank_eof(self):
        for text in ('','one','\n','\r','a\r\nb\n','x\u2028y\x85z\r'+('\n'*3),'\ufeffbom\n','line\n'*10+'tail'):
            self.sha=self.save(text);self.assertEqual(self.restore(self.view()),text)
        self.assertEqual(_lines('a\rb\u2028c\x85d\n'),['a\rb\u2028c\x85d\n'])
    def test_nonbeneficial_full_fallback(self):
        self.sha=self.save('a\nb\nc');self.assertEqual(self.view()['encoding'],'full')
    def test_indexes_types_ranges_and_count(self):
        for index in (True,-1,999,0.5,'0'):
            v=deepcopy(self.view());v['order'][0]=index
            with self.assertRaises(ValueError):self.restore(v)
        v=self.view();v['order'].append(0)
        with self.assertRaisesRegex(ValueError,'counts'):self.restore(v)
    def test_dictionary_duplicate_unused_type_and_partial_line(self):
        for extra in (self.view()['dictionary'][0],'unused\n',None,'two\nlines\n',''):
            v=self.view();v['dictionary'].append(extra)
            with self.assertRaises(ValueError):self.restore(v)
    def test_order_content_or_binding_tampering(self):
        for key,value in [('scope','closed'),('project_root','other'),('source',{'path':'wrong','sha256':self.sha}),('schema_version','v0'),('encoding','guess')]:
            v=self.view();v[key]=value
            with self.assertRaises(ValueError):self.restore(v)
        v=self.view();v['order'][1],v['order'][3]=v['order'][3],v['order'][1]
        with self.assertRaises(ValueError):self.restore(v)
        v=self.view();v['extra']='hidden'
        with self.assertRaises(ValueError):self.restore(v)
    def test_stale_source_and_invalid_sha(self):
        v=self.view();self.save('changed')
        with self.assertRaisesRegex(ValueError,'changed'):self.restore(v)
        for sha in (self.sha.upper(),None,'0'*63):
            with self.assertRaises(ValueError):text_view(self.root,'meeting.md',sha)
    def test_strict_json_duplicate_keys_nonfinite_unicode(self):
        wire=_wire(self.view())
        for bad in (wire.replace('"encoding":','"encoding":"full","encoding":',1),wire.replace('"order":[','"order":[NaN,',1),wire.replace('"order":[','"order":[1e999,',1),wire.replace('"dictionary":[','"dictionary":["\\ud800",',1)):
            with self.assertRaises(ValueError):restore_text_view(self.root,bad,'meeting.md',self.sha)
    def test_frame_and_source_display_bounds(self):
        for cap in (True,0,1000001,20):
            with self.assertRaises(ValueError):self.view(max_chars=cap)
        with self.assertRaises(ValueError):restore_text_view(self.root,{},'meeting.md',self.sha)
        with self.assertRaises(ValueError):restore_text_view(self.root,b'\xff','meeting.md',self.sha)
        with self.assertRaises(ValueError):restore_text_view(self.root,' '*1000001,'meeting.md',self.sha)
        with self.assertRaises(ValueError):self.view(full='yes')
    def test_expanded_character_guard_before_join(self):
        self.sha=self.save('x\n'*50000);v=self.view();v['dictionary']=['a'*30+'\n']
        with self.assertRaisesRegex(ValueError,'before allocation'):self.restore(v)
    def test_expanded_byte_guard_before_join(self):
        self.sha=self.save('x\n'*50000);v=self.view();v['dictionary']=['界'*18+'\n']
        with self.assertRaisesRegex(ValueError,'before allocation'):self.restore(v)
    def test_source_byte_line_and_character_limits(self):
        (self.root/'meeting.md').write_bytes(b'x'*(2*1024*1024+1))
        sha=hashlib.sha256((self.root/'meeting.md').read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError,'source exceeds'):text_view(self.root,'meeting.md',sha)
        self.sha=self.save('\n'*50001)
        with self.assertRaisesRegex(ValueError,'line count'):self.view()
        self.sha=self.save('a'*1000001)
        with self.assertRaisesRegex(ValueError,'expanded'):self.view()
    def test_invalid_utf8_and_paths(self):
        (self.root/'meeting.md').write_bytes(b'\xff');sha=hashlib.sha256(b'\xff').hexdigest()
        with self.assertRaises(UnicodeError):text_view(self.root,'meeting.md',sha)
        for path in ('../meeting.md','./meeting.md','/meeting.md','x\\meeting.md','C:meeting.md'):
            with self.assertRaises(ValueError):text_view(self.root,path,sha)
    def test_unterminated_entry_only_at_eof(self):
        v=self.view();v['order'][0]=len(v['dictionary'])-1
        with self.assertRaisesRegex(ValueError,'EOF'):self.restore(v)
    def test_symlink_refused(self):
        target=self.root/'link.md'
        try:target.symlink_to(self.root/'meeting.md')
        except OSError:self.skipTest('host symlink privilege unavailable')
        with self.assertRaises(ValueError):text_view(self.root,'link.md',self.sha)
    def test_cli_render_and_host_bound_restore(self):
        script=Path(__file__).resolve().parents[1]/'scripts/text_dictionary.py'
        args=[sys.executable,str(script),'--root',str(self.root),'--path','meeting.md','--sha256',self.sha,'--compact']
        p=subprocess.run(args,capture_output=True,text=True,encoding='utf8');self.assertEqual(p.returncode,0,p.stdout)
        v=json.loads(p.stdout);self.assertEqual(self.restore(v),self.text)
        (self.root/'packet.json').write_bytes(p.stdout.encode())
        p=subprocess.run(args+['--restore','packet.json'],capture_output=True,text=True,encoding='utf8')
        self.assertEqual(p.returncode,0,p.stdout);self.assertEqual(json.loads(p.stdout)['text'],self.text)
        p=subprocess.run(args+['--restore','packet.json','--full'],capture_output=True,text=True,encoding='utf8');self.assertEqual(p.returncode,1)

if __name__=='__main__':unittest.main()
