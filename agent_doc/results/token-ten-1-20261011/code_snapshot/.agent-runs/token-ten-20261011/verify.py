"""Fixed trusted host verifier, bound BEFORE dispatch; never a data-selected executable."""
import importlib,os,subprocess
from common import *
from agent_runtime.token_usage import short_appserver_usage
from agent_runtime.result_validation import validate_result_plan
case=importlib.import_module(f'case_{MODE}')
def verify(root,manifest,plan):
 assert Path(root)==R
 for path,expected in read(B/'freeze.json')['hashes'].items():assert sha(R/path)==expected,path
 assert read(B/'freeze.json')['verifier_sha256']==sha(P/'verify.py')
 inv=read(B/'source-inventory.json')
 for row in inv['files']:assert sha(R/row['path'])==sha(R/row['archive_path'])==row['sha256']
 config=read(B/'config.json');assert sha(EXE)==config['binary_sha256'] and sha(Path.home()/'.codex/config.toml')==config['user_config_sha256']
 data=case.build(R);assert data['report']==REPORT and data['oracle']==ORACLE
 assert all((B/(n+'.prompt.txt')).read_text(encoding='utf-8')==data['prompts'][n] and len(data['prompts'][n])<=2200 for n in NAMES)
 threads=read(B/'threads.json');catalogs=read(B/'tool-catalogs.json');controls=[{k:v for k,v in threads[n].items() if k!='thread'} for n in NAMES]
 assert len({threads[n]['thread']['id'] for n in NAMES})==len(NAMES)
 assert all(c==controls[0] for c in controls) and not any(s['tools'] for servers in catalogs.values() for s in servers)
 rows=[];instructions=[]
 for name in NAMES:
  t=threads[name];tid=t['thread']['id'];assert t['cwd']==str(R) and t['model']=='gpt-6.1-sol' and t['reasoningEffort']=='high'
  assert t['approvalPolicy']=='never' and t['sandbox']=={'type':'readOnly','networkAccess':False}
  assert catalogs[name]==catalogs[NAMES[0]]
  raw=(PRIVATE/(name+'.original.rpc.jsonl')).read_bytes();red=read(B/(name+'.redaction.json'));assert hashlib.sha256(raw).hexdigest()==red['original_sha256']
  original=[json.loads(s) for s in raw.decode().splitlines()];public=[];removed=[]
  for line in raw.decode().splitlines():
   e=json.loads(line)
   if e.get('method')=='account/rateLimits/updated':
    h=hashlib.sha256(line.encode()).hexdigest();removed.append(h);e={'method':'private/rateLimits-notification','params':{'raw_sha256':h}}
   public.append(json.dumps(e,ensure_ascii=False))
  assert (B/(name+'.rpc.jsonl')).read_bytes()==('\n'.join(public)+'\n').encode() and removed==red['removed_line_sha256']
  assert not any(e.get('method')=='model/rerouted' for e in original)
  starts=[e['params']['turn'] for e in original if e.get('method')=='turn/started' and e['params'].get('threadId')==tid];assert len(starts)==1
  usage=short_appserver_usage(original,tid,starts[0]['id']);rows.append({'name':name,**usage});assert usage['total_tokens']<=25000
  answer=[e['params']['item']['text'] for e in original if e.get('method')=='item/completed' and e['params'].get('threadId')==tid and e['params']['item']['type']=='agentMessage']
  assert len(answer)==1 and json.loads(answer[0])==ORACLE==read(B/(name+'.answer.json'))
  history=read(B/(name+'.history.json'));assert len(history)==1 and history[0]['status']=='completed'
  quota=read(B/(name+'.quota.json'));assert quota['ordinary_allowed'] and quota['windows'] and all(0<=x['usedPercent']<90 for x in quota['windows'])
  instructions.append(envelopes(PRIVATE/(name+'.rollout.private.jsonl'),data['prompts'][name]))
 assert all(i==instructions[0] for i in instructions) and len(instructions[0])>=4
 assert rows==read(B/'usage.json')['observations'] and read(B/'dispatch.json')['freeze_sha256']==sha(B/'freeze.json')
 assert read(B/'dispatch.json')['max_paid_calls']==len(NAMES)==plan['controls']['max_invocations']
 b=sum(x['total_tokens'] for x in rows if x['name'].startswith('baseline'));c=sum(x['total_tokens'] for x in rows if x['name'].startswith('candidate'))
 assert b>c and b+c<=50000
 assert read(B/'outcome.json')=={'status':'pending-independent-validation','baseline_total':b,'candidate_total':c,'saving_tokens':b-c,'total_spent':b+c}
 assert {m['name']:m['value'] for m in manifest['metrics']}=={'baseline_total':b,'candidate_total':c,'saving':b-c,'paired_spend':b+c}
 expected=[{'request':n,'decision':ORACLE,'outcome':'handled'} for n in NAMES]
 assert read(B/'trace.json')==expected
 replay=case.replay(R);assert replay==read(B/'producer-cpu.json')['replay']
 assert os.getpid()!=read(B/'producer-cpu.json')['pid']
 p=subprocess.run([sys.executable,'-X','utf8','-m','unittest',*case.TESTS,'-q'],cwd=R,capture_output=True,text=True,encoding='utf-8',timeout=60)
 (B/'independent-tests.log').write_bytes((p.stdout+p.stderr).encode());assert p.returncode==0 and f'Ran {case.COUNT} tests' in p.stderr
 validate_result_plan(read(B/'task-chain.json'))
 dump(B/'independent-control.json',{'actor':'host-token-ten-reviewer','pid':os.getpid(),'replay':replay,'tests_passed':case.COUNT,'all_observable_non_task_controls_exact':True,'baseline_total':b,'candidate_total':c,'saving_tokens':b-c,'paid_spend':b+c})
 bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
 for group in manifest['artifacts'].values():
  for item in group:assert ref(R/item['path'])==item;bindings[item['path']]=item['sha256']
 review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(B/'manifest.json'),'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':manifest['scope'],
 'verifier':{'actor':'host-token-ten-reviewer','source':'fixed pre-dispatch-bound separately executed host verifier','run_id':f'TOK-TEN-{MODE}-verify','method':'native originals, exact observable controls, independent oracle/reconstruction and CPU replay','independent':True},
 'limitations':['One short fixture; no long-context, complete project, deployment/cash or universal savings claim.','All billed tested requests included; root chat, development and static review excluded.','Service internal prompt assembly is unobservable; observable full instructions/catalogs compared exactly.'],
 'checks':{k:{'verdict':'pass','reason':v['acceptance'],'evidence':[ref(B/'independent-control.json'),ref(B/'independent-tests.log')]} for k,v in plan['criteria'].items()}}
 dump(B/'independent-review.json',review);return review
if __name__=='__main__':
 assert not (B/'acceptance.json').exists()
 manifest=read(B/'manifest.json');plan=read(B/'validation-plan.json');review=verify(R,manifest,plan)
 from agent_runtime.result_store import ResultStore
 def fixed(root,m,p):
  assert Path(root)==R and m==manifest and p==plan
  for path,h in review['artifact_hashes'].items():assert sha(R/path)==h
  return review
 accepted=ResultStore(R).register(read(B/'contract.json'),verifier=fixed)['record']['validation_at_registration']
 dump(B/'acceptance.json',accepted);assert accepted['status']=='usable-with-scope',accepted['errors']
 print(json.dumps({'status':accepted['status'],'saving_tokens':read(B/'outcome.json')['saving_tokens'],'tests_passed':case.COUNT}))
