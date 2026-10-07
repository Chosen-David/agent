"""Independent numerical result-gate fault probes; no implementation fixture reuse."""
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

from agent_runtime import result_validation as gate
from agent_runtime.core import Outcome
from agent_runtime.task_manifest import ReportingHandler, atomic_json


class ResultGateAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='result-gate-acceptance-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'TASK.md').write_text('- [ ] [DATA] Synthetic numerical validation\n')
        self.write('run/inputs.json', [-3, -1, 0, 2])
        self.write('run/config.json', {'operation':'sum_of_squares','exponent':2})
        self.write('run/environment.json', {'python':sys.version.split()[0], 'execution':'local synthetic fixture'})
        code = '''import json\nfrom pathlib import Path\np=Path(__file__).parent\nxs=json.loads((p/'inputs.json').read_text())\nrows=[{'x':x,'square':x ** 2} for x in xs]\n(p/'raw.json').write_text(json.dumps(rows,sort_keys=True)+'\\n')\n(p/'output.json').write_text(json.dumps({'sum_of_squares':sum(row['square'] for row in rows)},sort_keys=True)+'\\n')\n'''
        (self.root / 'run/producer.py').write_text(code)
        subprocess.run([sys.executable,'run/producer.py'],cwd=self.root,check=True,capture_output=True)
        scope='Deterministic integer sum-of-squares on the four synthetic boundary inputs only.'
        plan={'schema_version':'experiment-validation-plan/v1','scope':scope,
              'criteria':{name:{'procedure':'Independently recompute and inspect synthetic '+name,
                                'acceptance':'Exact finite reference and complete original input/raw correspondence.',
                                'allow_not_applicable':False} for name in gate.CHECKS}}
        self.write('validation/plan.json',plan)
        self.contract={'result_id':'synthetic-square-v1','producer_task_id':'produce',
                       'producer_actor':'synthetic-producer','manifest_path':'run/manifest.json',
                       'validation_plan':self.ref('validation/plan.json'),'scope':scope}
        self.manifest={**self.contract,'schema_version':'experiment-result/v1','run_id':'square-run-v1',
                       'code_revision':'synthetic-fixture-source',
                       'execution':{'command':[sys.executable,'run/producer.py'],'environment_description':'local synthetic fixture',
                                    'repeats':1,'seeds':[0]},
                       'artifacts':{role:[self.ref(path)] for role,path in
                           {'code':'run/producer.py','inputs':'run/inputs.json','config':'run/config.json',
                            'raw_data':'run/raw.json','outputs':'run/output.json','environment':'run/environment.json'}.items()},
                       'metrics':[{'name':'sum_of_squares','value':14,'unit':'dimensionless'}]}
        self.save_manifest()
        self.verifier_calls=0

    def write(self,path,value):
        target=self.root / path; target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(value,sort_keys=True)+'\n')

    def ref(self,path):
        return {'path':path,'sha256':hashlib.sha256((self.root / path).read_bytes()).hexdigest()}

    def save_manifest(self): self.write('run/manifest.json',self.manifest)

    def rebind(self,role,path):
        self.manifest['artifacts'][role]=[self.ref(path)];self.save_manifest()

    def independent_verifier(self,root,manifest,plan):
        self.verifier_calls+=1
        inputs=json.loads((root/'run/inputs.json').read_text())
        rows=json.loads((root/'run/raw.json').read_text())
        out=json.loads((root/'run/output.json').read_text())
        config=json.loads((root/'run/config.json').read_text())
        reference=sum(x*x for x in inputs)
        correspondence=(len(rows)==len(inputs) and all(row.get('x')==x and row.get('square')==x*x
                        for row,x in zip(rows,inputs)))
        numeric=(type(out.get('sum_of_squares')) in (int,float) and math.isfinite(out['sum_of_squares'])
                 and out['sum_of_squares']==reference==manifest['metrics'][0]['value'])
        applicable=(config=={'operation':'sum_of_squares','exponent':2} and len(inputs)==4
                    and any(x<0 for x in inputs) and 0 in inputs and any(x>0 for x in inputs))
        # Rerun the trusted fixture implementation in isolation, never rewrite raw evidence.
        import shutil
        with tempfile.TemporaryDirectory(prefix='independent-code-rerun-') as rerun:
            rerun_root=Path(rerun);(rerun_root/'run').mkdir()
            for name in ('producer.py','inputs.json','config.json'):
                shutil.copyfile(root/'run'/name,rerun_root/'run'/name)
            execution=subprocess.run([sys.executable,'run/producer.py'],cwd=rerun_root,
                                     capture_output=True,timeout=10)
            reproduced=(execution.returncode==0 and all((rerun_root/'run'/name).read_bytes()==(root/'run'/name).read_bytes()
                         for name in ('raw.json','output.json')))
        applicable=applicable and manifest['execution']['command']==[sys.executable,'run/producer.py']
        observed={'reference':reference,'input_rows':len(inputs),'raw_rows':len(rows),
                  'correspondence':correspondence,'numeric':numeric,'applicable':applicable,
                  'isolated_code_reexecution_matches':reproduced}
        self.write('validation/independent-observation.json',observed)
        artifact_hashes={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
        for refs in manifest['artifacts'].values():
            artifact_hashes.update({r['path']:r['sha256'] for r in refs})
        verdict='pass' if correspondence and numeric and applicable and reproduced else 'fail'
        return {'schema_version':'experiment-validation/v1',
                'manifest_sha256':hashlib.sha256((root/'run/manifest.json').read_bytes()).hexdigest(),
                'artifact_hashes':artifact_hashes,'validation_plan_sha256':manifest['validation_plan']['sha256'],
                'scope':plan['scope'],
                'verifier':{'actor':'independent-reference-checker','source':'test_result_gate_acceptance.independent_verifier',
                            'run_id':'independent-check-v1','method':'Reload originals; independently multiply inputs; rerun code in isolated workspace.',
                            'independent':True},
                'limitations':['Synthetic four-input integer fixture, not a general correctness or measurement-quality proof.'],
                'checks':{name:{'verdict':verdict,'reason':'Actual independent recomputation and row/finite/scope checks: '+str(observed),
                                'evidence':[self.ref('validation/independent-observation.json')]} for name in gate.CHECKS}}

    def inspect(self,verifier=None):
        return gate.inspect_result(self.root,self.contract,self.independent_verifier if verifier is None else verifier)

    def plan(self):
        c=copy.deepcopy(self.contract)
        return {'tasks':[
            {'task_id':'produce','owner':'synthetic-producer','action':'produce','depends_on':[],
             'task_type':'experiment','experiment_result':c},
            {'task_id':'validate','owner':'independent-reference-checker','action':'verify_experiment_result',
             'depends_on':['produce'],'result_validation':copy.deepcopy(c)},
            {'task_id':'consume','owner':'consumer','action':'consume','depends_on':['validate'],
             'required_result_refs':[copy.deepcopy(c)]}]}

    def test_real_reference_check_accepts_correct_result_with_scoped_evidence(self):
        result=self.inspect()
        self.assertEqual(result['status'],'usable-with-scope',result)
        self.assertEqual(self.verifier_calls,1)
        self.assertEqual(result['proof']['verifier']['actor'],'independent-reference-checker')
        self.assertIn('not a general correctness',result['proof']['limitations'][0])

    def test_worker_pass_and_named_independent_reviewer_do_not_replace_host(self):
        self.manifest['review']={'status':'pass','independent':True,'reviewer':'independent-reference-checker'}
        self.save_manifest();self.write('validation/forged-pass.json',self.manifest['review'])
        result=gate.inspect_result(self.root,self.contract)
        self.assertEqual(result['status'],'pending');self.assertEqual(self.verifier_calls,0)
        self.assertNotEqual(result['proof']['status'],'usable-with-scope')

    def test_rebound_wrong_output_is_rejected_by_actual_numerical_check(self):
        self.write('run/output.json',{'sum_of_squares':99});self.rebind('outputs','run/output.json')
        result=self.inspect();self.assertEqual(self.verifier_calls,1)
        self.assertEqual(result['status'],'invalid',result)

    def test_rebound_incorrect_code_cannot_reuse_previously_correct_outputs(self):
        path=self.root/'run/producer.py'
        path.write_text(path.read_text().replace('x ** 2','x ** 3'))
        self.rebind('code','run/producer.py')
        result=self.inspect();self.assertEqual(self.verifier_calls,1)
        self.assertEqual(result['status'],'invalid',result)

    def test_rebound_omitted_raw_row_is_rejected(self):
        self.write('run/raw.json',[{'x':-3,'square':9},{'x':-1,'square':1},{'x':0,'square':0}])
        self.rebind('raw_data','run/raw.json')
        self.assertEqual(self.inspect()['status'],'invalid')

    def test_nonfinite_manifest_metric_and_rebound_output_are_rejected(self):
        self.manifest['metrics'][0]['value']=float('nan');self.save_manifest()
        self.assertEqual(self.inspect()['status'],'invalid');self.assertEqual(self.verifier_calls,0)
        self.manifest['metrics'][0]['value']=14;self.save_manifest()
        self.write('run/output.json',{'sum_of_squares':float('inf')});self.rebind('outputs','run/output.json')
        self.assertEqual(self.inspect()['status'],'invalid')

    def test_domain_omission_self_review_and_unjustified_na_are_rejected(self):
        for mutation in ('missing','self','na'):
            with self.subTest(mutation=mutation):
                def verifier(root,manifest,plan):
                    review=self.independent_verifier(root,manifest,plan)
                    if mutation=='missing': del review['checks']['data_integrity']
                    elif mutation=='self': review['verifier']['actor']=manifest['producer_actor']
                    else: review['checks']['implementation']['verdict']='not_applicable'
                    return review
                self.assertEqual(self.inspect(verifier)['status'],'invalid')

    def test_missing_callback_result_stays_pending_and_exception_never_passes(self):
        self.assertEqual(self.inspect(lambda *_:None)['status'],'pending')
        def broken(*_): raise RuntimeError('synthetic verifier crashed')
        result=self.inspect(broken)
        self.assertIn(result['status'],('pending','invalid'));self.assertNotEqual(result['status'],'usable-with-scope')

    def test_source_changes_invalidate_before_verifier_is_invoked(self):
        originals={p:(self.root/p).read_bytes() for p in ['run/producer.py','run/inputs.json','run/config.json',
            'run/raw.json','run/output.json','run/environment.json','validation/plan.json']}
        for path,data in originals.items():
            with self.subTest(path=path):
                calls=self.verifier_calls;(self.root/path).write_bytes(data+b' ')
                self.assertEqual(self.inspect()['status'],'invalid');self.assertEqual(self.verifier_calls,calls)
                (self.root/path).write_bytes(data)

    def test_source_mutation_during_callback_blocks_mixed_snapshot_acceptance(self):
        original=(self.root/'run/raw.json').read_bytes()
        def racing(root,manifest,plan):
            review=self.independent_verifier(root,manifest,plan)
            (root/'run/raw.json').write_bytes(original+b' ')
            return review
        self.assertEqual(self.inspect(racing)['status'],'invalid')
        self.assertEqual((self.root/'run/raw.json').read_bytes(),original+b' ')

    def test_missing_producer_flag_does_not_bypass_trusted_consumer_requirement(self):
        plan=self.plan();self.assertTrue(gate.validate_result_plan(plan))
        del plan['tasks'][0]['task_type'];del plan['tasks'][0]['experiment_result']
        with self.assertRaises(ValueError): gate.validate_result_plan(plan)
        consumer={'required_result_refs':[self.contract]}
        with self.assertRaises(ValueError): gate.check_task_results(self.root,consumer)

    def test_downstream_without_gate_dependency_or_contract_is_rejected(self):
        for change in ('dependency','contract','owner'):
            with self.subTest(change=change):
                plan=self.plan()
                if change=='dependency':plan['tasks'][2]['depends_on']=['produce']
                elif change=='contract':del plan['tasks'][2]['required_result_refs']
                else:plan['tasks'][1]['owner']='synthetic-producer'
                with self.assertRaises(ValueError):gate.validate_result_plan(plan)

    def test_artifact_path_escape_and_symlink_are_rejected(self):
        original=self.manifest['artifacts']['outputs']
        self.manifest['artifacts']['outputs']=[dict(original[0],path='../outside.json')];self.save_manifest()
        self.assertEqual(self.inspect()['status'],'invalid')
        self.manifest['artifacts']['outputs']=original;self.save_manifest()
        target=self.root/'run/output.json';data=target.read_bytes();target.unlink()
        other=self.root/'independent-target.json';other.write_bytes(data);target.symlink_to(other)
        self.assertEqual(self.inspect()['status'],'invalid')

    def test_previous_gate_evidence_stales_after_rebound_result_change(self):
        handler=gate.ResultValidationHandler(self.root,self.independent_verifier)
        task={'result_validation':self.contract};outcome=handler.run(task,None)
        self.assertEqual(outcome.status,'complete');self.assertTrue(handler.verify(task,outcome.evidence))
        self.write('run/output.json',{'sum_of_squares':99});self.rebind('outputs','run/output.json')
        self.assertFalse(handler.verify(task,outcome.evidence))

    def test_reporting_handler_consumer_cannot_rely_on_producer_pass_report(self):
        calls=[]
        class Handler:
            idempotent=True;required_capabilities=()
            def run(self,task,context):
                calls.append(True);return Outcome('complete','synthetic consumer',[])
            def verify(self,task,evidence):return True
        task={'task_id':'consumer','required_result_refs':[self.contract],'report_path':'result.json'}
        atomic_json(self.root/'result.json',{'task_id':'consumer','summary':'Producer claims pass',
                    'data':[{'kind':'derived','description':'Unvalidated numerical result'}]})
        outcome=ReportingHandler(Handler(),self.root).run(task,SimpleNamespace())
        self.assertEqual(outcome.status,'blocked');self.assertEqual(calls,[])


if __name__=='__main__':unittest.main()
