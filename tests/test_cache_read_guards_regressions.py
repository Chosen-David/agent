import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from agent_runtime import legacy_result_paths as legacy, project_docs as docs
from agent_runtime import knowledge_index as index, source_context as source
from agent_runtime.knowledge import KnowledgeStore, KnowledgeError

class Cache(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)

    def test_fresh_bytes_and_bounded_immutable_cache(self):
        path=self.root/legacy.MARKER;path.parent.mkdir(parents=True)
        legacy._marker_files.cache_clear()
        for i in range(7):
            digest=hashlib.sha256(str(i).encode()).hexdigest()
            path.write_text(json.dumps({'schema_version':'agent-doc-relocation/v1','files':{'doc/results/a':digest}}),encoding='utf-8')
            self.assertEqual(legacy.legacy_read_binding(self.root,'doc/results/a'),('agent_doc/results/a',digest))
        info=legacy._marker_files.cache_info();self.assertEqual(info.currsize,4)
        legacy.legacy_read_binding(self.root,'doc/results/a')
        self.assertGreater(legacy._marker_files.cache_info().hits,info.hits)
        (self.root/'doc/results').mkdir(parents=True);(self.root/'doc/results/a').write_bytes(b'collision')
        with self.assertRaisesRegex(ValueError,'collision'):legacy.legacy_read_binding(self.root,'doc/results/a')

    def test_no_write_on_bad_rebuild(self):
        store=KnowledgeStore(Path(__file__).resolve().parents[1]/'knowledge')
        for value in (1,'false',None):
            with self.assertRaises(KnowledgeError):index.build_index(store,self.root/'new.sqlite',rebuild=value)
            self.assertFalse((self.root/'new.sqlite').exists())

    def test_consistent_sqlite_reader(self):
        from contextlib import closing
        store=KnowledgeStore(Path(__file__).resolve().parents[1]/'knowledge');path=self.root/'index.sqlite'
        index.build_index(store,path)
        with closing(sqlite3.connect(path)) as con:con.execute('PRAGMA journal_mode=WAL')
        original=index._connect;changed=[]
        class Connection:
            def __init__(self,con):self.con=con
            def close(self):self.con.close()
            def execute(self,sql,*args):
                if 'bm25(docs' in sql and not changed:
                    with closing(sqlite3.connect(path)) as writer:
                        with writer:
                            writer.execute('DELETE FROM docs');writer.execute('DELETE FROM chunks')
                            writer.execute("UPDATE meta SET value='new-snapshot' WHERE key='snapshot'")
                    changed.append(True)
                return self.con.execute(sql,*args)
        with patch.object(index,'_connect',side_effect=lambda *a,**kw:Connection(original(*a,**kw))):
            result=index.indexed_search(store,path,'memory')
        self.assertTrue(changed)
        self.assertTrue(any(any(m['retriever']=='document-bm25' for m in hit['matches']) for hit in result['results']))
        with self.assertRaisesRegex(KnowledgeError,'stale'):index.indexed_search(store,path,'memory')

    def test_parser_bound_before_read(self):
        raw=b'x'*270000;(self.root/'large.py').write_bytes(raw)
        request={'schema_version':'source-context/v1','source':{'path':'large.py','sha256':hashlib.sha256(raw).hexdigest()},'symbols':['x']}
        with patch('agent_runtime.result_validation.os.fdopen',wraps=__import__('os').fdopen) as opened:
            with self.assertRaises(ValueError):source.source_context(self.root,request)
            self.assertEqual(opened.call_count,1)
        from agent_runtime import result_validation as validation
        self.assertEqual(validation._bytes(self.root,'large.py'),raw)
        with self.assertRaises(ValueError):validation._bytes(self.root,'large.py',max_bytes=1)
        (self.root/'small').write_bytes(b'123')
        with patch.object(validation,'LIMIT',2):
            with self.assertRaisesRegex(ValueError,'exceeds'):validation._bytes(self.root,'small')

    def test_inventory_streams_exact(self):
        directory=self.root/'agent_doc/advice';directory.mkdir(parents=True);raw=b'x'*100000
        (directory/'evidence.md').write_bytes(raw)
        with patch.object(docs,'regular_bytes',side_effect=AssertionError('whole body allocation')):
            result=docs._inventory(self.root,'agent_doc/advice')
        self.assertEqual(result,{'agent_doc/advice/evidence.md':hashlib.sha256(raw).hexdigest()})

if __name__=='__main__':unittest.main()
