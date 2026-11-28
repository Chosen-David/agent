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

    def test_semantic_change_and_display_alias(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            request=dict(family='display-family',trajectory='one',goal='endpoint',purpose='normalize',
                         mode='NEW_TRAIN',scientific_context={'execution':{'seed':42}},evidence_gap='missing')
            cmd=[sys.executable,'-c','pass']
            self.assertEqual(execute(root/'db',request,cmd),0)
            self.assertEqual(execute(root/'db',dict(request,family='renamed'),cmd),75)
            changed=dict(request,scientific_context={'execution':{'seed':43}})
            self.assertEqual(execute(root/'db',changed,cmd),0)
