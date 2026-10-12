import pathlib,json,hashlib,subprocess,sys,os
ROOT=pathlib.Path.cwd(); B=ROOT/'agent_doc/results/token-fifty-01-r2-20261012'; P=ROOT/'.agent-runs/token-fifty/01-r2-private'; O=ROOT/'.agent-runs/token-fifty/reviews'
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
fixture=(B/'fixture.md').read_bytes(); lines=fixture.decode().splitlines(keepends=True)
topics=[{'heading':s[3:].strip(),'start_line':i+1} for i,s in enumerate(lines) if s.startswith('## ')]
for i,t in enumerate(topics):t['end_line']=topics[i+1]['start_line']-1 if i+1<len(topics) else len(lines)
target=next(t for t in topics if t['heading']=='VERIFY'); text=''.join(lines[target['start_line']-1:target['end_line']]); leading=''.join(lines[:topics[0]['start_line']-1])
assert 'Current run cancelled. Do not publish.' in text and 'remain pending until independent verification' in leading
oracle={'topics':[t['heading'] for t in topics],'publish':False,'blockers':['cancelled','pending_verification']}
assert oracle==read(B/'oracle.json')
packets=read(B/'packets.json'); ca=packets['candidate']; ba=packets['baseline']; selected=ca['selected_view']
assert ba['selected_view']==selected and ca['discovery']['topics']==topics
assert ca['discovery']['leading_text']==selected['leading_text']==leading
assert selected['selected_sections'][0]['text']==text and ba['discovery']['text']==fixture.decode()
assert selected['source']['sha256']==ca['discovery']['source']['sha256']==sha(B/'fixture.md')
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
test=subprocess.run([sys.executable,'-X','utf8','-m','unittest','tests.test_advice_discovery','tests.test_advice_context','-q'],capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=60)
log=O/'round01-r2-final-independent-tests.log';log.open('x',encoding='utf-8').write(test.stdout+test.stderr);assert test.returncode==0 and 'Ran 21 tests' in test.stderr
control={'actor':'/root/token_review','manifest_sha256':sha(B/'manifest.json'),'all_manifest_and_frozen_and_source_archive_hashes_match':True,'independently_derived_oracle':oracle,'fixture_topics_ranges':topics,'selected_and_leading_bytes_exact':True,'all_original_public_events_verified':True,'original_rpc_hashes':orig_hashes,'public_rpc_hashes':public_hashes,'observed_usage':stats,'saving_tokens':stats['baseline']['total']-stats['candidate']['total'],'paired_spend_tokens':sum(v['total'] for v in stats.values()),'same_non_task_plaintext_messages':4,'base_instructions_world_turn_context_equal':True,'exact_settings_catalog_equal':True,'distinct_fresh_threads':True,'actual_completed_calls':2,'no_tools_retries_rerouting':True,'quota_below90':True,'binary_and_user_config_unchanged':True,'tests_ran':21,'host_symlink_skip':True,'parser_code_review':'Shared existing parser; discovery-only title length limit correct; no default selection changes; SHA/path/budget/comment/fence/UTF8 failures verified.'}
dump(O/'round01-r2-independent-control.json',control);print(json.dumps(control))
