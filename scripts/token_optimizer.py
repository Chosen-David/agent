"""Single hourly host admission + bounded actual Codex worker, not a heartbeat-only task.

Run once from a tmux interval host. State/raw transport remain private and local.
Never force-push, auto-stash, remove user data, or count a skipped tick as savings.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import json,math,os,queue,subprocess,sys,threading,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.project_docs import guard_write_path

INTERVAL=3600
PROMPT='''PROJECT_ROOT=WORKFLOW_ROOT=current repository. Continue agent token optimization only, one concrete iteration. Read current human GUIDE, TASK/TOK-FIVE, progress.json and relevant prior results/advice, not historical full transcripts. Preserve concurrent work. Prefer high-frequency communication and long-context costs. No other project advice interaction, duplicate agents or schedules. Reuse current mechanisms. Limit one optional actual short no-tool A/B pair to 2200 supplied chars per prompt, at most 2 paid calls/50000 paired tokens, no retries; read fresh quota before paid tests. Provider totals and independent quality/source verification are required to count a success; CPU/estimates/negative results do not count. Preserve pending/failed data. Make a useful change, run necessary checks, fetch again and ordinary commit/push main (GitHub MCP non-force expected-SHA publication if native auth fails), independently read back remote and synchronize setup_codex.py then --check. Preserve conflicts and write a concise recovery record if blocked. Keep final report brief; no fabricated token/cash or weight-update claim.'''

def atomic(path,value):
    guard_write_path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.new')
    with tmp.open('wb') as stream:
        stream.write((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode());stream.flush();os.fsync(stream.fileno())
    os.replace(tmp,path)

def advance_due(previous,now):
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in (previous,now)):
        raise ValueError('finite nonnegative schedule timestamps required')
    return previous+max(1,math.floor((now-previous)/INTERVAL)+1)*INTERVAL

def quota_admission(result):
    if not isinstance(result,dict) or result.get('ordinaryUsageAllowed') is not True:
        return {'admitted':False,'reason':'ordinary usage not confirmed','windows':[]}
    windows=[]
    limits=result.get('rateLimitsByLimitId') or {'default':result.get('rateLimits',{})}
    if not isinstance(limits,dict):return {'admitted':False,'reason':'invalid quota','windows':[]}
    for limit in limits.values():
        if not isinstance(limit,dict) or limit.get('spendControlReached'):
            return {'admitted':False,'reason':'spend control or unknown limit','windows':windows}
        for name in ('primary','secondary'):
            v=limit.get(name)
            if v is None:continue
            used=v.get('usedPercent') if isinstance(v,dict) else None
            if type(used) not in (int,float) or not math.isfinite(used) or not 0<=used<=100:
                return {'admitted':False,'reason':'invalid quota window','windows':windows}
            windows.append({'window':name,'usedPercent':used,'resetsAt':v.get('resetsAt')})
    return {'admitted':bool(windows) and all(w['usedPercent']<90 for w in windows),
            'reason':'predeclared90percent admission','windows':windows}

@contextmanager
def exclusive(path):
    guard_write_path(path);path.parent.mkdir(parents=True,exist_ok=True)
    stream=path.open('a+b');locked=False
    try:
        if os.name=='nt':
            import msvcrt
            if path.stat().st_size==0:stream.write(b'\0');stream.flush()
            stream.seek(0)
            try:msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1);locked=True
            except OSError:pass
        else:
            import fcntl
            try:fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB);locked=True
            except OSError:pass
        yield locked
    finally:
        if locked:
            if os.name=='nt':
                stream.seek(0);msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(stream.fileno(),fcntl.LOCK_UN)
        stream.close()

def command(root,*args):
    env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',PYTHONUTF8='1')
    p=subprocess.run(args,cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',timeout=90)
    if p.returncode:raise RuntimeError('host preflight failed: '+args[0])
    return p.stdout.strip()

def synchronize(root):
    if command(root,'git','branch','--show-current')!='main':raise RuntimeError('main required')
    if command(root,'git','status','--porcelain'):raise RuntimeError('dirty tree preserved; no auto-stash')
    command(root,'git','fetch','origin','main');command(root,'git','pull','--ff-only','origin','main')
    head=command(root,'git','rev-parse','HEAD')
    if head!=command(root,'git','rev-parse','origin/main'):raise RuntimeError('fetched main mismatch')
    command(root,sys.executable,'scripts/setup_codex.py');command(root,sys.executable,'scripts/setup_codex.py','--check')
    return head

def observe_parent_turn(q,backlog,tid,turn,run,send,*,timeout_seconds,max_observed_tokens):
    """Observe native parent snapshots, never infer a final or cross-actor bill."""
    deadline=time.monotonic()+timeout_seconds;observed=None;previous=None;interrupted=False;saw_error=False
    fields=('inputTokens','cachedInputTokens','outputTokens','totalTokens','reasoningOutputTokens')
    def receipt(status,invalid=None):
        usage_status=('invalid' if invalid else 'missing' if observed is None else
                      'observed' if status=='worker-completed' and not saw_error else 'partial')
        return {'status':status,'model_requests':None,'thread_id':tid,'turn_id':turn,
                'observed_parent_total_tokens':None if invalid else observed,
                'last_observed_parent_total_tokens':observed,
                'usage_status':usage_status,'usage_complete':False,
                'usage_reason':invalid or ('no matching usage notification' if observed is None else
                    'parent snapshot only; terminal/final bill and child usage are not certified'),
                'counts_as_token_success':False}
    try:
        while time.monotonic()<deadline:
            try:event=backlog.pop(0) if backlog else q.get(timeout=min(2,max(.1,deadline-time.monotonic())))
            except queue.Empty:continue
            if not isinstance(event,dict) or event.get('local_error'):
                raise ValueError('damaged native transport')
            p=event.get('params',{})
            if not isinstance(p,dict):raise ValueError('invalid native event params')
            if p.get('threadId')!=tid:continue
            method=event.get('method')
            if method in ('thread/tokenUsage/updated','error'):
                if p.get('turnId')!=turn:continue
                if method=='error':saw_error=True;continue
                usage=p.get('tokenUsage')
                if not isinstance(usage,dict):raise ValueError('missing native usage')
                last=usage.get('last');total=usage.get('total')
                # Same five native counters/arithmetic as current_turn_usage; no cache subtraction.
                for u in (last,total):
                    if not isinstance(u,dict) or any(type(u.get(k)) is not int or u[k]<0 for k in fields):
                        raise ValueError('missing/inconsistent native counters')
                    if u['totalTokens']!=u['inputTokens']+u['outputTokens'] or u['cachedInputTokens']>u['inputTokens'] or u['reasoningOutputTokens']>u['outputTokens']:
                        raise ValueError('inconsistent native counter arithmetic')
                if any(total[k]<last[k] or (previous is not None and total[k]<previous[k]) for k in fields):
                    raise ValueError('invalid cumulative usage')
                observed=total['totalTokens'];previous=total.copy()
                atomic(run/'observed-usage.json',{'total_tokens':observed,'budget':max_observed_tokens,
                       'thread_id':tid,'turn_id':turn,'tokenUsage':usage,'usage_complete':False,
                       'scope':'parent thread only; child benchmarks must separately account all calls'})
                if observed>=max_observed_tokens and not interrupted:
                    send('turn/interrupt',{'threadId':tid,'turnId':turn});interrupted=True;deadline=min(deadline,time.monotonic()+15)
            if method=='turn/completed':
                terminal=p.get('turn')
                if not isinstance(terminal,dict):raise ValueError('invalid terminal turn')
                if terminal.get('id')!=turn:continue
                if terminal.get('status') not in ('completed','failed','interrupted'):
                    raise ValueError('invalid terminal status')
                if terminal.get('error'):saw_error=True
                return receipt('budget-interrupted' if interrupted else 'worker-'+terminal['status'])
        send('turn/interrupt',{'threadId':tid,'turnId':turn})
        return receipt('time-or-interrupt-deadline')
    except ValueError as exc:
        send('turn/interrupt',{'threadId':tid,'turnId':turn})
        return receipt('usage-invalid',str(exc))

def run_worker(root,exe,run,*,timeout_seconds=1200,max_observed_tokens=75000,probe_only=False):
    if os.name!='nt':raise ValueError('selected native backend requires Windows Python; WSL hosts the tmux timer')
    q=queue.Queue();counter=0;backlog=[]
    flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
    with (run/'stderr.private.log').open('x',encoding='utf-8') as err:
        proc=subprocess.Popen([str(exe),'app-server'],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                              stderr=err,text=True,encoding='utf-8',creationflags=flags)
        def reader():
            with (run/'transport.private.jsonl').open('x',encoding='utf-8') as raw:
                for line in proc.stdout:
                    raw.write(line);raw.flush()
                    try:q.put(json.loads(line))
                    except ValueError:q.put({'local_error':'damaged JSON transport'})
        threading.Thread(target=reader,daemon=True).start()
        def send(method,params):
            nonlocal counter
            counter+=1;proc.stdin.write(json.dumps({'id':counter,'method':method,'params':params})+'\n');proc.stdin.flush();return counter
        def call(method,params):
            identifier=send(method,params);end=time.monotonic()+30
            while time.monotonic()<end:
                event=q.get(timeout=max(.1,end-time.monotonic()))
                if event.get('id')==identifier:
                    if event.get('error'):raise RuntimeError('backend RPC failed: '+method)
                    return event['result']
                if method=='turn/start':backlog.append(event)
            raise TimeoutError(method)
        try:
            call('initialize',{'clientInfo':{'name':'hourly-token-optimizer','version':'1'},'capabilities':{'experimentalApi':True}})
            proc.stdin.write('{"method":"initialized","params":{}}\n');proc.stdin.flush()
            admission=quota_admission(call('account/rateLimits/read',{}));atomic(run/'admission.json',admission)
            if not admission['admitted'] or probe_only:
                return {'status':'quota-blocked' if not admission['admitted'] else 'probe-only','model_requests':0,'admission':admission}
            registry=json.loads((root/'config/role_registry.json').read_bytes())
            relevant={'code-reading','code-organization','model-with-knowledge','research-implement-optimize'}
            config={'features.apps':True,'mcp_servers.node_repl.enabled':False,'model_reasoning_effort':'high',
                    'skills.config':[{'path':str(Path.home()/'.agents/skills'/r['id']/'SKILL.md'),'enabled':r['id'] in relevant} for r in registry['roles']]}
            t=call('thread/start',{'cwd':str(root),'model':'gpt-6.1-sol','approvalPolicy':'never','sandbox':'danger-full-access','config':config})
            tid=t['thread']['id'];atomic(run/'thread.json',{'thread_id':tid,'model':t['model'],'effort':t['reasoningEffort'],'project_root':str(root)})
            turn=call('turn/start',{'threadId':tid,'input':[{'type':'text','text':PROMPT,'text_elements':[]}],'effort':'high'})['turn']['id']
            return observe_parent_turn(q,backlog,tid,turn,run,send,
                                       timeout_seconds=timeout_seconds,max_observed_tokens=max_observed_tokens)
        finally:
            # Only this owned backend PID/tree. Never kill unrelated Codex sessions.
            if proc.poll() is None:subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True,timeout=15)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=10)

def tick(root,state_dir,exe,*,now=None,probe_only=False):
    if not Path(root).is_absolute():raise ValueError('explicit absolute PROJECT_ROOT required')
    root=Path(root).resolve(strict=True);state_dir=Path(state_dir).resolve();exe=Path(exe).resolve(strict=True)
    if not state_dir.is_relative_to(root/'.agent-runs'):raise ValueError('private state must stay under PROJECT_ROOT/.agent-runs')
    now=time.time() if now is None else now
    if type(now) not in (int,float) or not math.isfinite(now) or now<0:raise ValueError('invalid clock')
    with exclusive(state_dir/'worker.lock') as locked:
        if not locked:return {'status':'another-worker-active','model_requests':0}
        if probe_only:
            # Probe admission without consuming, creating or advancing a due slot.
            run=state_dir/(str(time.time_ns())+'-probe');run.mkdir()
            try:
                synchronize(root)
                result=run_worker(root,exe,run,probe_only=True)
            except Exception as exc:
                result={'status':'host-blocked','error_type':type(exc).__name__,'model_requests':0}
            atomic(run/'receipt.json',result);return result
        path=state_dir/'state.json'
        state=json.loads(path.read_bytes()) if path.exists() else {'project_root':str(root),'next_due':now+INTERVAL,'interval_seconds':INTERVAL}
        if state.get('project_root')!=str(root) or state.get('interval_seconds')!=INTERVAL:raise ValueError('foreign schedule state')
        due=state['next_due'];advance_due(due,now) # validate before comparisons
        if now<due:
            atomic(path,state);return {'status':'not-due','next_due':due,'model_requests':0}
        state['next_due']=advance_due(due,now);state['last_started']=now;atomic(path,state)
        run=state_dir/(str(time.time_ns())+'-tick');run.mkdir();result={}
        try:
            head=synchronize(root)
            result={'base_revision':head,**run_worker(root,exe,run,probe_only=probe_only)}
            # Read-only postcondition; never count worker exit as a published improvement.
            result['dirty_tree']=bool(command(root,'git','status','--porcelain'))
            result['local_head']=command(root,'git','rev-parse','HEAD')
            command(root,'git','fetch','origin','main')
            result['remote_head']=command(root,'git','rev-parse','origin/main')
            result['publication_verified_by_host']=not result['dirty_tree'] and result['local_head']==result['remote_head']
            if result['publication_verified_by_host']:
                command(root,sys.executable,'scripts/setup_codex.py');command(root,sys.executable,'scripts/setup_codex.py','--check')
        except Exception as exc:result={'status':'host-blocked','error_type':type(exc).__name__,'reason':str(exc),'counts_as_token_success':False}
        atomic(run/'receipt.json',result);state['last_result']=result;state['last_finished']=time.time();atomic(path,state)
        return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--state-dir',required=True)
    p.add_argument('--codex',required=True);p.add_argument('--probe-only',action='store_true')
    a=p.parse_args();print(json.dumps(tick(a.root,a.state_dir,a.codex,probe_only=a.probe_only),ensure_ascii=False))
if __name__=='__main__':main()
