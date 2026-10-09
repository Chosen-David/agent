"""One native server, two fresh short turns. No inference retries."""
import hashlib
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R))
from agent_runtime.token_usage import short_appserver_usage
from agent_runtime.prompt_context import compose_entries
from agent_runtime.codex_tool_scope import resolve_tool_scope, check_scoped_catalog
from scripts.token_probe import digest, dump

P = Path(__file__).parent
OLD = R / 'agent_doc/results/token-001-20261009'
B = R / 'agent_doc/results/token-007-skills-20261010'
EXE = R / '.agent-runs/engineering-kb/tools/codex.exe'

def envelopes(path):
    rows = []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        event = json.loads(line)
        if event['type'] == 'session_meta':
            value = event['payload'].get('base_instructions')
            text = json.dumps(value, ensure_ascii=False, sort_keys=True)
            rows.append({'kind': 'base', 'sha256': hashlib.sha256(text.encode()).hexdigest()})
        elif event['type'] == 'response_item' and event['payload'].get('type') == 'message':
            message = event['payload']
            if message.get('role') not in ('developer', 'system', 'user'):
                continue
            text = ''.join(c.get('text', '') for c in message.get('content', []))
            if 'For this closed packet interpretation task, copy the current cancellation and unchanged blockers.' in text:
                continue
            # Only transport ids are omitted; all instruction/environment text stays exact.
            rows.append({'kind': message['role'], 'sha256': hashlib.sha256(text.encode()).hexdigest(),
                         'characters': len(text)})
    return rows

def main():
    if (B/'dispatch.json').exists():
        raise RuntimeError('already dispatched; never restart paid attempts')
    B.mkdir(parents=True, exist_ok=True)
    from skills_fixture import prepare
    schema, prompts, oracle = prepare(R, B, P)
    assert max(map(len, prompts.values())) <= 4000
    for name, prompt in prompts.items():
        (B/(name+'.prompt.txt')).write_bytes(prompt.encode('utf-8'))
    plan={'schema_version': 'experiment-validation-plan/v1', 'criteria': {'implementation': {'procedure': 'Replay actual skill-scope CLI on native host-selected metadata; compare declared exclusions and retained existing entries.', 'acceptance': 'Only eleven explicitly named irrelevant role skill paths disabled; five required roles retained; no global writes.', 'allow_not_applicable': False}, 'reference_boundary': {'procedure': 'Check unknown/incomplete requirements, required/disabled/system skills, duplicate/quoted/inline/out-of-section entries and project boundaries.', 'acceptance': 'Fail closed on unavailable required skills or ambiguity; unknown/unlisted/system entries and all non-catalog instructions remain.', 'allow_not_applicable': False}, 'data_integrity': {'procedure': 'Check frozen source, skill source/settings metadata, identical packet/schema and exactly two fresh successful native raw turns.', 'acceptance': 'Actual final provider input+output, reasoning included, no reused bills/tools/retries or cached-input subtraction.', 'allow_not_applicable': False}, 'numerical_sanity': {'procedure': 'Compare exact cancellation/version/action/three-blocker oracle and actual total tokens.', 'acceptance': 'Both exact answers pass and candidate total is lower, pair<=50000.', 'allow_not_applicable': False}, 'measurement_validity': {'procedure': 'Independently inspect every actual instruction byte/tool catalog and bind complete removed lines to excluded skill paths via unchanged root table.', 'acceptance': 'Only declared skill catalog full lines differ, all roots/permission/project/invocation rules/remaining messages/tools identical; same model/high/schema/question.', 'allow_not_applicable': False}, 'reproducibility': {'procedure': 'Separate host replays current actual CLI/source/native accounting, metadata/profile and five boundary tests without inference.', 'acceptance': 'Frozen six-domain plan and independent node gates main publication; one short closed task, no general long-context/whole-chat/cash claim.', 'allow_not_applicable': False}}, 'scope': 'one short closed synthetic interpretation task; explicit skill exposure only, actual native catalog delta required', 'controls': {'same_model': 'gpt-6.1-sol', 'same_effort': 'high', 'max_invocations': 2, 'retries': 0, 'timeout_seconds': 90, 'max_prompt_chars': 4000, 'first_total_cap': 25000, 'paired_total_cap': 50000, 'caps_are_dispatch_and_acceptance_not_service_output_limit': True}, 'success_requires': ['candidate provider total input+output decreases', 'both exact packet oracles pass', 'only host-bound complete skill catalog entries removed; all other actual text/tools identical', 'independent replay/source/quality validation passes']}
    plan['oracle']=oracle
    dump(B/'validation-plan.json',plan)
    dump(B/'source-inventory.json', {'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip(),
        'files':[{'path':s,'sha256':digest(R/s)} for s in [
'agent_runtime/codex_skill_scope.py','scripts/codex_skill_scope.py','tests/test_codex_skill_scope.py','agent_runtime/result_validation.py','agent_runtime/legacy_result_paths.py','agent_runtime/project_docs.py','agent_runtime/token_usage.py','agent_runtime/codex_tool_scope.py','.agent-runs/token-optimizer-20261009/skills_probe.py','.agent-runs/token-optimizer-20261009/skills_fixture.py','.agent-runs/token-optimizer-20261009/verify_skill_pair.py']]})
    archive=B/'code_snapshot';archive.mkdir()
    inventory=json.loads((B/'source-inventory.json').read_text())
    for item in inventory['files']:
        target=archive/item['path'];target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((R/item['path']).read_bytes())
        assert digest(target)==item['sha256']
        item['archive_path']=target.relative_to(R).as_posix()
    dump(B/'source-inventory.json',inventory)
    (B/'.gitattributes').write_text('* -text\n')
    (B/'producer.py').write_bytes(Path(__file__).read_bytes())
    (B/'skills_fixture.py').write_bytes((P/'skills_fixture.py').read_bytes())
    (B/'host_verify.py').write_bytes((P/'verify_skill_pair.py').read_bytes())
    dump(B/'config.json', {'binary_sha256':digest(EXE),'user_config_sha256':digest(Path.home()/'.codex/config.toml'),
        'transport':'one app-server; two fresh thread/start; same no-external profile, candidate explicit skill exclusions only',
        'model':'gpt-6.1-sol','reasoning_effort':'high'})
    messages = queue.Queue()
    with (B/'stderr.log').open('w',encoding='utf-8') as err:
        proc = subprocess.Popen([str(EXE),'app-server'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
            stderr=err,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
        def read():
            with (P/'skill-scope-rpc.jsonl').open('w',encoding='utf-8') as raw:
                for line in proc.stdout:
                    raw.write(line); raw.flush()
                    try: messages.put(json.loads(line))
                    except ValueError: messages.put({'method':'error','params':{'message':'damaged JSON'}})
        threading.Thread(target=read, daemon=True).start()
        rpc_id = 0
        def send(method, params=None):
            proc.stdin.write(json.dumps({'method':method,'params':params or {}})+'\n'); proc.stdin.flush()
        def call(method, params, events=None, absolute_deadline=None):
            nonlocal rpc_id
            rpc_id += 1
            proc.stdin.write(json.dumps({'id':rpc_id,'method':method,'params':params})+'\n'); proc.stdin.flush()
            deadline = time.monotonic()+25
            if absolute_deadline is not None: deadline=min(deadline,absolute_deadline)
            while True:
                if time.monotonic()>=deadline: raise TimeoutError(method)
                value = messages.get(timeout=max(.1,deadline-time.monotonic()))
                if events is not None: events.append(value)
                if value.get('id') == rpc_id:
                    if value.get('error'): raise RuntimeError(str(value['error']))
                    return value['result']
        def check_quota():
            quota=call('account/rateLimits/read',{})
            limits=quota.get('rateLimitsByLimitId') or {'default':quota.get('rateLimits',{})}
            windows=[]
            assert quota.get('ordinaryUsageAllowed') is True
            for limit in limits.values():
                assert not limit.get('spendControlReached')
                for name in ('primary','secondary'):
                    w=limit.get(name)
                    if w:
                        assert type(w.get('usedPercent')) in (int,float) and w['usedPercent']<90
                        windows.append({'limit':limit.get('limitId'),'window':name,'usedPercent':w['usedPercent']})
            assert windows
            return {'ordinary_allowed':True,'windows':windows,'observed_at':time.time()}
        events=[]
        active=None
        try:
            call('initialize',{'clientInfo':{'name':'agent-token-controls','version':'1.0'}})
            send('initialized')
            dump(B/'quota-admission.json',check_quota())
            threads = {}
            profiles = {name:resolve_tool_scope({'schema_version':'codex-tool-scope/v1','requirements_complete':True,'external_tool_requirements':[]}) for name in prompts}
            skill=json.loads((B/'candidate-skill-profile.json').read_text(encoding='utf-8'))
            profiles['candidate']['config_overrides'].update(skill['config_overrides'])
            dump(B/'profiles.json',profiles)
            for name in prompts:
                start = call('thread/start',{'cwd':str(R),'model':'gpt-6.1-sol','approvalPolicy':'never',
                    'sandbox':'read-only','ephemeral':False,'config':profiles[name]['config_overrides']})
                assert start['model']=='gpt-6.1-sol' and start['reasoningEffort']=='high'
                threads[name] = start
            dump(B/'threads.json',threads)
            catalogs = {}
            catalog_rows = {}
            for name, start in threads.items():
                data = []
                cursor = None
                for page in range(20):
                    inventory = call('mcpServerStatus/list', {'threadId':start['thread']['id'],
                        'cursor':cursor,'limit':100})
                    for server in inventory['data']:
                        if server.get('toolsError'):
                            raise RuntimeError('tool catalog unavailable; stop before inference')
                        data.append({'name':server['name'],'tools':server['tools']})
                    cursor=inventory.get('nextCursor')
                    if not cursor: break
                else: raise RuntimeError('tool catalog pagination exceeds bound')
                check_scoped_catalog(profiles[name]['profile'],data)
                catalog_rows[name]=data
                raw=json.dumps(sorted(data,key=lambda s:s['name']),sort_keys=True,ensure_ascii=False).encode()
                catalogs[name]={'sha256':hashlib.sha256(raw).hexdigest(),
                    'servers':len(data),'tools':sum(len(s['tools']) for s in data)}
            dump(B/'tool-catalog-hashes.json',catalogs)
            if catalogs['baseline']!=catalogs['candidate'] or catalogs['baseline']['tools']!=0:
                raise RuntimeError('catalogs must be identical and have no external tools')
            dump(P/'skill-scope-catalogs.private.json',catalog_rows)
            dump(B/'dispatch.json',{'server_pid':proc.pid,'max_paid_calls':2,'started_at':time.time(),
                'validation_plan_sha256':digest(B/'validation-plan.json'),'source_inventory_sha256':digest(B/'source-inventory.json'),
                'host_request_sha256':digest(B/'host-request.json'),'profiles_sha256':digest(B/'profiles.json'),
                'schema_sha256':digest(B/'output-schema.json'),
                'prompt_sha256':{name:digest(B/(name+'.prompt.txt')) for name in prompts}})
            observations=[]
            for name, prompt in prompts.items():
                dump(B/(name+'.quota.json'),check_quota())
                events=[]
                active=name
                thread=threads[name]['thread']
                dump(B/'live.json',{'phase':name,'pid':proc.pid,'thread_id':thread['id']})
                deadline=time.monotonic()+90
                start = call('turn/start',{'threadId':thread['id'],
                    'input':[{'type':'text','text':prompt,'text_elements':[]}],
                    'outputSchema':schema,'effort':'high'}, events, deadline)
                turn_id=start['turn']['id']
                while not any(e.get('method')=='turn/completed' and e.get('params',{}).get('threadId')==thread['id'] for e in events):
                    events.append(messages.get(timeout=max(.1,deadline-time.monotonic())))
                    if time.monotonic()>deadline: raise TimeoutError('turn timeout')
                (B/(name+'.rpc.jsonl')).write_bytes(('\n'.join(json.dumps(e,ensure_ascii=False) for e in events)+'\n').encode('utf-8'))
                usage=short_appserver_usage(events,thread['id'],turn_id)
                items=[e['params']['item'] for e in events if e.get('method')=='item/completed' and
                       e.get('params',{}).get('threadId')==thread['id'] and e.get('params',{}).get('item',{}).get('type')=='agentMessage']
                assert len(items)==1
                answer=json.loads(items[0]['text'])
                dump(B/(name+'.answer.json'),answer)
                assert answer==oracle, 'independent exact packet oracle mismatch'
                observations.append({'name':name,**usage,'answer':answer})
                dump(B/'usage.json',{'observations':observations})
                control=envelopes(thread['path'])
                dump(B/(name+'.envelope.json'),control)
                if name=='baseline' and usage['total_tokens']>25000: raise RuntimeError('first-turn dispatch budget exhausted')
            total=sum(r['total_tokens'] for r in observations)
            saving=observations[0]['total_tokens']-observations[1]['total_tokens']
            same=None  # independent owner must inspect allowed catalog-only differences
            dump(B/'outcome.json',{'status':'pending-independent-validation' if saving>0 and total<=50000 else 'failed',
                'non_catalog_control_pending':True,'saving_tokens':saving,'total_spent':total,'success_count':0,
                'scope':'this one short controlled pair; no long-text or whole-chat claim'})
            print(json.dumps({'non_catalog_control_pending':True,'saving_tokens':saving,'total_spent':total}))
        except Exception as exc:
            if active:
                (B/(active+'.rpc.jsonl')).write_bytes(('\n'.join(json.dumps(e,ensure_ascii=False) for e in events)+'\n').encode('utf-8'))
            dump(B/'outcome.json',{'status':'failed','error':type(exc).__name__+': '+str(exc),
                'success_count':0,'raw_rpc_preserved_privately':True})
            raise
        finally:
            proc.terminate()
            proc.wait(timeout=10)
            dump(B/'live.json',{'phase':'terminated','pid':proc.pid,'exit_code':proc.returncode})

if __name__ == '__main__': main()
