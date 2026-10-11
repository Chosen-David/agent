import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from agent_runtime.artifact_context import compare_artifacts,restore_comparison

class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()
        self.text='Keep pending and cancelled claims.\r\n'*20+'Unicode: 意见\n'
        for p in ('old.md','current.md'):(self.root/p).write_bytes(self.text.encode())
        self.refs=[{'path':p,'sha256':hashlib.sha256(self.text.encode()).hexdigest()} for p in ('old.md','current.md')]
    def view(self,**kwargs):return compare_artifacts(self.root,*self.refs,**kwargs)
    def test_exact_same_packet_base(self):
        v=self.view(reuse_identical=True)
        self.assertEqual(v['after']['representation'],'identical')
        self.assertEqual(restore_comparison(self.root,v,*self.refs),(self.text,self.text))
        self.assertLess(len(json.dumps(v)),len(json.dumps(self.view())))
    def test_default_and_full_compatible(self):
        self.assertEqual(self.view()['after']['representation'],'splice')
        self.assertEqual(self.view(full=True,reuse_identical=True)['after']['representation'],'full')
    def test_changed_target_not_aliased(self):
        p=self.root/'current.md';p.write_bytes((self.text+'BLOCK_CANCEL\n').encode())
        self.refs[1]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
        v=self.view(reuse_identical=True)
        self.assertNotEqual(v['after']['representation'],'identical')
        self.assertEqual(restore_comparison(self.root,v,*self.refs)[1],self.text+'BLOCK_CANCEL\n')
    def test_tampering_rejected(self):
        v=self.view(reuse_identical=True)
        for field,value in [('text','hidden'),('splice',{})]:
            bad=copy.deepcopy(v);bad['after'][field]=value
            with self.assertRaises(ValueError):restore_comparison(self.root,bad,*self.refs)
        bad=copy.deepcopy(v);bad['before']['text']='changed'
        with self.assertRaises(ValueError):restore_comparison(self.root,bad,*self.refs)
    def test_wrong_current_binding_rejected(self):
        v=self.view(reuse_identical=True);other=copy.deepcopy(self.refs)
        other[1]['sha256']='f'*64;v['after']['ref']=other[1]
        with self.assertRaises(ValueError):restore_comparison(self.root,v,*other)
    def test_stale_files_and_budget_rejected(self):
        (self.root/'current.md').write_bytes(b'changed')
        with self.assertRaises(ValueError):self.view(reuse_identical=True)
        (self.root/'current.md').write_bytes(self.text.encode())
        with self.assertRaises(ValueError):self.view(reuse_identical=True,max_chars=30)
    def test_bad_flag(self):
        with self.assertRaises(ValueError):self.view(reuse_identical=1)

if __name__=='__main__':unittest.main()
