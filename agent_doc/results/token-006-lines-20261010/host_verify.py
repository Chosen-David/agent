"""Explicit host verifier; no inference, external commands from data, or retries."""
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys

REL='agent_doc/results/token-006-lines-20261010'
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
            if 'For this two-version artifact comparison, report the current cancellation, input version and unchanged blockers.' in text:continue
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
            if 'For this two-version artifact comparison, report the current cancellation, input version and unchanged blockers.' not in text:rows.append((message['role'],text))
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
    raw_catalogs=read(root/'.agent-runs/token-optimizer-20261009','artifact-lines-catalogs.private.json')
    for name,data in raw_catalogs.items():
        raw=json.dumps(sorted(data,key=lambda s:s['name']),sort_keys=True,ensure_ascii=False).encode()
        assert hashlib.sha256(raw).hexdigest()==catalogs[name]['sha256']
        assert len(data)==catalogs[name]['servers'] and sum(len(s['tools']) for s in data)==catalogs[name]['tools']
    import importlib.util
    module_path=root/'.agent-runs/token-optimizer-20261009/lines_fixture.py'
    spec=importlib.util.spec_from_file_location('trusted_lines_fixture',module_path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    observed,commands=module.replay(root,base)
    baseline=read(base,'baseline.display.json');candidate=read(base,'candidate.display.json')
    assert observed=={'baseline':baseline,'candidate':candidate}
    before_ref=read(base,'before-ref.json');after_ref=read(base,'after-ref.json')
    from agent_runtime.artifact_context import restore_comparison
    original=((base/'before.md').read_bytes().decode('utf-8'),(base/'after.md').read_bytes().decode('utf-8'))
    for value in (baseline,candidate):assert restore_comparison(root,value,before_ref,after_ref)==original
    assert baseline['before']==candidate['before'] and baseline['before']['text']==original[0]
    assert baseline['after']['representation']=='full' and candidate['after']['representation']=='splice'
    for item in (before_ref,after_ref):assert ref(root,item['path'])==item
    a=(base/'baseline.prompt.txt').read_bytes().decode();b=(base/'candidate.prompt.txt').read_bytes().decode()
    aa=a.split('\n',2);bb=b.split('\n',2)
    assert aa[:2]==bb[:2] and max(len(a),len(b))<=7500
    assert aa[0]==module.PREFIX and aa[1]+'\n'==module.GUIDANCE
    assert json.loads(aa[2])==baseline and json.loads(bb[2])==candidate
    original_commands=read(base,'fixture-commands.json')
    assert len(original_commands)==2 and all(c['exit_code']==0 for c in original_commands)
    assert original_commands[0]['argv']==original_commands[1]['argv']+['--full']
    for c in original_commands:assert c['stdout_sha256']==sha(base/(c['name']+'.display.json'))
    current=original[1].splitlines()
    oracle={key:next(line[len(label):] for line in current if line.startswith(label)) for key,label in
        (('status','Status: '),('input_version','Input-Version: '),('next_action','Next-Action: '))}
    oracle['blockers']=[line[len('Blocker: '):] for line in current if line.startswith('Blocker: ')]
    assert oracle['status']=='cancelled' and oracle['input_version']=='figures:v2' and len(oracle['blockers'])==3
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
        raw=(private/(name+'-lines-original.rpc.jsonl')).read_bytes()
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
    proc=subprocess.run([sys.executable,'-X','utf8','-m','unittest','tests.test_artifact_context','-q'],cwd=root,
        capture_output=True,text=True,encoding='utf-8',timeout=90)
    (base/'independent-artifact-context.log').write_bytes((proc.stdout+proc.stderr).encode())
    assert proc.returncode==0 and 'Ran 7 tests' in proc.stderr,proc.stderr
    logs.append(ref(root,REL+'/independent-artifact-context.log'))
    from agent_runtime.result_validation import validate_result_plan
    validate_result_plan(read(base,'task-chain.json'))
    bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
    for group in manifest['artifacts'].values():
        for item in group:
            assert ref(root,item['path'])==item;bindings[item['path']]=item['sha256']
    evidence=[ref(root,REL+'/'+n) for n in ('baseline.rpc.jsonl','candidate.rpc.jsonl','baseline.envelope.json','candidate.envelope.json','published-source-inventory.json','tool-catalog-hashes.json','profiles.json','baseline.display.json','candidate.display.json')]+logs
    reasons={'implementation': 'Real CLI --full/default replay and exact two-text restoration; complete base always present, smaller single-splice current version; no persistent visibility assumption.', 'reference_boundary': 'Seven current tests cover 86 Unicode/CRLF/empty/random pairs, tamper/root/ref/range/duplicate/oversize-before-parse checks, full fallback/budgets/stale sources and no-write real CLI.', 'data_integrity': 'Pre-dispatch archive/source/input hashes, live-source equality, original private RPC and safe export reconcile; exactly two fresh completed no-tool native turns.', 'numerical_sanity': 'Actual provider total input+output decreases and both exact cancellation/new version/action/three unchanged blockers pass; cached input not subtracted.', 'measurement_validity': 'Same server/binary/config/model/high effort/cwd/schema/question/profile, all actual non-task instruction bytes and zero external catalog; only current-version representation differs; exact base/refs retained.', 'reproducibility': 'Independent host process replays real CLI/exact bytes/source/raw accounting and seven necessary tests without inference; frozen plan and separate verify node gate publication.'}
    review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(base/'manifest.json'),
        'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':plan['scope'],
        'verifier':{'actor':'host-lines-reviewer','independent':True,'source':'separate native host process',
            'run_id':'TOK-006-L-verify','method':'raw provider usage + exact actual non-task envelopes + live two-version CLI replay + independent cancellation/constraint oracle'},
        'limitations':['One short synthetic self-contained version comparison. Multi-turn/context-history/long-document/full-workflow quality and costs remain unmeasured.',
            'This chat/development/research bill and cash cost are not measured; reported tokens are inference pair only.',
            'One provider-default short synthetic sample; no cash price, population mean, statistical quality equivalence or general long-document claim.',
            'All visible non-task instructions and external catalog hashes match; opaque service internals remain unobservable.',
            'Private unredacted RPC/rollout evidence stays local; a different host must rerun independently rather than trust this stored report.',
            'Service output cap is not enforced; local dispatch/time/acceptance bounds and real quota admission apply.'],
        'checks':{k:{'verdict':'pass','reason':v,'evidence':evidence} for k,v in reasons.items()}}
    (base/'independent-review.json').write_bytes((json.dumps(review,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    return review
