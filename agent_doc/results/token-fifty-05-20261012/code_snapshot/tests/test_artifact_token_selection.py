"""Whole-packet objective, complete content and unchanged legacy behavior."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from agent_runtime.artifact_context import compare_artifacts,restore_comparison,_json_text
from scripts.artifact_context import main

class ArtifactTokenSelectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()
        self.old='pending independent review; tokens\n'+''.join(f'old-{i:03}\n'+('a'*40)+'\n' for i in range(64))
        self.new=self.old.replace('old-','new-')
        self.a=self.save('a',self.old);self.b=self.save('b',self.new)
    def save(self,n,s):
        raw=s.encode();(self.root/n).write_bytes(raw)
        return {'path':n,'sha256':hashlib.sha256(raw).hexdigest()}
    def packet(self,**kw):return compare_artifacts(self.root,self.a,self.b,**kw)
    def test_whole_packet_can_prefer_longer_full_and_preserves_text(self):
        seen=[]
        def counter(wire):
            p=json.loads(wire);seen.append(p)
            self.assertEqual(p['before'],{'ref':self.a,'text':self.old})
            self.assertEqual(p['after']['ref'],self.b)
            self.assertEqual(p['project_root'],str(self.root))
            self.assertEqual(restore_comparison(self.root,p,self.a,self.b),(self.old,self.new))
            return 0 if p['after']['representation']=='full' else 1
        legacy=self.packet(multi_edit=True);value=self.packet(multi_edit=True,token_counter=counter)
        self.assertEqual(legacy['after']['representation'],'edits')
        self.assertEqual(value['after']['representation'],'full')
        self.assertGreater(len(_json_text(value)),len(_json_text(legacy)))
        self.assertEqual([p['after']['representation'] for p in seen],['full','splice','edits'])
    def test_none_keeps_legacy_all_flags(self):
        for full in (False,True):
            for multi in (False,True):
                for reuse in (False,True):
                    kw=dict(full=full,multi_edit=multi,reuse_identical=reuse)
                    self.assertEqual(self.packet(**kw),self.packet(**kw,token_counter=None))
    def test_force_full_ignores_counter_and_optional_flags(self):
        def fail(_):raise AssertionError('counter called under full override')
        self.assertEqual(self.packet(full=True),self.packet(full=True,multi_edit=True,reuse_identical=True,token_counter=fail))
    def test_stable_tie_and_zero_are_valid(self):
        self.assertEqual(self.packet(multi_edit=True,token_counter=lambda _:0)['after']['representation'],'full')
    def test_invalid_counter_and_counts_refuse(self):
        for c in (0,'encoding',{},False):
            with self.assertRaisesRegex(ValueError,'callable'):self.packet(token_counter=c)
        for count in (-1,True,False,1.2,'1',None,float('nan')):
            with self.assertRaisesRegex(ValueError,'nonnegative integer'):self.packet(token_counter=lambda _,v=count:v)
    def test_counter_failure_propagates_no_fallback(self):
        def broken(_):raise RuntimeError('tokenizer failed')
        with self.assertRaisesRegex(RuntimeError,'tokenizer failed'):self.packet(token_counter=broken)
    def test_only_budget_fitting_complete_candidates_counted(self):
        legacy=self.packet(multi_edit=True);cap=len(_json_text(legacy));seen=[]
        def counter(w):seen.append(w);return 0
        p=self.packet(multi_edit=True,max_chars=cap,token_counter=counter)
        self.assertEqual(p,legacy);self.assertEqual(len(seen),1)
        self.assertLessEqual(len(seen[0]),cap)
        with self.assertRaisesRegex(ValueError,'budget'):self.packet(max_chars=1,token_counter=counter)
        self.assertEqual(len(seen),1)
    def test_flags_control_eligible_codecs(self):
        seen=[]
        self.packet(token_counter=lambda w:seen.append(json.loads(w)['after']['representation']) or 0)
        self.assertEqual(seen,['full','splice'])
        self.b=self.save('b',self.old);seen.clear()
        p=self.packet(reuse_identical=True,token_counter=lambda w:seen.append(json.loads(w)['after']['representation']) or (0 if 'identical' in w else 1))
        self.assertEqual(seen,['full','splice','identical']);self.assertEqual(p['after']['representation'],'identical')
        self.assertEqual(restore_comparison(self.root,p,self.a,self.b),(self.old,self.old))
    def test_stale_source_refuses_before_counter(self):
        (self.root/'b').write_text('changed')
        with self.assertRaisesRegex(ValueError,'stale'):self.packet(token_counter=lambda _:self.fail('counted stale'))
    def test_cli_explicit_encoding_uses_factory_default_does_not(self):
        args=['--root',str(self.root),'--before','before.json','--after','after.json','--multi-edit']
        (self.root/'before.json').write_text(json.dumps(self.a));(self.root/'after.json').write_text(json.dumps(self.b))
        with patch('builtins.print') as printed,patch('agent_runtime.handoff_basis.make_token_counter') as factory:
            self.assertEqual(main(args),0);factory.assert_not_called()
            self.assertEqual(json.loads(printed.call_args.args[0])['after']['representation'],'edits')
            factory.return_value=lambda w:0 if json.loads(w)['after']['representation']=='full' else 1
            self.assertEqual(main(args+['--encoding','explicit-test']),0);factory.assert_called_once_with('explicit-test')
            self.assertEqual(json.loads(printed.call_args.args[0])['after']['representation'],'full')
    def test_cli_unknown_encoding_is_error(self):
        (self.root/'before.json').write_text(json.dumps(self.a));(self.root/'after.json').write_text(json.dumps(self.b))
        with patch('builtins.print'),patch('agent_runtime.handoff_basis.make_token_counter',side_effect=ValueError('unknown encoding')):
            self.assertEqual(main(['--root',str(self.root),'--before','before.json','--after','after.json','--encoding','unknown']),1)

if __name__=='__main__':unittest.main()
