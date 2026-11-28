import concurrent.futures
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
from agent_runtime.training_claim import execute


class ClaimTest(unittest.TestCase):
    def test_atomic_launch_and_restart(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            out=root/'writes'
            command=[sys.executable,'-c',
                     'import sys;open(sys.argv[1],"a").write("x")',str(out)]
            request=dict(family='f',trajectory='t',purpose='loss',goal='100',mode='NEW_TRAIN',
                         scientific_context={'scope':'new test'},evidence_gap='terminal loss missing')
            args=(root/'db',request,command)
            with concurrent.futures.ThreadPoolExecutor(2) as pool:
                futures=[pool.submit(execute,*args) for _ in range(2)]
                self.assertEqual(sorted(f.result() for f in futures),[0,75])
            self.assertEqual(execute(*args),75)
            self.assertEqual(out.read_text(),'x')
