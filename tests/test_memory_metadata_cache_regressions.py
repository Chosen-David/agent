import gc
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import weakref
from agent_runtime import project_memory as m

class MemoryIndex(unittest.TestCase):
    def store(self, count=8):
        class Store:
            root=Path.cwd()
            def list(self,status,scope):
                return [{'id':str(i),'content':'body'+str(i),'kind':'claim'} for i in range(count)]
        return Store()

    def index(self,store,**kw): return m.MemoryLedger.index(store,**kw)

    def test_only_project_page(self):
        calls=[]; original=m.hashlib.sha256
        def tracked(data=b''): calls.append(data); return original(data)
        with patch.object(m.hashlib,'sha256',side_effect=tracked): result=self.index(self.store(),limit=1)
        self.assertEqual(len(result['entries']),1)
        self.assertIn(b'body0',calls)
        self.assertNotIn(b'body7',calls)
        class Bad:
            root=Path.cwd()
            def list(self,*args): return [{'id':'a','content':'ok'},{'id':'b','content':'\ud800'}]
        with self.assertRaises(m.MemoryError): self.index(Bad(),limit=1)

    def test_streaming_exact_canonical(self):
        for value in ({'中文':['ß',None,1,False,{'z':3,'a':'x'*200000}]},[],{},''):
            oracle=hashlib.sha256(m._index_json(value).encode()).hexdigest()
            self.assertEqual(m._index_digest(value),oracle)
        for value in (float('nan'),'\ud800',object()):
            with self.assertRaises(m.MemoryError): m._index_digest(value)

    def test_cursor_membership(self):
        first=self.index(self.store(),limit=2)
        page=self.index(self.store(),limit=2,after_id='1',expected_snapshot=first['snapshot'])
        self.assertEqual([e['id'] for e in page['entries']],['2','3'])
        with self.assertRaises(m.MemoryError): self.index(self.store(),after_id='missing',expected_snapshot=first['snapshot'])

    def test_exact_incremental_budget(self):
        store=self.store(); all_data=self.index(store,limit=8)
        import os
        size=len(m._index_json(all_data))+len(os.linesep)
        self.assertEqual(self.index(store,limit=8,max_chars=size),all_data)
        smaller=self.index(store,limit=8,max_chars=size-1)
        self.assertTrue(smaller['partial'])
        self.assertLess(len(smaller['entries']),8)

    def test_omitted_bodies_released(self):
        refs=[]; counts=[]
        class Body(str): pass
        class Store:
            root=Path.cwd()
            def list(self,*args):
                values=[Body('body'+str(i)) for i in range(30)]
                refs.extend(weakref.ref(x) for x in values)
                return [{'id':str(i),'content':x} for i,x in enumerate(values)]
        original=m._index_json
        def observed(value):
            if isinstance(value,dict) and value.get('schema_version')=='memory-index/v1':
                gc.collect(); counts.append(sum(r() is not None for r in refs))
            return original(value)
        with patch.object(m,'_index_json',side_effect=observed): self.index(Store(),limit=1)
        self.assertTrue(counts)
        self.assertLessEqual(max(counts),1)

if __name__=='__main__': unittest.main()
