from common import *
assert not (B/'manifest.json').exists()
inv=read(B/'source-inventory.json');plan=read(B/'validation-plan.json');out=read(B/'outcome.json')
contract={'result_id':B.name,'producer_task_id':f'TOK-FIVE-{MODE}-produce','producer_actor':'native-token-five-producer','manifest_path':REL+'/manifest.json','scope':plan['scope'],'validation_plan':ref(B/'validation-plan.json')}
dump(B/'contract.json',contract)
raw=[ref(f) for f in B.glob('*.rpc.jsonl')]+[ref(B/'producer-tests.log')]
outputs=[ref(B/name) for name in ('outcome.json','usage.json','trace.json','producer-cpu.json')]+[ref(B/(n+'.answer.json')) for n in NAMES]
dump(B/'manifest.json',{'schema_version':'experiment-result/v1',**contract,'run_id':B.name,'code_revision':inv['revision']+'+archived-sha256-bound-working-tree',
 'execution':{'command':['C:/Python312/python.exe','.agent-runs/token-five-20261011/native.py',str(MODE)],'environment_description':'Actual native Windows Codex app-server short no-tool turns plus separately executed fixed host CPU/native-data verifier','seeds':['deterministic-fixture-no-rng-model-nondeterministic'],'repeats':1},
 'artifacts':{'code':[{'path':r['archive_path'],'sha256':r['sha256']} for r in inv['files']],
 'inputs':[ref(B/'source-inventory.json'),ref(B/'oracle.json'),ref(B/'report.json')]+[ref(B/(n+'.prompt.txt')) for n in NAMES],
 'config':[ref(B/name) for name in ('config.json','settings.json','schema.json','freeze.json')],
 'raw_data':raw,'outputs':outputs,'environment':[ref(B/'threads.json'),ref(B/'tool-catalogs.json'),ref(B/'quota-admission.json')]},
 'metrics':[{'name':k,'value':v,'unit':'tokens'} for k,v in [('baseline_total',out['baseline_total']),('candidate_total',out['candidate_total']),('saving',out['saving_tokens']),('paired_spend',out['total_spent'])]]})
dump(B/'task-chain.json',{'tasks':[{'task_id':contract['producer_task_id'],'owner':contract['producer_actor'],'action':'short_native_fixture','task_type':'experiment','experiment_result':contract},
 {'task_id':f'TOK-FIVE-{MODE}-verify','owner':'host-token-five-reviewer','action':'verify_experiment_result','depends_on':[contract['producer_task_id']],'result_validation':contract},
 {'task_id':f'TOK-FIVE-{MODE}-publish','owner':'main-ai','action':'publish_upgrade','depends_on':[f'TOK-FIVE-{MODE}-verify'],'required_result_refs':[contract]}]})
print('raw native results pending independent verification')
