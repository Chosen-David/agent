"""Separate host verification of native closed-child control; no inference."""
import hashlib,json,subprocess,sys,tomllib
from pathlib import Path
REL='agent_doc/results/token-008-dispatch-20261010'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(b,n):return json.loads((b/n).read_text(encoding='utf-8'))
def ref(root,p):return {'path':p,'sha256':sha(root/p)}
def policies(path):
    out=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        e=json.loads(line);p=e.get('payload',{})
        if e.get('type')=='session_meta':out.append(('base',json.dumps(p.get('base_instructions'),sort_keys=True,ensure_ascii=False)))
        elif e.get('type')=='response_item' and p.get('type')=='message' and p.get('role') in ('system','developer'):
            out.append((p['role'],''.join(c.get('text','') for c in p.get('content',[]))))
    return out
def verify(root,manifest,plan):
    root=Path(root);base=root/REL;private=root/'.agent-runs/token-optimizer-20261009';sys.path.insert(0,str(root))
    from agent_runtime.dispatch_context import prepare_dispatch
    from agent_runtime.result_validation import validate_result_plan
    from agent_runtime.turn_usage import current_turn_usage
    measured=read(base,'source-inventory.json');dispatch=read(base,'dispatch.json')
    assert dispatch['max_paid_calls']==2
    assert set(dispatch['frozen_hashes'])=={'validation-plan.json','source-inventory.json','host-request.json','dispatch-plans.json','output-schema.json','parent-history.json','config.json','parent-settings-binding.json'}
    assert dispatch['frozen_hashes']['validation-plan.json']==manifest['validation_plan']['sha256']==sha(base/'validation-plan.json')
    assert set(dispatch['prompt_sha256'])=={'baseline','candidate'}
    for p,h in dispatch['frozen_hashes'].items():assert sha(base/p)==h
    for n,h in dispatch['prompt_sha256'].items():assert sha(base/(n+'.prompt.txt'))==h
    for s in measured['files']:
        assert sha(root/s['path'])==sha(root/s['archive_path'])==s['sha256']
    config=read(base,'config.json')
    assert sha(root/'.agent-runs/engineering-kb/tools/codex.exe')==config['binary_sha256']
    assert sha(Path.home()/'.codex/config.toml')==config['user_config_sha256']
    request=read(base,'host-request.json');plans=read(base,'dispatch-plans.json');packet=read(base,'packet.json')
    assert packet==plan['oracle'] and packet['status']=='cancelled' and packet['input_version']=='figures:v8' and len(packet['blockers'])==3
    assert request['settings_complete'] is True and request['needs_complete'] is True and request['history_required'] is False
    assert request['required_refs']==request['context_refs'] and len(request['required_refs'])==2
    assert request['context_refs'][0]==ref(root,'agent_doc/guide/GUIDE.md') and not (root/'agent_doc/guide/GUIDE.md').read_bytes()
    assert request['context_refs'][1]==ref(root,REL+'/packet.json')
    for name in ('baseline','candidate'):
        expected=prepare_dispatch(root,request,force_inherit=name=='baseline',max_chars=4000)
        assert expected==plans[name]
        cmd=[sys.executable,'-X','utf8',str(root/'scripts/dispatch_context.py'),'--root',str(root),'--request',REL+'/host-request.json','--max-chars','4000']
        if name=='baseline':cmd.append('--force-inherit')
        p=subprocess.run(cmd,cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=20)
        assert p.returncode==0 and not p.stderr and json.loads(p.stdout)==expected
    assert plans['baseline']['method']=='thread/fork' and plans['candidate']['method']=='thread/start'
    bp=dict(plans['baseline']['params']);assert bp.pop('threadId')==request['parent']['thread_id'];assert bp.pop('lastTurnId')==request['parent']['last_turn_id'];assert bp.pop('excludeTurns') is True
    assert bp==plans['candidate']['params']
    text=plans['candidate']['input_text'];assert text==plans['baseline']['input_text'] and len(text)<=4000
    assert all((base/(n+'.prompt.txt')).read_bytes()==text.encode() for n in ('baseline','candidate'))
    payload=json.loads(text);assert payload['documents'][1]['text']==(base/'packet.json').read_text(encoding='utf-8')
    parent=read(base,'parent-history.json');before=read(base,'baseline-history-before.json');assert parent==before and len(parent)==1
    assert parent[0]['id']==request['parent']['last_turn_id'] and parent[0]['status']=='completed'
    old=root/'agent_doc/results/token-007-skills-20261010';oldstart=read(old,'threads.json')['candidate']
    assert oldstart['thread']['id']==request['parent']['thread_id']
    assert request['parent']['config']==read(old,'profiles.json')['candidate']['config_overrides']
    binding=read(base,'parent-settings-binding.json');oldinv=read(old,'source-inventory.json')
    source=next(s for s in oldinv['files'] if s['path'].endswith('/skills_probe.py'))
    assert binding['creation_source']==source and sha(root/source['archive_path'])==source['sha256']
    assert binding['custom_base_developer_instruction_overrides'] is False
    assert binding['user_config_sha256']==read(old,'config.json')['user_config_sha256']==config['user_config_sha256']
    assert binding['project_config_sha256']==sha(root/'.codex/config.toml')
    project_raw=subprocess.check_output(['git','show',binding['project_layer_revision']+':.codex/config.toml'],cwd=root)
    assert hashlib.sha256(project_raw).hexdigest()==binding['project_layer_git_sha256']
    assert tomllib.loads(project_raw.decode())==tomllib.loads((root/'.codex/config.toml').read_text(encoding='utf-8'))
    assert binding['system_layer_absent'] is True and not Path('C:/ProgramData/OpenAI/Codex/config.toml').exists()
    assert binding['creation_response_controls']=={k:v for k,v in oldstart.items() if k not in ('thread','instructionSources')}
    olditems=parent[0]['items'];assert [x['type'] for x in olditems]==['userMessage','agentMessage']
    assert json.loads(olditems[1]['text'])==read(old,'candidate.answer.json')
    oldtext=''.join(x.get('text','') for x in olditems[0]['content'] if x.get('type')=='text')
    assert oldtext==(old/'candidate.prompt.txt').read_text(encoding='utf-8')
    threads=read(base,'threads.json');assert threads['baseline']['instructionSources']==threads['candidate']['instructionSources']==oldstart['instructionSources']
    catalogs=read(base,'tool-catalogs.json');assert catalogs['baseline']==catalogs['candidate'] and not any(s['tools'] for s in catalogs['baseline'])
    rows=[];control=[]
    for name in ('baseline','candidate'):
        start=threads[name];tid=start['thread']['id']
        assert start['model']=='gpt-6.1-sol' and start['reasoningEffort']=='high' and start['cwd']==str(root)
        assert start['approvalPolicy']=='never' and start['sandbox']=={'type':'readOnly','networkAccess':False}
        assert {k:v for k,v in start.items() if k not in ('thread','instructionSources')}==binding['creation_response_controls']
        raw=(private/(name+'-child8-original.rpc.jsonl')).read_bytes();red=read(base,name+'.redaction.json');assert hashlib.sha256(raw).hexdigest()==red['original_sha256']
        public=[];removed=[]
        for line in raw.decode().splitlines():
            e=json.loads(line)
            if e.get('method')=='account/rateLimits/updated':
                h=hashlib.sha256(line.encode()).hexdigest();removed.append(h);e={'method':'private/rateLimits-notification','params':{'raw_sha256':h}}
            public.append(json.dumps(e,ensure_ascii=False))
        assert ('\n'.join(public)+'\n').encode()==(base/(name+'.rpc.jsonl')).read_bytes() and removed==red['notification_line_sha256']
        events=[json.loads(x) for x in raw.decode().splitlines()]
        starts=[e['params']['turn'] for e in events if e.get('method')=='turn/started' and e['params']['threadId']==tid];assert len(starts)==1
        turn=starts[0]['id'];usage=current_turn_usage(events,tid,turn);rows.append({'name':name,**usage})
        # Independently read the final native current-turn counters rather than trusting producer extraction.
        native=[e['params']['tokenUsage']['last'] for e in events if e.get('method')=='thread/tokenUsage/updated' and e['params']['threadId']==tid and e['params']['turnId']==turn][-1]
        assert usage['total_tokens']==native['inputTokens']+native['outputTokens']==native['totalTokens']
        answers=[e['params']['item']['text'] for e in events if e.get('method')=='item/completed' and e['params'].get('threadId')==tid and e['params']['item']['type']=='agentMessage']
        assert len(answers)==1 and json.loads(answers[0])==packet==read(base,name+'.answer.json')
        hist=read(base,name+'.history-after.json')
        if name=='baseline':assert len(hist)==2 and hist[0]==parent[0]
        else:assert len(hist)==1
        now=hist[-1];assert now['id']==turn and now['status']=='completed'
        items=now['items'];assert [x['type'] for x in items]==['userMessage','agentMessage']
        assert ''.join(x.get('text','') for x in items[0]['content'] if x.get('type')=='text')==text and json.loads(items[1]['text'])==packet
        quota=read(base,name+'.quota.json');assert quota['ordinary_allowed'] and quota['windows'] and all(0<=x['usedPercent']<90 for x in quota['windows'])
        capture=private/(name+'-child8-rollout.private.jsonl');control.append(policies(capture))
    assert rows==read(base,'usage.json')['observations'] and rows[0]['thread_id']!=rows[1]['thread_id']
    # A fork may store prior policy records only in its ancestor rollout. Explicitly compare that ancestry when no current policy records are duplicated.
    inherited=control[0];fresh=control[1];oldpolicy=policies(Path(oldstart['thread']['path']))
    assert inherited and fresh and inherited[0]==fresh[0]==oldpolicy[0]
    bpol=[x for x in inherited if x[0]!='base'];fpol=[x for x in fresh if x[0]!='base'];opol=[x for x in oldpolicy if x[0]!='base']
    assert bpol==fpol or (not bpol and opol==fpol),'observable effective developer/system instructions differ'
    total=sum(x['total_tokens'] for x in rows);saving=rows[0]['total_tokens']-rows[1]['total_tokens']
    assert rows[0]['total_tokens']<=25000 and total<=50000 and saving>0
    assert {x['name']:x['value'] for x in manifest['metrics']}=={'baseline_total':rows[0]['total_tokens'],'candidate_total':rows[1]['total_tokens'],'saving':saving,'paired_spend':total}
    assert plan['controls']['max_invocations']==2 and plan['controls']['retries']==0
    p=subprocess.run([sys.executable,'-X','utf8','-m','unittest','tests.test_dispatch_context','tests.test_turn_usage','-q'],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=60)
    log=base/'independent-context.log';log.write_bytes((p.stdout+p.stderr).encode());assert p.returncode==0 and 'Ran 6 tests' in p.stderr
    validate_result_plan(read(base,'task-chain.json'))
    diff={'same_new_task_input':True,'same_observable_settings_instructions_tools':True,'baseline_prior_completed_turns':1,'candidate_prior_completed_turns':0,'excludeTurns_is_response_hydration_only':True,'provider_internal_prompt_assembly':'not observable','saving_tokens':saving}
    (base/'independent-control.json').write_text(json.dumps(diff,indent=2)+'\n',encoding='utf-8')
    bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
    for group in manifest['artifacts'].values():
        for x in group:assert ref(root,x['path'])==x;bindings[x['path']]=x['sha256']
    review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(base/'manifest.json'),'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':manifest['scope'],
        'verifier':{'actor':'host-child8-reviewer','source':'independently executed fixed host verifier; zero model calls','run_id':'TOK-008-verify','method':'real CLI/native originals/persisted history/policy ancestry and separate boundary tests','independent':True},
        'limitations':['One short synthetic complete task and one prior turn, not a long-context/full-workflow/cash study.','Native settings/history/policy records checked; provider internal final prompt assembly unobservable.','Settings/dependency completeness requires explicit host assessment; no automatic global adoption or context deletion.','Admission bounds are not service hard output limits; research/root chat/static review cost excluded.'],
        'checks':{k:{'verdict':'pass','reason':plan['criteria'][k]['acceptance'],'evidence':[ref(root,REL+'/independent-control.json'),ref(root,REL+'/independent-context.log')]} for k in plan['criteria']}}
    (base/'independent-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return review
