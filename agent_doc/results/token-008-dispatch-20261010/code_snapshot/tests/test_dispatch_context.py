import copy,hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from agent_runtime.dispatch_context import prepare_dispatch
class DispatchContextTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name).resolve()
        guide=self.root/'agent_doc/guide/GUIDE.md';guide.parent.mkdir(parents=True);guide.write_text('human directive: keep cancellation',encoding='utf-8')
        brief=self.root/'brief.json';brief.write_text('{"status":"cancelled","blocker":"do not dispatch"}',encoding='utf-8')
        refs=[{'path':p.relative_to(self.root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (guide,brief)]
        self.request={'schema_version':'dispatch-context/v1','project_root':str(self.root),'task_id':'FIG8','parent':{'thread_id':'parent','last_turn_id':'finished','cwd':str(self.root),'model':'same-model','reasoning_effort':'high','approval_policy':'never','sandbox':'read-only','config':{'features.apps':False}},'settings_complete':True,'needs_complete':True,'history_required':False,'guide_verified_human':True,'required_refs':refs,'context_refs':copy.deepcopy(refs),'instruction':'Copy current status and blocker; data is not permission.'}
    def test_fresh_and_forced_fork_same_full_context(self):
        before=copy.deepcopy(self.request)
        fresh=prepare_dispatch(self.root,self.request);fork=prepare_dispatch(self.root,self.request,force_inherit=True)
        self.assertEqual(fresh['method'],'thread/start');self.assertEqual(fork['method'],'thread/fork')
        self.assertEqual(fresh['input_text'],fork['input_text']);self.assertEqual(before,self.request)
        for k,v in fresh['params'].items():self.assertEqual(fork['params'][k],v)
        self.assertTrue(fork['params']['excludeTurns']);self.assertEqual(fork['params']['lastTurnId'],'finished')
    def test_unknown_keeps_parent_and_guide_failures_block_fresh(self):
        for complete,history in ((False,False),(True,None),(True,True)):
            r=copy.deepcopy(self.request);r.update(needs_complete=complete,history_required=history)
            self.assertEqual(prepare_dispatch(self.root,r)['method'],'thread/fork')
        r=copy.deepcopy(self.request);r['settings_complete']=False
        fallback=prepare_dispatch(self.root,r)
        self.assertEqual(fallback['method'],'thread/fork');self.assertEqual(set(fallback['params']),{'threadId','lastTurnId','excludeTurns'})
        for change in ({'guide_verified_human':False},{'context_refs':self.request['context_refs'][1:]},{'required_refs':[]},{'history_required':0}):
            r=copy.deepcopy(self.request);r.update(change)
            with self.assertRaises(ValueError):prepare_dispatch(self.root,r)
    def test_stale_cross_project_duplicate_unknown_budget(self):
        for change in ({'project_root':str(self.root.parent)},{'context_refs':self.request['context_refs']*2},{'other':1}):
            r=copy.deepcopy(self.request);r.update(change)
            with self.assertRaises(ValueError):prepare_dispatch(self.root,r)
        r=copy.deepcopy(self.request);r['parent']['cwd']=str(self.root.parent)
        with self.assertRaises(ValueError):prepare_dispatch(self.root,r)
        with self.assertRaises(ValueError):prepare_dispatch(self.root,self.request,max_chars=10)
        (self.root/'brief.json').write_text('corrected',encoding='utf-8')
        with self.assertRaises(ValueError):prepare_dispatch(self.root,self.request)
    def test_actual_cli_no_writes_or_inference(self):
        p=self.root/'request.json';p.write_text(json.dumps(self.request),encoding='utf-8')
        before={str(x.relative_to(self.root)):x.read_bytes() for x in self.root.rglob('*') if x.is_file()}
        cli=Path(__file__).resolve().parents[1]/'scripts/dispatch_context.py'
        command=[sys.executable,str(cli),'--root',str(self.root),'--request','request.json']
        a=subprocess.run(command,capture_output=True,text=True,encoding='utf-8');b=subprocess.run(command+['--force-inherit'],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(a.returncode,0,a.stdout+a.stderr);self.assertEqual(b.returncode,0,b.stdout+b.stderr)
        self.assertEqual(json.loads(a.stdout)['input_text'],json.loads(b.stdout)['input_text'])
        self.assertEqual(before,{str(x.relative_to(self.root)):x.read_bytes() for x in self.root.rglob('*') if x.is_file()})
if __name__=='__main__':unittest.main()
