import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/research-assistant/skills/research-implement-optimize/scripts'
sys.path.insert(0, str(SCRIPTS))
import gpu_adapter as g
sys.path.pop(0)


def snapshot(processes=''):
    return {'observed_at': time.time(), 'gpu': {
        'devices': {'status': 'observed', 'csv': 'uuid,name,driver_version,utilization.gpu [%],memory.used [MiB],memory.total [MiB]\nGPU-a,A,1,0 %,0 MiB,8000 MiB\nGPU-b,B,1,0 %,0 MiB,8000 MiB\n'},
        'processes': {'status': 'observed', 'csv': 'gpu_uuid,pid,used_gpu_memory [MiB]\n' + processes}}}


def request(mode='accuracy'):
    return {'mode': mode, 'authorized_devices': ['GPU-a', 'GPU-b'] if mode == 'accuracy' else ['GPU-a'],
            'sample_ids': ['a','b','c','d','e'], 'seed': 7, 'batch_size': 4, 'min_free_mib': 1000,
            'max_utilization': 5, 'protocol_sha256': 'a'*64, 'warmup': 1, 'repeats': 3}


class MockRunner:
    def __init__(self):
        self.seeds = {}
        self.calls = []
        self.exclusive = True
    def authorize(self, r, devices): return True
    def capabilities(self): return {'ready': True, 'modes': ['accuracy', 'performance'], 'id': 'cpu-mock', 'protocol_sha256': 'a'*64}
    def verify_admission(self, r, uuids): return {"allowed": True, "source": "mock full visibility", "observed_at": time.time()}
    def known_pids(self): return []
    def owns_exclusive_allocation(self, uuids): return self.exclusive
    def evaluate(self, uuid, ids, seeds, batch):
        self.calls.append((uuid, list(ids)))
        if len(ids) > 1: raise g.BatchOOM()
        self.seeds.update(zip(ids,seeds))
        return [{'id': i, 'prediction': seed} for i,seed in zip(ids,seeds)]
    def synchronize(self, uuid): self.calls.append(('sync', uuid))
    def run_variant(self, uuid, variant, seed):
        self.calls.append(('run', variant))
        return seed
    def equivalent(self, a,b): return a == b


class AdapterTests(unittest.TestCase):
    def test_shard_coverage_and_busy_filter(self):
        p = g.plan(request(), snapshot())
        self.assertEqual(p['shards'], {'GPU-a':['a','c','e'], 'GPU-b':['b','d']})
        p = g.plan(request(), snapshot('GPU-a,123,5 MiB\n'))
        self.assertEqual(list(p['shards']), ['GPU-b'])
        self.assertEqual(p['reservation'], 'none')

    def test_stale_unknown_malformed_block(self):
        for s in [snapshot() | {'observed_at': 1}, snapshot() | {'observed_at': time.time()+100}, {'gpu':{}}]:
            self.assertEqual(g.plan(request(), s)['status'], 'blocked')
        for text in ['garbage\nGPU-a,A,1,N/A,0 MiB,8000 MiB', 'uuid\nMIG-a,A,1,0 %,0 MiB,8000 MiB']:
            s=snapshot();s['gpu']['devices']['csv']=text
            self.assertEqual(g.plan(request(), s)['status'], 'blocked')

    def test_invalid_request(self):
        for key,value in [('batch_size',True), ('sample_ids',['a','a']), ('authorized_devices',[]), ('protocol_sha256','missing')]:
            r=request();r[key]=value
            with self.assertRaises(ValueError): g.request(r)

    def test_lease_excludes_cooperators_and_releases_on_error(self):
        with tempfile.TemporaryDirectory() as d:
            with g.cooperative_lease(d,['GPU-a']):
                with self.assertRaises(g.Blocked):
                    with g.cooperative_lease(d,['GPU-a']): pass
                with g.cooperative_lease(d,['GPU-b']): pass
            with self.assertRaises(RuntimeError):
                with g.cooperative_lease(d,['GPU-a']): raise RuntimeError()
            with g.cooperative_lease(d,['GPU-a']): pass

    def test_mock_parallel_oom_completeness_seed_invariance(self):
        with tempfile.TemporaryDirectory() as d:
            a=MockRunner();x=g.run(request(),a,d,observe=snapshot)
            r=request();r['authorized_devices']=['GPU-a'];r['batch_size']=1
            b=MockRunner();y=g.run(r,b,d,observe=snapshot)
            self.assertEqual(x['output'],y['output'])
            self.assertEqual(a.seeds,b.seeds)
            self.assertTrue(x['events'])
            self.assertEqual(len(x['output']['rows']),5)

    def test_authorization_before_probe_and_revocation(self):
        runner=MockRunner()
        runner.authorize=lambda *a:False
        with tempfile.TemporaryDirectory() as d, self.assertRaises(g.Blocked):
            g.run(request(),runner,d,observe=lambda: self.fail('unauthorized probe'))
        runner=MockRunner(); decisions=iter([True,False]);runner.authorize=lambda *a:next(decisions)
        with tempfile.TemporaryDirectory() as d, self.assertRaises(g.Blocked):
            g.run(request(),runner,d,observe=snapshot)
        self.assertEqual(runner.calls,[])

    def test_external_process_race_after_planning(self):
        calls=[]
        def observe():
            calls.append(1)
            return snapshot('GPU-a,987,100 MiB\n') if len(calls)>1 else snapshot()
        runner=MockRunner()
        with tempfile.TemporaryDirectory() as d, self.assertRaises(g.Blocked):
            g.run(request(),runner,d,observe=observe)
        self.assertEqual(runner.calls,[])

    def test_performance_requires_scheduler_and_synchronizes(self):
        runner=MockRunner();runner.exclusive=False
        with tempfile.TemporaryDirectory() as d, self.assertRaises(g.Blocked):
            g.run(request('performance'),runner,d,observe=snapshot)
        self.assertEqual(runner.calls,[])
        runner.exclusive=True
        with tempfile.TemporaryDirectory() as d:
            result=g.run(request('performance'),runner,d,observe=snapshot)
        self.assertEqual(len(result['output']['steady_pairs_ns']),3)
        for index,item in enumerate(runner.calls):
            if item[0]=='run':
                self.assertEqual(runner.calls[index-1][0],'sync')
                self.assertEqual(runner.calls[index+1][0],'sync')

    def test_wrong_coverage_and_nonoom_failure_propagate(self):
        for fn,error in [(lambda *a:[], ValueError), (lambda *a: (_ for _ in ()).throw(RuntimeError()),RuntimeError)]:
            runner=MockRunner();runner.evaluate=fn
            with tempfile.TemporaryDirectory() as d,self.assertRaises(error):
                g.run(request(),runner,d,observe=snapshot)

    def test_scaffold_defaults_blocked_and_compiles(self):
        compile(g.SCAFFOLD,'generated.py','exec')
        scope={};exec(g.SCAFFOLD,scope)
        self.assertFalse(scope['ProjectAdapter']().capabilities()['ready'])
        self.assertFalse(scope['ProjectAdapter']().authorize({},[]))

    def test_empty_headerless_process_and_wrong_units_block(self):
        for key,text in [('processes',''), ('processes','GPU-a,987,5 MiB'),
                         ('devices', snapshot()['gpu']['devices']['csv'].replace('8000 MiB','8000 bytes'))]:
            s=snapshot();s['gpu'][key]['csv']=text
            self.assertEqual(g.plan(request(),s)['status'],'blocked')

    def test_full_admission_required_and_late_external_process(self):
        runner=MockRunner();runner.verify_admission=lambda *a: {'allowed':False}
        with tempfile.TemporaryDirectory() as d,self.assertRaises(g.Blocked):
            g.run(request(),runner,d,observe=snapshot)
        self.assertEqual(runner.calls,[])
        runner=MockRunner()
        original=runner.evaluate
        def evaluate(*args):
            rows=original(*args)
            runner.external=True
            return rows
        runner.external=False;runner.evaluate=evaluate
        with tempfile.TemporaryDirectory() as d,self.assertRaises(g.Blocked):
            g.run(request(),runner,d,observe=lambda: snapshot('GPU-a,999,5 MiB\n') if runner.external else snapshot())

    def test_final_exclusion_revocation_blocks_completion(self):
        runner=MockRunner()
        runner.owns_exclusive_allocation=lambda uuids: len(runner.calls)<24
        with tempfile.TemporaryDirectory() as d,self.assertRaises(g.Blocked):
            g.run(request('performance'),runner,d,observe=snapshot)

    def test_protocol_mismatch_blocks_before_probe(self):
        runner=MockRunner()
        r=request();r['protocol_sha256']='b'*64
        with tempfile.TemporaryDirectory() as d,self.assertRaises(g.Blocked):
            g.run(r,runner,d,observe=lambda: self.fail('incompatible runner probed'))
