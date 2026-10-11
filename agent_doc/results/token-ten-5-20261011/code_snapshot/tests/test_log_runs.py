import copy,hashlib,tempfile,unittest
from pathlib import Path
from agent_runtime.log_context import log_view,restore_log_lines

class LogRunTests(unittest.TestCase):
    def view(self,text,**kwargs):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);p=Path(t.name).resolve();(p/'run.log').write_bytes(text.encode())
        return log_view(p,'run.log',hashlib.sha256(text.encode()).hexdigest(),encoding='runs',**kwargs)
    def test_counts_and_complete_bytes(self):
        text='pending\r\n'*25+'ERROR\n'*2+'last'
        v=self.view(text,head=100,tail=0)
        self.assertEqual([r['count'] for r in v['runs']],[25,2,1])
        self.assertEqual(''.join(r['text'] for r in restore_log_lines(v)),text)
    def test_disjoint_same_line_not_merged(self):
        v=self.view('same\nother\nsame\n',head=1,tail=1)
        self.assertEqual([r['start'] for r in v['runs']],[1,3])
        self.assertEqual(len(restore_log_lines(v)),2)
    def test_invalid_counts_ranges_and_terminator(self):
        good=self.view('a\n'*3,head=3,tail=0)
        for fields in ({'count':True},{'count':0},{'count':10**100},{'start':True},{'start':2},{'text':'a'},{'text':'a\nb\n'}):
            bad=copy.deepcopy(good);bad['runs'][0].update(fields)
            with self.assertRaises(ValueError):restore_log_lines(bad)
    def test_bounds_before_expansion(self):
        v=self.view('long\n'*5,head=5,tail=0)
        with self.assertRaises(ValueError):restore_log_lines(v,max_chars=24)
        v['runs'][0]['text']='x'*1000
        with self.assertRaisesRegex(ValueError,'exceeds budget'):restore_log_lines(v,max_chars=24)
        v['chunks']=[]
        with self.assertRaises(ValueError):restore_log_lines(v)
    def test_empty_and_unknown_encoding(self):
        self.assertEqual(restore_log_lines(self.view('',head=0,tail=0)),[])
        v=self.view('a\n');v['encoding']='future'
        with self.assertRaises(ValueError):restore_log_lines(v)
