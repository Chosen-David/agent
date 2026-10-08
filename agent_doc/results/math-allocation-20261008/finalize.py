from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[3];D=Path(__file__).parent

def cli(*a):
 r=subprocess.run(['python','-m','agent_runtime.knowledge','--root','knowledge',*a],cwd=R,capture_output=True,text=True,check=True)
 return json.loads(r.stdout)
queries=[{'prompt':'每层选一种设置，在总读取字节上限内，让冻结的误差总和尽量小；每层有哪些组合应保留？','query':'逐层 配置 总预算 误差','domain':'optimization'},{'prompt':'三路编码器都有有限比特档位，怎么在总存储限制内最小化相加的失真？','query':'比特 分配 编码失真','domain':'optimization'},{'prompt':'给资源乘一个价格并扫描所有价格，就一定能找到硬预算下最好的一档吗？','query':'lambda unsupported Pareto','domain':'optimization'}]
idx=R/'.agent-runs/math-allocation-20261008/search.sqlite';cli('index','--db',str(idx));records=[]
for x in queries:
 for backend in ['files','sqlite']:
  result=cli('search',x['query'],'--domain',x['domain'],'--limit','3',*(['--index',str(idx)] if backend=='sqlite' else []))
  records.append({'input':x,'backend':backend,'result':result})
show=cli('show','math.discrete-budget-allocation');dep=cli('show','math.dual-certificates');refs=show['knowledge_refs']
(D/'knowledge-usage.json').write_text(json.dumps({'knowledge_root':'knowledge','knowledge_refs':refs,'retrieval':records,'loaded_ids':['math.discrete-budget-allocation','math.dual-certificates'],'assumptions':'additivity and exact arithmetic checked manually; no model/refusal measurement','split':'all public developer queries'},ensure_ascii=False,indent=2)+'\n')
# Exact encoding of actual two CLI JSON outputs, not host context/billing.
try:
 import tiktoken
 enc=tiktoken.get_encoding('cl100k_base');n=sum(len(enc.encode(json.dumps(x,ensure_ascii=False))) for x in [show,dep])
except ImportError:n=None
(D/'cost.json').write_text(json.dumps({'retrieval_cli_calls':9,'formula':'1 index+6 search+2 show; excludes validation/test/host/web calls','body_package_cl100k_base_tokens':n,'measurement':'two complete serialized show outputs including prerequisite; not model billing','actual_model_AB_calls':0,'host_tokens':None,'quality_or_saving_claim':False},indent=2)+'\n')
scope=json.loads((D/'config.json').read_text())['scope']
def ref(p):return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
summary=json.loads((D/'summary.json').read_text());config=json.loads((D/'config.json').read_text())
manifest={'schema_version':'experiment-result/v1','result_id':'math-allocation-20261008','producer_task_id':'MATH-31','producer_actor':'/root','validation_plan':ref(D/'validation-plan.json'),'scope':scope,'run_id':'math-allocation-20261008','code_revision':'cba9ae98da7e09ff0ccbf924584c87b636897512 plus explicit file hashes','execution':{'command':['python doc/results/math-allocation-20261008/verify.py','python doc/results/math-allocation-20261008/finalize.py'],'environment_description':'CPU Python stdlib exact integer/Fraction; optional tiktoken encoding; no production/models','seeds':[config['seed']],'repeats':1},'artifacts':{'code':[ref(D/'verify.py'),ref(D/'finalize.py')]+[ref(p) for p in sorted((R/'agent_runtime').glob('knowledge*.py'))],'inputs':[ref(R/'knowledge/entries'/f'{stem}.{ext}') for stem in ['math.discrete-budget-allocation','math.dual-certificates'] for ext in ['json','md']],'config':[ref(D/'config.json')],'raw_data':[ref(D/'raw.json'),ref(D/'knowledge-usage.json')],'outputs':[ref(D/'summary.json'),ref(D/'cost.json')],'environment':[ref(D/'environment.json')]},'metrics':[{'name':'finite_assertions','value':summary['assertions'],'unit':'count'},{'name':'budget_cases','value':summary['budget_cases'],'unit':'count'}]}
(D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
contract={k:manifest[k] for k in ['result_id','producer_task_id','producer_actor','validation_plan','scope']};contract['manifest_path']=str((D/'manifest.json').relative_to(R))
dag={'tasks':[{'task_id':'MATH-31','owner':'/root','action':'produce','depends_on':[],'experiment_result':contract},{'task_id':'MATH-ALLOCATION-VERIFY','owner':'/root/allocation_verifier','action':'verify_experiment_result','depends_on':['MATH-31'],'result_validation':contract},{'task_id':'MATH-32','owner':'/root','action':'publish','depends_on':['MATH-ALLOCATION-VERIFY'],'required_result_refs':[contract]}],'execution_boundary':'bounded direct host maintenance; independent collaboration call; not deployed tmux/ManagedEngine/ReviewSession'}
(D/'task-dag.json').write_text(json.dumps(dag,ensure_ascii=False,indent=2)+'\n')
print('manifest',hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest(),'show_tokens',n)
