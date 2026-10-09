"""Independent host checks for one native skill-exposure pair; no inference."""
import hashlib,json,os,re,subprocess,sys
from pathlib import Path
REL='agent_doc/results/token-007-skills-20261010'
PREFIX='For this closed packet interpretation task, copy the current cancellation and unchanged blockers.'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(base,name):return json.loads((base/name).read_text(encoding='utf-8'))
def ref(root,path):return {'path':path,'sha256':sha(root/path)}
def messages(path):
    rows=[]
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        e=json.loads(line)
        if e['type']=='session_meta':rows.append(('base',json.dumps(e['payload'].get('base_instructions'),ensure_ascii=False,sort_keys=True)))
        elif e['type']=='response_item' and e['payload'].get('type')=='message' and e['payload'].get('role') in ('developer','system','user'):
            rows.append((e['payload']['role'],''.join(x.get('text','') for x in e['payload'].get('content',[]))))
    return rows
def norm(path):return os.path.normcase(str(Path(path).resolve(strict=False)))

def verify(root,manifest,plan):
    root=Path(root);base=root/REL;private=root/'.agent-runs/token-optimizer-20261009'
    sys.path.insert(0,str(root))
    from agent_runtime.codex_skill_scope import resolve_skill_scope,check_skill_catalog_delta
    from agent_runtime.codex_tool_scope import resolve_tool_scope
    inv=read(base,'published-source-inventory.json')
    measured=read(base,'source-inventory.json');dispatch=read(base,'dispatch.json')
    assert measured['revision']==inv['revision']
    assert inv['files']==[{'path':x['archive_path'],'sha256':x['sha256']} for x in measured['files']]
    assert inv['live_sources']==[{'path':x['path'],'sha256':x['sha256']} for x in measured['files'] if not x['path'].startswith('.agent-runs/')]
    assert dispatch['source_inventory_sha256']==sha(base/'source-inventory.json')
    assert dispatch['validation_plan_sha256']==sha(base/'validation-plan.json')==manifest['validation_plan']['sha256']
    assert dispatch['host_request_sha256']==sha(base/'host-request.json') and dispatch['profiles_sha256']==sha(base/'profiles.json')
    assert dispatch['schema_sha256']==sha(base/'output-schema.json')
    assert dispatch['prompt_sha256']=={name:sha(base/(name+'.prompt.txt')) for name in ('baseline','candidate')}
    assert dispatch['max_paid_calls']==2
    for x in inv['files']:assert ref(root,x['path'])==x
    for x in inv['live_sources']:assert ref(root,x['path'])==x
    config=read(base,'config.json')
    assert sha(root/'.agent-runs/engineering-kb/tools/codex.exe')==config['binary_sha256']
    assert sha(Path.home()/'.codex/config.toml')==config['user_config_sha256']
    request=read(base,'host-request.json');metadata=read(base,'metadata-discovery.json')
    binding=read(base,'request-binding.json')
    assert sha(base/'host-request.json')==binding['request_sha256'] and sha(base/'metadata-discovery.json')==binding['metadata_sha256']
    assert metadata['effective_skills'] is None and all(x['skills'] is None for x in metadata['layer_skills'])
    assert metadata['user_settings_sha256']==config['user_config_sha256']==binding['source_settings_sha256']
    assert request['project_root']==str(root) and request['catalog']['cwd']==str(root)
    assert request['catalog']==metadata['catalog']['data'][0] and request['current_skills_config']==[]
    for x in binding['skill_sources']:assert sha(Path(x['path']))==x['sha256']
    profile=resolve_skill_scope(request['contract'],request['catalog'],request['current_skills_config'])
    assert profile==read(base,'candidate-skill-profile.json') and len(profile['excluded_skill_paths'])==11
    packet=read(base,'packet.json');assert packet==plan['oracle']
    assert packet['status']=='cancelled' and packet['input_version']=='figures:v7' and len(packet['blockers'])==3
    a=(base/'baseline.prompt.txt').read_bytes();b=(base/'candidate.prompt.txt').read_bytes()
    assert a==b and len(a.decode())<=4000
    text=a.decode();assert text.startswith(PREFIX+'\n') and json.loads(text.split('\n',2)[2])==packet
    schema=read(base,'output-schema.json');assert schema['additionalProperties'] is False and set(schema['required'])==set(packet)
    command=[sys.executable,'-X','utf8',str(root/'scripts/codex_skill_scope.py'),'--root',str(root),'--request',(base/'host-request.json').relative_to(root).as_posix()]
    p=subprocess.run(command,cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=20)
    assert p.returncode==0 and not p.stderr and json.loads(p.stdout)==profile
    observed=read(base,'fixture-command.json');assert observed['argv']==command and observed['exit_code']==0 and hashlib.sha256(p.stdout.encode()).hexdigest()==observed['stdout_sha256']
    tools=resolve_tool_scope({'schema_version':'codex-tool-scope/v1','requirements_complete':True,'external_tool_requirements':[]})
    expected={name:json.loads(json.dumps(tools)) for name in ('baseline','candidate')}
    expected['candidate']['config_overrides'].update(profile['config_overrides'])
    assert read(base,'profiles.json')==expected
    catalogs=read(base,'tool-catalog-hashes.json');assert catalogs['baseline']==catalogs['candidate'] and catalogs['baseline']['tools']==0
    raw_catalogs=read(private,'skill-scope-catalogs.private.json')
    for name,data in raw_catalogs.items():
        raw=json.dumps(sorted(data,key=lambda x:x['name']),sort_keys=True,ensure_ascii=False).encode()
        assert hashlib.sha256(raw).hexdigest()==catalogs[name]['sha256']
    threads=read(base,'threads.json');rows=[];texts=[]
    for name in ('baseline','candidate'):
        start=threads[name];tid=start['thread']['id']
        assert start['model']=='gpt-6.1-sol' and start['reasoningEffort']=='high' and start['cwd']==str(root)
        assert start['approvalPolicy']=='never' and start['sandbox']=={'type':'readOnly','networkAccess':False}
        raw=(private/(name+'-skills-original.rpc.jsonl')).read_bytes();red=read(base,name+'.redaction.json')
        assert hashlib.sha256(raw).hexdigest()==red['original_sha256']
        pub=[];removed=[]
        for line in raw.decode().splitlines():
            e=json.loads(line)
            if e.get('method')=='account/rateLimits/updated':
                h=hashlib.sha256(line.encode()).hexdigest();removed.append(h);e={'method':'private/rateLimits-notification','params':{'raw_sha256':h}}
            pub.append(json.dumps(e,ensure_ascii=False))
        assert ('\n'.join(pub)+'\n').encode()==(base/(name+'.rpc.jsonl')).read_bytes()
        assert removed==red['notification_line_sha256']
        events=[json.loads(x) for x in raw.decode().splitlines()];relevant=[e for e in events if e.get('params',{}).get('threadId')==tid]
        begins=[e for e in relevant if e.get('method')=='turn/started'];ends=[e for e in relevant if e.get('method')=='turn/completed']
        assert len(begins)==len(ends)==1
        turn=ends[0]['params']['turn'];vid=turn['id'];assert turn['status']=='completed' and not turn['error']
        assert begins[0]['params']['turn']['id']==vid and relevant.index(begins[0])<relevant.index(ends[0])
        assert not any(e.get('method')=='error' for e in events)
        items=[e['params']['item'] for e in relevant if e.get('method') in ('item/started','item/completed')]
        assert items and all(x['type'] in ('userMessage','agentMessage','reasoning') for x in items)
        updates=[e for e in relevant if e.get('method')=='thread/tokenUsage/updated']
        assert updates and all(e['params']['turnId']==vid for e in updates)
        assert relevant.index(updates[-1])<relevant.index(ends[0])
        usage=updates[-1]['params']['tokenUsage'];u=usage['last'];assert u==usage['total']
        assert all(type(u[k]) is int and u[k]>=0 for k in ('inputTokens','outputTokens','cachedInputTokens','totalTokens','reasoningOutputTokens'))
        assert u['cachedInputTokens']<=u['inputTokens'] and u['reasoningOutputTokens']<=u['outputTokens']
        assert u['totalTokens']==u['inputTokens']+u['outputTokens']
        answers=[e['params']['item']['text'] for e in relevant if e.get('method')=='item/completed' and e['params']['item']['type']=='agentMessage']
        assert len(answers)==1 and json.loads(answers[0])==packet==read(base,name+'.answer.json')
        quota=read(base,name+'.quota.json');assert quota['ordinary_allowed'] and quota['windows'] and all(0<=x['usedPercent']<90 for x in quota['windows'])
        captured=messages(start['thread']['path']);assert any(role=='user' and t==text for role,t in captured)
        texts.append(captured);rows.append({'name':name,'thread_id':tid,'total':u['totalTokens'],'input':u['inputTokens'],'output':u['outputTokens']})
    assert rows[0]['thread_id']!=rows[1]['thread_id'] and len(texts[0])==len(texts[1])>=5
    # Only one actual skills message may differ. Bind aliases to native absolute
    # excluded paths; unknown entries are not silently removed.
    changed=[i for i,(a,b) in enumerate(zip(*texts)) if a!=b]
    assert len(changed)==1,'exactly one declared catalog-only message difference required'
    i=changed[0];role,old=texts[0][i];newrole,new=texts[1][i];assert role==newrole=='developer'
    roots=dict(re.findall(r'^- `(r\d+)` = `([^`]+)`$',old,re.M))
    excluded={norm(x):x for x in profile['excluded_skill_paths']};selected=[];selected_paths=[];seen_paths=[]
    for line in old.splitlines(keepends=True):
        match=re.fullmatch(r'- ([\w:-]+):[^\n]* \(file: (r\d+)/([^\n)]+)\)\n',line)
        if match and match[2] in roots:
            path=norm(Path(roots[match[2]])/match[3])
            seen_paths.append(path)
            if path in excluded:selected.append(line);selected_paths.append(path)
    assert len(selected)==len(selected_paths)==11 and set(selected_paths)==set(excluded)
    assert all(seen_paths.count(norm(x))==1 for x in profile['required_skill_paths']),'all five required roles must actually be present'
    delta=check_skill_catalog_delta(old,new,selected)
    diff={'removed_entries':delta['removed_entries'],'remaining_plaintext_exact':True,'removed_paths':[excluded[x] for x in selected_paths],
      'baseline_skill_message_sha256':hashlib.sha256(old.encode()).hexdigest(),'candidate_skill_message_sha256':hashlib.sha256(new.encode()).hexdigest(),
      'all_other_actual_messages_exact':True,'tool_catalogs_exact':True}
    (base/'independent-allowed-diff.json').write_text(json.dumps(diff,indent=2)+'\n',encoding='utf-8')
    total=sum(x['total'] for x in rows);saving=rows[0]['total']-rows[1]['total']
    assert rows[0]['total']<=25000 and total<=50000 and saving>0
    assert [x['total_tokens'] for x in read(base,'usage.json')['observations']]==[x['total'] for x in rows]
    assert {x['name']:x['value'] for x in manifest['metrics']}=={'baseline_total':rows[0]['total'],'candidate_total':rows[1]['total'],'saving':saving,'paired_spend':total}
    assert plan['controls']['max_invocations']==2 and plan['controls']['retries']==0 and plan['controls']['timeout_seconds']==90
    p=subprocess.run([sys.executable,'-X','utf8','-m','unittest','tests.test_codex_skill_scope','-q'],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=90)
    log=base/'independent-skill-scope.log';log.write_bytes((p.stdout+p.stderr).encode());assert p.returncode==0 and 'Ran 5 tests' in p.stderr
    from agent_runtime.result_validation import validate_result_plan
    validate_result_plan(read(base,'task-chain.json'))
    bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
    for group in manifest['artifacts'].values():
        for x in group:assert ref(root,x['path'])==x;bindings[x['path']]=x['sha256']
    review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(base/'manifest.json'),
      'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':manifest['scope'],
      'verifier':{'actor':'host-skill-reviewer','source':'explicit independently executed host verifier; no model call',
        'run_id':'TOK-007-verify','method':'replay real CLI/native originals, exact catalog-only binding and separate boundary tests','independent':True},
      'limitations':['One short synthetic interpretation pair, not a long-document or full workflow quality study.',
        'Native admission/control bounds are not a provider output hard cap; development/research/chat use and cash cost excluded.',
        'Native discovery inventory is partial relative to actual catalog; only exact named exclusions verified.',
        'Explicit host invocation required; repository installation does not automatically rewrite a running conversation.'],
      'checks':{k:{'verdict':'pass','reason':plan['criteria'][k]['acceptance'],'evidence':[ref(root,REL+'/independent-allowed-diff.json'),ref(root,REL+'/independent-skill-scope.log')]} for k in plan['criteria']}}
    (base/'independent-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return review
