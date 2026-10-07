from pathlib import Path
import json,hashlib,subprocess,time
r=Path('.');d=r/'doc/results/math-weighted-bilinear-20261007';ID='math.weighted-bilinear-low-rank'
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def ref(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
commands=[]
def cli(args):
 t=time.perf_counter();p=subprocess.run(['python','-m','agent_runtime.knowledge','--root','knowledge',*args],capture_output=True,text=True)
 assert p.returncode==0,p.stderr
 commands.append({'arguments':args,'duration_seconds':time.perf_counter()-t,'returncode':p.returncode})
 return json.loads(p.stdout)
idx='.knowledge-cache/weighted-bilinear.sqlite';cli(['index','--db',idx])
qs=[('score','query key score compression'),('sensor','传感器 响应 双线性'),('dependent','双侧 二阶矩 相关'),('singular','双侧 二阶矩 不可逆')]
results=[]
for backend in ['files','sqlite']:
 for case,q in qs:
  args=['search',q,'--limit','3']
  if backend=='sqlite':args+=['--index',idx]
  out=cli(args);results.append({'case':case,'query':q,'backend':backend,'ids':[z['id'] for z in out['results']],'decision':'human prerequisite review; no LLM run'})
show=cli(['show',ID]);put(d/'knowledge-usage.json',{'knowledge_root':'knowledge','knowledge_refs':show['knowledge_refs'],'retrieval':results,'queries_are':'public development; English/Chinese structure extraction is manual'})
try:
 import tiktoken
 text=json.dumps(show,ensure_ascii=False)
 tokens=len(tiktoken.get_encoding('cl100k_base').encode(text))
except ImportError:tokens=None
put(d/'cost.json',{'commands':commands,'tool_processes':len(commands),'local_encoder':'cl100k_base' if tokens else 'unavailable','single_show_tokens':tokens,'single_show_characters':len(json.dumps(show,ensure_ascii=False)),'scope':'local encoding estimate, not host tokenizer/bill or performance savings','model_AB_calls':0,'host_token_cost':'unknown'})
put(d/'holdout-protocol.json',{'status':'not-run','reserve':'independent document/model requests not loaded by developer; future holder chooses undisclosed cases before candidate freeze','required_cases':['unnamed bilinear compression','cross-domain sensor response','correlated or singular premise trap'],'acceptance':'correct retrieval AND premise acceptance/refusal AND derivation; same model/tools/budget baseline comparison','public_cases':'all config.json and verify.py fixtures are now development data; never rebrand as unseen'})
put(d/'research.json',{'accessed':'2026-10-07','RoLA':{'version':'2609.06712v3','revised':'2026-09-21','status':'arXiv preprint; no formal venue verified','url':'https://arxiv.org/html/2609.06712v3','read':'§4.1–4.4, §9.1 structural identity; targeted, not full experiment replication','takeaway':'separate learned position-free low-rank features then apply retained rotary pairs; relative geometry of this branch is not original dense softmax equivalence','decision':'defer direct adoption; video-DiT global linear branch differs from autoregressive decoder indexer'},'SALS':{'version':'2510.24273v1','submitted':'2025-10-28','status':'arXiv preprint; no formal venue verified','url':'https://arxiv.org/html/2510.24273v1','read':'§3.1–3.2,§4.1,§7 targeted','takeaway':'pre-RoPE latent token selection followed by selected reconstruction and RoPE; observed rank increase is not universal theorem; OS named overlap in §3.2 is retained probability mass','decision':'adapt reconstruction/position accounting as comparison design; no reproduction or production modification'}})
contract={'result_id':'math-weighted-bilinear-20261007','producer_task_id':'MATH-29','producer_actor':'/root','manifest_path':str(d/'manifest.json'),'validation_plan':ref(d/'validation-plan.json'),'scope':json.loads((d/'validation-plan.json').read_text())['scope']}
put(d/'task-dag.json',{'tasks':[{'task_id':'MATH-29','owner':'/root','action':'produce','depends_on':[],'experiment_result':contract},{'task_id':'MATH-WEIGHTED-VERIFY','owner':'/root/weighted_bilinear_verifier','action':'verify_experiment_result','depends_on':['MATH-29'],'result_validation':contract},{'task_id':'MATH-30','owner':'/root','action':'publish','depends_on':['MATH-WEIGHTED-VERIFY'],'required_result_refs':[contract]}],'execution_boundary':'bounded direct host maintenance with actual independent collaboration call; not ManagedEngine or authenticated ReviewSession deployment'})
summary=json.loads((d/'summary.json').read_text())
put(d/'manifest.json',{'schema_version':'experiment-result/v1',**{k:v for k,v in contract.items() if k!='manifest_path'},'run_id':'math-weighted-bilinear-20261007','code_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'execution':{'command':['python doc/results/math-weighted-bilinear-20261007/verify.py','python .agent-runs/math-weighted-bilinear-20261007/finalize_inputs.py'],'environment_description':'CPU NumPy float64; file and SQLite structural retrieval; no model/GPU','seeds':[291007],'repeats':1},'artifacts':{'code':[ref(d/'verify.py'),ref(r/f'knowledge/entries/{ID}.md'),ref(r/f'knowledge/entries/{ID}.json')],'inputs':[ref(d/'prior-results.json'),ref(d/'knowledge-usage.json'),ref(d/'research.json')],'config':[ref(d/'config.json')],'raw_data':[ref(d/'raw.json')],'outputs':[ref(d/'summary.json'),ref(d/'cost.json'),ref(d/'holdout-protocol.json')],'environment':[ref(d/'environment.json')]},'metrics':[{'name':'finite_assertions','value':summary['finite_assertions'],'unit':'count'}]})
print(json.dumps({'retrieval':results,'single_show_tokens':tokens,'contract':contract},ensure_ascii=False))
