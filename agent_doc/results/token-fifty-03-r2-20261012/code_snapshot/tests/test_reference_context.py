import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from agent_runtime.reference_context import reference_view, restore_reference_view


class ReferenceContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve();self.path='agent_doc/advice/refs.json'
        self.file=self.root/self.path;self.file.parent.mkdir(parents=True)
        self.prefix='agent_doc/results/long-independent-reproduction-run-evidence/'
        self.data={'global_rule':'independent verification','unit':'tokens','status':'pending',
                   'references':[{'path':self.prefix+f'part-{n}.json','sha256':hashlib.sha256(str(n).encode()).hexdigest()} for n in range(3)],
                   'unknown_metadata':{'failure':['cancelled',None,False,1.25],'unicode':'中文\u2028正文'}}
        self.write(self.data)

    def write(self,value):
        self.raw(json.dumps(value,ensure_ascii=False).encode())

    def raw(self,data):
        self.file.write_bytes(data);self.sha=hashlib.sha256(data).hexdigest()

    def view(self,**kwargs):
        return reference_view(self.root,self.path,self.sha,**kwargs)

    def restore(self,value,**kwargs):
        return restore_reference_view(self.root,json.dumps(value,ensure_ascii=False),self.path,self.sha,**kwargs)

    def test_exact_values_order_and_original_bytes(self):
        before=self.file.read_bytes();v=self.view()
        self.assertEqual(v['encoding'],'directory-prefix')
        self.assertEqual(v['path_prefix'],self.prefix)
        self.assertEqual(json.dumps(self.restore(v),ensure_ascii=False),json.dumps(self.data,ensure_ascii=False))
        self.assertEqual(self.file.read_bytes(),before)

    def test_full_mode_and_short_fallback(self):
        v=self.view(full=True);self.assertEqual(v['encoding'],'full');self.assertEqual(self.restore(v),self.data)
        self.write({'references':[{'path':'a/b','sha256':'a'*64}]})
        self.assertEqual(self.view()['encoding'],'full')

    def test_empty_and_no_common_directory_fallback(self):
        self.write({'references':[]});self.assertEqual(self.view()['encoding'],'full')
        self.write({'references':[{'path':p,'sha256':'a'*64} for p in ('a/x','b/y')]})
        self.assertEqual(self.view()['encoding'],'full')

    def test_unknown_reference_fields_preserved_full(self):
        self.data['references'][0]['negative_evidence']={'failed':True};self.write(self.data)
        v=self.view();self.assertEqual(v['encoding'],'full');self.assertEqual(self.restore(v),self.data)

    def test_duplicate_reference_preserved(self):
        self.data['references'].append(dict(self.data['references'][0]));self.write(self.data)
        self.assertEqual(self.restore(self.view()),self.data)

    def test_metadata_hash_path_and_order_tampering_rejected(self):
        for change in ('metadata','hash','path','order','keys'):
            v=self.view()
            if change=='metadata':v['data']['status']='approved'
            elif change=='hash':v['data']['references'][0]['sha256']='0'*64
            elif change=='path':v['data']['references'][0]['path']='different.json'
            elif change=='order':v['data']['references'].reverse()
            else:v['data']=dict(reversed(list(v['data'].items())))
            with self.subTest(change=change):
                with self.assertRaises(ValueError):self.restore(v)

    def test_directory_boundary_and_unsafe_suffix_rejected(self):
        for prefix,suffix in ((self.prefix[:-1],'x'),('/','x'),('../','x'),(self.prefix,'../x'),(self.prefix,'/x')):
            v=self.view();v['path_prefix']=prefix;v['data']['references'][0]['path']=suffix
            with self.assertRaises(ValueError):self.restore(v)

    def test_unknown_frame_and_binding_rejected(self):
        for field,value in (('schema_version','wrong'),('encoding','unknown'),('project_root','elsewhere'),('scope','approved'),('extra',True),('source',{'path':self.path,'sha256':'0'*64})):
            v=self.view();v[field]=value
            with self.assertRaises(ValueError):self.restore(v)

    def test_truncated_or_extended_references_rejected(self):
        for append in (False,True):
            v=self.view()
            if append:v['data']['references'].append(dict(v['data']['references'][0]))
            else:v['data']['references'].pop()
            with self.assertRaises(ValueError):self.restore(v)

    def test_duplicate_keys_and_nonfinite_source_rejected(self):
        for raw in (b'{"references":[],"references":[]}',b'{"references":[],"m":{"x":1,"x":2}}',b'{"references":[],"m":NaN}',b'{"references":[],"m":1e999}'):
            self.raw(raw)
            with self.assertRaises(ValueError):self.view()

    def test_invalid_unicode_and_utf8_source_rejected(self):
        for raw in (b'{"references":[],"m":"\\ud800"}',b'{"references":[],"m":"\xff"}'):
            self.raw(raw)
            with self.assertRaises(ValueError):self.view()

    def test_reference_path_sha_shapes_rejected(self):
        for path in ('../x','/x','a//x','a/./x','a\\x','C:x','a/'):
            self.write({'references':[{'path':path,'sha256':'a'*64}]})
            with self.assertRaises(ValueError):self.view()
        for sha in ('bad',True,'A'*64):
            self.write({'references':[{'path':'a/x','sha256':sha}]})
            with self.assertRaises(ValueError):self.view()

    def test_stale_source_rejected_for_view_and_restore(self):
        v=self.view();self.file.write_bytes(b'changed')
        with self.assertRaises(ValueError):self.view()
        with self.assertRaises(ValueError):self.restore(v)

    def test_source_path_and_invalid_sha_rejected(self):
        for path in ('../escape','/absolute','a\\b'):
            with self.assertRaises(ValueError):reference_view(self.root,path,self.sha)
        with self.assertRaises(ValueError):reference_view(self.root,self.path,'bad')

    def test_budget_and_flag_fail_without_truncation(self):
        for n in (1,0,True,1000001):
            with self.assertRaises(ValueError):self.view(max_chars=n)
            with self.assertRaises(ValueError):self.restore(self.view(),max_chars=n)
        with self.assertRaises(ValueError):self.view(full=1)

    def test_source_byte_limit(self):
        self.raw(b'{"references":[],"m":"'+b'x'*(2*1024*1024)+b'"}')
        with self.assertRaises(ValueError):self.view()

    def test_symlink_rejected(self):
        link=self.root/'linked.json'
        try:link.symlink_to(self.file)
        except OSError:self.skipTest('host cannot create symlinks')
        with self.assertRaises(ValueError):reference_view(self.root,'linked.json',self.sha)

    def test_cli_matches_api_full_and_compact(self):
        cli=Path(__file__).resolve().parents[1]/'scripts/reference_context.py'
        args=[sys.executable,'-X','utf8',str(cli),'--root',str(self.root),'--path',self.path,'--sha256',self.sha,'--compact']
        for full in (False,True):
            p=subprocess.run(args+(['--full'] if full else []),capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout),self.view(full=full))
