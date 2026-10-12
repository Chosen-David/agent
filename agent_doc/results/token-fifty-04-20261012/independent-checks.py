import pathlib,json,hashlib,subprocess,sys,os
ROOT=pathlib.Path.cwd(); B=ROOT/'agent_doc/results/token-fifty-04-20261012'; P=ROOT/'.agent-runs/token-fifty-04/04-private'; O=ROOT/'.agent-runs/token-fifty-04/reviews'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def rows(p):return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines()]
def dump(p,v):p.open('x',encoding='utf-8').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
manifest=read(B/'manifest.json'); plan=read(B/'validation-plan.json'); freeze=read(B/'freeze.json'); inventory=read(B/'source-inventory.json'); hashes={}
assert sha(B/'validation-plan.json')==manifest['validation_plan']['sha256']
for group in manifest['artifacts'].values():
    for x in group:
        assert sha(ROOT/x['path'])==x['sha256'],x['path']; hashes[x['path']]=x['sha256']
for path,h in freeze['hashes'].items():assert sha(ROOT/path)==h,path
for x in inventory['files']:assert sha(ROOT/x['path'])==x['sha256']==sha(ROOT/x['archive_path']),x['path']
fixture=(B/'fixture.json').read_bytes();original=json.loads(fixture);coords=original['coordinates'];assert len(coords)==64 and all(type(x) is int for x in coords)
assert original['current_status']=='pending' and 'independent verification' in original['global_rule']
assert all(coords[i+1]-coords[i]==coords[1]-coords[0] for i in range(len(coords)-1))
oracle={'coordinate_count':len(coords),'first':coords[0],'last':coords[-1],'step':coords[1]-coords[0],'publish':False,'unit':original['metric_unit']};assert oracle==read(B/'oracle.json')
packets=read(B/'packets.json');ca=packets['candidate'];ba=packets['baseline']
wire=lambda v:json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'))
assert ba['encoding']=='full' and ca['encoding']=='arithmetic' and wire(ba['data'])==wire(original)
assert ba['source']==ca['source'] and ca['source']['sha256']==sha(B/'fixture.json') and ba['project_root']==ca['project_root']==str(ROOT)
import copy
independent=copy.deepcopy(ca['data']);grid=independent['coordinates'];independent['coordinates']=[grid['start']+i*grid['step'] for i in range(grid['count'])];assert wire(independent)==wire(original)
from agent_runtime.grid_context import restore_grid_view,grid_view
for packet in (ca,ba):assert wire(restore_grid_view(ROOT,wire(packet),packet['source']['path'],packet['source']['sha256']))==wire(original)
assert wire(grid_view(ROOT,ca['source']['path'],ca['source']['sha256']))==wire(ca)
preflight=read(O/'round04-preflight-v2.json');assert preflight['decision']=='approve'
for e in preflight['evidence']:assert sha(ROOT/e['path'])==e['sha256']
assert preflight['confirmed_tests']['new_unique_total_cases']==18
profile=read(B/'native-profile.json');assert sha(B/'native-profile.json')==plan['profile_sha256']
assert sha(B/'ThreadStartParams.json')==profile['schema_sha256']
assert len(profile['baseInstructions'])==308
assert sha(B/'task-chain.json')=='c8dd3808d427154d62ecc8be3a7e513632b12fd6368254815f32a36ed50f98f3'
assert sha(B/'manifest.json')=='d7bcf4f1cee269761e87d1a9f2c226c9a6f6d771c4ac33514cf0348688376525'
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
priorpath=ROOT/'.agent-runs/token-fifty-03-r2/03-r2-private/baseline.rollout.private.jsonl'
prior=rows(priorpath);pm=msgs(prior);assert len(pm)==5
for old,new in zip(pm[:-1],a[:-1]):assert old['role']==new['role'] and old['content']==new['content']
assert turn(prior)==turn(rollouts['baseline'])
for rr in rollouts.values():
    assert rr[0]['payload']['base_instructions']['text']==profile['baseInstructions']
    assert rr[0]['payload']['base_instructions']['provenance']=={'type':'custom'}
settings=read(B/'settings.json');assert settings['baseInstructions']==profile['baseInstructions'] and settings['developerInstructions']==profile['developerInstructions']==None
assert all(len((B/(name+'.prompt.txt')).read_text(encoding='utf-8'))<=14000 for name in stats)
assert sum(e.get('method')=='model/rerouted' or e.get('method')=='error' for e in full)==0
log=ROOT/'.agent-runs/token-fifty-04/reviews/round04-independent-preflight-tests.log';assert 'Ran 17 tests' in log.read_text(encoding='utf-8') and '\nOK' in log.read_text(encoding='utf-8')
delta=ROOT/'.agent-runs/token-fifty-04/reviews/round04-independent-delta-tests.raw';delta_text=delta.read_bytes().decode('utf-8',errors='replace');assert 'Ran 2 tests' in delta_text and '\nOK' in delta_text
control={'actor':'/root/token_review','manifest_sha256':sha(B/'manifest.json'),'all_manifest_and_frozen_and_source_archive_hashes_match':True,'independently_derived_oracle':oracle,'complete_coordinate_count':64,'all_ordered_values_types_metadata_restored':True,'all_original_public_events_verified':True,'original_rpc_hashes':orig_hashes,'public_rpc_hashes':public_hashes,'observed_usage':stats,'saving_tokens':stats['baseline']['total']-stats['candidate']['total'],'paired_spend_tokens':sum(v['total'] for v in stats.values()),'same_non_task_plaintext_messages':4,'four_protected_messages_exact_previous_round03':True,'previous_round03_rollout_sha256':sha(priorpath),'current_rollout_sha256':{n:sha(P/(n+'.rollout.private.jsonl')) for n in stats},'explicit_custom_base_exact_frozen_profile':True,'base_profile_chars':308,'profile_sha256':sha(B/'native-profile.json'),'profile_no_causal_saving_claim':True,'permission_model_turn_context_exact_previous_round03':True,'base_instructions_world_turn_context_equal':True,'exact_settings_catalog_equal':True,'distinct_fresh_threads':True,'actual_completed_calls':2,'no_tools_retries_rerouting':True,'quota_below90':True,'binary_and_user_config_unchanged':True,'tests_unique_cases':18,'reused_preflight_old17_plus_delta2':True,'host_symlink_skip':False,'parser_code_review':'Exact signed integer progression/source restoration with corrected expanded output refusal before allocation; actual frozen implementation and all v2 preflight evidence unchanged; no tests/native repetitions.'}
dump(O/'round04-independent-control.json',control);print(json.dumps({'decision':'pass','saving_tokens':control['saving_tokens'],'paired_spend':control['paired_spend_tokens'],'protected_messages':4,'source_files':len(inventory['files']),'oracle':oracle}))
