import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from agent_runtime import result_validation as v

def graph(count, task_type=dict):
    contract={'result_id':'r','producer_task_id':'p','producer_actor':'root','manifest_path':'manifest.json','scope':'local','validation_plan':{'path':'plan.json','sha256':'0'*64}}
    tasks=[task_type(task_id='p',owner='root',action='produce',experiment_result=contract),task_type(task_id='gate',owner='other',action='verify_experiment_result',depends_on=['p'],result_validation=contract)]
    for i in range(count):
        tasks.append(task_type(task_id='t'+str(i),owner='root',action='consume',depends_on=[tasks[-1]['task_id']],required_result_refs=[contract]))
    return {'tasks':tasks}

class Validation(unittest.TestCase):
    def test_R26_deep_valid_dag(self):
        self.assertTrue(v.validate_result_plan(graph(1100)))
        bad=graph(2);bad['tasks'][-1]['depends_on']=['p']
        with self.assertRaises(v.ResultValidationError):v.validate_result_plan(bad)

    def test_R27_shared_ancestry_work(self):
        reads=[]
        class Task(dict):
            def get(self,key,*default):
                if key=='depends_on':reads.append(key)
                return super().get(key,*default)
        self.assertTrue(v.validate_result_plan(graph(300,Task)))
        self.assertLessEqual(len(reads),4*302)
        bad=graph(2);bad['tasks'][-1]['depends_on']=['missing']
        with self.assertRaises(v.ResultValidationError):v.validate_result_plan(bad)

    def fixture(self,root,metric=1):
        def put(name,data):
            path=root/name;path.write_bytes(data)
            return {'path':name,'sha256':hashlib.sha256(data).hexdigest()}
        plan={'schema_version':'experiment-validation-plan/v1','scope':'local','criteria':{k:{'procedure':'literal','acceptance':'exact','allow_not_applicable':False} for k in v.CHECKS}}
        plan_ref=put('plan.json',json.dumps(plan).encode())
        blob=put('blob',b'x'*200000)
        contract={'result_id':'r','producer_task_id':'p','producer_actor':'root','scope':'local','manifest_path':'manifest.json','validation_plan':plan_ref}
        manifest={'schema_version':'experiment-result/v1',**contract,'run_id':'run','code_revision':'fixture','execution':{'command':['fixture'],'environment_description':'local','repeats':1,'seeds':[0]},'artifacts':{k:[blob] for k in v.ARTIFACT_ROLES},'metrics':[{'name':'count','value':metric,'unit':'count'}]}
        put('manifest.json',json.dumps(manifest).encode())
        return contract,blob

    def test_R28_unique_hash_once_per_fresh_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);contract,blob=self.fixture(root)
            with patch.object(v,'_hash_bound',wraps=v._hash_bound) as bound:
                v._snapshot(root,contract)
                self.assertEqual(bound.call_count,1)
                v._snapshot(root,contract)
                self.assertEqual(bound.call_count,2)
            (root/'blob').write_bytes(b'changed')
            with self.assertRaises(v.ResultValidationError):v._snapshot(root,contract)

    def test_R29_streamed_digest_exact(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);_,blob=self.fixture(root)
            self.assertIsNone(v._hash_bound(root,blob))
            with self.assertRaises(v.ResultValidationError):v._hash_bound(root,dict(blob,sha256='0'*64))
            (root/'blob').write_bytes(b'')
            empty={'path':'blob','sha256':hashlib.sha256(b'').hexdigest()}
            self.assertIsNone(v._hash_bound(root,empty))

    def test_R30_large_finite_integer(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);contract,_=self.fixture(root,10**1000)
            self.assertEqual(v._snapshot(root,contract)[0]['metrics'][0]['value'],10**1000)
            contract,_=self.fixture(root,True)
            with self.assertRaises(v.ResultValidationError):v._snapshot(root,contract)

if __name__=='__main__':unittest.main()
