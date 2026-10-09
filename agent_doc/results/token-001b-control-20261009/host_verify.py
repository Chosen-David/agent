"""Explicit host verifier; no inference, external commands from data, or retries."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

REL='agent_doc/results/token-001b-control-20261009'
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
            if 'For this fictional case, should work start?' in text:continue
            rows.append({'kind':message['role'],'sha256':hashlib.sha256(text.encode()).hexdigest(),'characters':len(text)})
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
    assert catalogs['baseline']==catalogs['candidate'] and catalogs['baseline']['tools']>0
    from agent_runtime.prompt_context import compose_entries
    fixture=root/'agent_doc/results/token-001-20261009/fixture'
    full=compose_entries(fixture,deduplicate=False)['prompt']
    short=compose_entries(fixture)['prompt']
    a=(base/'baseline.prompt.txt').read_bytes().decode('utf-8')
    b=(base/'candidate.prompt.txt').read_bytes().decode('utf-8')
    assert a.startswith(full) and b==short+a[len(full):] and max(len(a),len(b))<=2200
    assert len(a)-len(b)>0
    rows=[]; controls=[]
    private=root/'.agent-runs/token-optimizer-20261009'
    for name in ('baseline','candidate'):
        start=threads[name]; tid=start['thread']['id']
        assert start['model']=='gpt-6.1-sol' and start['reasoningEffort']=='high'
        assert start['approvalPolicy']=='never' and start['sandbox']['type']=='readOnly'
        assert start['cwd']==str(root) and start['thread']['turns']==[]
        raw=(private/(name+'-original.rpc.jsonl')).read_bytes()
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
        assert answer==read(base,name+'.answer.json') and set(answer)=={'proceed','reasons'}
        assert answer['proceed'] is False and sorted(answer['reasons'])==['R_CANCEL','R_CAP','R_VERIFY']
        quota=read(base,name+'.quota.json')
        assert quota['ordinary_allowed'] is True and quota['windows']
        assert all(0<=w['usedPercent']<90 for w in quota['windows'])
        control=actual_envelopes(start['thread']['path'])
        assert control==read(base,name+'.envelope.json')
        controls.append(control)
        rows.append({'name':name,'thread_id':tid,'total':u['totalTokens'], 'input':u['inputTokens'],'output':u['outputTokens']})
    assert rows[0]['thread_id']!=rows[1]['thread_id'] and controls[0]==controls[1] and len(controls[0])>=4
    total=sum(r['total'] for r in rows); saving=rows[0]['total']-rows[1]['total']
    assert rows[0]['total']<=25000 and total<=50000 and saving>0
    assert total==41794 and saving==98
    controls_plan=read(base,'validation-plan.json')['controls']
    assert controls_plan['max_invocations']==2 and controls_plan['retries']==0 and controls_plan['timeout_seconds']==90
    logs=[]
    for label,pattern in (('composer','test_prompt_context.py'),('entry-contract','test_main_ai_contract.py')):
        proc=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','tests','-p',pattern,'-v'],cwd=root,
            capture_output=True,text=True,encoding='utf-8',timeout=60)
        (base/('independent-'+label+'.log')).write_bytes((proc.stdout+proc.stderr).encode('utf-8'))
        assert proc.returncode==0,proc.stdout+proc.stderr
        logs.append(ref(root,REL+'/independent-'+label+'.log'))
    from agent_runtime.result_validation import validate_result_plan
    validate_result_plan(read(base,'task-chain.json'))
    bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
    for group in manifest['artifacts'].values():
        for item in group:
            assert ref(root,item['path'])==item;bindings[item['path']]=item['sha256']
    evidence=[ref(root,REL+'/'+n) for n in ('baseline.rpc.jsonl','candidate.rpc.jsonl','baseline.envelope.json','candidate.envelope.json','published-source-inventory.json','tool-catalog-hashes.json')]+logs
    reasons={
        'implementation':'Actual shared composer replay matches the prompts; standalone unique/conflicting instructions retained.',
        'reference_boundary':'Targeted tests cover scope ambiguity, outer fences/comments, caps and stale/corrupt usage; no cross-thread read cache.',
        'data_integrity':'Independent raw RPC accounting, original-private/public-redacted equality and bindings; exactly two distinct fresh successful no-tool turns.',
        'numerical_sanity':f'Provider input+output independently recomputed: {rows[0]["total"]}->{rows[1]["total"]}, saving {saving}, paired spend {total}; caches not subtracted; all three oracle blockers agree.',
        'measurement_validity':'Same server/binary/config/model/high effort/cwd/schema; actual non-task rollout plaintext and warmed tool catalogs match; quota and two-call/zero-retry dispatch checked.',
        'reproducibility':'Separate host process replayed fixtures/accounting/source contracts without inference; formal plan explicitly post-data binds existing pre-dispatch controls and original six-domain criteria.'}
    review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(base/'manifest.json'),
        'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':plan['scope'],
        'verifier':{'actor':'host-controlled-result-reviewer','independent':True,'source':'separate native host process',
            'run_id':'TOK-001-verify-b','method':'raw provider usage + actual local instruction envelopes + oracle + deterministic code replay'},
        'limitations':['One observed short A/B pair, no statistical/general long-paper or all-workflow quality claim.',
            'This chat/development/research bill and cash cost are not measured; reported tokens are inference pair only.',
            'Model sampling seed not controlled; reasoning tokens increased by 20 while input fell by 120.',
            'Exact instruction text and local warmed tool declarations match; opaque service internals are not visible.',
            'Private unredacted RPC/rollout evidence stays local; a different host must rerun independently rather than trust this stored report.',
            'Service output cap is not enforced; local dispatch/time/acceptance bounds and real quota admission apply.'],
        'checks':{k:{'verdict':'pass','reason':v,'evidence':evidence} for k,v in reasons.items()}}
    (base/'independent-review.json').write_bytes((json.dumps(review,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    return review
