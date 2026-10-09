"""Separate host audit: independently recompute provider usage and frozen inputs."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

REL='agent_doc/results/token-001-20261009'
def ref(root,path): return {'path':path,'sha256':hashlib.sha256((root/path).read_bytes()).hexdigest()}

def verify(root,manifest,plan):
    root=Path(root); base=root/REL
    # This first actual pair exposed changing host developer instructions.
    # The apparent usage improvement therefore cannot pass a causal A/B gate.
    envelopes=json.loads((root/'.agent-runs/token-optimizer-20261009/envelopes.json').read_text(encoding='utf-8'))
    left=[x for x in envelopes[0]['envelopes'] if x['kind']!='task']
    right=[x for x in envelopes[1]['envelopes'] if x['kind']!='task']
    if left!=right:
        raise ValueError('non-task input envelopes differ; this pair is confounded and not accepted')
    inventory=json.loads((base/'source-inventory.json').read_text(encoding='utf-8'))
    for item in inventory['files']: assert ref(root,item['path'])==item,item['path']
    from agent_runtime.prompt_context import compose_entries
    full=compose_entries(base/'fixture',deduplicate=False)['prompt']
    short=compose_entries(base/'fixture')['prompt']
    a=(base/'baseline.prompt.txt').read_bytes().decode('utf-8')
    b=(base/'candidate.prompt.txt').read_bytes().decode('utf-8')
    assert a.startswith(full) and b==short+a[len(full):]
    assert a[len(full):].strip() and len(a)<=2200 and len(b)<=2200
    rows=[]
    for name in ('baseline','candidate'):
        events=[json.loads(line) for line in (base/(name+'.jsonl')).read_text(encoding='utf-8').splitlines()]
        assert [e['type'] for e in events[:2]]==['thread.started','turn.started']
        assert events[-1]['type']=='turn.completed'
        assert sum(e['type']=='turn.completed' for e in events)==1
        assert all(e['type'].startswith('item.') and e['item']['type'] in ('reasoning','agent_message') for e in events[2:-1])
        u=events[-1]['usage']
        assert all(type(u[k]) is int and u[k]>=0 for k in ('input_tokens','output_tokens','cached_input_tokens'))
        assert u['cached_input_tokens']<=u['input_tokens']
        process=json.loads((base/(name+'.process.json')).read_text(encoding='utf-8'))
        assert process['exit_code']==0 and process['prompt_sha256']==ref(root,REL+'/'+name+'.prompt.txt')['sha256']
        answer=json.loads((base/(name+'.answer.json')).read_text(encoding='utf-8'))
        assert set(answer)=={'proceed','reasons'} and answer['proceed'] is False
        assert sorted(answer['reasons'])==['R_CANCEL','R_CAP','R_VERIFY']
        messages=[e['item']['text'] for e in events[2:-1] if e['type']=='item.completed' and e['item']['type']=='agent_message']
        assert len(messages)==1 and json.loads(messages[0])==answer
        rows.append({'name':name,'thread_id':events[0]['thread_id'],**u,'total':u['input_tokens']+u['output_tokens'],
                     'command':process['command']})
    assert rows[0]['thread_id']!=rows[1]['thread_id']
    # Both invocations have exactly the same flags; only the output path differs.
    commands=[]
    for row in rows:
        command=list(row['command']); command[command.index('-o')+1]='<output>'
        commands.append(command)
    assert commands[0]==commands[1] and '--sandbox' in commands[0] and '--json' in commands[0]
    total=sum(r['total'] for r in rows); saving=rows[0]['total']-rows[1]['total']
    assert rows[0]['total']<=25000 and total<=50000 and saving>0
    config=json.loads((base/'config.json').read_text(encoding='utf-8'))
    assert config['max_invocations']==2 and config['retries']==0 and config['timeout_seconds']==90
    import os, tomllib
    cfgpath=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'config.toml'
    assert hashlib.sha256(cfgpath.read_bytes()).hexdigest()==config['user_config_sha256']
    actual=tomllib.loads(cfgpath.read_text(encoding='utf-8'))
    assert actual.get('model')==config['model'] and actual.get('model_reasoning_effort')==config['reasoning_effort']
    assert hashlib.sha256(Path(rows[0]['command'][0]).read_bytes()).hexdigest()==config['binary_sha256']
    admission=json.loads((base/'quota-admission.json').read_text(encoding='utf-8'))
    private=json.loads((root/'.agent-runs/token-optimizer-20261009/quota.json').read_text(encoding='utf-8'))['result']
    assert private['ordinaryUsageAllowed'] is True and admission['ordinary_allowed'] is True
    limits=private.get('rateLimitsByLimitId') or {'default':private['rateLimits']}
    windows=[]
    for limit in limits.values():
        assert not limit.get('spendControlReached')
        for name in ('primary','secondary'):
            if limit.get(name):
                assert limit[name]['usedPercent']<90
                windows.append({'limit':limit.get('limitId'),'window':name,'usedPercent':limit[name]['usedPercent']})
    assert windows==admission['windows'] and windows
    focused=[]
    for name,pattern in (('composer','test_prompt_context.py'),('entry-contract','test_main_ai_contract.py')):
        p=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p',pattern,'-v'],cwd=root,
                         capture_output=True,text=True,encoding='utf-8',timeout=60)
        log=base/('independent-'+name+'.log'); log.write_bytes((p.stdout+p.stderr).encode('utf-8'))
        assert p.returncode==0,p.stdout+p.stderr
        assert re.search(r'Ran [1-9][0-9]* tests',p.stdout+p.stderr)
        focused.append(ref(root,REL+'/'+log.name))
    bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
    for group in manifest['artifacts'].values():
        for item in group:
            assert ref(root,item['path'])==item
            bindings[item['path']]=item['sha256']
    observations=[ref(root,REL+'/'+n) for n in ('source-inventory.json','baseline.jsonl','candidate.jsonl',
                         'baseline.answer.json','candidate.answer.json','config.json','quota-admission.json')]+focused
    reasons={
      'implementation':'Actual composer and CLI preserve exact unique and conflicting text; separate host reconstruction matches both supplied prompts.',
      'reference_boundary':'Fresh deterministic replay includes outer fences, HTML comments, corrupted and out-of-order usage, absent policy/caps and Windows symlink permission skip.',
      'data_integrity':'One fresh no-tool successful terminal provider usage in each raw stdout; separate stderr and bound code/fixture/process/config/answers.',
      'numerical_sanity':f'Independent raw total: {rows[0]["total"]} to {rows[1]["total"]}, difference {saving}; paired spend {total}, cached not subtracted; exact three-blocker oracle both pass.',
      'measurement_validity':'Same binary/config/flags/schema/root, one small supplied pair; provider host context is included in totals, not independently assumed constant semantic content.',
      'reproducibility':'Separate actual host process reproduced composer and targeted source contracts without extra billed model calls; private quota snapshot matched sanitized admission.'}
    return {'schema_version':'experiment-validation/v1','manifest_sha256':ref(root,REL+'/manifest.json')['sha256'],
        'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':plan['scope'],
        'verifier':{'actor':'host-token-001-reviewer','independent':True,'source':'explicit separate controller process',
                    'run_id':'host-token-001-20261009','method':'independent raw usage/oracle accounting and code/fixture replay'},
        'limitations':['One short observed A/B pair, not statistical average or general long-paper quality.',
                       'Full hidden provider input envelopes were not captured; same client configuration is verified, not hidden backend identity.',
                       'This chat, development/research token bill, cash prices and whole workflow quality were not measured.',
                       'Quota is an actual local authenticated admission snapshot, not a future entitlement or service-enforced output cap.'],
        'checks':{key:{'verdict':'pass','reason':reason,'evidence':observations} for key,reason in reasons.items()}}
