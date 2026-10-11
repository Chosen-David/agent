import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from agent_runtime.context_serialization import render_context

class SerializationTests(unittest.TestCase):
    def test_default_exact_valid_payload(self):
        v={'status':'pending','errors':['BLOCK_VERIFY'],'text':'意见\r\n"quote"','n':4}
        self.assertEqual(render_context(v),json.dumps(v,ensure_ascii=False))
        self.assertEqual(render_context(v,indent=2),json.dumps(v,ensure_ascii=False,indent=2))
    def test_compact_exact_decoded_payload(self):
        v={'status':'invalid','errors':['BLOCK_CANCEL'],'nested':[{'a':[1,False,None],'b':'\n'}]*10}
        self.assertEqual(json.loads(render_context(v,compact=True,indent=2)),v)
        self.assertLess(len(render_context(v,compact=True)),len(render_context(v,indent=2)))
    def test_small_values(self):
        for v in ({},[],None,False,0,''):
            self.assertEqual(json.loads(render_context(v,compact=True)),v)
    def test_invalid_flags(self):
        for kw in ({'compact':1},{'indent':True},{'indent':9}):
            with self.assertRaises(ValueError):render_context({},**kw)
    def test_nonfinite_rejected(self):
        for n in (float('nan'),float('inf')):
            with self.assertRaises(ValueError):render_context({'n':n},compact=True)
    def test_real_log_cli(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d).resolve();raw=b'ERROR BLOCK_VERIFY\nINFO pending\n';(root/'run.log').write_bytes(raw)
            cmd=[sys.executable,'-X','utf8',str(Path(__file__).resolve().parents[1]/'scripts/log_context.py'),'--root',str(root),'--path','run.log','--sha256',hashlib.sha256(raw).hexdigest(),'--head','2','--tail','0']
            old=subprocess.check_output(cmd).decode('utf-8');new=subprocess.check_output(cmd+['--compact']).decode('utf-8')
            self.assertEqual(json.loads(old),json.loads(new));self.assertLess(len(new),len(old))

if __name__=='__main__':unittest.main()
