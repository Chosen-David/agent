import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from agent_runtime.record_context import record_view


class RecordContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.path = 'agent_doc/advice/meeting.ndjson'
        self.file = self.root / self.path
        self.file.parent.mkdir(parents=True)
        self.write(b'{"rule":"independent verification"}\r\n{"old":"history"}\n{"current":"cancelled"}')

    def write(self, data):
        self.file.write_bytes(data)
        self.sha = hashlib.sha256(data).hexdigest()

    def view(self, **kwargs):
        defaults = dict(lines=[3], global_lines=[1])
        defaults.update(kwargs)
        return record_view(self.root, self.path, self.sha, **defaults)

    def test_exact_global_current_order_and_eof(self):
        v = self.view()
        self.assertEqual(v['records'], [{'line':1,'text':'{"rule":"independent verification"}\r\n'}, {'line':3,'text':'{"current":"cancelled"}'}])
        self.assertEqual((v['total_records'],v['omitted_records']), (3,1))

    def test_overlap_is_single_exact_record(self):
        self.assertEqual(len(self.view(lines=[3,1])['records']),2)

    def test_full_selection_recovers_exact_source(self):
        v=self.view(lines=[3,2,1])
        self.assertEqual(''.join(x['text'] for x in v['records']).encode(),self.file.read_bytes())
        self.assertEqual(v['omitted_records'],0)

    def test_unicode_separator_is_not_physical_line(self):
        self.write('{"s":"a\u2028b\u2029c"}\n{}\r\n'.encode())
        self.assertEqual(self.view(lines=[2])['total_records'],2)

    def test_unselected_malformed_record_rejected(self):
        self.write(b'{}\ninvalid\n{}\n')
        with self.assertRaises(ValueError):self.view()

    def test_nested_duplicate_key_rejected(self):
        self.write(b'{}\n{"x":{"k":1,"k":2}}\n{}\n')
        with self.assertRaises(ValueError):self.view()

    def test_nonfinite_literals_and_overflow_rejected(self):
        for bad in (b'NaN',b'Infinity',b'-Infinity',b'1e999',b'-1e999'):
            with self.subTest(bad=bad):
                self.write(b'{}\n'+bad+b'\n{}\n')
                with self.assertRaises(ValueError):self.view()

    def test_blank_and_empty_source_rejected(self):
        for data in (b'',b'{}\n\n{}\n',b'{}\n \n{}'):
            self.write(data)
            with self.assertRaises(ValueError):self.view()

    def test_utf8_rejected(self):
        self.write(b'{}\n\xff\n{}')
        with self.assertRaises(UnicodeDecodeError):self.view()

    def test_indices_rejected(self):
        for indices in ([],[0],[-1],[True],[1.0],[3,3],[4],list(range(1,130))):
            for key in ('lines','global_lines'):
                with self.subTest(key=key,indices=indices):
                    with self.assertRaises(ValueError):self.view(**{key:indices})

    def test_stale_and_invalid_sha(self):
        for sha in ('0'*64,'bad',None):
            with self.assertRaises(ValueError):record_view(self.root,self.path,sha,lines=[3],global_lines=[1])

    def test_output_budget_refuses_without_truncation(self):
        for limit in (1,0,True,1000001):
            with self.assertRaises(ValueError):self.view(max_chars=limit)

    def test_source_byte_bound(self):
        self.write(b'"'+b'x'*(2*1024*1024)+b'"')
        with self.assertRaises(ValueError):self.view(lines=[1])

    def test_record_count_bound(self):
        self.write(b'{}\n'*50001)
        with self.assertRaises(ValueError):self.view(lines=[1])

    def test_path_escape_rejected(self):
        for path in ('../escape','/absolute','agent_doc\\advice\\meeting.ndjson'):
            with self.assertRaises(ValueError):record_view(self.root,path,self.sha,lines=[3],global_lines=[1])

    def test_symlink_rejected(self):
        link=self.root/'link.ndjson'
        try:link.symlink_to(self.file)
        except OSError:self.skipTest('host cannot create symlinks')
        with self.assertRaises(ValueError):record_view(self.root,'link.ndjson',self.sha,lines=[3],global_lines=[1])

    def test_cli_requires_globals_and_matches_api(self):
        cli=Path(__file__).resolve().parents[1]/'scripts/record_context.py'
        args=[sys.executable,str(cli),'--root',str(self.root),'--path',self.path,'--sha256',self.sha,'--line','3']
        p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
        self.assertNotEqual(p.returncode,0)
        p=subprocess.run(args+['--global-line','1','--compact'],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout),self.view())
