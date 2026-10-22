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
    def test_write_scope_bounds_defaults_and_exclusions(self):
        from agent_runtime.dispatch_context import task_write_scope
        self.assertEqual(task_write_scope('FIG8'),['agent_doc/task/task_details/FIG8.md','.agent-runs/FIG8/'])
        self.assertEqual(task_write_scope('FIG8','run-1'),['agent_doc/task/task_details/FIG8.md','.agent-runs/run-1/'])
        self.assertEqual(prepare_dispatch(self.root,self.request)['write_scope'],['agent_doc/task/task_details/FIG8.md','.agent-runs/FIG8/'])
        r=copy.deepcopy(self.request);r['write_scope']=[]
        self.assertEqual(prepare_dispatch(self.root,r)['write_scope'],[])
        r=copy.deepcopy(self.request);r['write_scope']=['agent_doc/task/task_details/FIG8.md','agent_doc/results/fig8-run/']
        plan=prepare_dispatch(self.root,r)
        self.assertEqual(plan['write_scope'],r['write_scope'])
        self.assertEqual(json.loads(plan['input_text'])['write_scope'],r['write_scope'])
        for bad in (['/abs'],['../outside'],['agent_doc/guide/GUIDE.md'],['doc/guide/GUIDE.md'],
                    ['agent_doc/task/TASK.md'],['TASK.md'],['a\x00b'],[''],['x']*33):
            b=copy.deepcopy(self.request);b['write_scope']=bad
            with self.assertRaises(ValueError):prepare_dispatch(self.root,b)
    def test_scope_ancestors_cannot_include_reserved_outputs(self):
        for scope in ('.', 'agent_doc', 'agent_doc/task', 'doc'):
            for inherit in (False, True):
                with self.subTest(scope=scope, inherit=inherit):
                    request=copy.deepcopy(self.request);request['write_scope']=[scope]
                    with self.assertRaises(ValueError):
                        prepare_dispatch(self.root,request,force_inherit=inherit)

    def test_scope_aliases_cannot_target_reserved_outputs(self):
        task=self.root/'agent_doc/task/TASK.md';task.parent.mkdir();task.write_text('fixture task index')
        try:
            (self.root/'guide-alias').symlink_to('agent_doc/guide',target_is_directory=True)
            (self.root/'index-alias').symlink_to('agent_doc/task/TASK.md')
            (self.root/'task-alias').symlink_to('agent_doc/task',target_is_directory=True)
        except (OSError,NotImplementedError) as exc:
            self.skipTest('native symlinks unavailable: '+str(exc))
        for scope in ('guide-alias', 'guide-alias/GUIDE.md', 'guide-alias/future.md',
                      'index-alias', 'task-alias', 'task-alias/TASK.md'):
            for inherit in (False,True):
                with self.subTest(scope=scope,inherit=inherit):
                    request=copy.deepcopy(self.request);request['write_scope']=[scope]
                    with self.assertRaises(ValueError):
                        prepare_dispatch(self.root,request,force_inherit=inherit)
        self.assertEqual(task.read_text(),'fixture task index')
        self.assertEqual((self.root/'agent_doc/guide/GUIDE.md').read_text(),
                         'human directive: keep cancellation')

    def test_allowed_internal_alias_keeps_plan_and_native_settings(self):
        (self.root/'outputs').mkdir()
        try:
            (self.root/'output-alias').symlink_to('outputs',target_is_directory=True)
            (self.root/'scope-loop').symlink_to('scope-loop')
        except (OSError,NotImplementedError) as exc:
            self.skipTest('native symlinks unavailable: '+str(exc))
        request=copy.deepcopy(self.request);request['write_scope']=['output-alias/future.txt']
        plan=prepare_dispatch(self.root,request)
        self.assertEqual(plan['write_scope'],request['write_scope'])
        self.assertEqual(json.loads(plan['input_text'])['write_scope'],request['write_scope'])
        self.assertEqual(plan['params'],prepare_dispatch(self.root,self.request)['params'])
        request['write_scope']=['scope-loop/new.txt']
        with self.assertRaises(ValueError):prepare_dispatch(self.root,request)

    def test_cli_rejects_guide_alias_without_writes(self):
        try:
            (self.root/'guide-alias').symlink_to('agent_doc/guide',target_is_directory=True)
        except (OSError,NotImplementedError) as exc:
            self.skipTest('native symlinks unavailable: '+str(exc))
        request=copy.deepcopy(self.request);request['write_scope']=['guide-alias/GUIDE.md']
        p=self.root/'request.json';p.write_text(json.dumps(request),encoding='utf-8')
        guide=self.root/'agent_doc/guide/GUIDE.md';before=guide.read_bytes()
        cli=Path(__file__).resolve().parents[1]/'scripts/dispatch_context.py'
        result=subprocess.run([sys.executable,str(cli),'--root',str(self.root),'--request',p.name],
                              capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,1,result.stdout+result.stderr)
        self.assertIn('error',json.loads(result.stdout))
        self.assertEqual(before,guide.read_bytes())

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
