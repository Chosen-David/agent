"""Fixed CPU producer / distinct owner host verifier. No model inference."""
import hashlib,json,os,platform,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=Path(__file__).parent;sys.path.insert(0,str(R))
REL='agent_doc/results/token-five-hourly-cpu-20261011';B=R/REL
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((B/n).read_bytes())
def dump(n,v):(B/n).write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
def ref(n):return {'path':REL+'/'+n,'sha256':sha(B/n)}
def source_check():
 for row in read('source-inventory.json')['files']:assert sha(R/row['path'])==sha(R/row['archive_path'])==row['sha256']
 assert sha(P/'scheduler_cpu.py')==read('config.json')['host_verifier_sha256']
def checks(mode):
 source_check()
 tests=['tests.test_token_optimizer']
 p=subprocess.run([sys.executable,'-X','utf8','-m','unittest',*tests,'-q'],cwd=R,capture_output=True,text=True,encoding='utf-8',timeout=60)
 (B/(mode+'-tests.log')).write_bytes((p.stdout+p.stderr).encode());assert p.returncode==0 and 'Ran 8 tests' in p.stderr
 value={'actor':'native-hourly-cpu-producer' if mode=='producer' else 'host-hourly-cpu-reviewer','pid':os.getpid(),'platform':platform.platform(),'tests_passed':8,'model_requests':0}
 if mode=='producer':
  from scripts.token_optimizer import run_worker
  probe=P/'scheduler-probe';assert not probe.exists();probe.mkdir()
  exe=R/'.agent-runs/engineering-kb/tools/codex.exe';assert sha(exe)==read('config.json')['binary_sha256']
  result=run_worker(R,exe,probe,probe_only=True);assert result['model_requests']==0 and result['status'] in ('probe-only','quota-blocked')
  dump('native-probe.json',result)
 else:
  modules=['tests.test_project_docs_workflow','tests.test_project_docs_init','tests.test_project_docs_acceptance','tests.test_task_manifest']
  p=subprocess.run([sys.executable,'-X','utf8','-m','unittest',*modules,'-q'],cwd=R,capture_output=True,text=True,encoding='utf-8',timeout=60)
  (B/'independent-regression.log').write_bytes((p.stdout+p.stderr).encode());assert p.returncode==0 and 'Ran 104 tests' in p.stderr
  value['regression_tests_passed']=104
 dump(mode+'-checks.json',value);return value
def bind():
 inv=read('source-inventory.json');plan=read('validation-plan.json')
 contract={'result_id':B.name,'producer_task_id':'TOK-HOURLY-produce','producer_actor':'native-hourly-cpu-producer','manifest_path':REL+'/manifest.json','scope':plan['scope'],'validation_plan':ref('validation-plan.json')}
 dump('contract.json',contract)
 dump('manifest.json',{'schema_version':'experiment-result/v1',**contract,'run_id':B.name,'code_revision':inv['revision']+'+archived-sha256-bound-working-tree','execution':{'command':['C:/Python312/python.exe','.agent-runs/token-five-20261011/scheduler_cpu.py','producer'],'environment_description':'Windows8 CPU cases/real quota-only backend probe; independent Linux8+104 regression cases','seeds':['deterministic-no-rng'],'repeats':1},
 'artifacts':{'code':[{'path':r['archive_path'],'sha256':r['sha256']} for r in inv['files']],'inputs':[ref('source-inventory.json')],'config':[ref('config.json')],'raw_data':[ref('producer-tests.log')],'outputs':[ref('producer-checks.json'),ref('native-probe.json')],'environment':[ref('producer-checks.json')]},'metrics':[{'name':'tests_passed','value':8,'unit':'count'},{'name':'model_requests','value':0,'unit':'count'}]})
 dump('task-chain.json',{'tasks':[{'task_id':'TOK-HOURLY-produce','owner':'native-hourly-cpu-producer','action':'cpu_and_quota_probe','task_type':'experiment','experiment_result':contract},
 {'task_id':'TOK-HOURLY-verify','owner':'host-hourly-cpu-reviewer','action':'verify_experiment_result','depends_on':['TOK-HOURLY-produce'],'result_validation':contract},
 {'task_id':'TOK-HOURLY-deploy','owner':'main-ai','action':'deploy_hourly_timer','depends_on':['TOK-HOURLY-verify'],'required_result_refs':[contract]}]})
def verify(root,manifest,plan):
 assert Path(root)==R
 current=checks('independent');assert current['pid']!=read('producer-checks.json')['pid']
 raw=(P/'scheduler-probe/transport.private.jsonl').read_text(encoding='utf-8')
 events=[json.loads(l) for l in raw.splitlines()]
 assert not any(e.get('method','').startswith(('turn/','thread/')) for e in events)
 quota=[e['result'] for e in events if e.get('id')==2];assert len(quota)==1
 from scripts.token_optimizer import quota_admission
 assert read('native-probe.json')['admission']==quota_admission(quota[0])
 assert read('native-probe.json')['model_requests']==0
 from agent_runtime.result_validation import validate_result_plan
 validate_result_plan(read('task-chain.json'))
 bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
 for group in manifest['artifacts'].values():
  for item in group:assert sha(R/item['path'])==item['sha256'];bindings[item['path']]=item['sha256']
 review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(B/'manifest.json'),'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':manifest['scope'],
 'verifier':{'actor':'host-hourly-cpu-reviewer','source':'fixed pre-dispatch-bound separately executed WSL CPU host','run_id':'TOK-HOURLY-verify','method':'current/archive source equality,8+104 actual CPU regression and original zero-inference probe readback','independent':True},
 'limitations':['No new token saving success, paid hourly optimization, model quality or hard cash-cap claim.','Timer liveness/deployment is verified separately operationally; reboot/shutdown is outside tmux guarantees.','Parent cumulative usage excludes separately billed child benchmark calls; in-flight overshoot possible.'],
 'checks':{k:{'verdict':'pass','reason':v['acceptance'],'evidence':[ref('independent-checks.json'),ref('independent-tests.log'),ref('independent-regression.log')]} for k,v in plan['criteria'].items()}}
 dump('independent-review.json',review);return review
if __name__=='__main__':
 if sys.argv[1]=='producer':
  assert not (B/'producer-checks.json').exists();checks('producer');bind();print('CPU8 and real native quota probe complete, zero inference; pending independent gate')
 elif sys.argv[1]=='verify':
  assert not (B/'acceptance.json').exists()
  manifest=read('manifest.json');plan=read('validation-plan.json');review=verify(R,manifest,plan)
  from agent_runtime.result_store import ResultStore
  def fixed(root,m,p):
   assert Path(root)==R and m==manifest and p==plan
   for path,h in review['artifact_hashes'].items():assert sha(R/path)==h
   return review
  accepted=ResultStore(R).register(read('contract.json'),verifier=fixed)['record']['validation_at_registration'];dump('acceptance.json',accepted)
  assert accepted['status']=='usable-with-scope',accepted['errors'];print('usable-with-scope: Windows8 / Linux8+104 CPU cases; zero additional model requests')
 else:raise ValueError('known producer/reviewer modes only')
