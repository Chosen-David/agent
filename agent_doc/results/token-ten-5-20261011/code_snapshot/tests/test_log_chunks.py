import copy,hashlib,tempfile,unittest
from pathlib import Path
from agent_runtime.log_context import log_view,restore_log_lines

class LogChunkTests(unittest.TestCase):
    def make(self,text,**options):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);root=Path(t.name).resolve()
        (root/'run.log').write_bytes(text.encode());digest=hashlib.sha256(text.encode()).hexdigest()
        return log_view(root,'run.log',digest,**options)
    def test_complete_exact_terminators(self):
        for text in ('a\r\nb\nlast','a\rb\r','x\u2028y\n',''):
            plain=self.make(text,head=100);packed=self.make(text,head=100,encoding='chunks')
            self.assertEqual(restore_log_lines(packed),plain['lines'])
    def test_gaps_metadata_and_unknown_failure(self):
        text='first\nignored\nERROR fail\nignored\nlast\n'
        plain=self.make(text,head=1,tail=1,context=0,needles=['ERROR'])
        packed=self.make(text,head=1,tail=1,context=0,needles=['ERROR'],encoding='chunks')
        self.assertEqual(restore_log_lines(packed),plain['lines'])
        for key in ('selection','literal_match_line_counts','total_lines','omitted_lines','scope','source'):
            self.assertEqual(plain[key],packed[key])
    def test_unordered_overlap_bool_and_empty_reject(self):
        value=self.make('a\nb\n',head=2,encoding='chunks')
        for chunks in ([{'start':True,'text':'a\nb\n'}],[{'start':1,'text':''}],
                       [{'start':2,'text':'b\n'},{'start':1,'text':'a\n'}],
                       [{'start':1,'text':'a\nb\n'},{'start':2,'text':'b\n'}]):
            bad=copy.deepcopy(value);bad['chunks']=chunks
            with self.assertRaises(ValueError):restore_log_lines(bad)
    def test_budget_and_count(self):
        value=self.make('abc\ndef\n',head=2,encoding='chunks')
        with self.assertRaises(ValueError):restore_log_lines(value,max_chars=7)
        value['omitted_lines']=1
        with self.assertRaises(ValueError):restore_log_lines(value)
    def test_default_and_empty_selection(self):
        value=self.make('unknown failure\n',head=0,tail=0,encoding='chunks')
        self.assertEqual(restore_log_lines(value),[]);self.assertIn('no proof',value['scope'])
        self.assertNotIn('encoding',self.make('a\n'))
    def test_ambiguous_lines_reject(self):
        for explicit in (False,True):
            value=self.make('a\n');value['chunks']=[]
            if explicit:value['encoding']='lines'
            with self.assertRaises(ValueError):restore_log_lines(value)
