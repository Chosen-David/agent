"""Fixed3 actual short requests, baseline2 versus opted-in candidate1; no retry."""
import sys,queue,subprocess,threading,time,json
from copy import deepcopy
from common import *
sys.path.insert(0,str(R))
from agent_runtime.token_usage import short_appserver_usage
from agent_runtime.maintenance_gate import MaintenanceGate,MaintenanceOutcome

def main():
    assert not (B/'dispatch.json').exists(), 'never repeat dispatch'
    assert not (P/'native-rpc.private.jsonl').exists(), 'never repeat transport'
    frozen=read(B/'freeze.json')
    for path,expected in frozen['hashes'].items():assert sha(R/path)==expected,path
    n=0;q=queue.Queue();active=None;events=[];rows=[];trace=[]
    with (B/'stderr.log').open('w',encoding='utf-8') as err:
        proc=subprocess.Popen([str(EXE),'app-server'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,
                              text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
        def reader():
            with (P/'native-rpc.private.jsonl').open('x',encoding='utf-8') as raw:
                for line in proc.stdout:raw.write(line);raw.flush();q.put(json.loads(line))
        threading.Thread(target=reader,daemon=True).start()
        def call(method,params,capture=None,deadline=None):
            nonlocal n
            n+=1;proc.stdin.write(json.dumps({'id':n,'method':method,'params':params})+'\n');proc.stdin.flush()
            end=min(time.monotonic()+30,deadline or float('inf'))
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
                for key in ('primary','secondary'):
                    v=limit.get(key)
                    if v:assert type(v.get('usedPercent')) in (int,float) and 0<=v['usedPercent']<90;windows.append({'window':key,'usedPercent':v['usedPercent']})
            assert windows
            return {'ordinary_allowed':True,'windows':windows}
        try:
            call('initialize',{'clientInfo':{'name':'maintenance-event-control','version':'1'},'capabilities':{'experimentalApi':True}})
            proc.stdin.write('{"method":"initialized","params":{}}\n');proc.stdin.flush()
            dump(B/'quota-admission.json',quota())
            settings=read(B/'settings.json');threads={};catalogs={}
            for name in ('baseline1','baseline2','candidate1'):
                t=call('thread/start',settings);threads[name]=t
                assert t['cwd']==str(R) and t['model']=='gpt-6.1-sol' and t['reasoningEffort']=='high'
                assert t['approvalPolicy']=='never' and t['sandbox']=={'type':'readOnly','networkAccess':False}
                servers=[];cursor=None
                for _ in range(20):
                    result=call('mcpServerStatus/list',{'threadId':t['thread']['id'],'limit':100,'cursor':cursor})
                    for s in result['data']:assert not s.get('toolsError');servers.append({'name':s['name'],'tools':s['tools']})
                    cursor=result.get('nextCursor')
                    if not cursor:break
                else:raise RuntimeError('catalog pagination')
                assert not any(s['tools'] for s in servers);catalogs[name]=servers
            controls=[{k:v for k,v in t.items() if k!='thread'} for t in threads.values()]
            assert controls[0]==controls[1]==controls[2]
            assert catalogs['baseline1']==catalogs['baseline2']==catalogs['candidate1']
            dump(B/'threads.json',threads);dump(B/'tool-catalogs.json',catalogs)
            dump(B/'dispatch.json',{'pid':proc.pid,'max_paid_calls':3,'retries':0,'freeze_sha256':sha(B/'freeze.json')})
            def infer(name,report):
                nonlocal active,events
                assert len(rows)<3;active=name;events=[];tid=threads[name]['thread']['id']
                text=prompt(report);assert text==(B/'prompt.txt').read_text(encoding='utf-8')
                dump(B/(name+'.quota.json'),quota());deadline=time.monotonic()+90
                r=call('turn/start',{'threadId':tid,'input':[{'type':'text','text':text,'text_elements':[]}],
                    'outputSchema':read(B/'schema.json'),'effort':'high'},events,deadline)
                turn=r['turn']['id']
                while not any(e.get('method')=='turn/completed' and e.get('params',{}).get('threadId')==tid for e in events):
                    if time.monotonic()>=deadline:raise TimeoutError('turn absolute deadline')
                    events.append(q.get(timeout=max(.1,deadline-time.monotonic())))
                    if time.monotonic()>deadline:raise TimeoutError('late terminal/event')
                raw=('\n'.join(json.dumps(e,ensure_ascii=False) for e in events)+'\n').encode()
                (P/(name+'.original.rpc.jsonl')).write_bytes(raw)
                public=[];removed=[]
                for line in raw.decode().splitlines():
                    event=json.loads(line)
                    if event.get('method')=='account/rateLimits/updated':
                        h=hashlib.sha256(line.encode()).hexdigest();removed.append(h);event={'method':'private/rateLimits-notification','params':{'raw_sha256':h}}
                    public.append(json.dumps(event,ensure_ascii=False))
                (B/(name+'.rpc.jsonl')).write_bytes(('\n'.join(public)+'\n').encode())
                dump(B/(name+'.redaction.json'),{'original_sha256':hashlib.sha256(raw).hexdigest(),'removed_line_sha256':removed})
                usage=short_appserver_usage(events,tid,turn);rows.append({'name':name,**usage});dump(B/'usage.json',{'observations':rows})
                assert not any(e.get('method')=='model/rerouted' for e in events)
                assert usage['total_tokens']<=25000 and sum(x['total_tokens'] for x in rows)<=75000
                answers=[e['params']['item']['text'] for e in events if e.get('method')=='item/completed' and e['params'].get('threadId')==tid and e['params']['item']['type']=='agentMessage']
                assert len(answers)==1 and json.loads(answers[0])==ORACLE
                dump(B/(name+'.answer.json'),json.loads(answers[0]))
                history=call('thread/turns/list',{'threadId':tid,'limit':10,'sortDirection':'asc','itemsView':'full'});assert not history.get('nextCursor');dump(B/(name+'.history.json'),history['data'])
                (P/(name+'.rollout.private.jsonl')).write_bytes(Path(threads[name]['thread']['path']).read_bytes())
                trace.append({'request':name,'decision':ORACLE,'outcome':'handled'})
                return MaintenanceOutcome('handled')
            report=deepcopy(REPORT)
            infer('baseline1',report);report['updated_at']=2;infer('baseline2',report)
            report=deepcopy(REPORT)
            gate=MaintenanceGate(lambda r:infer('candidate1',r),lambda:{'project_root':str(R),'run_id':REPORT['run_id'],'events':read(B/'external-events.json')},
                project_root=R,run_id=REPORT['run_id'],max_quiet_seconds=300,clock=lambda:0)
            assert gate(report).status=='handled';report['updated_at']=2
            status=gate(report).status;assert status=='unchanged'
            trace.append({'request':None,'decision':ORACLE,'outcome':status})
            dump(B/'trace.json',trace)
            baseline=rows[0]['total_tokens']+rows[1]['total_tokens'];candidate=rows[2]['total_tokens']
            dump(B/'outcome.json',{'status':'pending-independent-validation','baseline_total':baseline,'candidate_total':candidate,'saving_tokens':baseline-candidate,'total_spent':baseline+candidate})
            assert sha(Path.home()/'.codex/config.toml')==read(B/'config.json')['user_config_sha256']
            print(json.dumps(read(B/'outcome.json')))
        except Exception as exc:
            if active and events:(P/(active+'.failure.rpc.jsonl')).write_text('\n'.join(json.dumps(e) for e in events)+'\n',encoding='utf-8')
            dump(B/'failure.json',{'error':type(exc).__name__+': '+str(exc),'paid_calls_with_usage':len(rows),'success_count_increment':0});raise
        finally:
            proc.terminate()
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
            dump(B/'live.json',{'phase':'terminated','pid':proc.pid,'exit_code':proc.returncode})

if __name__=='__main__':main()
