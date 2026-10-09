#!/usr/bin/env python3
"""Bounded fresh native Codex A/B, using actual provider usage, never estimates."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import tomllib

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.prompt_context import compose_entries, ENTRIES, MARKER
from agent_runtime.project_docs import assert_ai_writable
from agent_runtime.token_usage import short_probe_usage

def dump(path,value):
    path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True); p.add_argument('--output',required=True)
    p.add_argument('--codex',required=True); p.add_argument('--quota',required=True)
    a=p.parse_args(); root=Path(a.root).resolve(); output=Path(a.output).resolve()
    assert_ai_writable(root,output)
    output.mkdir(parents=True,exist_ok=True)
    if (output/'baseline.jsonl').exists() or (output/'candidate.jsonl').exists():
        raise RuntimeError('A/B attempt already exists; inspect it, no retry or duplicate billing')
    quota=json.loads(Path(a.quota).read_text(encoding='utf-8'))['result']
    if quota.get('ordinaryUsageAllowed') is not True:
        raise RuntimeError('ordinary model use is not confirmed allowed')
    limits=quota.get('rateLimitsByLimitId') or {'default':quota.get('rateLimits',{})}
    windows=[]
    for limit in limits.values():
        if limit.get('spendControlReached'): raise RuntimeError('spend control reached')
        for name in ('primary','secondary'):
            window=limit.get(name)
            if window:
                if not isinstance(window.get('usedPercent'),(int,float)) or window['usedPercent']>=90:
                    raise RuntimeError('quota unknown or stop threshold reached')
                windows.append({'limit':limit.get('limitId'),'window':name,'usedPercent':window['usedPercent']})
    if not windows: raise RuntimeError('quota window unavailable')
    dump(output/'quota-admission.json',{'ordinary_allowed':True,'windows':windows,
                                      'source':'authenticated account/rateLimits/read; no inference', 'observed_at':time.time()})
    fixture=output/'fixture'; fixture.mkdir(exist_ok=True)
    block=MARKER+'\n'+(
        'Apply this policy globally. Preserve negative evidence and cancelled work. Earlier success labels do not '
        'promote pending evidence. Evaluate every distinct local rule even when this shared policy is repeated. '
        'Missing budget or permission must not be invented. Report all applicable blocking rule identifiers. '
        'For this fictional reading question do not use tools, delegate or read external files.')
    local={'decision':'If lifecycle=cancelled, starting is forbidden (R_CANCEL). Lifecycle=cancelled.',
           'general':'If evidence=pending, starting is forbidden (R_VERIFY). Evidence=pending.',
           'research':'If budget=unknown, starting is forbidden (R_CAP). Budget=unknown.'}
    for entry,name in ENTRIES.items():
        path=fixture/name; path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(('# '+entry+'\n\n```text\n'+block+'\n【local】\n'+local[entry]+'\n```\n').encode('utf-8'))
    question='\nFor this fictional case, should work start? Return only JSON with proceed (boolean) and reasons (list of the exact blocking rule IDs). No tools.'
    full=compose_entries(fixture,deduplicate=False); chosen=compose_entries(fixture)
    prompts={'baseline':full['prompt']+question,'candidate':chosen['prompt']+question}
    if any(len(text)>2200 for text in prompts.values()):
        raise RuntimeError('supplied short prompt exceeds frozen 2200 character cap')
    schema={'type':'object','properties':{'proceed':{'type':'boolean'},
                'reasons':{'type':'array','items':{'type':'string'},'maxItems':6}},
            'required':['proceed','reasons'],'additionalProperties':False}
    dump(output/'output-schema.json',schema)
    exe=Path(a.codex).resolve()
    config_path=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'config.toml'
    config=tomllib.loads(config_path.read_text(encoding='utf-8'))
    sources=['agent_runtime/prompt_context.py','agent_runtime/token_usage.py','scripts/prompt_context.py',
             'scripts/token_probe.py','tests/test_prompt_context.py']
    dump(output/'source-inventory.json',{'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip(),
        'files':[{'path':s,'sha256':digest(root/s)} for s in sources]})
    dump(output/'config.json',{'binary_sha256':digest(exe),'cli_version':subprocess.check_output([str(exe),'--version']).decode().strip(),
        'model':config.get('model'),'reasoning_effort':config.get('model_reasoning_effort'),
        'user_config_sha256':digest(config_path),'max_invocations':2,'retries':0,
        'max_supplied_chars':2200,'timeout_seconds':90,'first_total_cap':25000,'paired_total_cap':50000,
        'scope':'Explicit short no-tool inference only; hidden host instructions not estimated or omitted from server usage.'})
    collected=[]
    for name,prompt in prompts.items():
        prompt_path=output/(name+'.prompt.txt'); prompt_path.write_bytes(prompt.encode('utf-8'))
        log_path=output/(name+'.jsonl'); final_path=output/(name+'.answer.json')
        command=[str(exe),'exec','--sandbox','read-only','-c','approval_policy="never"',
                 '--json','--output-schema',str(output/'output-schema.json'),'-C',str(root),'-o',str(final_path),'-']
        with log_path.open('wb') as log, (output/(name+'.stderr.log')).open('wb') as err:
            proc=subprocess.Popen(command,cwd=root,stdin=subprocess.PIPE,stdout=log,stderr=err,
                env=dict(os.environ,PYTHONUTF8='1'),creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW)
            dump(output/'live.json',{'phase':name,'pid':proc.pid,'started_at':time.time(),'owned':True})
            try: proc.communicate(prompt.encode('utf-8'),timeout=90)
            except subprocess.TimeoutExpired:
                subprocess.run(['taskkill.exe','/PID',str(proc.pid),'/T','/F'],capture_output=True)
                proc.wait(timeout=10)
                dump(output/'live.json',{'phase':'timeout','attempt':name,'pid':proc.pid})
                return 124
        dump(output/(name+'.process.json'),{'exit_code':proc.returncode,'command':command,'prompt_sha256':digest(prompt_path)})
        if proc.returncode:
            dump(output/'live.json',{'phase':'failed','attempt':name,'exit_code':proc.returncode})
            return proc.returncode
        usage=short_probe_usage(log_path.read_text(encoding='utf-8',errors='replace').splitlines())
        answer=json.loads(final_path.read_text(encoding='utf-8'))
        if answer.get('proceed') is not False or sorted(answer.get('reasons',[]))!=['R_CANCEL','R_CAP','R_VERIFY']:
            raise RuntimeError('quality oracle failed; no success or further model calls')
        collected.append({'name':name,**usage,'answer':answer})
        dump(output/'usage.json',{'observations':collected,'scope':usage['scope']})
        if name=='baseline' and usage['total_tokens']>25000:
            dump(output/'live.json',{'phase':'budget-stop','first_total':usage['total_tokens']})
            return 2
    total=sum(x['total_tokens'] for x in collected)
    savings=collected[0]['total_tokens']-collected[1]['total_tokens']
    dump(output/'outcome.json',{'status':'pending-independent-validation','total_spent':total,
        'measured_saving_tokens':savings,'quality_oracle_passed':True,
        'scope':'This short fixture and fresh model turns only; not long-paper quality or this chat total.'})
    dump(output/'live.json',{'phase':'completed','eligible_for_review':total<=50000 and savings>0})
    print(json.dumps({'status':'pending-independent-validation','measured_saving_tokens':savings,'total_spent':total}))
    return 0 if total<=50000 and savings>0 else 2

if __name__=='__main__': raise SystemExit(main())
