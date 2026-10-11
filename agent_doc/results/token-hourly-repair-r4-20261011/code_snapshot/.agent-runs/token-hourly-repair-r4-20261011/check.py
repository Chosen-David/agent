"""Prebound diagnostic producer and separately executed independent host verifier."""
import hashlib,json,os,platform,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=Path(__file__).parent;sys.path.insert(0,str(R))
REL='agent_doc/results/token-hourly-repair-r4-20261011';B=R/REL
SCOPE='r2 native health reused unchanged; generic guard log compatibility fixed with fresh CPU checks. Hourly repair CPU boundaries and one short native tool turn plus same-thread continuation; four archived failed-run observations only, no savings/full optimization/billing claim'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(B/n).write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
def read(n):return json.loads((B/n).read_bytes())
def ref(n):return {'path':REL+'/'+n,'sha256':sha(B/n)}
def sources():
 for row in read('inventory.json')['files']:
  assert sha(R/row['path'])==sha(R/row['archive_path'])==row['sha256'],row['path']
 assert sha(P/'check.py')==read('config.json')['fixed_host_sha256']
def tests(mode,full=False):
 args=[sys.executable,'-X','utf8','-m','unittest']+(['discover','-s','tests','-q'] if full else ['tests.test_token_optimizer','tests.test_crash_restart']+(['tests.test_managed_supervisor'] if mode=='independent' else [])+['-q'])
 p=subprocess.run(args,cwd=R,capture_output=True,text=True,encoding='utf-8',timeout=150)
 (B/(mode+'-tests.log')).write_bytes((p.stdout+p.stderr).encode());assert p.returncode==0,p.stderr[-1000:]
 dump(mode+'-environment.json',{'actor':mode,'pid':os.getpid(),'platform':platform.platform(),'python':sys.version,'command':args,'returncode':p.returncode})
def native_events(run):return [json.loads(x) for x in (run/'transport.private.jsonl').read_text(encoding='utf-8').splitlines()]
def summary(run):
 events=native_events(run);used=[];commands=[];terminal=[];final=[]
 for e in events:
  p=e.get('params',{})
  if e.get('method')=='thread/tokenUsage/updated':used.append(p['tokenUsage'])
  if e.get('method')=='turn/completed':terminal.append(p['turn']['status'])
  if e.get('method')=='item/completed':
   it=p['item']
   if it['type']=='commandExecution':commands.append({'command':it['command'],'output_chars':len(it.get('aggregatedOutput') or '')})
   if it['type']=='agentMessage':final.append(it.get('text',''))
 return {'original_transport_sha256':sha(run/'transport.private.jsonl'),'usage_snapshots':used,'commands':commands,'terminal':terminal,'last_message':final[-1] if final else None}
def freeze():
 assert not B.exists();B.mkdir(parents=True)
 files=['scripts/token_optimizer.py','tests/test_token_optimizer.py','agent_runtime/project_docs.py','config/role_registry.json','agent_runtime/task_supervisor.py','agent_runtime/crash_restart.py','tests/test_crash_restart.py','tests/test_managed_supervisor.py',str((P/'check.py').relative_to(R)).replace('\\','/'),str((P/'full_checks.py').relative_to(R)).replace('\\','/')]
 rows=[]
 for name in files:
  archive=REL+'/code_snapshot/'+name;p=R/archive;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((R/name).read_bytes())
  rows.append({'path':name,'archive_path':archive,'sha256':sha(p)})
 dump('inventory.json',{'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip(),'files':rows})
 dump('config.json',{'fixed_host_sha256':sha(P/'check.py'),'profile_version':'bounded-resumable-v1','max_observed_tokens_per_diagnostic_turn':75000,'paid_turns_max':0,'reused_paid_turns':2,'retries':0,'scope':SCOPE})
 dump('validation-plan.json',{'schema_version':'experiment-validation-plan/v1','scope':SCOPE,'criteria':{k:{'procedure':v,'acceptance':v,'allow_not_applicable':False} for k,v in {
 'implementation':'Independent source review and archived/current SHA equality; producer focused suite and independent complete required suite pass in source-bound isolated Linux checkout',
 'reference_boundary':'Actual Git Unicode/index edit detection, unchanged-publication denial, resume/latch/clock synthetic boundaries',
 'data_integrity':'Original private transport re-read independently and exact sanitized summaries; same native thread for two diagnostic turns',
 'numerical_sanity':'Counters finite integer, total=input+output, monotone cumulative; per-turn delta never sums cumulative snapshots',
 'measurement_validity':'Native completion and exact health outputs; no errors/reroutes/subagents; no savings or final bill assertion',
 'reproducibility':'Separate-owner Linux complete required rerun and exact original event reanalysis, not another paid model invocation'}.items()}})
 print('Frozen source, protocol and fixed verifier before diagnostic inference')
def produce():
 assert not (B/'manifest.json').exists();sources();tests('producer')
 original=R/'agent_doc/results/token-hourly-repair-r2-20261011'
 original_private=R/'.agent-runs/token-hourly-repair-r2-20261011'
 assert sha(R/'scripts/token_optimizer.py')==sha(original/'code_snapshot/scripts/token_optimizer.py')
 assert sha(R/'tests/test_token_optimizer.py')==sha(original/'code_snapshot/tests/test_token_optimizer.py')
 dump('reuse.json',{'source_result_id':original.name,'manifest_sha256':sha(original/'manifest.json'),'reason':'Native hourly source/profile/usage monitor unchanged; only generic supervisor crash log changed. No new model call.', 'source_snapshot_sha256':sha(original/'code_snapshot/scripts/token_optimizer.py')})
 receipts=[]
 for i in range(2):
  value=json.loads((original/('native-'+str(i)+'-receipt.json')).read_bytes())
  dump('native-'+str(i)+'-receipt.json',value)
  dump('native-'+str(i)+'-summary.json',summary(original_private/('native-'+str(i))))
  receipts.append(value)
 assert receipts[0]['thread_id']==receipts[1]['thread_id']
 historical=[]
 for run in sorted((R/'.agent-runs/token-optimizer-hourly').glob('*-tick')):
  if run.name in read('historical-inputs.json')['run_names']:
   historical.append({'run':run.name,**summary(run)})
 dump('historical-summaries.json',historical)
 contract={'result_id':B.name,'producer_task_id':'TOK-HOURLY-REPAIR-produce','producer_actor':'producer','manifest_path':REL+'/manifest.json','scope':SCOPE,'validation_plan':ref('validation-plan.json')}
 dump('contract.json',contract)
 manifest={'schema_version':'experiment-result/v1',**contract,'run_id':B.name,'code_revision':read('inventory.json')['revision']+'+archived-bound-working-tree','execution':{'command':[sys.executable,str(P/'check.py'),'producer'],'environment_description':'Reused Windows r2 native configured tool health/resumed turn, new focused CPU suite plus source-bound complete Linux suite; independent Linux complete required rerun/original reanalysis','seeds':['deterministic-no-rng'],'repeats':1},
 'artifacts':{'code':[{'path':r['archive_path'],'sha256':r['sha256']} for r in read('inventory.json')['files']],'inputs':[ref('historical-inputs.json'),ref('inventory.json'),ref('reuse.json')],'config':[ref('config.json')],'raw_data':[ref('producer-tests.log'),ref('native-0-summary.json'),ref('native-1-summary.json'),ref('historical-summaries.json')],'outputs':[ref('native-0-receipt.json'),ref('native-1-receipt.json')],'environment':[ref('producer-environment.json')]},'metrics':[{'name':'new_paid_turns','value':0,'unit':'count'}]}
 dump('manifest.json',manifest)
 dump('task-chain.json',{'tasks':[{'task_id':contract['producer_task_id'],'owner':'producer','action':'native_health','task_type':'experiment','experiment_result':contract},{'task_id':'TOK-HOURLY-REPAIR-verify','owner':'independent-host','action':'verify_experiment_result','depends_on':[contract['producer_task_id']],'result_validation':contract},{'task_id':'TOK-HOURLY-REPAIR-deploy','owner':'main-ai','action':'resume_single_timer','depends_on':['TOK-HOURLY-REPAIR-verify'],'required_result_refs':[contract]}]})
 print('Produced actual diagnostic, pending independent host verification')
def verify(root,manifest,plan):
 assert Path(root)==R;sources();from full_checks import full_suite;full_suite(R,B,read('inventory.json'))
 original=R/'agent_doc/results/token-hourly-repair-r2-20261011'
 assert sha(original/'manifest.json')==read('reuse.json')['manifest_sha256']
 assert sha(R/'scripts/token_optimizer.py')==sha(original/'code_snapshot/scripts/token_optimizer.py')==read('reuse.json')['source_snapshot_sha256']
 assert read('producer-environment.json')['pid']!=read('independent-environment.json')['pid']
 from scripts.token_optimizer import observe_parent_turn
 import queue
 receipts=[read('native-'+str(i)+'-receipt.json') for i in range(2)]
 for i in range(2):
  run=R/'.agent-runs/token-hourly-repair-r2-20261011'/('native-'+str(i));s=summary(run);assert s==read('native-'+str(i)+'-summary.json')
  assert s['terminal']==['completed'];assert s['last_message']==('HOURLY_REPAIR_OK' if i==0 else 'HOURLY_RESUME_OK')
  events=native_events(run)
  assert not any(e.get('method') in ('error','model/rerouted') for e in events)
  assert len(s['commands'])==(1 if i==0 else 0)
  assert all(e.get('params',{}).get('item',{}).get('type') not in ('collabAgentToolCall','mcpToolCall') for e in events)
  matching=[e for e in events if e.get('params',{}).get('threadId')==receipts[i]['thread_id'] and e.get('method') in ('thread/tokenUsage/updated','turn/completed')]
  replay=P/('independent-replay-'+str(i));replay.mkdir()
  r=observe_parent_turn(queue.Queue(),matching,receipts[i]['thread_id'],receipts[i]['turn_id'],replay,lambda *args:(_ for _ in ()).throw(AssertionError('unexpected interrupt')),timeout_seconds=1,max_observed_tokens=75000,initial_total_tokens=receipts[i-1]['thread_total_tokens'] if i else 0)
  for k in ('status','observed_parent_total_tokens','thread_total_tokens','initial_total_tokens'):assert r[k]==receipts[i][k],k
 assert receipts[0]['thread_id']==receipts[1]['thread_id']
 for row in read('historical-summaries.json'):
  assert row=={'run':row['run'],**summary(R/'.agent-runs/token-optimizer-hourly'/row['run'])}
 from agent_runtime.result_validation import validate_result_plan
 validate_result_plan(read('task-chain.json'))
 bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
 for group in manifest['artifacts'].values():
  for item in group:assert sha(R/item['path'])==item['sha256'];bindings[item['path']]=item['sha256']
 review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(B/'manifest.json'),'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':SCOPE,'verifier':{'actor':'independent-host','independent':True,'source':'fixed pre-dispatch-bound separate WSL process','run_id':'TOK-HOURLY-REPAIR-verify','method':'Independent frozen source/boundary rerun and original native transport reanalysis'},'limitations':['This health diagnostic is not a completed optimization or token-saving success.','Observed parent snapshots are not a certified final/cross-actor bill.','tmux protects detachment only; shutdown/reboot and network outages remain external.'],'checks':{k:{'verdict':'pass','reason':v['acceptance'],'evidence':[ref('independent-environment.json'),ref('independent-tests.log'),ref('native-0-summary.json'),ref('native-1-summary.json')]} for k,v in plan['criteria'].items()}}
 dump('independent-review.json',review);return review
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='freeze':freeze()
 elif mode=='producer':produce()
 elif mode=='verify':
  assert not (B/'acceptance.json').exists()
  m=read('manifest.json');p=read('validation-plan.json');review=verify(R,m,p)
  from agent_runtime.result_store import ResultStore
  def fixed(root,manifest,plan):
   assert Path(root)==R and manifest==m and plan==p
   for path,h in review['artifact_hashes'].items():assert sha(R/path)==h
   return review
  accepted=ResultStore(R).register(read('contract.json'),verifier=fixed)['record']['validation_at_registration'];dump('acceptance.json',accepted)
  assert accepted['status']=='usable-with-scope',accepted['errors'];print('Independent diagnostic usable-with-scope; zero repeated paid checks')
 else:raise ValueError('known fixed mode required')
