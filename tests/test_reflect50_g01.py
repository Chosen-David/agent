"""Resource ownership and literal streaming-digest regression oracles."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from agent_runtime import project_docs as docs, maintenance_observer as observer
from agent_runtime import knowledge_index, artifact_index

class Resources(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'a.md').write_bytes(b'original')

    def failed_setup(self, module, call):
        opened=[]
        original=os.open
        def tracked(*args, **kw):
            fd=original(*args, **kw); opened.append(fd); return fd
        with patch.object(module.os,'open',tracked), patch.object(module.os,'fdopen',side_effect=RuntimeError('setup')):
            with self.assertRaisesRegex(RuntimeError,'setup'):
                call()
        self.assertTrue(opened)
        for fd in opened:
            with self.assertRaises(OSError):
                os.fstat(fd)

    def test_R01_read_setup_closes(self):
        self.failed_setup(docs,lambda:docs.regular_bytes(self.root,'a.md'))
        self.assertEqual(docs.regular_bytes(self.root,'a.md'),b'original')

    def test_R02_atomic_setup_preserves(self):
        self.failed_setup(docs,lambda:docs.atomic_write(self.root,'a.md',b'replacement'))
        self.assertEqual((self.root/'a.md').read_bytes(),b'original')
        self.assertEqual(sorted(p.name for p in self.root.iterdir()),['a.md'])
        docs.atomic_write(self.root,'a.md',b'replacement')
        self.assertEqual((self.root/'a.md').read_bytes(),b'replacement')

    def test_R03_observer_closes_and_bounds(self):
        self.failed_setup(observer,lambda:observer.read_bound(self.root,'a.md'))
        with self.assertRaisesRegex(ValueError,'budget'):
            observer.read_bound(self.root,'a.md',max_bytes=3)
        self.assertEqual(observer.read_bound(self.root,'a.md'),b'original')

    def test_R04_pragma_closes(self):
        class Connection:
            closed=False
            def execute(self,*args): raise RuntimeError('pragma')
            def close(self): self.closed=True
        con=Connection()
        with patch.object(knowledge_index.sqlite3,'connect',return_value=con):
            with self.assertRaisesRegex(RuntimeError,'pragma'):
                knowledge_index._connect(self.root/'cache.sqlite')
        self.assertTrue(con.closed)

    def test_R05_streaming_exact_growth_bound(self):
        raw=bytes(range(256))*4000
        (self.root/'a.md').write_bytes(raw)
        expected=hashlib.sha256(raw).hexdigest()
        self.assertEqual(docs.regular_digest(self.root,'a.md'),(expected,len(raw)))
        indexed=artifact_index.build_artifact_index(self.root)
        self.assertEqual(indexed['files']['a.md']['sha256'],expected)
        self.assertEqual(indexed['files']['a.md']['size'],len(raw))
        with self.assertRaises(docs.DocumentError):
            docs.regular_digest(self.root,'a.md',max_bytes=len(raw)-1)
        self.assertEqual(docs.regular_digest(self.root,'a.md',max_bytes=len(raw)),(expected,len(raw)))

if __name__=='__main__': unittest.main()
