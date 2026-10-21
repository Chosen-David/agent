import json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from agent_runtime.external_json import ExternalJSONError
from scripts.token_optimizer import INTERVAL,advance_due,atomic,exclusive,quota_admission,tick

def write_registry(root,roles=()):
    (root/'config').mkdir(exist_ok=True)
    (root/'config/role_registry.json').write_text(
        json.dumps({'schema_version':1,'roles':list(roles)}),encoding='utf-8')

class OptimizerTests(unittest.TestCase):
    def test_cadence_skips_catchup_and_backward_time(self):
        self.assertEqual(advance_due(100,100),3700)
        self.assertEqual(advance_due(100,10000),10900)
        self.assertEqual(advance_due(100,50),3700)
        for value in (True,float('nan'),float('inf'),-1):
            with self.assertRaises(ValueError):advance_due(value,100)
    def test_quota_fail_closed_all_windows_and_spend(self):
        def q(used):return {'ordinaryUsageAllowed':True,'rateLimits':{'primary':{'usedPercent':used}}}
        self.assertTrue(quota_admission(q(2))['admitted'])
        for value in (90,99,True,float('nan'),-1):self.assertFalse(quota_admission(q(value))['admitted'])
        self.assertFalse(quota_admission({})['admitted'])
        self.assertFalse(quota_admission({'ordinaryUsageAllowed':True,'rateLimits':{}})['admitted'])
        self.assertFalse(quota_admission({'ordinaryUsageAllowed':True,'rateLimitsByLimitId':{'a':{'primary':{'usedPercent':1}},'b':{'secondary':{'usedPercent':95}}}})['admitted'])
        self.assertFalse(quota_admission({'ordinaryUsageAllowed':True,'rateLimits':{'spendControlReached':True,'primary':{'usedPercent':1}}})['admitted'])
    def fixture(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        root=Path(temp.name).resolve();state=root/'.agent-runs/hourly';exe=root/'codex.exe';exe.write_bytes(b'not invoked')
        return root,state,exe
    def registry(self,root,value=...):
        (root/'config').mkdir(exist_ok=True)
        role={'id':'code-reading','kind':'code_reading','skill':'skill','workflow':'workflow','execution':'execution'}
        value={'schema_version':1,'roles':[role]} if value is ... else value
        (root/'config/role_registry.json').write_text(json.dumps(value),encoding='utf-8')
    def test_fresh_not_due_never_invokes_backend(self):
        root,state,exe=self.fixture()
        with patch('scripts.token_optimizer.synchronize') as sync,patch('scripts.token_optimizer.run_worker') as run:
            self.assertEqual(tick(root,state,exe,now=100)['status'],'not-due');sync.assert_not_called();run.assert_not_called()
            self.assertEqual(json.loads((state/'state.json').read_bytes())['next_due'],3700)
    def test_one_due_tick_persisted_before_model_and_no_second_tick(self):
        root,state,exe=self.fixture();self.registry(root);atomic(state/'state.json',{'project_root':str(root),'interval_seconds':INTERVAL,'next_due':100})
        def worker(*args,**kwargs):
            self.assertEqual(json.loads((state/'state.json').read_bytes())['next_due'],10900)
            return {'status':'quota-blocked','model_requests':0}
        with patch('scripts.token_optimizer.synchronize',return_value='fixed'),patch('scripts.token_optimizer.run_worker',side_effect=worker) as run,patch('scripts.token_optimizer.command',return_value=''):
            self.assertEqual(tick(root,state,exe,now=10000)['status'],'quota-blocked')
            self.assertEqual(tick(root,state,exe,now=10000)['status'],'not-due');self.assertEqual(run.call_count,1)
    def test_preflight_failure_preserves_slot_and_zero_model(self):
        root,state,exe=self.fixture();self.registry(root);atomic(state/'state.json',{'project_root':str(root),'interval_seconds':INTERVAL,'next_due':100})
        with patch('scripts.token_optimizer.synchronize',side_effect=RuntimeError('dirty tree preserved')),patch('scripts.token_optimizer.run_worker') as run:
            self.assertEqual(tick(root,state,exe,now=100)['status'],'host-blocked');run.assert_not_called()
            self.assertEqual(json.loads((state/'state.json').read_bytes())['next_due'],3700)
    def test_exclusion_lock_actual_file(self):
        root,state,exe=self.fixture()
        with exclusive(state/'worker.lock') as first:
            self.assertTrue(first)
            with exclusive(state/'worker.lock') as second:self.assertFalse(second)
        with exclusive(state/'worker.lock') as again:self.assertTrue(again)
    def test_probe_does_not_consume_due_tick(self):
        root,state,exe=self.fixture();self.registry(root);saved={'project_root':str(root),'interval_seconds':INTERVAL,'next_due':100}
        atomic(state/'state.json',saved)
        with patch('scripts.token_optimizer.synchronize'),patch('scripts.token_optimizer.run_worker',return_value={'status':'probe-only','model_requests':0}) as run:
            self.assertEqual(tick(root,state,exe,now=100,probe_only=True)['status'],'probe-only')
            self.assertEqual(json.loads((state/'state.json').read_bytes()),saved)
            self.assertTrue(run.call_args.kwargs['probe_only'])
    def test_foreign_state_and_outside_paths_rejected(self):
        root,state,exe=self.fixture()
        with self.assertRaises(ValueError):tick(root,root/'public-state',exe,now=100)
        atomic(state/'state.json',{'project_root':'foreign','interval_seconds':INTERVAL,'next_due':100})
        with self.assertRaises(ValueError):tick(root,state,exe,now=100)

    def test_bad_registry_is_pure_before_due_tick(self):
        bad_values=([],None,{'schema_version':1,'roles':[None]},
                    {'schema_version':1,'roles':[{'kind':'x'}]},
                    {'schema_version':1,'roles':[{'id':'../escape','kind':'x','skill':'x','workflow':'x','execution':'x'}]},
                    {'schema_version':1,'roles':[{'id':'same','kind':'x','skill':'x','workflow':'x','execution':'x'}]*2})
        for value in bad_values:
            with self.subTest(value=value):
                root,state,exe=self.fixture();self.registry(root,value)
                saved={'project_root':str(root),'interval_seconds':INTERVAL,'next_due':100}
                atomic(state/'state.json',saved);before=(state/'state.json').read_bytes()
                with patch('scripts.token_optimizer.synchronize') as sync,patch('scripts.token_optimizer.run_worker') as worker:
                    with self.assertRaises(ValueError):tick(root,state,exe,now=100)
                self.assertEqual((state/'state.json').read_bytes(),before)
                self.assertEqual(list(state.glob('*-tick')),[])
                sync.assert_not_called();worker.assert_not_called()

    @unittest.skipUnless(hasattr(os,'mkfifo'),'requires POSIX special files')
    def test_special_registry_is_pure_before_due_tick(self):
        for kind in ('fifo','directory','symlink'):
            with self.subTest(kind=kind):
                root,state,exe=self.fixture();(root/'config').mkdir();target=root/'config/role_registry.json'
                if kind=='fifo':os.mkfifo(target)
                elif kind=='directory':target.mkdir()
                else:
                    elsewhere=root/'elsewhere.json';elsewhere.write_text('{"schema_version":1,"roles":[]}',encoding='utf-8')
                    target.symlink_to(elsewhere)
                saved={'project_root':str(root),'interval_seconds':INTERVAL,'next_due':100}
                atomic(state/'state.json',saved);before=(state/'state.json').read_bytes()
                with patch('scripts.token_optimizer.run_worker') as worker:
                    with self.assertRaises(ExternalJSONError):tick(root,state,exe,now=100)
                self.assertEqual((state/'state.json').read_bytes(),before)
                self.assertEqual(list(state.glob('*-tick')),[]);worker.assert_not_called()

    def test_registry_parser_boundaries_and_cli_no_traceback(self):
        from scripts.token_optimizer import worker_config
        cases=('1e400','{"schema_version":1,"roles":[],"schema_version":1}',
               '{"schema_version":1,"roles":'+'['*257+'0'+']'*257+'}')
        for raw in cases:
            with self.subTest(raw=raw[:30]):
                root,state,exe=self.fixture();(root/'config').mkdir();(root/'config/role_registry.json').write_text(raw,encoding='utf-8')
                with self.assertRaises((ExternalJSONError,ValueError)):worker_config(root)
        root,state,exe=self.fixture();self.registry(root,[])
        saved={'project_root':str(root),'interval_seconds':INTERVAL,'next_due':100};atomic(state/'state.json',saved)
        proc=subprocess.run([sys.executable,'scripts/token_optimizer.py','--root',str(root),
            '--state-dir',str(state),'--codex',str(exe)],cwd=Path(__file__).resolve().parents[1],
            capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(proc.returncode,2);self.assertNotIn('Traceback',proc.stderr)
        self.assertEqual((state/'state.json').read_bytes(),(json.dumps(saved,ensure_ascii=False,indent=2)+'\n').encode())
        self.assertEqual(list(state.glob('*-tick')),[])

class ParentUsageTests(unittest.TestCase):
    """Synthetic native-shaped transport only; never starts an app-server."""
    def usage(self,n=100,**changes):
        counters={'inputTokens':n,'cachedInputTokens':0,'outputTokens':0,
                  'reasoningOutputTokens':0,'totalTokens':n}
        value={'last':dict(counters),'total':dict(counters)}
        value.update(changes)
        return {'method':'thread/tokenUsage/updated','params':{
            'threadId':'thread','turnId':'turn','tokenUsage':value}}

    def terminal(self,status='completed',**changes):
        return {'method':'turn/completed','params':{'threadId':'thread',
                'turn':{'id':'turn','status':status,**changes}}}

    def replay(self,events,*,budget=1000):
        import queue
        from scripts.token_optimizer import observe_parent_turn
        with tempfile.TemporaryDirectory() as tmp:
            now=[0.0];sent=[]
            class Queue:
                def get(self,timeout):
                    now[0]+=timeout
                    raise queue.Empty
            with patch('scripts.token_optimizer.time.monotonic',side_effect=lambda:now[0]):
                result=observe_parent_turn(Queue(),list(events),'thread','turn',Path(tmp),
                    lambda method,params:sent.append((method,params)),timeout_seconds=3,max_observed_tokens=budget)
            path=Path(tmp)/'observed-usage.json'
            saved=json.loads(path.read_bytes()) if path.exists() else None
        self.assertFalse(result['usage_complete'])
        self.assertFalse(result['counts_as_token_success'])
        self.assertIsNone(result['model_requests'])
        return result,saved,sent

    def test_missing_completion_and_timeout_are_unknown(self):
        for events in ([self.terminal()],[]):
            with self.subTest(events=events):
                result,saved,sent=self.replay(events)
                self.assertIsNone(result['observed_parent_total_tokens'])
                self.assertEqual(result['usage_status'],'missing');self.assertIsNone(saved)
                self.assertEqual(len(sent),0 if events else 1)

    def test_observed_zero_normal_and_equal_repeated_snapshots(self):
        for n in (0,123):
            with self.subTest(n=n):
                event=self.usage(n)
                event['params']['tokenUsage']['total']['cacheWriteInputTokens']=7
                result,saved,sent=self.replay([event,event,self.terminal()])
                self.assertEqual(result['observed_parent_total_tokens'],n)
                self.assertEqual(result['usage_status'],'observed');self.assertEqual(sent,[])
                self.assertEqual(saved['tokenUsage'],event['params']['tokenUsage'])
                self.assertFalse(saved['usage_complete'])

    def test_foreign_identity_cannot_supply_usage_or_end_turn(self):
        import copy
        thread=copy.deepcopy(self.usage());thread['params']['threadId']='foreign'
        turn=copy.deepcopy(self.usage());turn['params']['turnId']='foreign'
        missing=copy.deepcopy(self.usage());del missing['params']['turnId']
        terminal=self.terminal();terminal['params']['turn']['id']='foreign'
        result,_,_=self.replay([thread,turn,missing,terminal,self.terminal()])
        self.assertEqual(result['usage_status'],'missing')
        self.assertIsNone(result['observed_parent_total_tokens'])

    def test_partial_fields_and_bad_transport_remain_unknown(self):
        partial=self.usage();del partial['params']['tokenUsage']['total']['outputTokens']
        for bad in (partial,[],{'local_error':'damaged JSON transport'},
                    {'params':[]},self.usage(last=None),self.usage(total={'totalTokens':2})):
            with self.subTest(bad=bad):
                result,saved,sent=self.replay([bad,self.terminal()])
                self.assertEqual(result['usage_status'],'invalid')
                self.assertIsNone(result['observed_parent_total_tokens']);self.assertIsNone(saved)
                self.assertEqual(sent,[('turn/interrupt',{'threadId':'thread','turnId':'turn'})])

    def test_invalid_counters_preserve_last_valid_snapshot_without_final_total(self):
        for field,value in (('totalTokens',True),('totalTokens',101),('inputTokens',-1),
                            ('cachedInputTokens',101),('reasoningOutputTokens',1),('outputTokens',None)):
            with self.subTest(field=field,value=value):
                bad=self.usage();bad['params']['tokenUsage']['total'][field]=value
                result,saved,_=self.replay([self.usage(50),bad,self.terminal()])
                self.assertEqual(result['usage_status'],'invalid')
                self.assertIsNone(result['observed_parent_total_tokens'])
                self.assertEqual(result['last_observed_parent_total_tokens'],50)
                self.assertEqual(saved['total_tokens'],50)

    def test_regression_and_last_larger_than_total_rejected(self):
        for events in ([self.usage(100),self.usage(99)],
                       [self.usage(100,last=self.usage(101)['params']['tokenUsage']['last'])]):
            result,_,_=self.replay(events+[self.terminal()])
            self.assertEqual(result['usage_status'],'invalid')
        first=self.usage();first['params']['tokenUsage']['total']['cachedInputTokens']=10
        result,_,_=self.replay([first,self.usage(),self.terminal()])
        self.assertEqual(result['usage_status'],'invalid')

    def test_failure_retry_interrupt_and_timeout_are_partial(self):
        error={'method':'error','params':{'threadId':'thread','turnId':'turn','willRetry':True}}
        for tail in ([self.terminal('failed')],[self.terminal('interrupted')],[],
                     [error,self.usage(200),self.terminal()],
                     [self.terminal(error={'message':'failure'})]):
            with self.subTest(tail=tail):
                result,_,_=self.replay([self.usage()]+tail)
                self.assertEqual(result['usage_status'],'partial')
                self.assertIn(result['observed_parent_total_tokens'],(100,200))
        result,_,_=self.replay([error,self.terminal('failed')])
        self.assertEqual(result['usage_status'],'missing')
        self.assertIsNone(result['observed_parent_total_tokens'])

    def test_budget_interrupt_retains_partial_usage(self):
        result,_,sent=self.replay([self.usage(101),self.terminal()],budget=100)
        self.assertEqual(result['status'],'budget-interrupted')
        self.assertEqual(result['usage_status'],'partial')
        self.assertEqual(result['observed_parent_total_tokens'],101)
        self.assertEqual(len(sent),1)

    def test_worker_wires_monitor_without_launching_backend(self):
        import io
        from types import SimpleNamespace
        from unittest.mock import Mock
        from scripts.token_optimizer import run_worker
        for tail in ([json.dumps(self.terminal())],['not JSON']):
            with self.subTest(tail=tail),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);write_registry(root)
                replies=[{'id':1,'result':{}},{'id':2,'result':{'ordinaryUsageAllowed':True,
                    'rateLimits':{'primary':{'usedPercent':0}}}},
                    {'id':3,'result':{'thread':{'id':'thread'},'model':'fake','reasoningEffort':'high'}},
                    {'id':4,'result':{'turn':{'id':'turn'}}}]
                proc=Mock(stdin=io.StringIO(),stdout=iter([json.dumps(x)+'\n' for x in replies]+[x+'\n' for x in tail]))
                proc.poll.return_value=0
                with (patch('scripts.token_optimizer.os',SimpleNamespace(name='nt',environ={})),
                     patch('scripts.token_optimizer.atomic'),
                     patch('scripts.token_optimizer.subprocess.CREATE_NO_WINDOW',0,create=True),
                     patch('scripts.token_optimizer.subprocess.Popen',return_value=proc),
                     patch('scripts.token_optimizer.subprocess.run') as external):
                    result=run_worker(root,root/'fake-codex',root)
                external.assert_not_called()
                self.assertIsNone(result['observed_parent_total_tokens'])
                self.assertEqual(result['usage_status'],'missing' if tail[0].startswith('{') else 'invalid')

    def test_tick_persists_unknown_without_zero_coercion(self):
        result,_,_=self.replay([self.terminal()])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();state=root/'.agent-runs/synthetic-test';exe=root/'fake';exe.write_bytes(b'not invoked')
            write_registry(root)
            atomic(state/'state.json',{'project_root':str(root),'interval_seconds':INTERVAL,'next_due':100})
            with patch('scripts.token_optimizer.synchronize',return_value='base'),patch('scripts.token_optimizer.run_worker',return_value=result),patch('scripts.token_optimizer.command',return_value=''):
                saved=tick(root,state,exe,now=100)
            persisted=json.loads((state/'state.json').read_bytes())['last_result']
            receipt=json.loads(next(state.glob('*-tick/receipt.json')).read_bytes())
            for value in (saved,persisted,receipt):
                self.assertIsNone(value['observed_parent_total_tokens'])
                self.assertIsNone(value['model_requests'])
                self.assertFalse(value['usage_complete'])
                self.assertFalse(value['counts_as_token_success'])

class HourlyRepairTests(unittest.TestCase):
    def test_unchanged_remote_is_not_new_publication(self):
        from scripts.token_optimizer import publication_state
        self.assertTrue(publication_state('a','a','a',False)['current_snapshot_verified'])
        self.assertFalse(publication_state('a','a','a',False)['new_remote_snapshot_verified'])
        self.assertTrue(publication_state('a','b','b',False)['new_remote_snapshot_verified'])
        self.assertIn('unknown',publication_state('a','b','b',False)['publication_attribution'])
        for args in (('a','b','c',False),('a','b','b',True)):
            self.assertFalse(publication_state(*args)['new_remote_snapshot_verified'])

    def test_resumed_usage_budget_is_delta_not_old_total(self):
        import queue
        from scripts.token_optimizer import observe_parent_turn
        p=ParentUsageTests()
        with tempfile.TemporaryDirectory() as tmp:
            sent=[]
            result=observe_parent_turn(queue.Queue(),[p.usage(100100),p.terminal()],
                'thread','turn',Path(tmp),lambda *args:sent.append(args),timeout_seconds=2,
                max_observed_tokens=1000,initial_total_tokens=100000)
            self.assertEqual(result['observed_parent_total_tokens'],100)
            self.assertEqual(result['thread_total_tokens'],100100)
            self.assertEqual(sent,[])
            result=observe_parent_turn(queue.Queue(),[p.usage(99999)],
                'thread','turn',Path(tmp),lambda *args:sent.append(args),timeout_seconds=2,
                max_observed_tokens=1000,initial_total_tokens=100000)
            self.assertEqual(result['usage_status'],'invalid')

    def test_failure_latch_advances_clock_without_model_or_sync(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();state=root/'.agent-runs/repair';exe=root/'fake';exe.write_bytes(b'not invoked')
            write_registry(root)
            atomic(state/'state.json',{'project_root':str(root),'interval_seconds':INTERVAL,
                   'next_due':100,'failure_latch':'usage-invalid'})
            with patch('scripts.token_optimizer.run_worker') as worker,patch('scripts.token_optimizer.synchronize') as sync:
                result=tick(root,state,exe,now=100)
                self.assertEqual(result['status'],'failure-latched');self.assertEqual(result['model_requests'],0)
                worker.assert_not_called();sync.assert_not_called()
                self.assertEqual(json.loads((state/'state.json').read_bytes())['next_due'],3700)

    def test_bounded_profile_preserves_publication_apps(self):
        from scripts.token_optimizer import worker_config,TOOL_OUTPUT_TOKENS
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);write_registry(root)
            config=worker_config(root)
            self.assertEqual(config['tool_output_token_limit'],TOOL_OUTPUT_TOKENS)
            self.assertTrue(config['features.apps'])

    def test_snapshot_detects_actual_edited_bytes(self):
        from scripts.token_optimizer import work_snapshot
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for args in (('init','-q'),('config','user.email','fixture@local'),('config','user.name','fixture')):
                subprocess.run(['git',*args],cwd=root,check=True,capture_output=True)
            (root/'x.py').write_text('original')
            subprocess.run(['git','add','x.py'],cwd=root,check=True)
            subprocess.run(['git','commit','-qm','fixture'],cwd=root,check=True)
            (root/'x.py').write_text('owned')
            (root/'中文 name.py').write_text('Unicode owned')
            (root/' leading space.py').write_text('space owned')
            first=work_snapshot(root)
            self.assertEqual(first,work_snapshot(root))
            (root/' leading space.py').write_text('space concurrent')
            self.assertNotEqual(first,work_snapshot(root))
            (root/' leading space.py').write_text('space owned')
            (root/'x.py').write_text('concurrent')
            self.assertNotEqual(first,work_snapshot(root))
            (root/'x.py').write_text('owned')
            (root/'中文 name.py').write_text('Unicode concurrent')
            self.assertNotEqual(first,work_snapshot(root))
            (root/'中文 name.py').write_text('Unicode owned')
            subprocess.run(['git','add','x.py'],cwd=root,check=True)
            first=work_snapshot(root)
            oldblob=subprocess.check_output(['git','rev-parse','HEAD:x.py'],cwd=root).decode().strip()
            subprocess.run(['git','update-index','--cacheinfo','100644',oldblob,'x.py'],cwd=root,check=True)
            self.assertNotEqual(first['index_sha256'],work_snapshot(root)['index_sha256'])

    def test_exception_after_worker_attempt_latches_and_keeps_unknown_usage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();state=root/'.agent-runs/repair';exe=root/'fake';exe.write_bytes(b'not invoked')
            write_registry(root)
            atomic(state/'state.json',{'project_root':str(root),'interval_seconds':INTERVAL,'next_due':100})
            with patch('scripts.token_optimizer.synchronize',return_value='base'),patch('scripts.token_optimizer.run_worker',side_effect=TimeoutError('RPC')) as worker:
                first=tick(root,state,exe,now=100)
                second=tick(root,state,exe,now=3700)
                self.assertIsNone(first['model_requests'])
                self.assertEqual(second['status'],'failure-latched');self.assertEqual(worker.call_count,1)

    def test_checkpoint_reused_and_changed_owned_bytes_blocked(self):
        from scripts.token_optimizer import PROFILE_VERSION
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();state=root/'.agent-runs/repair';exe=root/'fake';exe.write_bytes(b'not invoked')
            write_registry(root)
            snapshot={'head':'a'*40,'status':' M owned.py','files':{'owned.py':'1'*64},'index_sha256':'2'*64}
            checkpoint={'thread_id':'persisted','thread_total_tokens':100000,'work_snapshot':snapshot,
                        'profile_version':PROFILE_VERSION,'stagnant_ticks':0}
            saved={'project_root':str(root),'interval_seconds':INTERVAL,'next_due':100,'checkpoint':checkpoint}
            atomic(state/'state.json',saved)
            result={'status':'budget-interrupted','thread_id':'persisted','thread_total_tokens':180000,
                    'observed_parent_total_tokens':80000,'counts_as_token_success':False}
            def command_result(root,*args):
                return ' M owned.py' if args[1:]==('status','--porcelain') else 'a'*40 if args[1]=='rev-parse' else ''
            with patch('scripts.token_optimizer.work_snapshot',return_value=snapshot),patch('scripts.token_optimizer.command',side_effect=command_result),patch('scripts.token_optimizer.run_worker',return_value=result) as worker,patch('scripts.token_optimizer.synchronize') as sync:
                tick(root,state,exe,now=100)
                self.assertEqual(worker.call_args.kwargs['checkpoint'],checkpoint);sync.assert_not_called()
                self.assertEqual(json.loads((state/'state.json').read_bytes())['checkpoint']['thread_total_tokens'],180000)
            with patch('scripts.token_optimizer.work_snapshot',return_value={**snapshot,'index_sha256':'concurrent'}),patch('scripts.token_optimizer.run_worker') as worker:
                result=tick(root,state,exe,now=3700)
                self.assertEqual(result['status'],'host-blocked');self.assertEqual(result['model_requests'],0)
                worker.assert_not_called()
                self.assertIn('failure_latch',json.loads((state/'state.json').read_bytes()))
