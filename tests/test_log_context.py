import hashlib,tempfile,unittest
from pathlib import Path
from agent_runtime.log_context import log_view
class LogViewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.path=self.root/'job.log'
    def view(self,text,**kwargs):
        self.path.write_bytes(text.encode());self.sha=hashlib.sha256(self.path.read_bytes()).hexdigest()
        return log_view(self.root,'job.log',self.sha,**kwargs)
    def test_exact_literal_context_and_dedup(self):
        text='head\nignored\nbefore\nERROR X\nERROR Y\nafter\nignored\ntail'
        v=self.view(text,needles=['ERROR'],head=1,tail=1,context=1)
        self.assertEqual([r['line'] for r in v['lines']],[1,3,4,5,6,8])
        self.assertEqual(v['literal_match_line_counts'],{'ERROR':2});self.assertEqual(v['omitted_lines'],2)
        self.assertEqual([r['text'] for r in v['lines']],[text.splitlines(keepends=True)[i-1] for i in [1,3,4,5,6,8]])
    def test_overlapping_complete_and_crlf(self):
        text='a\r\nb\r\nc\r\n';v=self.view(text,head=3,tail=3)
        self.assertEqual(''.join(r['text'] for r in v['lines']),text);self.assertEqual(v['omitted_lines'],0)
    def test_empty_and_no_matches_are_partial(self):
        self.assertEqual(self.view('',needles=['ERROR'])['lines'],[])
        v=self.view('unknown failure\nother\n',needles=['ERROR'],head=0,tail=0)
        self.assertEqual(v['literal_match_line_counts']['ERROR'],0);self.assertEqual(v['omitted_lines'],2)
        self.assertIn('no proof',v['scope'])
    def test_match_over_budget_never_truncated(self):
        with self.assertRaises(ValueError):self.view('ERROR\n'*50,needles=['ERROR'],max_chars=700)
    def test_stale_and_bad_arguments(self):
        self.view('one\n');self.path.write_bytes(b'two\n')
        with self.assertRaises(ValueError):log_view(self.root,'job.log',self.sha)
        for kwargs in ({'head':True},{'tail':-1},{'needles':['','ERROR']},{'context':1001},{'needles':['x','x']}):
            with self.assertRaises(ValueError):self.view('one\n',**kwargs)
    def test_literal_is_not_regex(self):
        v=self.view('.*\nother\n',needles=['.*'],head=0,tail=0,context=0)
        self.assertEqual([r['line'] for r in v['lines']],[1])

    def test_impossible_line_budget_rejects_before_json_serialization(self):
        from unittest.mock import patch
        with patch('agent_runtime.log_context.json.dumps', side_effect=AssertionError('oversized selection serialized')):
            with self.assertRaisesRegex(ValueError, 'selected log exceeds budget; no silent truncation'):
                self.view('ERROR\n' * 1002, needles=['ERROR'], max_chars=1000)

    def test_initial_selection_and_packed_raw_caps_still_reject(self):
        for encoding in ('lines', 'chunks', 'runs'):
            with self.subTest(encoding=encoding), self.assertRaisesRegex(ValueError, 'selected log exceeds budget'):
                self.view('x\n' * 1002, head=1000, tail=1000, max_chars=1000, encoding=encoding)
