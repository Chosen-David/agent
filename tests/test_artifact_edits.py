import copy,hashlib,json,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
from agent_runtime.artifact_context import compare_artifacts,restore_comparison,_edits

class EditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name).resolve()
        self.old='header\r\n'+''.join(f'unchanged {i:02}: preserve every constraint\r\n' for i in range(30))+'footer\n'
        self.new=self.old.replace('header','BLOCK_CANCEL').replace('footer','BLOCK_VERIFY')
        self.refs=[]
        for p,t in [('old.md',self.old),('current.md',self.new)]:
            (self.root/p).write_bytes(t.encode());self.refs.append({'path':p,'sha256':hashlib.sha256(t.encode()).hexdigest()})
    def view(self,**kw):return compare_artifacts(self.root,*self.refs,**kw)
    def test_two_separated_edits(self):
        v=self.view(multi_edit=True)
        self.assertEqual(v['after']['representation'],'edits')
        self.assertEqual(len(v['after']['patch']['edits']),2)
        self.assertEqual(restore_comparison(self.root,v,*self.refs),(self.old,self.new))
        self.assertLess(len(json.dumps(v)),len(json.dumps(self.view())))
    def test_full_and_default(self):
        self.assertNotEqual(self.view()['after']['representation'],'edits')
        self.assertEqual(self.view(full=True,multi_edit=True)['after']['representation'],'full')
    def test_empty_and_bound_fallback(self):
        self.assertIsNone(_edits('x','x'))
        self.assertIsNone(_edits('a'*65537,'b'))
        self.assertIsNone(_edits('a\n'*2049,'b'))
    def test_insert_delete_unicode(self):
        old='A\r\nB\nC\n'+'middle\n'*20+'D\n'
        new='A\r\n新\n'+'middle\n'*20+'D\nE\n'
        p=_edits(old,new);self.assertIsNotNone(p)
        lines=old.splitlines(keepends=True)
        for e in reversed(p['edits']):lines[e['start']:e['start']+e['delete']]=[e['insert']]
        self.assertEqual(''.join(lines),new)
    def test_bad_edits(self):
        v=self.view(multi_edit=True)
        for edits in ([],[v['after']['patch']['edits'][0]]*2,[{'start':True,'delete':0,'insert':''}],[{'start':-1,'delete':0,'insert':''}]):
            bad=copy.deepcopy(v);bad['after']['patch']['edits']=edits
            with self.assertRaises(ValueError):restore_comparison(self.root,bad,*self.refs)
    def test_hash_and_unknown_fields(self):
        v=self.view(multi_edit=True)
        for field,value in [('base_sha256','f'*64),('extra',1)]:
            bad=copy.deepcopy(v);bad['after']['patch'][field]=value
            with self.assertRaises(ValueError):restore_comparison(self.root,bad,*self.refs)
    def test_no_compression_bloat_or_bad_flags(self):
        self.assertIsNotNone(self.view(multi_edit=True))
        with self.assertRaises(ValueError):self.view(multi_edit=1)
        with self.assertRaises(ValueError):self.view(multi_edit=True,max_chars=30)
    def test_direct_dict_aggregate_budget_before_join(self):
        v=self.view(multi_edit=True)
        v['after']['patch']['edits']=[{'start':0,'delete':0,'insert':'x'*1000},{'start':1,'delete':0,'insert':'x'*1000}]
        with patch('agent_runtime.artifact_context.LIMIT',1600):
            with self.assertRaisesRegex(ValueError,'budget exceeded'):restore_comparison(self.root,v,*self.refs)
        v['after']['patch']['edits']=[{'start':0,'delete':0,'insert':'x'*1601}]
        with patch('agent_runtime.artifact_context.LIMIT',1600):
            with self.assertRaisesRegex(ValueError,'insert exceeds character'):restore_comparison(self.root,v,*self.refs)

if __name__=='__main__':unittest.main()
