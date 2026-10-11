import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from scripts.token_optimizer import INTERVAL,advance_due,atomic,exclusive,quota_admission,tick
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
    def test_fresh_not_due_never_invokes_backend(self):
        root,state,exe=self.fixture()
        with patch('scripts.token_optimizer.synchronize') as sync,patch('scripts.token_optimizer.run_worker') as run:
            self.assertEqual(tick(root,state,exe,now=100)['status'],'not-due');sync.assert_not_called();run.assert_not_called()
            self.assertEqual(json.loads((state/'state.json').read_bytes())['next_due'],3700)
    def test_one_due_tick_persisted_before_model_and_no_second_tick(self):
        root,state,exe=self.fixture();atomic(state/'state.json',{'project_root':str(root),'interval_seconds':INTERVAL,'next_due':100})
        def worker(*args,**kwargs):
            self.assertEqual(json.loads((state/'state.json').read_bytes())['next_due'],10900)
            return {'status':'quota-blocked','model_requests':0}
        with patch('scripts.token_optimizer.synchronize',return_value='fixed'),patch('scripts.token_optimizer.run_worker',side_effect=worker) as run,patch('scripts.token_optimizer.command',return_value=''):
            self.assertEqual(tick(root,state,exe,now=10000)['status'],'quota-blocked')
            self.assertEqual(tick(root,state,exe,now=10000)['status'],'not-due');self.assertEqual(run.call_count,1)
    def test_preflight_failure_preserves_slot_and_zero_model(self):
        root,state,exe=self.fixture();atomic(state/'state.json',{'project_root':str(root),'interval_seconds':INTERVAL,'next_due':100})
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
        root,state,exe=self.fixture();saved={'project_root':str(root),'interval_seconds':INTERVAL,'next_due':100}
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
