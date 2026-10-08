"""Independent reuse probes with current actual numerical/code revalidation."""
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from agent_runtime.core import Outcome, Store
from agent_runtime.task_manifest import ReportingHandler
from unittest.mock import patch

from agent_runtime import result_store as reuse
from agent_runtime import result_validation as gate
from agent_runtime import project_docs as docs
sys.path.insert(0,str(Path(docs.__file__).resolve().parents[1]/'tests'))
import test_result_gate_acceptance as gate_fixture


class PriorResultReuseAcceptanceTests(unittest.TestCase):
    write=gate_fixture.ResultGateAcceptanceTests.write
    ref=gate_fixture.ResultGateAcceptanceTests.ref
    save_manifest=gate_fixture.ResultGateAcceptanceTests.save_manifest
    rebind=gate_fixture.ResultGateAcceptanceTests.rebind

    def setUp(self):
        gate_fixture.ResultGateAcceptanceTests.setUp(self)
        self.store=reuse.ResultStore(self.root)
        self.manifest['execution']['environment_description']='CPython local CPU; integer dtype; shape 4; batch 1; deterministic synthetic fixture'
        self.save_manifest()
        self.context=reuse.result_context(self.manifest)
        self.run_id=self.manifest['run_id']
        self.original_code_sha=self.ref('run/producer.py')['sha256']

    def verifier(self,root,manifest,plan,*,reexecute=True):
        self.verifier_calls+=1
        paths={role:manifest['artifacts'][role][0]['path'] for role in gate.ARTIFACT_ROLES}
        xs=json.loads((root/paths['inputs']).read_text());rows=json.loads((root/paths['raw_data']).read_text())
        output=json.loads((root/paths['outputs']).read_text())
        reference=sum(x*x for x in xs)
        valid=(len(rows)==len(xs) and all(r.get('x')==x and r.get('square')==x*x for r,x in zip(rows,xs))
               and type(output.get('sum_of_squares')) in (float,int)
               and math.isfinite(output['sum_of_squares']) and output['sum_of_squares']==reference==manifest['metrics'][0]['value'])
        if reexecute:
            with tempfile.TemporaryDirectory(prefix='reuse-reference-rerun-') as rerun:
                rr=Path(rerun)
                for role in ('code','inputs','config'):
                    target=rr/paths[role];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/paths[role],target)
                executed=subprocess.run([sys.executable,paths['code']],cwd=rr,capture_output=True,timeout=10)
                valid=valid and executed.returncode==0 and all((rr/paths[role]).read_bytes()==(root/paths[role]).read_bytes()
                       for role in ('raw_data','outputs'))
        else:
            valid=valid and manifest['artifacts']['code'][0]['sha256']==self.original_code_sha
        evidence='validation/reuse-independent.json';self.write(evidence,{'reference':reference,'valid':valid,'rows':len(rows)})
        bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
        for refs in manifest['artifacts'].values():bindings.update({r['path']:r['sha256'] for r in refs})
        return {'schema_version':'experiment-validation/v1','manifest_sha256':hashlib.sha256((root/self.contract['manifest_path']).read_bytes()).hexdigest(),
                'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':plan['scope'],
                'verifier':{'actor':'independent-reuse-checker','source':'test_result_reuse_acceptance.verifier','run_id':'reuse-reference-v1',
                            'method':('Original input arithmetic and isolated producer reexecution.' if reexecute else
                                      'Original input arithmetic and original executed source binding; no producer rerun.'),'independent':True},
                'limitations':['Four synthetic integer boundary inputs; not general semantic, hardware, or performance certification.'],
                'checks':{name:{'verdict':'pass' if valid else 'fail','reason':'Independent arithmetic and actual isolated source execution.',
                                'evidence':[self.ref(evidence)]} for name in gate.CHECKS}}

    def cheap_verifier(self,root,manifest,plan):
        return self.verifier(root,manifest,plan,reexecute=False)

    def register(self,**kwargs):
        return self.store.register(self.contract,historical=True,measured_at='2026-10-06T00:00:00+00:00',**kwargs)

    def decision(self,**kwargs):
        return self.store.decide_run(self.run_id,self.context,verifier=self.verifier,**kwargs)

    def bytes(self):
        return {p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob('*') if p.is_file() and not p.is_symlink()}

    def test_exact_prior_result_requires_and_obtains_current_trusted_revalidation(self):
        self.register();before=self.verifier_calls
        result=self.decision()
        self.assertEqual(result['decision'],'reuse',result);self.assertGreater(self.verifier_calls,before)
        self.assertEqual(result['validation_status'],'usable-with-scope')
        self.assertFalse(result['automatic_skip_authorized'])

    def test_native_storage_is_central_and_legacy_paths_are_explicit(self):
        with self.assertRaises(ValueError):self.store.register(self.contract)
        before=(self.root/'run/raw.json').read_bytes()
        record=self.register()['record']
        self.assertEqual(record['origin'],'historical-external-reference')
        self.assertEqual((self.root/'run/raw.json').read_bytes(),before)
        self.assertTrue((self.root/'agent_doc/results'/self.run_id/'record.json').is_file())

    def test_central_manifest_raw_and_outputs_register_natively(self):
        base=f'agent_doc/results/{self.run_id}'
        for role in ('raw_data','outputs'):
            old=self.manifest['artifacts'][role][0]['path'];new=base+'/'+Path(old).name
            (self.root/new).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(self.root/old,self.root/new)
            self.manifest['artifacts'][role]=[self.ref(new)]
        self.contract['manifest_path']=base+'/manifest.json';self.manifest['manifest_path']=self.contract['manifest_path']
        self.write(self.contract['manifest_path'],self.manifest)
        record=self.store.register(self.contract)['record']
        self.assertEqual(record['origin'],'native')
        self.assertEqual(record['validation_at_registration']['status'],'pending')

    def test_unknown_matches_unknown_is_not_reuse_evidence(self):
        self.manifest['code_revision']='unknown'
        self.manifest['execution']['environment_description']='unknown'
        self.save_manifest();self.context=reuse.result_context(self.manifest)
        self.register();self.assertNotEqual(self.decision()['decision'],'reuse')

    def test_missing_conditions_and_metric_or_hardware_changes_do_not_reuse(self):
        self.register()
        for mutation in ('missing','metric','hardware','units'):
            with self.subTest(mutation=mutation):
                context=copy.deepcopy(self.context)
                if mutation=='missing':del context['execution']
                elif mutation=='metric':context['metrics'][0]['name']='different_metric'
                elif mutation=='units':context['metrics'][0]['unit']='seconds'
                else:context['execution']['environment_description']='different GPU; float16; shape 4096; batch 8'
                result=self.store.decide_run(self.run_id,context,verifier=self.verifier)
                self.assertNotEqual(result['decision'],'reuse',result)

    def test_stale_frozen_inputs_and_data_block_reuse(self):
        self.register()
        paths=['run/producer.py','run/inputs.json','run/config.json','run/raw.json','run/output.json','run/environment.json','validation/plan.json']
        for path in paths:
            with self.subTest(path=path):
                original=(self.root/path).read_bytes();calls=self.verifier_calls
                (self.root/path).write_bytes(original+b' ')
                result=self.decision();self.assertNotEqual(result['decision'],'reuse',result)
                self.assertEqual(self.verifier_calls,calls)
                (self.root/path).write_bytes(original)

    def test_registry_scope_labels_cannot_replace_bound_manifest_conditions(self):
        shown=self.register();path=self.root/shown['record_ref']['path']
        record=json.loads(path.read_text());record['context']['execution']['environment_description']='pretend different hardware'
        self.write(shown['record_ref']['path'],record)
        result=self.store.decide_run(self.run_id,record['context'],verifier=self.verifier)
        self.assertNotEqual(result['decision'],'reuse')

    def test_forged_stored_pass_and_missing_host_cannot_authorize_reuse(self):
        shown=self.register();record=shown['record']
        record['validation_at_registration']={'status':'usable-with-scope','proof':{'independent':True,'reviewer':'claimed reviewer'}}
        self.write(shown['record_ref']['path'],record)
        result=self.store.decide_run(self.run_id,self.context)
        self.assertNotEqual(result['decision'],'reuse');self.assertEqual(self.verifier_calls,0)

    def test_self_review_callback_cannot_authorize_reuse(self):
        self.register()
        def self_review(root,manifest,plan):
            review=self.verifier(root,manifest,plan);review['verifier']['actor']=manifest['producer_actor'];return review
        result=self.store.decide_run(self.run_id,self.context,verifier=self_review)
        self.assertNotEqual(result['decision'],'reuse')

    def test_duplicate_run_identity_preserves_all_original_data(self):
        self.register();before=self.bytes()
        with self.assertRaises(ValueError):self.register()
        self.assertEqual(self.bytes(),before)

    def test_valid_negative_finding_remains_distinct_from_invalid_result(self):
        negative='Negative hypothesis finding: numerical baseline is valid but fails the hoped-for target.'
        self.contract['scope']=negative;self.manifest['scope']=negative
        plan=json.loads((self.root/'validation/plan.json').read_text());plan['scope']=negative;self.write('validation/plan.json',plan)
        self.contract['validation_plan']=self.ref('validation/plan.json');self.manifest['validation_plan']=self.contract['validation_plan']
        self.save_manifest();self.context=reuse.result_context(self.manifest)
        self.register();self.assertEqual(self.decision()['decision'],'reuse')
        self.assertEqual(self.store.search('negative')['status'],'candidates')
        self.write('run/output.json',{'sum_of_squares':99})
        result=self.decision();self.assertNotEqual(result['decision'],'reuse')

    def test_explicit_reproduction_new_claim_and_unknown_age_force_nonreuse(self):
        self.register()
        self.assertEqual(self.decision(explicit_reproduction=True)['decision'],'rerun')
        self.assertEqual(self.decision(new_claim=True)['decision'],'rerun')
        self.assertNotEqual(self.decision(max_age_seconds=1,now='2026-10-07T00:00:00+00:00')['decision'],'reuse')

    def test_bounded_search_is_read_only_and_does_not_execute_recorded_commands(self):
        self.register();before=self.bytes()
        for limit,max_scan in ((0,200),(21,200),(1,0),(1,5001)):
            with self.assertRaises(ValueError):self.store.search('synthetic',limit=limit,max_scan=max_scan)
        with patch.object(subprocess,'run',side_effect=AssertionError('search cannot execute')):
            result=self.store.search('synthetic',limit=1,max_scan=1)
        self.assertLessEqual(result['scanned'],1);self.assertLessEqual(len(result['results']),1)
        self.assertEqual(self.bytes(),before)

    def test_exact_context_fallback_does_not_require_lexical_overlap(self):
        self.register()
        result=self.store.decide('zxqvnonoverlappingnonce',self.context,verifier=self.cheap_verifier)
        self.assertTrue(any(item['run_id']==self.run_id and item['decision']=='reuse' for item in result['results']),result)

    def test_partial_broken_scan_and_unbound_fresh_timestamp_do_not_claim_completeness(self):
        (self.root/'agent_doc/results/empty-first').mkdir(parents=True)
        shown=self.register()
        result=self.store.search('not-matching-anything',limit=1,max_scan=1)
        self.assertNotEqual(result['status'],'no_hits')
        self.assertTrue(result['partial'] or result['errors'])
        record=shown['record'];record['measured_at']='2026-10-07T00:00:00+00:00'
        self.write(shown['record_ref']['path'],record)
        result=self.store.decide_run(self.run_id,self.context,verifier=self.cheap_verifier,
                                    max_age_seconds=1,now='2026-10-07T00:00:00+00:00')
        self.assertNotEqual(result['decision'],'reuse')

    def test_existing_historical_registration_does_not_bypass_central_raw_path_rule(self):
        base=f'agent_doc/results/{self.run_id}'
        self.contract['manifest_path']=base+'/manifest.json'
        self.manifest['manifest_path']=self.contract['manifest_path']
        self.write(self.contract['manifest_path'],self.manifest)
        self.store.register(self.contract,historical=True)
        before=self.bytes()
        with self.assertRaises(ValueError):
            reuse.register_task_result(self.root,{'experiment_result':self.contract,'result_storage':'central'})
        self.assertEqual(self.bytes(),before)

    def test_history_without_contract_never_becomes_usable_by_matching_unknowns(self):
        self.store.register_history('pre-contract','Synthetic old data',[self.ref('run/raw.json')],context={})
        result=self.store.decide_run('pre-contract',{},verifier=self.verifier)
        self.assertNotEqual(result['decision'],'reuse');self.assertEqual(self.verifier_calls,0)

    def test_result_registry_alias_and_rebased_guide_root_are_protected(self):
        guide=self.root/'agent_doc/guide';guide.mkdir(parents=True)
        (guide/'policy.md').write_text('Synthetic human-only policy.\n')
        (self.root/'agent_doc/results').symlink_to(guide,target_is_directory=True)
        with self.assertRaises(ValueError):self.register()
        self.assertEqual([p.name for p in guide.iterdir()],['policy.md'])
        (self.root/'agent_doc/results').unlink()
        nested=reuse.ResultStore(guide)
        with self.assertRaises(ValueError):nested.register_history('bad','Synthetic',[{'path':'policy.md','sha256':hashlib.sha256((guide/'policy.md').read_bytes()).hexdigest()}])
        self.assertEqual([p.name for p in guide.iterdir()],['policy.md'])

    def test_interrupted_record_commit_keeps_old_records_and_recovers(self):
        original=self.bytes()
        with patch.object(reuse.os,'link',side_effect=OSError('synthetic interrupted publish')):
            with self.assertRaises(OSError):self.register()
        self.assertFalse((self.root/'agent_doc/results'/self.run_id/'record.json').exists())
        self.assertEqual(self.bytes(),original)
        self.register();self.assertEqual(self.decision()['decision'],'reuse')

    def task_and_observer(self):
        calls=[]
        class Observer:
            idempotent=True;required_capabilities=()
            def run(self,task,context):
                calls.append(copy.deepcopy(task))
                return Outcome('pending','Synthetic producer dispatch observed; no new execution.')
            def verify(self,task,evidence):return False
        task={'task_id':'new-production','action':'produce','produces_data':True,'inputs':{'goal':'synthetic'}}
        return task,calls,Observer()

    def test_actual_no_hit_lookup_precedes_producer_and_does_not_create_store(self):
        task,calls,observer=self.task_and_observer()
        task['prior_result_search']={'status':'forged cached data'}
        outcome=ReportingHandler(observer,self.root).run(task,SimpleNamespace(idempotency_key='first'))
        self.assertEqual(outcome.status,'pending');self.assertEqual(len(calls),1)
        search=calls[0]['prior_result_search']
        self.assertEqual(search['status'],'no_hits');self.assertFalse(search['partial']);self.assertEqual(search['errors'],[])
        self.assertFalse((self.root/'agent_doc/results').exists())

    def test_real_candidate_blocks_producer_even_if_plan_forges_no_hits(self):
        self.register();task,calls,observer=self.task_and_observer()
        task['prior_result_search']={'status':'no_hits','results':[],'partial':False,'errors':[]}
        outcome=ReportingHandler(observer,self.root).run(task,SimpleNamespace(idempotency_key='candidate'))
        self.assertEqual(outcome.status,'blocked');self.assertEqual(calls,[])
        hits=self.store.search('synthetic')['results']
        task['prior_result_review']={'decision':'rerun','reason':'Explicit synthetic independent reproduction.',
                  'record_refs':[{'run_id':h['run_id'],'record_sha256':h['record_sha256']} for h in hits]}
        outcome=ReportingHandler(observer,self.root).run(task,SimpleNamespace(idempotency_key='reviewed'))
        self.assertEqual(outcome.status,'pending');self.assertEqual(len(calls),1)
        task['prior_result_review']['record_refs'][0]['record_sha256']='0'*64
        self.assertEqual(ReportingHandler(observer,self.root).run(task,SimpleNamespace()).status,'blocked')
        self.assertEqual(len(calls),1)

    def test_failed_or_partial_lookup_is_not_silently_treated_as_no_hit(self):
        task,calls,observer=self.task_and_observer()
        with patch.object(reuse.ResultStore,'search',side_effect=OSError('synthetic lookup interruption')):
            wrapped=ReportingHandler(observer,self.root)
            self.assertEqual(wrapped.run(task,SimpleNamespace()).status,'blocked')
            self.assertEqual(calls,[])
            task['prior_result_review']={'decision':'verify_delta','reason':'Diagnose missing local index before a bounded authorized probe.',
                                         'record_refs':[]}
            self.assertEqual(ReportingHandler(observer,self.root).run(task,SimpleNamespace()).status,'pending')
        self.assertEqual(calls[0]['prior_result_search']['status'],'unavailable')
        self.assertTrue(calls[0]['prior_result_search']['partial'])
        self.assertTrue(calls[0]['prior_result_search']['errors'])

    def test_lookup_journal_is_durable_and_restart_refreshes_cached_first_dispatch(self):
        task,calls,observer=self.task_and_observer();store=Store(self.root/'lookup.sqlite')
        context=SimpleNamespace(idempotency_key='same-owned-job',store=store,run_id='synthetic-journal',clock=lambda:1234.)
        wrapped=ReportingHandler(observer,self.root)
        wrapped.run(task,context);wrapped.run(task,context)
        with store.transaction() as db:
            rows=db.execute("SELECT detail FROM journal WHERE kind='prior_result_search'").fetchall()
        self.assertEqual(len(rows),1)
        self.assertEqual(json.loads(rows[0][0])['search']['status'],'no_hits')
        self.register()
        # A new wrapper simulates restart: a fresh result must supersede cached no-hit.
        self.assertEqual(ReportingHandler(observer,self.root).run(task,context).status,'blocked')
        with store.transaction() as db:
            rows=db.execute("SELECT detail FROM journal WHERE kind='prior_result_search' ORDER BY seq").fetchall()
        self.assertEqual(len(rows),2);self.assertEqual(json.loads(rows[-1][0])['search']['status'],'candidates')
        self.assertEqual(len(calls),2)

    def test_exact_reuse_action_does_not_execute_producer_again_and_cannot_override_repeat(self):
        shown=self.register(verifier=self.cheap_verifier)
        selection={'run_id':self.run_id,'record_sha256':shown['record_ref']['sha256'],'query':'synthetic',
                   'context':self.context,'explicit_reproduction':False,'new_claim':False}
        task={'action':'reuse_validated_result','result_reuse':selection}
        original=(self.root/'run/raw.json').read_bytes()
        handler=reuse.ReuseResultHandler(self.root,self.cheap_verifier)
        with patch.object(subprocess,'run',side_effect=AssertionError('reuse must not reexecute producer')) as execute:
            outcome=handler.run(task,None)
            self.assertEqual(outcome.status,'complete');self.assertTrue(handler.verify(task,outcome.evidence))
            self.assertEqual(execute.call_count,0)
            # Consumer-owned repeat intent wins even if nested producer selection says false.
            repeat=copy.deepcopy(task);repeat['explicit_reproduction']=True
            self.assertNotEqual(handler.run(repeat,None).status,'complete')
            changed=copy.deepcopy(task);changed['result_reuse']['context']['artifacts']['inputs'][0]['sha256']='0'*64
            self.assertNotEqual(handler.run(changed,None).status,'complete')
        self.assertEqual((self.root/'run/raw.json').read_bytes(),original)

    def test_pinned_reuse_choice_fails_after_registry_change(self):
        shown=self.register()
        task={'action':'reuse_validated_result','result_reuse':{'run_id':self.run_id,
            'record_sha256':shown['record_ref']['sha256'],'query':'synthetic','context':self.context,
            'explicit_reproduction':False,'new_claim':False}}
        self.assertTrue(reuse.check_task_reuse(self.root,task,self.verifier))
        record=shown['record'];record['summary']+=' changed';self.write(shown['record_ref']['path'],record)
        with self.assertRaises(ValueError):reuse.check_task_reuse(self.root,task,self.verifier)


if __name__=='__main__':unittest.main()
