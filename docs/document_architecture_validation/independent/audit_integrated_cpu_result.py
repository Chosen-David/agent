"""Independent read-only source/data audit; deliberately never executes producer."""
import argparse, copy, datetime, hashlib, json, pathlib, subprocess, sys
from unittest.mock import patch
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=pathlib.Path,default=pathlib.Path.cwd())
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
ROOT=args.root.resolve()
OUT=args.output.resolve()
sys.path.insert(0,str(ROOT))
from agent_runtime.result_store import ResultStore, ReuseResultHandler, result_context
from agent_runtime.result_validation import CHECKS
from agent_runtime.project_docs import guard_write_path
guard_write_path(args.output / 'actual-result-independent.json')
OUT.mkdir(parents=True,exist_ok=True)
REL='doc/results/prior-result-store-cpu-20261007'
RUN=ROOT/REL
AUDITED_SOURCE_SHA='c9b0182deb2f002009ec8f7be80eb57c098904537ae97cbcaa6434bd20895c65'
checks_observed={};reviews=[];counter=[0]

def read(name): return json.loads((RUN/name).read_text())
def ref(name):
    path=REL+'/'+name
    return {'path':path,'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()}
def inventory():return {str(p.relative_to(RUN)):hashlib.sha256(p.read_bytes()).hexdigest() for p in RUN.rglob('*') if p.is_file()}

def verify(root,manifest,plan):
    counter[0]+=1
    source=(RUN/'producer.py').read_bytes()
    assert hashlib.sha256(source).hexdigest()==AUDITED_SOURCE_SHA
    # Source was independently read: exact x*x comprehension over every repeat/input,
    # no filtering, ordinary Python integer arithmetic, explicit raw and sum/count outputs.
    assert manifest['code_revision']=='source-sha256:'+AUDITED_SOURCE_SHA
    values=read('inputs.json')['values'];config=read('config.json');environment=read('environment.json')
    rows=read('raw/samples.json');summary=read('derived/summary.json');receipt=read('execution-receipt.json')
    invocations=[json.loads(line) for line in (RUN/'raw/producer-invocations.jsonl').read_text().splitlines() if line]
    assert values==[-3,-1,0,2] and all(type(x) is int for x in values)
    assert config['repeats']==3 and config['seeds']==[0] and config['dtype']=='Python exact integer'
    expected=[{'input':x,'repeat':r,'value':pow(abs(x),2)} for r in range(3) for x in values]
    assert rows==expected and len({(r['input'],r['repeat']) for r in rows})==12
    assert summary=={'sum_of_squares':42,'samples':12}
    assert sum(row['value'] for row in rows)==sum(pow(abs(x),2) for x in values)*3==42
    assert manifest['metrics']==[{'name':'sum_of_squares','value':42,'unit':'dimensionless'},
                                 {'name':'samples','value':12,'unit':'count'}]
    assert environment['device']=='CPU' and environment['timed'] is False
    assert receipt['exit_code']==0 and receipt['producer_subprocess_calls']==1
    assert receipt['command']==manifest['execution']['command']
    assert len(invocations)==1 and invocations[0]['command']==receipt['command'][1:]
    t=lambda v:datetime.datetime.fromisoformat(v)
    assert t(receipt['started_at'])<=t(invocations[0]['time'])<=t(receipt['finished_at'])
    assert manifest['execution']['repeats']==3 and manifest['execution']['seeds']==[0]
    bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
    for items in manifest['artifacts'].values():
        for item in items:
            assert hashlib.sha256((root/item['path']).read_bytes()).hexdigest()==item['sha256']
            bindings[item['path']]=item['sha256']
    reasons={
       'implementation':'Independently read audited source; source SHA matches exact x*x comprehension, repeat traversal, sum/count and raw writes.',
       'reference_boundary':'Independent abs(x)**2 reference covers negative, zero and positive frozen integer inputs and matches all 12 rows.',
       'data_integrity':'Exact ordered input-repeat pairs are complete and unique; raw total/count, derived summary and manifest metric values/units agree.',
       'numerical_sanity':'All inputs and outputs are exact finite integers; 3*(9+1+0+4)=42 and 3*4=12.',
       'measurement_validity':'No runtime/throughput metric or speed claim exists; environment explicitly timed=false. Numerical observations only.',
       'reproducibility':'Source/input/config/environment/receipt hashes bound; independent formula reproduces every row without invoking producer again. Initial process receipt checked for internal consistency.'}
    evidence={
       'implementation':[ref('producer.py'),ref('config.json')],
       'reference_boundary':[ref('inputs.json'),ref('raw/samples.json')],
       'data_integrity':[ref('raw/samples.json'),ref('derived/summary.json')],
       'numerical_sanity':[ref('raw/samples.json'),ref('derived/summary.json')],
       'measurement_validity':[ref('environment.json'),ref('derived/summary.json')],
       'reproducibility':[ref('execution-receipt.json'),ref('raw/producer-invocations.jsonl'),ref('producer.py')]}
    review={'schema_version':'experiment-validation/v1','scope':plan['scope'],
       'manifest_sha256':hashlib.sha256((RUN/'manifest.json').read_bytes()).hexdigest(),
       'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],
       'verifier':{'actor':'independent-document-architecture-reviewer','source':'audit_integrated_cpu_result.py',
          'run_id':'actual-cpu-independent-20261007','method':'Independent source read, frozen-artifact/receipt checks and exact mathematical recomputation; zero producer calls.','independent':True},
       'limitations':['Only this frozen four-input, three-repeat exact-integer scope is accepted; no general bug-free, performance, model or hardware-transfer claim.',
          'Initial execution receipt came from the producing worker; independently checked source/data/receipt consistency, not OS-level attestation of that historical process.',
          'Cheap independent reference validation did not rerun the producer; saved work is only the avoided duplicate producer invocation in this controlled local case.'],
       'checks':{name:{'verdict':'not_applicable' if name=='measurement_validity' else 'pass',
                       'reason':reasons[name],'evidence':evidence[name]} for name in CHECKS}}
    reviews.append(review)
    checks_observed.update(sum_of_squares=42,samples=12,source_sha256=AUDITED_SOURCE_SHA,initial_producer_invocations=len(invocations))
    return review

before=inventory();contract=read('contract.json');manifest=read('manifest.json');context=result_context(manifest)
store=ResultStore(ROOT);shown=store.show(manifest['run_id'])
assert shown['record']['validation_at_registration']['status']=='pending'
selection={'run_id':manifest['run_id'],'record_sha256':shown['record_ref']['sha256'],'query':'CPU平方和数值测试',
           'context':context,'explicit_reproduction':False,'new_claim':False}
handler=ReuseResultHandler(ROOT,verify)
with patch.object(subprocess,'run',side_effect=AssertionError('Independent audit must not execute producer')) as executed:
    eligible=store.decide_run(manifest['run_id'],context,verifier=verify)
    assert eligible['decision']=='reuse',eligible
    task={'action':'reuse_validated_result','result_reuse':selection}
    outcome=handler.run(task,None);assert outcome.status=='complete';assert handler.verify(task,outcome.evidence)
    changed=copy.deepcopy(context);changed['artifacts']['inputs'][0]['sha256']='0'*64
    delta=store.decide_run(manifest['run_id'],changed,verifier=verify);assert delta['decision']!='reuse'
    repeat=store.decide_run(manifest['run_id'],context,verifier=verify,explicit_reproduction=True);assert repeat['decision']=='rerun'
    task['explicit_reproduction']=True;assert handler.run(task,None).status!='complete'
    actual_producer_calls=executed.call_count
    assert actual_producer_calls==0
assert inventory()==before
assert len((RUN/'raw/producer-invocations.jsonl').read_text().splitlines())==1
report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target':'integrated candidate','status':'independently-usable-with-scope',
    'run_id':manifest['run_id'],'record_ref':shown['record_ref'],'observations':checks_observed,
    'source_and_raw_bytes_unchanged':True,'producer_invocations_before':1,'producer_invocations_after':1,
    'producer_calls_during_reuse_validation':actual_producer_calls,'cheap_reference_callback_calls':counter[0],
    'exact_request_decision':eligible['decision'],'reuse_handler_status':outcome.status,
    'changed_input_request_decision':delta['decision'],'explicit_reproduction_decision':repeat['decision'],
    'original_record_left_pending':store.show(manifest['run_id'])['record']['validation_at_registration']['status']=='pending',
    'review':reviews[0],'run_file_hashes':before,
    'auditor_source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
(OUT/'actual-result-independent.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('review','run_file_hashes')},ensure_ascii=False,indent=2))
