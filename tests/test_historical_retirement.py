import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.checkpoint_retention import CheckpointRetention
from agent_runtime.historical_retirement import authorize, retire, file_fence


class ScopedRetirement(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=os.getenv('RETIRE_TEST_FS'))
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.store=CheckpointRetention(self.root/'registry')
        self.addCleanup(self.store.db.close)
        self.old,self.new=self.generate('A',201),self.generate('A',401)
        self.key=authorize(self.store,self.old,self.new,'batch')
        self.other=self.generate('B',401)

    def generate(self,run,step):
        p=self.root/run/f'step_{step}'
        p.mkdir(parents=True)
        (p/'rank_00000.pt').write_bytes(b'fixture')
        m=dict(step=step,rank_count=1,world_size=1,ep_size=1,format='fsdp2_rank_local_shards',identity_sha256='test',
               files=[dict(rank=0,path='rank_00000.pt',bytes=7)])
        data=json.dumps(m).encode()
        (p/'manifest.json').write_bytes(data)
        (p.parent/'LATEST').write_text(json.dumps(dict(directory=p.name,manifest_sha256=hashlib.sha256(data).hexdigest())))
        return p

    def run_retire(self):
        return retire(self.store,self.key,live_check=lambda a,b:None)

    def test_reader_then_retry(self):
        with (self.old/'rank_00000.pt').open('rb'):
            with self.assertRaisesRegex(RuntimeError,'file lease unavailable'):
                self.run_retire()
        self.assertEqual(self.run_retire()['status'],'purged')
        self.assertEqual(self.run_retire()['status'],'already-purged')
        self.assertTrue(self.new.exists() and self.other.exists())

    def test_open_during_fence(self):
        p=self.old/'rank_00000.pt'
        with file_fence([p]):
            proc=subprocess.run([sys.executable,'-c','import os,sys,errno\ntry: os.open(sys.argv[1],os.O_RDONLY|os.O_NONBLOCK)\nexcept BlockingIOError as e: sys.exit(0 if e.errno==errno.EAGAIN else 2)\nsys.exit(1)',str(p)])
            self.assertEqual(proc.returncode,0)

    def test_replaced_directory(self):
        self.old.rename(self.old.with_name('previous'))
        import shutil
        shutil.copytree(self.old.with_name('previous'),self.old)
        with self.assertRaisesRegex(ValueError,'generation identity changed'):
            self.run_retire()
        self.assertTrue(self.old.exists())

    def test_pin(self):
        self.store.reference(self.key,'evaluation','milestone')
        with self.assertRaisesRegex(ValueError,'active registry reference'):
            self.run_retire()
        self.assertTrue(self.old.exists())

    def test_resume_quarantine(self):
        with patch.object(Path,'unlink',side_effect=InterruptedError):
            with self.assertRaises(InterruptedError):self.run_retire()
        self.assertFalse(self.old.exists())
        self.assertEqual(self.run_retire()['status'],'purged')
