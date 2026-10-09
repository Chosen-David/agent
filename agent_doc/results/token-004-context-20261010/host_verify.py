"""Explicit host verifier; no inference, external commands from data, or retries."""
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys

REL='agent_doc/results/token-004-context-20261010'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(root,path):return {'path':path,'sha256':sha(root/path)}
def read(base,name):return json.loads((base/name).read_text(encoding='utf-8'))

def actual_envelopes(path):
    rows=[]
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        event=json.loads(line)
        if event['type']=='session_meta':
            text=json.dumps(event['payload'].get('base_instructions'),ensure_ascii=False,sort_keys=True)
            rows.append({'kind':'base','sha256':hashlib.sha256(text.encode()).hexdigest()})
        elif event['type']=='response_item' and event['payload'].get('type')=='message':
            message=event['payload']
            if message.get('role') not in ('developer','system','user'):continue
            text=''.join(c.get('text','') for c in message.get('content',[]))
            if 'For this observed validation, may the workflow consume the experiment result now?' in text:continue
            rows.append({'kind':message['role'],'sha256':hashlib.sha256(text.encode()).hexdigest(),'characters':len(text)})
    return rows

def controlled_texts(path):
    rows=[]
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        event=json.loads(line)
        if event['type']=='session_meta':
            rows.append(('base',json.dumps(event['payload'].get('base_instructions'),ensure_ascii=False,sort_keys=True)))
        elif event['type']=='response_item' and event['payload'].get('type')=='message':
            message=event['payload']
            if message.get('role') not in ('developer','system','user'):continue
            text=''.join(c.get('text','') for c in message.get('content',[]))
            if 'For this observed validation, may the workflow consume the experiment result now?' not in text:rows.append((message['role'],text))
    return rows

def verify(root,manifest,plan):
    root=Path(root); base=root/REL
    threads=read(base,'threads.json')
    config=read(base,'config.json')
    inventory=read(base,'published-source-inventory.json')
    for item in inventory['files']:assert ref(root,item['path'])==item
    binary=root/'.agent-runs/engineering-kb/tools/codex.exe'
    assert sha(binary)==config['binary_sha256']
    assert sha(Path.home()/'.codex/config.toml')==config['user_config_sha256']
    assert config['model']=='gpt-6.1-sol' and config['reasoning_effort']=='high'
    catalogs=read(base,'tool-catalog-hashes.json')
    assert catalogs['baseline']==catalogs['candidate'] and catalogs['baseline']['tools']==0
    profiles=read(base,'profiles.json')
    from agent_runtime.codex_tool_scope import resolve_tool_scope
    profile=resolve_tool_scope({'schema_version':'codex-tool-scope/v1','requirements_complete':True,'external_tool_requirements':[]})
    assert profiles=={name:profile for name in ('baseline','candidate')}
    raw_catalogs=read(root/'.agent-runs/token-optimizer-20261009','validation-context-catalogs.private.json')
    for name,data in raw_catalogs.items():
        raw=json.dumps(sorted(data,key=lambda s:s['name']),sort_keys=True,ensure_ascii=False).encode()
        assert hashlib.sha256(raw).hexdigest()==catalogs[name]['sha256']
        assert len(data)==catalogs[name]['servers'] and sum(len(s['tools']) for s in data)==catalogs[name]['tools']
    from agent_runtime.validation_context import write_validation_context,restore_validation_context
    baseline=read(base,'baseline.display.json');candidate=read(base,'candidate.display.json')
    assert baseline['status']=='pending' and baseline['proof']['status']=='pending'
    assert restore_validation_context(root,candidate['record_ref'])==baseline
    assert write_validation_context(root,baseline,REL+'/context')==candidate
    for key in ('status','scope','errors','next_action'):assert candidate[key]==baseline[key]
    original_proof=baseline['proof'];visible_proof=candidate['proof']
    assert {k:v for k,v in original_proof.items() if k not in ('artifact_hashes','review_evidence')}==visible_proof
    assert candidate['detail_counts']=={'artifact_hashes':len(original_proof['artifact_hashes'])}
    assert 'Display only' in candidate['trust'] and len(original_proof['artifact_hashes'])==38
    a=(base/'baseline.prompt.txt').read_bytes().decode('utf-8');b=(base/'candidate.prompt.txt').read_bytes().decode('utf-8')
    aa=a.split('\n',2);bb=b.split('\n',2)
    assert aa[:2]==bb[:2] and len(aa)==len(bb)==3 and max(len(a),len(b))<=7500
    assert json.loads(aa[2])==baseline and json.loads(bb[2])==candidate
    commands=read(base,'fixture-commands.json')
    assert len(commands)==2 and all(c['exit_code']==2 for c in commands)
    for c in commands:
        assert c['stdout_sha256']==sha(base/(c['name']+'.display.json'))
        assert '--verifier-adapter' not in c['argv']
    assert commands[1]['argv']==commands[0]['argv']+['--context-dir',REL+'/context']
    oracle={'consume':False,**{k:baseline[k] for k in ('status','errors','next_action','scope')}}
    assert oracle==read(base,'validation-plan.json')['oracle']
    assert read(base,'dispatch.json')['validation_plan_sha256']==sha(base/'validation-plan.json')
    for item in inventory['live_sources']:assert ref(root,item['path'])==item
    rows=[]; controls=[]
    private=root/'.agent-runs/token-optimizer-20261009'
    for name in ('baseline','candidate'):
        start=threads[name]; tid=start['thread']['id']
        assert start['model']=='gpt-6.1-sol' and start['reasoningEffort']=='high'
        assert start['approvalPolicy']=='never' and start['sandbox']['type']=='readOnly'
        assert start['cwd']==str(root) and start['thread']['turns']==[]
        raw=(private/(name+'-context-original.rpc.jsonl')).read_bytes()
        redaction=read(base,name+'.redaction.json')
        assert hashlib.sha256(raw).hexdigest()==redaction['original_sha256']
        # Prove the public export changes only sensitive account notifications.
        public=[]; removed=[]
        for line in raw.decode('utf-8').splitlines():
            event=json.loads(line)
            if event.get('method')=='account/rateLimits/updated':
                h=hashlib.sha256(line.encode()).hexdigest();removed.append(h)
                event={'method':'private/rateLimits-notification','params':{'raw_sha256':h}}
            public.append(json.dumps(event,ensure_ascii=False))
        assert ('\n'.join(public)+'\n').encode()==(base/(name+'.rpc.jsonl')).read_bytes()
        assert removed==redaction['notification_line_sha256']
        events=[json.loads(line) for line in raw.decode('utf-8').splitlines()]
        relevant=[e for e in events if e.get('params',{}).get('threadId')==tid]
        begins=[e for e in relevant if e.get('method')=='turn/started']
        ends=[e for e in relevant if e.get('method')=='turn/completed']
        assert len(begins)==len(ends)==1
        turn=ends[0]['params']['turn']; vid=turn['id']
        assert begins[0]['params']['turn']['id']==vid and turn['status']=='completed' and not turn['error']
        assert relevant.index(begins[0])<relevant.index(ends[0])
        assert not any(e.get('method')=='error' for e in events)
        items=[e['params']['item'] for e in relevant if e.get('method') in ('item/started','item/completed')]
        assert items and all(i['type'] in ('userMessage','agentMessage','reasoning') for i in items)
        updates=[e for e in relevant if e.get('method')=='thread/tokenUsage/updated']
        assert updates and all(e['params']['turnId']==vid for e in updates)
        assert relevant.index(updates[-1])<relevant.index(ends[0])
        usage=updates[-1]['params']['tokenUsage']; u=usage['last']
        assert u==usage['total']
        assert all(type(u[k]) is int and u[k]>=0 for k in ('inputTokens','outputTokens','cachedInputTokens','totalTokens','reasoningOutputTokens'))
        assert u['cachedInputTokens']<=u['inputTokens'] and u['reasoningOutputTokens']<=u['outputTokens']
        assert u['totalTokens']==u['inputTokens']+u['outputTokens']
        answers=[i['text'] for i in items if i['type']=='agentMessage' and 'text' in i]
        # item/started usually empty; final only is the authoritative answer.
        answers=[e['params']['item']['text'] for e in relevant if e.get('method')=='item/completed' and e['params']['item']['type']=='agentMessage']
        assert len(answers)==1
        answer=json.loads(answers[0])
        assert answer==read(base,name+'.answer.json')==oracle
        quota=read(base,name+'.quota.json')
        assert quota['ordinary_allowed'] is True and quota['windows']
        assert all(0<=w['usedPercent']<90 for w in quota['windows'])
        control=actual_envelopes(start['thread']['path'])
        assert control==read(base,name+'.envelope.json')
        controls.append(control)
        rows.append({'name':name,'thread_id':tid,'total':u['totalTokens'], 'input':u['inputTokens'],'output':u['outputTokens']})
    assert rows[0]['thread_id']!=rows[1]['thread_id'] and len(controls[0])==len(controls[1])>=4
    assert controls[0]==controls[1], 'any non-task instruction/environment difference invalidates A/B'
    assert controlled_texts(threads['baseline']['thread']['path'])==controlled_texts(threads['candidate']['thread']['path'])
    total=sum(r['total'] for r in rows); saving=rows[0]['total']-rows[1]['total']
    assert rows[0]['total']<=25000 and total<=50000 and saving>0
    reported=read(base,'usage.json')['observations']
    assert [x['total_tokens'] for x in reported]==[x['total'] for x in rows]
    metrics={x['name']:x['value'] for x in manifest['metrics']}
    assert metrics=={'baseline_total':rows[0]['total'],'candidate_total':rows[1]['total'],'saving':saving,'paired_spend':total}
    controls_plan=read(base,'validation-plan.json')['controls']
    assert controls_plan['max_invocations']==2 and controls_plan['retries']==0 and controls_plan['timeout_seconds']==90
    logs=[]
    for label,pattern in (('context','test_validation_context.py'),):
        proc=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','tests','-p',pattern,'-v'],cwd=root,
            capture_output=True,text=True,encoding='utf-8',timeout=90,env={**__import__('os').environ,'PYTHONUTF8':'1'})
        (base/('independent-'+label+'.log')).write_bytes((proc.stdout+proc.stderr).encode('utf-8'))
        assert proc.returncode==0,proc.stdout+proc.stderr
        logs.append(ref(root,REL+'/independent-'+label+'.log'))
    # WSL supports real symlink/FIFO cases; Windows cannot create test symlinks.
    proc=subprocess.run(['wsl.exe','-d','Ubuntu-26.04','-u','wi','--cd','/mnt/c/Users/WI/Desktop/home_work/AI_LLM/agent',
        '--','python3','-m','unittest','tests.test_result_validation','-q'],cwd=root,capture_output=True,timeout=60)
    path=base/'independent-result-validation-wsl.log'
    path.write_bytes(proc.stdout+proc.stderr)
    assert proc.returncode==0 and b'Ran 18 tests' in proc.stdout+proc.stderr
    logs.append(ref(root,REL+'/independent-result-validation-wsl.log'))
    from agent_runtime.result_validation import validate_result_plan
    validate_result_plan(read(base,'task-chain.json'))
    bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
    for group in manifest['artifacts'].values():
        for item in group:
            assert ref(root,item['path'])==item;bindings[item['path']]=item['sha256']
    evidence=[ref(root,REL+'/'+n) for n in ('baseline.rpc.jsonl','candidate.rpc.jsonl','baseline.envelope.json','candidate.envelope.json','published-source-inventory.json','tool-catalog-hashes.json','profiles.json','baseline.display.json','candidate.display.json')]+logs
    reasons={
        'implementation':'Actual captured validation CLI default/context observations and pending exits; current projection replays the receipt exactly and restores the complete inspection tree.',
        'reference_boundary':'Six Windows tests cover guide-root rebasing, cross-project copied records, unknown fields, modified hashes, complete failures/limits and unchanged real CLI pending exits; 18 WSL result-gate tests include symlink/FIFO cases.',
        'data_integrity':'Measured code bytes archived before dispatch, current code hashes agree; private original RPC and safe exports reconcile; exactly two distinct fresh successful no-tool native turns with final usage snapshots.',
        'numerical_sanity':f'Actual input+output {rows[0]["total"]}->{rows[1]["total"]}, saving {saving}, paired spend {total}; exact pending-block/status/errors/action/scope answers match. Cache not subtracted.',
        'measurement_validity':'Same native server/binary/config/model/high effort/cwd/schema/question/profile and every actual non-task instruction byte, same zero external tool catalog; only observed full JSON versus recoverable display differs; quota/dispatch checked.',
        'reproducibility':'Separate host restored original observation, replayed candidate representation/source and raw accounting, and ran current real CLI/gate tests without inference. The observed pending result is input, not scientific acceptance; frozen plan binds distinct producer/verification/publication tasks.'}
    review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(base/'manifest.json'),
        'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':plan['scope'],
        'verifier':{'actor':'host-context-reviewer','independent':True,'source':'separate native host process',
            'run_id':'TOK-004-verify','method':'raw provider usage + exact actual envelopes + recoverable observed CLI JSON + independent pending oracle'},
        'limitations':['One observed short coordination-only pair; needed-detail restore/reacquisition cost and long-horizon/general task quality remain unmeasured.',
            'This chat/development/research bill and cash cost are not measured; reported tokens are inference pair only.',
            'One observed provider-default sample; no cash price, population mean, statistical quality equivalence or general long-document claim.',
            'All visible non-task instructions and external catalog hashes match; opaque service internals remain unobservable.',
            'Private unredacted RPC/rollout evidence stays local; a different host must rerun independently rather than trust this stored report.',
            'Service output cap is not enforced; local dispatch/time/acceptance bounds and real quota admission apply.'],
        'checks':{k:{'verdict':'pass','reason':v,'evidence':evidence} for k,v in reasons.items()}}
    (base/'independent-review.json').write_bytes((json.dumps(review,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    return review
