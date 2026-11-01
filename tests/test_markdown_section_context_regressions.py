import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

class MarkdownContext(unittest.TestCase):
    def setUp(self):
        from agent_runtime import markdown_context as module
        self.m=module
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)
        self.raw='preamble\r\n# Global\r\nrequired\r\n```\r\n# example\r\n```\r\n## A\r\n原文\u2028# literal\r\n## B\r\nother\r\n'
        (self.root/'doc.md').write_bytes(self.raw.encode())
        self.ref={'path':'doc.md','sha256':hashlib.sha256(self.raw.encode()).hexdigest()}

    def test_outline_literal_headings(self):
        result=self.m.outline(self.root,self.ref)
        self.assertEqual([n['title'] for n in result['nodes']],['doc.md','Global','A','B'])
        self.assertTrue(all('text' not in n for n in result['nodes']))
        with self.assertRaises(ValueError):self.m.outline(self.root,dict(self.ref,sha256='0'*64))

    def test_exact_selected_original_text(self):
        result=self.m.read_sections(self.root,self.ref,['s2'])
        self.assertEqual([n['node'] for n in result['sections']],['intro','s2'])
        self.assertEqual(result['sections'][1]['text'],'## A\r\n原文\u2028# literal\r\n')
        with self.assertRaises(ValueError):self.m.read_sections(self.root,self.ref,['missing'])

    def test_whole_node_pages(self):
        first=self.m.outline(self.root,self.ref,limit=1)
        second=self.m.outline(self.root,self.ref,limit=1,after_id=first['next_after_id'],expected_snapshot=first['snapshot'])
        self.assertEqual(second['nodes'][0]['node'],'s1')
        with self.assertRaises(ValueError):self.m.outline(self.root,self.ref,limit=1,after_id='intro')
        with self.assertRaises(ValueError):self.m.outline(self.root,self.ref,expected_snapshot='0'*64)

    def test_actual_cli_wire_and_refusal(self):
        command=[sys.executable,'-X','utf8','-B',str(Path(__file__).resolve().parents[1]/'scripts/markdown_context.py'),'--root',str(self.root),'--path','doc.md','--sha256',self.ref['sha256'],'outline','--limit','1']
        run=subprocess.run(command,capture_output=True);self.assertEqual(run.returncode,0,run.stderr)
        result=json.loads(run.stdout);self.assertEqual(len(result['nodes']),1)
        size=len(run.stdout.decode())
        exact=subprocess.run(command[:-3]+['--max-chars',str(size)]+command[-3:],capture_output=True)
        self.assertEqual(exact.returncode,0,exact.stderr)
        fail=subprocess.run(command[:-3]+['--max-chars',str(size-1)]+command[-3:],capture_output=True)
        self.assertEqual(fail.returncode,2);self.assertEqual(json.loads(fail.stdout)['status'],'blocked')
        native=[sys.executable,'-B',command[4],*command[5:-3],'read','--section','s2']
        env=dict(os.environ,PYTHONUTF8='0',PYTHONIOENCODING='cp936')
        unicode_run=subprocess.run(native,capture_output=True,env=env)
        self.assertEqual(unicode_run.returncode,0,unicode_run.stderr)
        self.assertIn('原文',json.loads(unicode_run.stdout)['sections'][-1]['text'])

    def test_mandatory_global_blocks(self):
        result=self.m.read_sections(self.root,self.ref,['s2'],mandatory=['s1'])
        self.assertEqual([n['node'] for n in result['sections']],['intro','s1','s2'])
        self.assertIn('required',result['sections'][1]['text'])
        with self.assertRaises(ValueError):self.m.read_sections(self.root,self.ref,['s2'],mandatory=['missing'])
        with self.assertRaises(ValueError):self.m.read_sections(self.root,self.ref,['s2'],mandatory=['s1','s1'])

    def test_counting_rejects_changed_or_missing_source(self):
        for mode in ('outline','read'):
            for change in ('replace','delete'):
                with self.subTest(mode=mode,change=change):
                    path=self.root/'doc.md';path.write_bytes(self.raw.encode())
                    def counter(_text):
                        if change=='delete':path.unlink()
                        else:path.write_text('# Global\npolicy withdrawn\n## A\nchanged instruction\n',encoding='utf-8')
                        return 1  # Timing hook, not measured token use.
                    with self.assertRaises((ValueError,OSError)):
                        if mode=='outline':self.m.outline(self.root,self.ref,max_tokens=10,token_counter=counter)
                        else:self.m.read_sections(self.root,self.ref,['s2'],mandatory=['s1'],max_tokens=10,token_counter=counter)

    def test_counting_keeps_captured_source_binding(self):
        for mode in ('outline','read'):
            with self.subTest(mode=mode):
                (self.root/'doc.md').write_bytes(self.raw.encode())
                ref=dict(self.ref)
                other=b'# Global\nother instruction\n'
                (self.root/'other.md').write_bytes(other)
                def counter(_text):
                    (self.root/'doc.md').write_bytes(b'# Changed\nnew source\n')
                    ref.update(path='other.md',sha256=hashlib.sha256(other).hexdigest())
                    return 1
                with self.assertRaises(ValueError):
                    if mode=='outline':self.m.outline(self.root,ref,max_tokens=10,token_counter=counter)
                    else:self.m.read_sections(self.root,ref,['s2'],mandatory=['s1'],max_tokens=10,token_counter=counter)

    def test_counting_preserves_unchanged_and_identically_replaced_source(self):
        for mode in ('outline','read'):
            for replace in (False,True):
                with self.subTest(mode=mode,replace=replace):
                    (self.root/'doc.md').write_bytes(self.raw.encode())
                    calls=[]
                    def view(**kwargs):
                        return (self.m.outline(self.root,self.ref,**kwargs) if mode=='outline' else
                                self.m.read_sections(self.root,self.ref,['s2'],mandatory=['s1'],**kwargs))
                    expected=view()
                    def counter(text):
                        calls.append(text)
                        if replace:
                            temporary=self.root/'same.md';temporary.write_bytes(self.raw.encode())
                            temporary.replace(self.root/'doc.md')
                        return 1
                    self.assertEqual(view(max_tokens=10,token_counter=counter),expected)
                    self.assertEqual(len(calls),1)
                    if mode=='read':
                        self.assertEqual([s['node'] for s in expected['sections']],['intro','s1','s2'])
                        self.assertIn('原文\u2028# literal',expected['sections'][-1]['text'])

    def test_cli_counting_rejects_source_change_without_old_payload(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from unittest.mock import patch
        for mode in ('outline','read'):
            with self.subTest(mode=mode):
                (self.root/'doc.md').write_bytes(self.raw.encode())
                def counter(_text):
                    (self.root/'doc.md').write_text('# Global\nchanged\n',encoding='utf-8')
                    return 1
                args=['--root',str(self.root),'--path','doc.md','--sha256',self.ref['sha256'],
                      '--max-tokens','10','--tokenizer','fixture',mode]
                if mode=='read':args+=['--section','s2','--mandatory','s1']
                output=StringIO()
                with patch('agent_runtime.handoff_basis.make_token_counter',return_value=counter),redirect_stdout(output):
                    code=self.m.main(args)
                self.assertEqual(code,2)
                value=json.loads(output.getvalue());self.assertEqual(value['status'],'blocked')
                self.assertNotIn('nodes',value);self.assertNotIn('sections',value)

if __name__=='__main__':unittest.main()
