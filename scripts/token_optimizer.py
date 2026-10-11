"""Single hourly host admission + bounded actual Codex worker, not a heartbeat-only task.

Run once from a tmux interval host. State/raw transport remain private and local.
Never force-push, auto-stash, remove user data, or count a skipped tick as savings.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import hashlib,json,math,os,queue,subprocess,sys,threading,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.project_docs import guard_write_path

INTERVAL=3600
PROMPT='''PROJECT_ROOT=WORKFLOW_ROOT=current repository. Continue agent token optimization only, one concrete iteration. Read current human GUIDE, TASK/TOK-FIVE, progress.json and relevant prior results/advice, not historical full transcripts. Preserve concurrent work. Prefer high-frequency communication and long-context costs. No other project advice interaction, duplicate agents or schedules. Reuse current mechanisms. Limit one optional actual short no-tool A/B pair to 2200 supplied chars per prompt, at most 2 paid calls/50000 paired tokens, no retries; read fresh quota before paid tests. Provider totals and independent quality/source verification are required to count a success; CPU/estimates/negative results do not count. Preserve pending/failed data. Make a useful change, run necessary checks, fetch again and ordinary commit/push main (GitHub MCP non-force expected-SHA publication if native auth fails), independently read back remote and synchronize setup_codex.py then --check. Preserve conflicts and write a concise recovery record if blocked. Keep final report brief; no fabricated token/cash or weight-update claim.'''
PROMPT+=''' Host already pulled verified main and synchronized skills. Do not repeat host bootstrap or list all repository/results paths. Use UTF-8 explicitly (Get-Content -Encoding UTF8, python -X utf8). Read exact selected task rows with task_context, not full TASK; read only the relevant Plan/Progress section and progress counters, not the full upgrades ledger. Bound rg by known directories and return at most 20 matches. Request <=768 output tokens per command; batch independent small reads. Truncated output is incomplete evidence: recover exact required lines before edits/claims. Prioritize one small actionable change; consolidate commands and preserve an explicit checkpoint before spending the tick budget. An interrupted thread will resume next hour, so do not restart finished reads.'''
PROFILE_VERSION='bounded-resumable-v1'
TOOL_OUTPUT_TOKENS=768

def worker_config(root):
    registry=json.loads((root/'config/role_registry.json').read_bytes())
    relevant={'code-reading','code-organization','model-with-knowledge','research-implement-optimize'}
    return {'features.apps':True,'mcp_servers.node_repl.enabled':False,
            'tool_output_token_limit':TOOL_OUTPUT_TOKENS,'model_reasoning_effort':'high',
            'skills.config':[{'path':str(Path.home()/'.agents/skills'/r['id']/'SKILL.md'),
                             'enabled':r['id'] in relevant} for r in registry['roles']]}

def work_snapshot(root):
    """Exact host-owned continuation boundary; no overwriting concurrent bytes."""
    status=command(root,'git','status','--porcelain')
    paths=set()
    for args in (('diff','--name-only','-z'),('diff','--cached','--name-only','-z'),
                 ('ls-files','--others','--exclude-standard','-z')):
        paths.update(p for p in command(root,'git',*args).split('\0') if p)
    if len(paths)>100:raise RuntimeError('too many dirty paths for bounded recovery')
    files={}
    for name in sorted(paths):
        path=root/name
        guard_write_path(path)
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise RuntimeError('unsafe continuation path')
        if path.exists():
            if not path.is_file() or path.stat().st_size>2*1024*1024:
                raise RuntimeError('unbounded continuation file')
            files[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        else:files[name]=None
    index=command(root,'git','ls-files','--stage','-z')
    return {'head':command(root,'git','rev-parse','HEAD'),'status':status,'files':files,
            'index_sha256':hashlib.sha256(index.encode('utf-8')).hexdigest()}

def publication_state(base,local,remote,dirty):
    current=not dirty and local==remote
    return {'current_snapshot_verified':current,
            'new_remote_snapshot_verified':current and local!=base,
            'publication_attribution':'unknown; equality is not evidence of worker authorship'}

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
    return p.stdout if '-z' in args else p.stdout.strip()

def synchronize(root):
    if command(root,'git','branch','--show-current')!='main':raise RuntimeError('main required')
    if command(root,'git','status','--porcelain'):raise RuntimeError('dirty tree preserved; no auto-stash')
    command(root,'git','fetch','origin','main');command(root,'git','pull','--ff-only','origin','main')
    head=command(root,'git','rev-parse','HEAD')
    if head!=command(root,'git','rev-parse','origin/main'):raise RuntimeError('fetched main mismatch')
    command(root,sys.executable,'scripts/setup_codex.py');command(root,sys.executable,'scripts/setup_codex.py','--check')
    return head

def observe_parent_turn(q,backlog,tid,turn,run,send,*,timeout_seconds,max_observed_tokens,initial_total_tokens=0):
    """Observe native parent snapshots, never infer a final or cross-actor bill."""
    if type(initial_total_tokens) is not int or initial_total_tokens<0:raise ValueError('invalid resumed usage baseline')
    deadline=time.monotonic()+timeout_seconds;observed=None;absolute=None;previous=None;interrupted=False;saw_error=False
    fields=('inputTokens','cachedInputTokens','outputTokens','totalTokens','reasoningOutputTokens')
    def receipt(status,invalid=None):
        usage_status=('invalid' if invalid else 'missing' if observed is None else
                      'observed' if status=='worker-completed' and not saw_error else 'partial')
        return {'status':status,'model_requests':None,'thread_id':tid,'turn_id':turn,
                'observed_parent_total_tokens':None if invalid else observed,
                'last_observed_parent_total_tokens':observed,
                'thread_total_tokens':absolute,'initial_total_tokens':initial_total_tokens,
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
                if total['totalTokens']<initial_total_tokens:raise ValueError('resumed cumulative usage regressed')
                absolute=total['totalTokens'];observed=absolute-initial_total_tokens;previous=total.copy()
                atomic(run/'observed-usage.json',{'total_tokens':observed,'budget':max_observed_tokens,
                       'thread_id':tid,'turn_id':turn,'tokenUsage':usage,'initial_total_tokens':initial_total_tokens,'usage_complete':False,
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

def run_worker(root,exe,run,*,timeout_seconds=1200,max_observed_tokens=75000,probe_only=False,checkpoint=None,prompt=None):
    if os.name!='nt':raise ValueError('selected native backend requires Windows Python; WSL hosts the tmux timer')
    q=queue.Queue();counter=0;backlog=[]
    flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
    with (run/'stderr.private.log').open('x',encoding='utf-8') as err:
        proc=subprocess.Popen([str(exe),'app-server'],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                              stderr=err,text=True,encoding='utf-8',creationflags=flags,
                              env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8'))
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
            config=worker_config(root);atomic(run/'profile.json',{'version':PROFILE_VERSION,'config':config})
            params={'cwd':str(root),'model':'gpt-6.1-sol','approvalPolicy':'never','sandbox':'danger-full-access','config':config}
            if checkpoint:params['threadId']=checkpoint['thread_id']
            t=call('thread/resume' if checkpoint else 'thread/start',params)
            tid=t['thread']['id'];atomic(run/'thread.json',{'thread_id':tid,'model':t['model'],'effort':t['reasoningEffort'],'project_root':str(root)})
            text=prompt or PROMPT
            if checkpoint:text='Continue this persisted optimization, avoiding repeated bootstrap. Host checked exact owned local bytes and fetched current origin/main; resolve any remote advance before ordinary publication. '+text
            turn=call('turn/start',{'threadId':tid,'input':[{'type':'text','text':text,'text_elements':[]}],'effort':'high'})['turn']['id']
            return observe_parent_turn(q,backlog,tid,turn,run,send,
                                       timeout_seconds=timeout_seconds,max_observed_tokens=max_observed_tokens,
                                       initial_total_tokens=checkpoint['thread_total_tokens'] if checkpoint else 0)
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
        run=state_dir/(str(time.time_ns())+'-tick');run.mkdir();result={};worker_attempted=False
        try:
            if state.get('failure_latch'):
                result={'status':'failure-latched','model_requests':0,'reason':state['failure_latch'],'counts_as_token_success':False}
                atomic(run/'receipt.json',result);state['last_result']=result;state['last_finished']=time.time();atomic(path,state)
                return result
            checkpoint=state.get('checkpoint')
            if checkpoint:
                current=work_snapshot(root);saved=checkpoint['work_snapshot']
                clean_advance=not current['status'] and not saved['status']
                if checkpoint.get('profile_version')!=PROFILE_VERSION or (saved!=current and not clean_advance):
                    raise RuntimeError('continuation changed; preserve concurrent work and require recovery')
                command(root,'git','fetch','origin','main')
                if clean_advance:
                    command(root,'git','merge-base','--is-ancestor',saved['head'],'HEAD')
                    head=synchronize(root)
                else:head=checkpoint['work_snapshot']['head']
            else:head=synchronize(root)
            worker_attempted=True
            result={'base_revision':head,**run_worker(root,exe,run,probe_only=probe_only,checkpoint=checkpoint)}
            # Read-only postcondition; never count worker exit as a published improvement.
            result['dirty_tree']=bool(command(root,'git','status','--porcelain'))
            result['local_head']=command(root,'git','rev-parse','HEAD')
            command(root,'git','fetch','origin','main')
            result['remote_head']=command(root,'git','rev-parse','origin/main')
            result.update(publication_state(head,result['local_head'],result['remote_head'],result['dirty_tree']))
            if result['current_snapshot_verified']:
                command(root,sys.executable,'scripts/setup_codex.py');command(root,sys.executable,'scripts/setup_codex.py','--check')
            if result['status'] in ('budget-interrupted','worker-completed') and not result['new_remote_snapshot_verified'] and type(result.get('thread_total_tokens')) is int:
                snapshot=work_snapshot(root)
                stagnant=(checkpoint.get('stagnant_ticks',0)+1 if checkpoint and checkpoint['work_snapshot']==snapshot else 0)
                state['checkpoint']={'thread_id':result['thread_id'],'thread_total_tokens':result['thread_total_tokens'],
                                     'work_snapshot':snapshot,'profile_version':PROFILE_VERSION,'stagnant_ticks':stagnant}
                if stagnant>=2:state['failure_latch']='three consecutive ticks without a changed work snapshot; recovery required'
            elif result['status']=='worker-completed' and result['new_remote_snapshot_verified']:state.pop('checkpoint',None)
            elif result['status']!='quota-blocked':state['failure_latch']=result['status']
        except Exception as exc:result={'status':'host-blocked','error_type':type(exc).__name__,'reason':str(exc),
                                       'model_requests':None if worker_attempted else 0,'counts_as_token_success':False}
        if result['status']=='host-blocked' and (worker_attempted or state.get('checkpoint')):
            state['failure_latch']=result['reason']
        atomic(run/'receipt.json',result);state['last_result']=result;state['last_finished']=time.time();atomic(path,state)
        return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--state-dir',required=True)
    p.add_argument('--codex',required=True);p.add_argument('--probe-only',action='store_true')
    a=p.parse_args();print(json.dumps(tick(a.root,a.state_dir,a.codex,probe_only=a.probe_only),ensure_ascii=False))
if __name__=='__main__':main()
