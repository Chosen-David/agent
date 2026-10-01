import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import fitz

spec=importlib.util.spec_from_file_location('reader_app',Path(__file__).resolve().parents[1]/'app.py')
app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)

class ReaderTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.server=app.make_server(self.temp.name,0)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base=f'http://127.0.0.1:{self.server.server_port}'
        d=fitz.open()
        for i in (1,2):d.new_page().insert_text((72,72),f'Synthetic page {i}')
        self.pdf=d.tobytes();d.close()
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.temp.cleanup()
    def call(self,path,body=None,headers=None):
        h={'X-Reader-Token':self.server.token};h.update(headers or {})
        data=body if isinstance(body,bytes) else json.dumps(body).encode() if body is not None else None
        with urlopen(Request(self.base+path,data=data,headers=h),timeout=5) as r:return r.read()
    def test_import_pages_progress_persistence(self):
        p=json.loads(self.call('/api/upload',self.pdf));key=p['id'];self.assertEqual(p['pages'],2)
        self.assertEqual(self.call('/api/papers/'+key+'/pdf'),self.pdf)
        self.assertTrue(self.call('/api/papers/'+key+'/page/2.png').startswith(b'\x89PNG'))
        self.assertIn('Synthetic page 2',self.call('/api/papers/'+key+'/page/2').decode())
        self.call('/api/progress',{'paper':key,'page':2})
        self.call('/api/notes',{'paper':key,'page':2,'question':'Q','answer':'<script>example</script>'})
        reopened=app.Store(self.temp.name);self.assertEqual(reopened.info(key)['page'],2)
        self.assertEqual(reopened.notes(key)[0]['answer'],'<script>example</script>')
        with self.assertRaises(HTTPError):self.call('/api/papers/'+key+'/page/0')
    def test_request_boundary_and_invalid_pdf(self):
        for headers in ({'X-Reader-Token':'wrong'},{'Origin':'https://unrelated.example'},{'Host':'unrelated.example'}):
            with self.assertRaises(HTTPError) as result:self.call('/api/upload',self.pdf,headers)
            self.assertEqual(result.exception.code,403)
        with self.assertRaises(HTTPError):self.call('/api/upload',b'not a PDF')
        for invalid in ('http://127.0.0.1/secret','https://arxiv.org.evil.example/pdf/2609.36760','https://arxiv.org/pdf/../../x','https://arxiv.org:9443/pdf/2609.36760'):
            with self.assertRaises(ValueError):app.arxiv_url(invalid)
        self.assertEqual(app.arxiv_url('https://arxiv.org/abs/2609.36760v2'),'https://arxiv.org/pdf/2609.36760v2')
    def test_model_completion_is_required(self):
        paper=self.server.store.add(self.pdf);key=paper['id']
        events='\n'.join(json.dumps(x) for x in [{'type':'item.completed','item':{'type':'agent_message','text':'Test-only answer'}},{'type':'turn.completed'}])
        with patch.object(app.shutil,'which',return_value='/test/codex'),patch.object(app.subprocess,'run',return_value=subprocess.CompletedProcess([],0,events,'')) as run:
            answer=app.codex_question(self.server.store,key,2,'What is this?','page 2',False)
            self.assertEqual(answer['page'],2);kwargs=run.call_args.kwargs
            self.assertIn('Synthetic page 2',kwargs['input']);self.assertNotIn('shell',kwargs)
            self.assertIn('read-only',run.call_args.args[0])
        self.assertEqual(len(self.server.store.notes(key)),1)
        with patch.object(app.shutil,'which',return_value='/test/codex'),patch.object(app.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','simulated failure')):
            with self.assertRaises(ValueError):app.codex_question(self.server.store,key,2,'Question','',False)
        self.assertEqual(len(self.server.store.notes(key)),1)

if __name__=='__main__':unittest.main()
