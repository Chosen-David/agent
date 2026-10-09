"""Explicit host verifier; no inference, external commands from data, or retries."""
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys

REL='agent_doc/results/token-003-deployment-20261010'
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
            if 'For this supplied synthetic handoff, which claims are ready?' in text:continue
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
            if 'For this supplied synthetic handoff, which claims are ready?' not in text:rows.append((message['role'],text))
    return rows

def verify(root,manifest,plan):
    root=Path(root); base=root/REL
    reuse=read(base,'reuse.json')
    assert reuse['new_model_calls']==0 and reuse['additional_provider_tokens']==0
    assert ref(root,reuse['original_manifest']['path'])==reuse['original_manifest']
    assert ref(root,reuse['measured_mailbox_archive']['path'])==reuse['measured_mailbox_archive']
    assert ref(root,reuse['current_mailbox']['path'])==reuse['current_mailbox']
    original=root/'agent_doc/results/token-003-claims-20261010'
    for name in ('baseline','candidate'):
        for suffix in ('.prompt.txt','.answer.json','.rpc.jsonl'):
            assert (base/(name+suffix)).read_bytes()==(original/(name+suffix)).read_bytes()
    for name in ('validation-plan.json','config.json','profiles.json','output-schema.json','threads.json','usage.json'):
        assert (base/name).read_bytes()==(original/name).read_bytes()
    assert sha(base/'validation-plan.json')==reuse['same_plan_sha256']
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
    raw_catalogs=read(root/'.agent-runs/token-optimizer-20261009','claims-catalogs.private.json')
    for name,data in raw_catalogs.items():
        raw=json.dumps(sorted(data,key=lambda s:s['name']),sort_keys=True,ensure_ascii=False).encode()
        assert hashlib.sha256(raw).hexdigest()==catalogs[name]['sha256']
        assert len(data)==catalogs[name]['servers'] and sum(len(s['tools']) for s in data)==catalogs[name]['tools']
    from agent_runtime.communication import Mailbox
    from agent_runtime.handoff_encoding import decode_basis_payload
    import tempfile
    with tempfile.TemporaryDirectory(dir=root/'.agent-runs/token-optimizer-20261009') as temporary:
        box=Mailbox(Path(temporary)/'verify.sqlite',read(base,'mailbox-plan.json'),root)
        seq=box.publish(read(base,'event.json'))['seq']
        request=read(base,'consumer-request.json')
        full=box.prepare_context('baseline-reader',seq,request)['payload']
        short=box.prepare_context('table-reader',seq,{**request,'context_format':'claims-table/v1'})['payload']
    assert decode_basis_payload(short)==json.loads(full)
    a=(base/'baseline.prompt.txt').read_bytes().decode('utf-8')
    b=(base/'candidate.prompt.txt').read_bytes().decode('utf-8')
    aa=a.split('\n',2);bb=b.split('\n',2)
    assert aa[:2]==bb[:2] and len(aa)==len(bb)==3
    assert aa[2]==full and bb[2]==short and max(len(a),len(b))<=4000
    record=read(base,'handoff.json');claims=record['evidence_claims'];graph={c['id']:c for c in claims}
    ready=[]
    for claim in claims:
        ancestors=set();todo=list(claim['depends_on'])
        while todo:
            parent=todo.pop()
            if parent not in ancestors:
                ancestors.add(parent);todo.extend(graph[parent]['depends_on'])
        if (claim['status']=='supported' and all(graph[c]['status']=='supported' for c in ancestors)
                and all(p['status']=='satisfied' for p in claim['assumptions'])):
            ready.append(claim['id'])
    oracle={'ready':sorted(ready),'blocked':sorted(set(graph)-set(ready)),
        'input_version':record['input_version'],'artifact_sha256':record['artifacts'][0]['sha256']}
    assert oracle==read(base,'validation-plan.json')['oracle']
    assert read(base,'dispatch.json')['validation_plan_sha256']==sha(base/'validation-plan.json')
    rows=[]; controls=[]
    private=root/'.agent-runs/token-optimizer-20261009'
    for name in ('baseline','candidate'):
        start=threads[name]; tid=start['thread']['id']
        assert start['model']=='gpt-6.1-sol' and start['reasoningEffort']=='high'
        assert start['approvalPolicy']=='never' and start['sandbox']['type']=='readOnly'
        assert start['cwd']==str(root) and start['thread']['turns']==[]
        raw=(private/(name+'-claims-original.rpc.jsonl')).read_bytes()
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
    for label,pattern in (('encoding','test_handoff_encoding.py'),('basis','test_handoff_basis.py'),('communication','test_communication.py'),('communication-regressions','test_communication_regressions.py')):
        proc=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','tests','-p',pattern,'-v'],cwd=root,
            capture_output=True,text=True,encoding='utf-8',timeout=90,env={**__import__('os').environ,'PYTHONUTF8':'1'})
        (base/('independent-'+label+'.log')).write_bytes((proc.stdout+proc.stderr).encode('utf-8'))
        assert proc.returncode==0,proc.stdout+proc.stderr
        logs.append(ref(root,REL+'/independent-'+label+'.log'))
    from agent_runtime.result_validation import validate_result_plan
    validate_result_plan(read(base,'task-chain.json'))
    bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
    for group in manifest['artifacts'].values():
        for item in group:
            assert ref(root,item['path'])==item;bindings[item['path']]=item['sha256']
    evidence=[ref(root,REL+'/'+n) for n in ('baseline.rpc.jsonl','candidate.rpc.jsonl','baseline.envelope.json','candidate.envelope.json','published-source-inventory.json','tool-catalog-hashes.json','profiles.json')]+logs
    reasons={
        'implementation':'Independent real Mailbox delivery/request replay reconstructs exact original JSON tree; all ancestors, negative/candidate claims, assumptions and reference hashes preserved.',
        'reference_boundary':'Independent targeted suites refuse malformed/unknown table fields/versions/rows, stale artifacts and exceeded full-basis budgets; default JSON and existing source gates pass.',
        'data_integrity':'Original raw RPC and safe public export independently reconciled; actual final usage verified for exactly two distinct fresh successful no-tool turns, source/input/config bindings match.',
        'numerical_sanity':f'Actual input+output: {rows[0]["total"]}->{rows[1]["total"]}; saving {saving}; paired spend {total}. Both ready/blocked/version/hash oracle answers match; cache not subtracted.',
        'measurement_validity':'Same server/binary/config/model/high effort/cwd/schema/profile and every actual non-task rollout instruction byte; same zero external tool catalogs; only serialized claim encoding differs; quota and dispatch limits checked.',
        'reproducibility':'Separate host process replayed actual mailbox, strict decoder, six-claim reference decisions, source and raw accounting with no model invocation. Frozen six-domain plan and distinct verification task gate publication.'}
    review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(base/'manifest.json'),
        'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':plan['scope'],
        'verifier':{'actor':'host-claims-reviewer','independent':True,'source':'separate native host process',
            'run_id':'TOK-003-verify','method':'raw provider usage + exact actual envelopes + real mailbox/decoder + independent reference oracle'},
        'limitations':['One observed short A/B pair, no statistical/general long-paper or all-workflow quality claim.',
            'This chat/development/research bill and cash cost are not measured; reported tokens are inference pair only.',
            'One observed provider-default sample; no cash price, population mean, statistical quality equivalence or general long-document claim.',
            'All visible non-task instructions and external catalog hashes match; opaque service internals remain unobservable.',
            'Same existing native pair reused after archived measured-Mailbox binding and exact model-input replay under current merged Mailbox; no new provider sample or cost.',
            'Private unredacted RPC/rollout evidence stays local; a different host must rerun independently rather than trust this stored report.',
            'Service output cap is not enforced; local dispatch/time/acceptance bounds and real quota admission apply.'],
        'checks':{k:{'verdict':'pass','reason':v,'evidence':evidence} for k,v in reasons.items()}}
    (base/'independent-review.json').write_bytes((json.dumps(review,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    return review
