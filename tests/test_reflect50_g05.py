import datetime as dt
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from agent_runtime import result_store as r

class Results(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)
        (self.root/'tiny').write_bytes(b'abc')

    def test_R21_overflow_is_record_error(self):
        for value in ('0001-01-01T00:00:00+01:00','9999-12-31T23:59:59-01:00'):
            with self.assertRaises(r.ResultStoreError): r._timestamp(value)
        self.assertEqual(r._timestamp('2026-10-21T08:00:00+08:00'),dt.datetime(2026,10,21,tzinfo=dt.timezone.utc))

    def stream_reads(self,operation):
        requests=[];original=r.os.fdopen
        class Stream:
            def __init__(self,stream): self.stream=stream
            def __getattr__(self,key): return getattr(self.stream,key)
            def __enter__(self): self.stream.__enter__();return self
            def __exit__(self,*args): return self.stream.__exit__(*args)
            def read(self,size=-1): requests.append(size);return self.stream.read(size)
        with patch.object(r.os,'fdopen',side_effect=lambda *a,**k:Stream(original(*a,**k))): operation()
        return requests

    def test_R22_tiny_probe(self):
        requests=self.stream_reads(lambda:self.assertEqual(r._read(self.root,'tiny'),b'abc'))
        self.assertEqual(requests,[4])
        with self.assertRaises(r.ResultStoreError):r._read(self.root,'tiny',2)

    def test_R23_tiny_hash_scratch(self):
        requests=self.stream_reads(lambda:r._check_ref(self.root,{'path':'tiny','sha256':hashlib.sha256(b'abc').hexdigest()}))
        self.assertTrue(requests);self.assertLessEqual(max(requests),4)
        with self.assertRaises(r.ResultStoreError):r._check_ref(self.root,{'path':'tiny','sha256':'0'*64})

    def test_R24_literal_full_json_score(self):
        for data in ({'a':'x'*65534+'Straße中文','b':['a','b',None]}, {'a':'A\\\n"B','b':{'z':'ss'}}):
            tokens=['strasse','中文','a", "b','ss','\\n','missing','e中']
            oracle=json.dumps(data,ensure_ascii=False).casefold()
            self.assertEqual(r._lexical_score(data,tokens),sum(t in oracle for t in set(tokens)))

    def test_R25_bounded_rank_preserves_errors(self):
        class Store(r.ResultStore):
            def _directories(self,max_scan): return [str(i) for i in range(30)],False,None
            def show(self,name):
                if name=='4': raise r.ResultStoreError('bad')
                record={'summary':'word','run_id':name,'result_id':None,'producer_task_id':None,'context':{},'origin':'historical','validation_at_registration':{'status':'pending'}}
                return {'record':record,'record_ref':{'sha256':'0'*64,'path':name}}
        result=Store(self.root).search('word',limit=2)
        self.assertEqual([x['run_id'] for x in result['results']],['0','1'])
        self.assertTrue(result['partial']);self.assertEqual(result['errors'],[{'run_id':'4','error':'bad'}])

    def test_R24_custom_show_serializes_once(self):
        class Store(r.ResultStore):
            def _directories(self,max_scan): return ['a'],False,None
            def show(self,name):
                return {'record':{'summary':'word other','context':{},'origin':'historical','validation_at_registration':{'status':'pending'}},'record_ref':{'sha256':'0'*64,'path':'a'}}
        original=r.json.dumps
        with patch.object(r.json,'dumps',wraps=original) as dumps:
            result=Store(self.root).search('word other',limit=1)
        self.assertEqual(result['results'][0]['score'],2)
        self.assertEqual(dumps.call_count,1)

if __name__=='__main__':unittest.main()
