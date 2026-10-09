"""Exactly two new short paid turns; fork versus dependency-complete fresh child."""
import hashlib,json,queue,subprocess,sys,threading,time
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=Path(__file__).parent;sys.path.insert(0,str(R))
from agent_runtime.turn_usage import current_turn_usage
from scripts.token_probe import dump,digest
from child8_fixture import prepare
B=R/'agent_doc/results/token-008-dispatch-20261010';EXE=R/'.agent-runs/engineering-kb/tools/codex.exe'
SOURCES=['agent_runtime/dispatch_context.py','scripts/dispatch_context.py','agent_runtime/turn_usage.py','tests/test_dispatch_context.py','tests/test_turn_usage.py','agent_runtime/result_validation.py','agent_runtime/legacy_result_paths.py','agent_runtime/project_docs.py','.agent-runs/token-optimizer-20261009/child8_probe.py','.agent-runs/token-optimizer-20261009/child8_fixture.py','.agent-runs/token-optimizer-20261009/verify_child8_pair.py']
def main():
    if (B/'dispatch.json').exists():raise RuntimeError('already dispatched: no inference retries')
    B.mkdir(parents=True,exist_ok=True);schema,plans,oracle=prepare(R,B,P)
    criteria={
        'implementation':('Replay actual CLI and full required SHA-bound guide/packet, all settings and fail-closed defaults.','Fresh only for explicit complete closed task; no dependency truncation/settings writes.'),
        'reference_boundary':('Run six boundary/accounting tests, project/guide/provenance/settings/history gates.','Missing/stale/cross-project/unknown settings or history cannot silently drop context.'),
        'data_integrity':('Verify pre-dispatch sources/plan/input/parent/schema, native completed current-turn bills and original redaction.','Two new no-tool turns only; exact provider last input+output, cache included, no parent bill reuse.'),
        'numerical_sanity':('Compare exact revised v8 cancellation/three-blocker oracle and total input+output.','Both exact oracle answers; candidate strictly lower; first<=25000 and pair<=50000.'),
        'measurement_validity':('Inspect parent/full persisted turns and actual response policies/effort/instructionSources; identical new input/schema/config/tools.','Baseline has exact prior completed parent plus current; candidate only current. Same live declared settings/instructions, no claim of visibility into provider internal hidden assembly.'),
        'reproducibility':('Independent host checks current CLI/source, original raw bills, history snapshots and six tests without inference.','Separate verify_experiment_result owner gates publication; scope one short closed child, not long-paper/full-workflow/cash.')}
    plan={'schema_version':'experiment-validation-plan/v1','criteria':{k:{'procedure':v[0],'acceptance':v[1],'allow_not_applicable':False} for k,v in criteria.items()},
        'scope':'one dependency-complete short synthetic child; inherited one-turn parent versus fresh thread; observable native history/settings controls, provider internal assembly unobservable',
        'controls':{'same_model':'gpt-6.1-sol','same_effort':'high','max_invocations':2,'retries':0,'timeout_seconds':90,'max_prompt_chars':4000,'first_total_cap':25000,'paired_total_cap':50000,'caps_are_dispatch_and_acceptance_not_service_output_limit':True},'oracle':oracle}
    dump(B/'validation-plan.json',plan)
    for n,p in plans.items():(B/(n+'.prompt.txt')).write_bytes(p['input_text'].encode())
    inv={'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'files':[]}
    for s in SOURCES:
        dest=B/'code_snapshot'/s;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((R/s).read_bytes())
        inv['files'].append({'path':s,'sha256':digest(R/s),'archive_path':dest.relative_to(R).as_posix()})
    dump(B/'source-inventory.json',inv);(B/'.gitattributes').write_bytes(b'* -text\n')
    (B/'host_verify.py').write_bytes((P/'verify_child8_pair.py').read_bytes())
    dump(B/'config.json',{'binary_sha256':digest(EXE),'user_config_sha256':digest(Path.home()/'.codex/config.toml'),'model':'gpt-6.1-sol','reasoning_effort':'high'})
    q=queue.Queue();n=0;events=[];active=None
    with (B/'stderr.log').open('w',encoding='utf-8') as err:
        proc=subprocess.Popen([str(EXE),'app-server'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
        def reader():
            with (P/'child8-rpc.private.jsonl').open('w',encoding='utf-8') as raw:
                for line in proc.stdout:raw.write(line);raw.flush();q.put(json.loads(line))
        threading.Thread(target=reader,daemon=True).start()
        def call(method,params,capture=None,absolute_deadline=None):
            nonlocal n
            n+=1;proc.stdin.write(json.dumps({'id':n,'method':method,'params':params})+'\n');proc.stdin.flush();end=time.monotonic()+30
            if absolute_deadline is not None:end=min(end,absolute_deadline)
            while True:
                if time.monotonic()>=end:raise TimeoutError(method)
                e=q.get(timeout=max(.1,end-time.monotonic()))
                if capture is not None:capture.append(e)
                if e.get('id')==n:
                    if e.get('error'):raise RuntimeError(str(e['error']))
                    return e['result']
        def quota():
            r=call('account/rateLimits/read',{});assert r.get('ordinaryUsageAllowed') is True
            windows=[]
            for limit in (r.get('rateLimitsByLimitId') or {'default':r.get('rateLimits',{})}).values():
                assert not limit.get('spendControlReached')
                for k in ('primary','secondary'):
                    w=limit.get(k)
                    if w:assert type(w.get('usedPercent')) in (int,float) and 0<=w['usedPercent']<90;windows.append({'window':k,'usedPercent':w['usedPercent']})
            assert windows
            return {'ordinary_allowed':True,'windows':windows}
        def history(tid):
            r=call('thread/turns/list',{'threadId':tid,'limit':10,'sortDirection':'asc','itemsView':'full'})
            assert not r.get('nextCursor');return r['data']
        try:
            call('initialize',{'clientInfo':{'name':'closed-child-context-pair','version':'1'},'capabilities':{'experimentalApi':True}})
            proc.stdin.write('{"method":"initialized","params":{}}\n');proc.stdin.flush();dump(B/'quota-admission.json',quota())
            assert history(plans['baseline']['params']['threadId'])==json.loads((B/'parent-history.json').read_text())
            threads={name:call(p['method'],p['params']) for name,p in plans.items()};dump(B/'threads.json',threads)
            for start in threads.values():
                assert start['cwd']==str(R) and start['model']=='gpt-6.1-sol' and start['reasoningEffort']=='high'
                assert start['approvalPolicy']=='never' and start['sandbox']=={'type':'readOnly','networkAccess':False}
            assert threads['baseline']['instructionSources']==threads['candidate']['instructionSources']
            old_controls=json.loads((B/'parent-settings-binding.json').read_text())['creation_response_controls']
            for start in threads.values():assert {k:v for k,v in start.items() if k not in ('thread','instructionSources')}==old_controls
            dump(B/'baseline-history-before.json',history(threads['baseline']['thread']['id']))
            assert json.loads((B/'baseline-history-before.json').read_text())==json.loads((B/'parent-history.json').read_text())
            catalogs={}
            for name,start in threads.items():
                rows=[];cursor=None
                for _ in range(20):
                    r=call('mcpServerStatus/list',{'threadId':start['thread']['id'],'limit':100,'cursor':cursor})
                    for s in r['data']:assert not s.get('toolsError');rows.append({'name':s['name'],'tools':s['tools']})
                    cursor=r.get('nextCursor')
                    if not cursor:break
                else:raise RuntimeError('catalog pagination')
                assert not any(s['tools'] for s in rows)
                catalogs[name]=rows
            assert catalogs['baseline']==catalogs['candidate'];dump(B/'tool-catalogs.json',catalogs)
            bound=['validation-plan.json','source-inventory.json','host-request.json','dispatch-plans.json','output-schema.json','parent-history.json','config.json','parent-settings-binding.json']
            dump(B/'dispatch.json',{'server_pid':proc.pid,'max_paid_calls':2,'started_at':time.time(),'frozen_hashes':{s:digest(B/s) for s in bound},'prompt_sha256':{n:digest(B/(n+'.prompt.txt')) for n in plans}})
            observations=[]
            for name,p in plans.items():
                dump(B/(name+'.quota.json'),quota());active=name;events=[];tid=threads[name]['thread']['id']
                dump(B/'live.json',{'phase':name,'pid':proc.pid,'thread_id':tid});deadline=time.monotonic()+90
                r=call('turn/start',{'threadId':tid,'input':[{'type':'text','text':p['input_text'],'text_elements':[]}],'outputSchema':schema,'effort':'high'},events,deadline);turn=r['turn']['id']
                while not any(e.get('method')=='turn/completed' and e.get('params',{}).get('threadId')==tid for e in events):
                    events.append(q.get(timeout=max(.1,deadline-time.monotonic())))
                    if time.monotonic()>deadline:raise TimeoutError('turn timeout')
                (B/(name+'.rpc.jsonl')).write_bytes(('\n'.join(json.dumps(e,ensure_ascii=False) for e in events)+'\n').encode())
                usage=current_turn_usage(events,tid,turn)
                answers=[e['params']['item']['text'] for e in events if e.get('method')=='item/completed' and e.get('params',{}).get('threadId')==tid and e['params']['item']['type']=='agentMessage']
                assert len(answers)==1;answer=json.loads(answers[0]);dump(B/(name+'.answer.json'),answer);assert answer==oracle
                observations.append({'name':name,**usage});dump(B/'usage.json',{'observations':observations})
                dump(B/(name+'.history-after.json'),history(tid))
                (P/(name+'-child8-rollout.private.jsonl')).write_bytes(Path(threads[name]['thread']['path']).read_bytes())
                if name=='baseline' and usage['total_tokens']>25000:raise RuntimeError('first dispatch cap exceeded')
            spent=sum(x['total_tokens'] for x in observations);saving=observations[0]['total_tokens']-observations[1]['total_tokens']
            dump(B/'outcome.json',{'status':'pending-independent-validation' if saving>0 and spent<=50000 else 'failed','saving_tokens':saving,'total_spent':spent,'success_count':0})
            assert digest(Path.home()/'.codex/config.toml')==json.loads((B/'config.json').read_text())['user_config_sha256']
            print(json.dumps({'saving_tokens':saving,'total_spent':spent,'independent_validation_pending':True}))
        except Exception as exc:
            if active:(B/(active+'.rpc.jsonl')).write_bytes(('\n'.join(json.dumps(e,ensure_ascii=False) for e in events)+'\n').encode())
            dump(B/'outcome.json',{'status':'failed','error':type(exc).__name__+': '+str(exc),'success_count':0});raise
        finally:proc.terminate();proc.wait(timeout=10);dump(B/'live.json',{'phase':'terminated','pid':proc.pid,'exit_code':proc.returncode})
if __name__=='__main__':main()
