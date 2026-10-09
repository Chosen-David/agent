"""Exact byte semantics, host references and self-contained CLI comparisons."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from agent_runtime.artifact_context import compare_artifacts,restore_comparison


class ArtifactContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def save(self,name,text):
        data=text.encode('utf-8');(self.root/name).write_bytes(data)
        return {'path':name,'sha256':hashlib.sha256(data).hexdigest()}

    def test_real_edit_roundtrip_and_new_cancellation(self):
        before='Keep scope and current independent evidence.\r\n'*30+'Status: running\r\n'
        after=before.replace('Status: running','Status: cancelled; stop model dispatch')
        a=self.save('before.md',before);b=self.save('after.md',after)
        value=compare_artifacts(self.root,a,b)
        self.assertEqual(value['after']['representation'],'splice')
        self.assertEqual(restore_comparison(self.root,value,a,b),(before,after))
        self.assertEqual(value['before']['text'],before)
        self.assertIn('cancelled',value['after']['splice']['insert'])
        full=compare_artifacts(self.root,a,b,full=True)
        self.assertEqual(full['after']['representation'],'full')
        self.assertLess(len(json.dumps(value)),len(json.dumps(full)))

    def test_random_edits_unicode_empty_crlf_order(self):
        rng=random.Random(607)
        cases=[('', ''),('', 'new'),('old',''),('a\r\nb','a\nb'),('龙🐈A\r\n','龙🐈B\r\n'),('abc','cba')]
        for _ in range(80):
            text=''.join(rng.choice('α🐈ab\r\n') for _ in range(rng.randrange(100)))
            left=rng.randrange(len(text)+1);right=rng.randrange(left,len(text)+1)
            cases.append((text,text[:left]+'cancelled'+text[right:]))
        for old,new in cases:
            a=self.save('a',old);b=self.save('b',new)
            value=compare_artifacts(self.root,a,b)
            self.assertEqual(restore_comparison(self.root,json.dumps(value),a,b),(old,new))

    def test_unknown_tampered_refs_ranges_and_root(self):
        a=self.save('a','same prefix\n'*30+'old');b=self.save('b','same prefix\n'*30+'new')
        value=compare_artifacts(self.root,a,b)
        cases=[]
        for field,replacement in [('start',True),('delete',-1),('insert','wrong'),('base_sha256','0'*64)]:
            v=deepcopy(value);v['after']['splice'][field]=replacement;cases.append(v)
        v=deepcopy(value);v['extra']='hidden';cases.append(v)
        v=deepcopy(value);v['before']['text']='other';cases.append(v)
        v=deepcopy(value);v['position_unit']='bytes';cases.append(v)
        for v in cases:
            with self.assertRaises(ValueError):restore_comparison(self.root,v,a,b)
        with tempfile.TemporaryDirectory() as other, self.assertRaises(ValueError):
            restore_comparison(Path(other),value,a,b)
        with self.assertRaises(ValueError):restore_comparison(self.root,value,b,a)
        bad=json.dumps(value).replace('"schema_version":','"schema_version":"duplicate","schema_version":',1)
        with self.assertRaises(ValueError):restore_comparison(self.root,bad,a,b)

    def test_full_fallback_budgets_and_stale_source(self):
        a=self.save('a','abc');b=self.save('b','xyz')
        self.assertEqual(compare_artifacts(self.root,a,b)['after']['representation'],'full')
        for cap in (0,True,20):
            with self.assertRaises(ValueError):compare_artifacts(self.root,a,b,max_chars=cap)
        with self.assertRaises(ValueError):compare_artifacts(self.root,dict(a,unused='x'),b)
        with self.assertRaises(ValueError):compare_artifacts(self.root,dict(a,path='../outside'),b)
        (self.root/'a').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'stale'):compare_artifacts(self.root,a,b)

    def test_cli_is_self_contained_and_never_writes_guide(self):
        before='Known unchanged requirements.\n'*20+'Status: running\n'
        after=before.replace('running','cancelled')
        a=self.save('a',before);b=self.save('b',after)
        (self.root/'old.json').write_text(json.dumps(a));(self.root/'new.json').write_text(json.dumps(b))
        command=[sys.executable,str(Path(__file__).resolve().parents[1]/'scripts/artifact_context.py'),
                 '--root',str(self.root),'--before','old.json','--after','new.json']
        contents={p.name:p.read_bytes() for p in self.root.iterdir()}
        for extra in ([],['--full']):
            proc=subprocess.run(command+extra,capture_output=True,text=True,timeout=10)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertEqual(restore_comparison(self.root,proc.stdout,a,b),(before,after))
        self.assertEqual(contents,{p.name:p.read_bytes() for p in self.root.iterdir()})
        proc=subprocess.run(command+['--max-chars','2'],capture_output=True,text=True,timeout=10)
        self.assertEqual(proc.returncode,1)
        self.assertIn('never truncate',json.loads(proc.stdout)['error'])

    def test_restore_rejects_oversized_before_parse_or_text_encode(self):
        a=self.save('a','prefix\n'*50+'old');b=self.save('b','prefix\n'*50+'new')
        value=compare_artifacts(self.root,a,b)
        with patch('agent_runtime.artifact_context.LIMIT',32):
            with patch('agent_runtime.artifact_context._json',side_effect=AssertionError('must not parse')):
                for raw in (' '*33,b' '*129,b' '*33):
                    with self.assertRaises(ValueError):restore_comparison(self.root,raw,a,b)
            # The pre-existing object also rejects text before allocating UTF-8.
            with self.assertRaisesRegex(ValueError,'character bound'):
                restore_comparison(self.root,value,a,b)
