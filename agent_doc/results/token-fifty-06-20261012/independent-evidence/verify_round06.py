import pathlib,json,hashlib,sys,os,re
ROOT=pathlib.Path.cwd();B=ROOT/'agent_doc/results/token-fifty-06-20261012';P=ROOT/'.agent-runs/token-fifty-06/06-private';O=ROOT/'.agent-runs/token-fifty-06/reviews'
sys.path.insert(0,str(ROOT));sys.dont_write_bytecode=True
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
rows=lambda p:[json.loads(l) for l in p.read_text(encoding='utf-8').splitlines()]
def dump(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
manifest=read(B/'manifest.json');plan=read(B/'validation-plan.json');freeze=read(B/'freeze.json');inventory=read(B/'source-inventory.json');hashes={}
assert sha(B/'validation-plan.json')==manifest['validation_plan']['sha256']=='b2c7650ee1e0d89f18f180355e9be51dba7a09d45c2160ec4effdb77f196a130'
assert sha(B/'task-chain.json')=='63e6f6525332e263acfd52e74c2d55ce96d3bc071cdcb9936377ce78c23edf64'
for group in manifest['artifacts'].values():
 for x in group:assert sha(ROOT/x['path'])==x['sha256'],x['path'];hashes[x['path']]=x['sha256']
for p,h in freeze['hashes'].items():assert sha(ROOT/p)==h,p
for x in inventory['files']:assert sha(ROOT/x['path'])==x['sha256']==sha(ROOT/x['archive_path']),x['path']
assert len(inventory['files'])==15
raw=(B/'fixture.md').read_bytes();text=raw.decode('utf8')
assert raw==(ROOT/'.agent-runs/token-fifty-06/fixture.md').read_bytes()
parts=text.split('\n');lines=[p+'\n' for p in parts[:-1]]+([parts[-1]] if parts[-1] else [])
assert len(lines)==65 and len(set(lines))==34
ids=re.findall(r'^Issue-(\d{3}): status=(\w+); owner=reviewer-(\d+)\.$',text,re.M)
assert ids==[(f'{i:03}','pending',str(i%3)) for i in range(32)]
assert text.startswith('Global: all advice remains pending current independent verification; metric_unit=tokens; publication blocked.\n')
oracle={'issue_ids':['Issue-'+x[0] for x in ids],'issue_count':len(ids),'last_status':ids[-1][1],'unit':'tokens','publish':False};assert oracle==read(B/'oracle.json')
packets=read(B/'packets.json');ba=packets['baseline'];ca=packets['candidate']
wire=lambda v:json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'))
assert ba['encoding']=='full' and ca['encoding']=='dictionary' and ba['text'].encode()==raw
assert ba['source']==ca['source']=={'path':str((B/'fixture.md').relative_to(ROOT)).replace('\\','/'),'sha256':sha(B/'fixture.md')}
assert ba['project_root']==ca['project_root']==str(ROOT) and ba['scope']==ca['scope']
table=[];order=[]
for line in lines:
 if line not in table:table.append(line)
 order.append(table.index(line))
assert ca['dictionary']==table and ca['order']==order and b''.join(ca['dictionary'][i].encode() for i in ca['order'])==raw
from agent_runtime.text_dictionary import restore_text_view,text_view
for packet in (ba,ca):assert restore_text_view(ROOT,wire(packet),**{'path':ba['source']['path'],'expected_sha256':ba['source']['sha256']}).encode()==raw
assert text_view(ROOT,ba['source']['path'],ba['source']['sha256'],full=True)==ba
assert text_view(ROOT,ba['source']['path'],ba['source']['sha256'])==ca
prefixes=[]
for name,packet in packets.items():
 prompt=(B/(name+'.prompt.txt')).read_text(encoding='utf8');assert prompt.endswith(wire(packet));prefixes.append(prompt[:-len(wire(packet))])
assert prefixes[0]==prefixes[1]
preflight=read(O/'round06-preflight-review.json');pc=read(O/'round06-preflight-control.json')
assert preflight['decision']=='approve' and pc['tests']['unique']==pc['tests']['passed']==16 and pc['tests']['skipped']==0
for p,h in preflight['source_hashes'].items():assert sha(ROOT/p)==h,p
for e in preflight['evidence']:assert sha(ROOT/e['path'])==e['sha256'],e['path']
assert sha(O/'round06-preflight-tests.raw')==pc['tests']['raw_sha256']
assert sha(O/'round06-preflight-tests.log')==pc['tests']['log_sha256']
assert 'Ran 16 tests' in (O/'round06-preflight-tests.log').read_text() and '\nOK' in (O/'round06-preflight-tests.log').read_text()
assert (B/'producer-tests.log').read_bytes()==(O/'round06-preflight-tests.log').read_bytes()
profile=read(B/'native-profile.json');assert sha(B/'native-profile.json')==plan['profile_sha256']=='2cef2a6c80a06dac5b885b2974c50ce8ed93fca5ce08f2e839ca413e3e5c8516'
assert sha(B/'ThreadStartParams.json')==profile['schema_sha256']=='80a40a7fac15b4bf70efb7f893fb353acc0a0d30c68f54aee4f01923deca85de'
assert len(profile['baseInstructions'])==308
assert read(B/'schema.json')['properties']['issue_ids']['maxItems']>=32
stats={}; rollouts={}; orig_hashes={}; public_hashes={}
for name in ('baseline','candidate'):
    private=P/(name+'.original.rpc.jsonl'); raw_lines=private.read_text(encoding='utf-8').splitlines(); original=[json.loads(l) for l in raw_lines]; public=rows(B/(name+'.rpc.jsonl')); redaction=read(B/(name+'.redaction.json'))
    assert len(original)==len(public) and sha(private)==redaction['original_sha256']
    removed=[]
    for line,event,shown in zip(raw_lines,original,public):
        if event.get('method')=='account/rateLimits/updated':
            h=hashlib.sha256(line.encode()).hexdigest();removed.append(h); assert shown=={'method':'private/rateLimits-notification','params':{'raw_sha256':h}}
        else:assert shown==event
    assert removed==redaction['removed_line_sha256']
    updates=[e['params'] for e in original if e.get('method')=='thread/tokenUsage/updated']; assert len(updates)==1
    u=updates[0]; total=u['tokenUsage']['total']; assert total==u['tokenUsage']['last']
    assert all(type(v) is int and v>=0 for v in total.values());assert total['totalTokens']==total['inputTokens']+total['outputTokens'];assert total['reasoningOutputTokens']<=total['outputTokens']
    assert total['totalTokens']<=25000
    completed=[e['params'] for e in original if e.get('method')=='turn/completed'];assert len(completed)==1 and completed[0]['turn']['status']=='completed' and completed[0]['turn']['error'] is None
    assert completed[0]['threadId']==u['threadId'] and completed[0]['turn']['id']==u['turnId']
    assert not any(e.get('method') in ('model/rerouted','error') for e in original)
    finished=[e['params']['item'] for e in original if e.get('method')=='item/completed'];assert all(e['type'] in ('userMessage','reasoning','agentMessage') for e in finished)
    answers=[x['text'] for x in finished if x['type']=='agentMessage'];assert len(answers)==1 and json.loads(answers[0])==oracle==read(B/(name+'.answer.json'))
    history=read(B/(name+'.history.json'));assert len(history)==1 and history[0]['id']==u['turnId'] and history[0]['status']=='completed'
    user=[x for x in history[0]['items'] if x['type']=='userMessage'];assert len(user)==1 and user[0]['content'][0]['text']==(B/(name+'.prompt.txt')).read_text(encoding='utf-8')
    quota=read(B/(name+'.quota.json'));assert quota['ordinary_allowed'] is True and quota['windows'] and all(0<=v['usedPercent']<90 for v in quota['windows'])
    rr=rows(P/(name+'.rollout.private.jsonl'));rollouts[name]=rr
    recorded=[x['payload'] for x in rr if x['type']=='token_usage_record'];assert len(recorded)==1
    assert recorded[0]['usage']['total_tokens']==total['totalTokens'] and recorded[0]['usage']['input_tokens']==total['inputTokens'] and recorded[0]['usage']['output_tokens']==total['outputTokens']
    stats[name]={'input':total['inputTokens'],'output':total['outputTokens'],'reasoning_in_output':total['reasoningOutputTokens'],'total':total['totalTokens'],'cached_input':total['cachedInputTokens'],'thread_id':u['threadId'],'turn_id':u['turnId']}
    orig_hashes[name]=sha(private);public_hashes[name]=sha(B/(name+'.rpc.jsonl'))
assert stats['baseline']['thread_id']!=stats['candidate']['thread_id']
assert stats['baseline']['total']>stats['candidate']['total'] and sum(v['total'] for v in stats.values())<=50000
full=rows(P/'native-rpc.private.jsonl');assert sum(e.get('method')=='turn/started' for e in full)==2 and sum(e.get('method')=='turn/completed' for e in full)==2
assert sum(e.get('method')=='thread/started' for e in full)==2
def msgs(rr):return [x['payload'] for x in rr if x['type']=='response_item' and x['payload'].get('type')=='message' and x['payload'].get('role')!='assistant']
a,b=msgs(rollouts['baseline']),msgs(rollouts['candidate']);assert len(a)==len(b)==5
for x,y in zip(a[:-1],b[:-1]):
    assert x['role']==y['role'] and x['content']==y['content']
    mx=x['internal_chat_message_metadata_passthrough'];my=y['internal_chat_message_metadata_passthrough'];assert {k:v for k,v in mx.items() if k not in ('turn_id','create_time')}=={k:v for k,v in my.items() if k not in ('turn_id','create_time')}
for name,m in (('baseline',a),('candidate',b)):assert m[-1]['content']==[{'type':'input_text','text':(B/(name+'.prompt.txt')).read_text(encoding='utf-8')}]
assert rollouts['baseline'][0]['payload']['base_instructions']==rollouts['candidate'][0]['payload']['base_instructions']
def turn(rr):return {k:v for k,v in next(x['payload'] for x in rr if x['type']=='turn_context').items() if k not in ('turn_id','root_turn_id')}
assert turn(rollouts['baseline'])==turn(rollouts['candidate'])
assert [x['payload'] for x in rollouts['baseline'] if x['type']=='world_state']==[x['payload'] for x in rollouts['candidate'] if x['type']=='world_state']
threads=read(B/'threads.json');assert {k:v for k,v in threads['baseline'].items() if k!='thread'}=={k:v for k,v in threads['candidate'].items() if k!='thread'}
tools=read(B/'tool-catalogs.json');assert tools['baseline']==tools['candidate'] and not any(x['tools'] for x in tools['baseline'])
environment=read(B/'environment.json');config=read(B/'config.json');binary=pathlib.Path('C:/Users/WI/Desktop/home_work/AI_LLM/agent/.agent-runs/engineering-kb/tools/codex.exe')
assert sha(binary)==environment['binary_sha256']==config['binary_sha256'];assert sha(pathlib.Path.home()/'.codex/config.toml')==config['user_config_sha256']
priorpath=ROOT/'.agent-runs/token-fifty-04/04-private/baseline.rollout.private.jsonl'
prior=rows(priorpath);pm=msgs(prior);assert len(pm)==5
for old,new in zip(pm[:-1],a[:-1]):assert old['role']==new['role'] and old['content']==new['content']
assert turn(prior)==turn(rollouts['baseline'])
for rr in rollouts.values():
    assert rr[0]['payload']['base_instructions']['text']==profile['baseInstructions']
    assert rr[0]['payload']['base_instructions']['provenance']=={'type':'custom'}
settings=read(B/'settings.json');assert settings['baseInstructions']==profile['baseInstructions'] and settings['developerInstructions']==profile['developerInstructions']==None
assert all(len((B/(name+'.prompt.txt')).read_text(encoding='utf-8'))<=14000 for name in stats)
assert sum(e.get('method')=='model/rerouted' or e.get('method')=='error' for e in full)==0

quota_results=[e['result'] for e in full if isinstance(e.get('result'),dict) and 'ordinaryUsageAllowed' in e['result']]
assert len(quota_results)==3
for result in quota_results:
 assert result['ordinaryUsageAllowed'] is True
 windows=[]
 for limit in (result.get('rateLimitsByLimitId') or {'default':result.get('rateLimits',{})}).values():
  assert not limit.get('spendControlReached')
  for key in ('primary','secondary'):
   value=limit.get(key)
   if value:assert type(value['usedPercent']) in (int,float) and 0<=value['usedPercent']<90;windows.append({'window':key,'usedPercent':value['usedPercent']})
 assert windows
for e in full:
 if e.get('method')=='account/rateLimits/updated':
  for limit in [e['params'].get('rateLimits',{})]:
   assert not limit.get('spendControlReached')
   for key in ('primary','secondary'):
    value=limit.get(key)
    if value:assert 0<=value['usedPercent']<90
assert read(B/'dispatch.json')['retries']==0 and read(B/'dispatch.json')['max_paid_calls']==2
expected={'baseline_total':stats['baseline']['total'],'candidate_total':stats['candidate']['total'],'saving':stats['baseline']['total']-stats['candidate']['total'],'paired_spend':sum(x['total'] for x in stats.values())}
assert {m['name']:m['value'] for m in manifest['metrics']}==expected and all(m['unit']=='tokens' for m in manifest['metrics'])
outcome=read(B/'outcome.json');assert outcome['baseline_total']==expected['baseline_total'] and outcome['candidate_total']==expected['candidate_total'] and outcome['saving_tokens']==expected['saving'] and outcome['total_spent']==expected['paired_spend']
control={'actor':'/root/token_review','manifest_sha256':sha(B/'manifest.json'),'all_manifest_frozen_source_archive_hashes_match':True,'source_files':len(inventory['files']),'independently_derived_oracle':oracle,'all65physicalLF_indexes_all32IDs_and_complete_source_bytes_restored':True,'dictionary_canonical_first_occurrence_exact':True,'same_question_only_representation_changed':True,'all_original_public_events_verified':True,'original_rpc_hashes':orig_hashes,'public_rpc_hashes':public_hashes,'observed_usage':stats,'saving_tokens':expected['saving'],'paired_spend_tokens':expected['paired_spend'],'same_non_task_plaintext_messages':4,'four_protected_messages_exact_previous_round04':True,'previous_round04_rollout_sha256':sha(priorpath),'current_rollout_sha256':{n:sha(P/(n+'.rollout.private.jsonl')) for n in stats},'explicit_custom_base_exact_frozen_profile':True,'profile_sha256':sha(B/'native-profile.json'),'profile_no_causal_saving_claim':True,'permission_model_turn_context_exact_previous_round04':True,'base_world_turn_context_equal':True,'settings_catalog_equal':True,'distinct_fresh_threads':True,'actual_completed_calls':2,'no_tools_retries_rerouting':True,'original_quotas_below90':True,'private_quota_response_count':len(quota_results),'binary_and_user_config_unchanged':True,'tests_unique_cases':16,'reused_preflight16':True,'implementation_scope':'Exact whole physical-LF-line dictionary/ordered canonical indexes/complete UTF8 bytes and all statuses/rules/units; no selection, scientific acceptance, meeting closure or workflow/netcost claim. Existing reference decoder is used only for _wire/_json/_budget helpers; unrelated reference-view expansion correctness issue is outside this measured call chain and frozen evidence remains unchanged.'}
dump(O/'round06-independent-control.json',control)
print(json.dumps({'decision':'pass','manifest_sha256':sha(B/'manifest.json'),'saving_tokens':expected['saving'],'paired_spend':expected['paired_spend'],'source_files':len(inventory['files']),'usage':{n:{k:v for k,v in x.items() if k not in ('thread_id','turn_id')} for n,x in stats.items()}}))
