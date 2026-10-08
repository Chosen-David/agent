from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[3];D=Path(__file__).parent

def cli(*a):
 r=subprocess.run(['python','-m','agent_runtime.knowledge','--root','knowledge',*a],cwd=R,capture_output=True,text=True,check=True)
 return json.loads(r.stdout)
queries=[{'prompt':'从很多冻结配置里挑平均误差最小的一个，怎样控制挑选后的总体误差？','query':'method 海选 选择偏差 总体 风险','domain':'probability-and-optimization'},{'prompt':'独立重复测量上比较多个滤波档位，如何给选中档位的平均失真作保证？','query':'传感器 滤波 档位 校准','domain':'probability-and-optimization'},{'prompt':'观察完这一批数据才造唯一规则，再按只有一个候选的样本区间认证它可以吗？','query':'候选 泄漏 多重选择','domain':'probability-and-optimization'}]
idx=R/'.agent-runs/math-selection-20261008/search.sqlite';cli('index','--db',str(idx));records=[]
for x in queries:
 for backend in ['files','sqlite']:
  result=cli('search',x['query'],'--domain',x['domain'],'--limit','3',*(['--index',str(idx)] if backend=='sqlite' else []))
  records.append({'input':x,'backend':backend,'result':result})
show=cli('show','math.finite-menu-selection');dep=cli('show','math.hoeffding-bounded-mean');refs=show['knowledge_refs']
(D/'knowledge-usage.json').write_text(json.dumps({'knowledge_root':'knowledge','knowledge_refs':refs,'retrieval':records,'loaded_ids':['math.finite-menu-selection','math.hoeffding-bounded-mean'],'assumptions':'frozen measurable losses, known ranges, iid sampling and no leakage checked manually; no model/refusal measurement','split':'all public developer queries'},ensure_ascii=False,indent=2)+'\n')
# Exact encoding of actual two CLI JSON outputs, not host context/billing.
try:
 import tiktoken
 enc=tiktoken.get_encoding('cl100k_base');n=sum(len(enc.encode(json.dumps(x,ensure_ascii=False))) for x in [show,dep])
except ImportError:n=None
(D/'cost.json').write_text(json.dumps({'retrieval_cli_calls':9,'formula':'1 index+6 search+2 show; excludes validation/test/host/web calls','body_package_cl100k_base_tokens':n,'measurement':'two complete serialized show outputs including prerequisite; not model billing','actual_model_AB_calls':0,'host_tokens':None,'quality_or_saving_claim':False},indent=2)+'\n')
scope=json.loads((D/'config.json').read_text())['scope']
def ref(p):return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
summary=json.loads((D/'summary.json').read_text());config=json.loads((D/'config.json').read_text())
manifest={'schema_version':'experiment-result/v1','result_id':'math-selection-20261008','producer_task_id':'MATH-33','producer_actor':'/root','validation_plan':ref(D/'validation-plan.json'),'scope':scope,'run_id':'math-selection-20261008','code_revision':'7e997b54348554553e287d3cf4069df791f69fb9 plus explicit file hashes','execution':{'command':['python doc/results/math-selection-20261008/verify.py','python doc/results/math-selection-20261008/finalize.py'],'environment_description':'CPU Python stdlib exact integer/Fraction; optional tiktoken encoding; no production/models','seeds':[config['seed']],'repeats':1},'artifacts':{'code':[ref(D/'verify.py'),ref(D/'finalize.py')]+[ref(p) for p in sorted((R/'agent_runtime').glob('knowledge*.py'))]+[ref(R/'agent_runtime/project_docs.py')],'inputs':[ref(R/'knowledge/entries'/f'{stem}.{ext}') for stem in ['math.finite-menu-selection','math.hoeffding-bounded-mean'] for ext in ['json','md']]+[ref(D/'retrieval-corpus.json'),ref(D/'research.json')],'config':[ref(D/'config.json')],'raw_data':[ref(D/'raw.json'),ref(D/'knowledge-usage.json')],'outputs':[ref(D/'summary.json'),ref(D/'cost.json')],'environment':[ref(D/'environment.json')]},'metrics':[{'name':'finite_assertions','value':summary['assertions'],'unit':'count'},{'name':'binomial_profiles','value':summary['exact_binomial_profiles'],'unit':'count'}]}
(D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
contract={k:manifest[k] for k in ['result_id','producer_task_id','producer_actor','validation_plan','scope']};contract['manifest_path']=str((D/'manifest.json').relative_to(R))
dag={'tasks':[{'task_id':'MATH-33','owner':'/root','action':'produce','produces_data':True,'task_type':'experiment','depends_on':[],'experiment_result':contract},{'task_id':'MATH-SELECTION-VERIFY','owner':'/root/selection_verifier','action':'verify_experiment_result','depends_on':['MATH-33'],'result_validation':contract},{'task_id':'MATH-34','owner':'/root','action':'publish','depends_on':['MATH-SELECTION-VERIFY'],'required_result_refs':[contract]}],'execution_boundary':'bounded direct host maintenance; independent collaboration call; not deployed tmux/ManagedEngine/ReviewSession'}
(D/'task-dag.json').write_text(json.dumps(dag,ensure_ascii=False,indent=2)+'\n')
print('manifest',hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest(),'show_tokens',n)
