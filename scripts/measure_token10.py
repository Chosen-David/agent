"""Ten bounded transport measurements; actual stdout bytes, no model accounting."""
from copy import deepcopy
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'.agent-runs/memory-index96-deps')]
os.environ.setdefault('TIKTOKEN_CACHE_DIR',str(ROOT/'.agent-runs/memory-index96-token-cache'))
TARGETS={1:'automatic complete basis selection',2:'communication',3:'project_memory',4:'project_docs',
         5:'result_store',6:'validate_experiment_result',7:'core capabilities',8:'discover_backends',
         9:'role dry-run',10:'validation_context recovery'}
SOURCES={1:['agent_runtime/handoff_encoding.py','agent_runtime/handoff_basis.py'],
    2:['agent_runtime/communication.py'],3:['agent_runtime/project_memory.py'],4:['agent_runtime/project_docs.py'],
    5:['scripts/result_store.py'],6:['scripts/validate_experiment_result.py'],7:['agent_runtime/__main__.py'],
    8:['scripts/discover_backends.py'],9:['scripts/run_role.py'],10:['scripts/validation_context.py']}


def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def write(path,value):path.write_bytes((dump(value)+'\n').encode())
def ref(path):return {'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path.read_bytes())}
def inventory(root):return {p.relative_to(root).as_posix():sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file()}


def prepare(n,out):
    out.mkdir(exist_ok=False)
    (out/'.gitattributes').write_bytes(b'* -text whitespace=-trailing-space\n')
    scope=f'TOK10 round {n:02d}: {TARGETS[n]}; exact lossless local '+('payload' if n==1 else 'UTF-8 binary stdout including native newline')+' tokens/bytes; no total session/model cost, QA, cash, latency or blanket correctness claim'
    criteria={}
    procedures={
        'implementation':'Read actual changed entry and dependencies, preserve default bytes, source/trust/exit/budget boundaries; compare live hashes.',
        'reference_boundary':'Independent type-sensitive JSON oracle, representative plus empty/small and entry-specific rejection case; auto enumerate every feasible format and deterministic token/char/order tie.',
        'data_integrity':'Check complete configured case inventory and raw stdout/stderr/exit, exact fixture archive and before/after source hashes; no omitted failures.',
        'numerical_sanity':'Independently recount every recorded UTF-8 text token and byte length, finite integer counts, exact value equality and exit codes.',
        'measurement_validity':'Pinned tiktoken0.12.0/o200k_base; payload only for01 or entire real subprocess stdout for02–10, including CRLF; no wrapper omission or model inference.',
        'reproducibility':'Read frozen executed code/fixture, independently replay representative commands and rejection or enumerate01; compare with raw outputs and fresh counts.'}
    for key,procedure in procedures.items():
        criteria[key]={'procedure':procedure,'acceptance':'Applicable checks pass within declared scope; at least one representative strict reduction, negative controls retained; all full values/status/exit paths preserved.','allow_not_applicable':False}
    write(out/'validation_plan.json',{'schema_version':'experiment-validation-plan/v1','scope':scope,'criteria':criteria})
    write(out/'config.json',{'round':n,'target':TARGETS[n],'version':1,'tokenizer':'o200k_base','tiktoken':'0.12.0',
        'cases':['large','small','rejected'],'tie_break':['tokens','chars','format_order'],'repeats':1,'seed':'deterministic-public-v1'})


def memory(root,count):
    from agent_runtime.project_memory import MemoryLedger
    ledger=MemoryLedger(root,create=True)
    for i in range(count):ledger.add(f'm{i}','observation',f'完整原文 🧠 {i}: preserve blocker and unit.','synthetic:token10',evidence='verified',deps=[f'm{i-1}'] if i else [])
    with ledger._connect(write=True) as db:db.execute("UPDATE entries SET created_at='2026-10-21T00:00:00.000Z'")
    return ledger


def mailbox(root,count):
    from agent_runtime.communication import Mailbox
    memory(root,count)
    plan={'schema_version':1,'run_id':'synthetic-token10','input_version':'v1','routes':[
        {'sender':'code','recipient':r,'task_id':'T1','kind':'artifact'} for r in ('reader','auto')]}
    box=Mailbox(root/'mail.sqlite',plan,root)
    artifact=root/'raw.json';write(artifact,{'value':1,'limitation':'fixture only'})
    record={'schema_version':1,'run_id':plan['run_id'],'role':'code','input_version':'v1',
        'status':'completed','limitations':['synthetic only'],'artifacts':[{'id':'raw','path':'raw.json','sha256':sha(artifact.read_bytes())}],
        'checks':[{'criterion':'fixture','status':'pass','artifact_ids':['raw']}],
        'tasks':[{'task_id':'T1','status':'done','evidence':['raw']}],
        'knowledge_refs':[],'memory_refs':[f'm{count-1}'] if count else [],'evidence_claims':[]}
    handoff=root/'handoff.json';write(handoff,record)
    box.publish({'event_id':'E1','run_id':plan['run_id'],'input_version':'v1','sender':'code',
        'task_id':'T1','kind':'artifact','summary':'保留完整事实','action':'Review, not acceptance',
        'refs':[{'id':'handoff','path':'handoff.json','sha256':sha(handoff.read_bytes())}]})
    write(root/'plan.json',plan)
    request={'schema_version':1,'input_version':'v1','tasks':[{'task_id':'T1'}],
             'knowledge_refs':[],'memory_refs':record['memory_refs'],'memory_required':bool(count),'knowledge_required':False}
    return box,record,request


def fixture(n,home):
    home.mkdir(parents=True,exist_ok=False)
    def module(name,*args):return [sys.executable,'-X','utf8','-m',name,*map(str,args)]
    def script(name,*args):return [sys.executable,'-X','utf8',str(ROOT/'scripts'/name),*map(str,args)]
    commands=[]
    if n==2:
        mailbox(home,8)
        prefix=module('agent_runtime.communication','--root',home,'--db',home/'mail.sqlite','--plan',home/'plan.json')
        commands=[prefix+['inbox','reader'],prefix+['usage'],prefix+['inbox','unknown']]
    elif n==3:
        memory(home,16)
        prefix=module('agent_runtime.project_memory','--root',home)
        commands=[prefix+['list'],prefix+['storage'],prefix+['show','missing']]
    elif n==4:
        from agent_runtime.project_docs import initialize_project_docs
        initialize_project_docs(home)
        task=home/'agent_doc/task/TASK.md';task.write_text('# Tasks\n\n## 2026-10-21\n\n'+''.join(f'- [ ] [T{i}] Preserve blocker ([detail](task_details/T{i}.md))\n' for i in range(12)),encoding='utf-8')
        details=home/'agent_doc/task/task_details';details.mkdir(exist_ok=True)
        for i in range(12):(details/f'T{i}.md').write_text(f'# T{i}\n\n## Plan\nKeep all evidence.\n\n## Progress\n- blocker 🧠 {i}\n',encoding='utf-8')
        prefix=module('agent_runtime.project_docs','--root',home)
        commands=[prefix+['inspect'],prefix+['nav'],prefix+['guard-write','../escape']]
    elif n==5:
        from agent_runtime.result_store import ResultStore
        write(home/'synthetic.json',{'preserve':True})
        store=ResultStore(home)
        for i in range(8):store.register_history(f'fixture-{i}','synthetic blocker memory context',[{'path':'synthetic.json','sha256':sha((home/'synthetic.json').read_bytes())}])
        prefix=script('result_store.py','--root',home)
        commands=[prefix+['search','blocker','--max-scan','500'],prefix+['search','no-such-term'],prefix+['show','missing']]
    elif n==6:
        # Structurally valid pending fixture: no trusted verifier is supplied.
        base=home/'agent_doc/results/fixture';base.mkdir(parents=True)
        data=base/'data.txt';data.write_bytes(b'synthetic input, not a scientific result\n')
        dataref={'path':data.relative_to(home).as_posix(),'sha256':sha(data.read_bytes())}
        plan={'schema_version':'experiment-validation-plan/v1','scope':'synthetic pending fixture',
            'criteria':{k:{'procedure':'fixture','acceptance':'fixture','allow_not_applicable':False} for k in ('implementation','reference_boundary','data_integrity','numerical_sanity','measurement_validity','reproducibility')}}
        write(base/'plan.json',plan)
        contract={'result_id':'fixture','producer_task_id':'producer','producer_actor':'synthetic',
            'manifest_path':'agent_doc/results/fixture/manifest.json','validation_plan':{'path':'agent_doc/results/fixture/plan.json','sha256':sha((base/'plan.json').read_bytes())},'scope':plan['scope']}
        manifest={'schema_version':'experiment-result/v1',**contract,'run_id':'fixture','code_revision':'synthetic',
            'execution':{'command':['synthetic fixture only'],'environment_description':'synthetic','seeds':['fixed'],'repeats':1},
            'artifacts':{k:[dataref] for k in ('code','inputs','config','raw_data','outputs','environment')},
            'metrics':[{'name':'fixture','value':1,'unit':'dimensionless'}]}
        write(base/'manifest.json',manifest);write(home/'contract.json',contract);write(home/'small.json',{})
        prefix=script('validate_experiment_result.py','--root',home)
        commands=[prefix+['--contract',str(home/'contract.json')],prefix+['--contract',str(home/'small.json')],prefix+['--contract',str(home/'missing.json')]]
    elif n==7:
        from agent_runtime.core import Store
        Store(home/'state.sqlite')
        prefix=module('agent_runtime','--db',home/'state.sqlite')
        commands=[prefix+['capabilities'],prefix+['capabilities'],prefix+['init',home/'missing.json']]
    elif n==8:
        prefix=script('discover_backends.py')
        commands=[prefix, prefix+['--only','definitely-missing'],prefix+['--only','definitely-missing']]
    elif n==9:
        spec=importlib.util.spec_from_file_location('token10_setup',ROOT/'setup.py');setup=importlib.util.module_from_spec(spec);spec.loader.exec_module(setup);setup.install(home)
        prefix=script('run_role.py','--project',home,'--dry-run')
        commands=[prefix+['--role','research-implement-optimize'],prefix+['--role','research-write'],prefix+['--role','missing']]
    else:
        from agent_runtime.validation_context import write_validation_context
        result={'status':'pending','scope':'synthetic complete recovery','errors':['no trusted verifier'],
            'next_action':'independent review required','proof':{'limitations':['not acceptance'],
                'artifact_hashes':{f'file{i}.txt':'a'*64 for i in range(32)}}}
        large=write_validation_context(home,result,'agent_doc/results/large')['record_ref']
        result['proof']=None;small=write_validation_context(home,result,'agent_doc/results/small')['record_ref']
        prefix=script('validation_context.py','--root',home)
        commands=[prefix+['--path',large['path'],'--sha256',large['sha256']],prefix+['--path',small['path'],'--sha256',small['sha256']],prefix+['--path',large['path'],'--sha256','0'*64]]
    return commands


def measure(n,out):
    import tiktoken
    if tiktoken.__version__!='0.12.0':raise ValueError('pinned tiktoken required')
    encoding=tiktoken.get_encoding('o200k_base')
    count=lambda s:len(encoding.encode(s,disallowed_special=()))
    base=ROOT/'.agent-runs/token10-20261021';home=base/f'fixture-{n:02d}'
    raw=[];codes=set(SOURCES[n])|{'scripts/measure_token10.py','agent_runtime/context_serialization.py','agent_runtime/external_json.py'}
    if n==1:
        from agent_runtime.handoff_encoding import choose_basis_payload,encode_claims_table,encode_basis_tables,decode_basis_payload
        from agent_runtime.handoff_basis import make_token_counter
        from test_token10 import payload
        home.mkdir(parents=True,exist_ok=False)
        for name,size in [('large',32),('small',0)]:
            value=payload(size)
            options=[dump(f(value)) for f in (deepcopy,encode_claims_table,encode_basis_tables)]
            chosen,tokens=choose_basis_payload(value,count)
            if dump(decode_basis_payload(chosen))!=dump(value):raise ValueError('lossy auto')
            raw.append({'case':name,'before':options[-1],'after':chosen,'before_tokens':count(options[-1]),'after_tokens':tokens,
                        'before_bytes':len(options[-1].encode()),'after_bytes':len(chosen.encode()),'candidates':options})
        box,record,request=mailbox(home,4)
        auto={**request,'context_format':'auto-lossless/v1'}
        counter=make_token_counter('o200k_base')
        plain=box.prepare_context('reader',1,request,token_counter=counter,max_chars=200000)
        selected=box.prepare_context('auto',1,auto,token_counter=counter,max_chars=200000)
        if dump(decode_basis_payload(selected['payload']))!=dump(json.loads(plain['payload'])):raise ValueError('Mailbox loss')
        rejected=[]
        for kwargs in ({'max_chars':1},{'max_tokens':1}):
            try:box.prepare_context('auto',1,auto,token_counter=counter,**kwargs)
            except ValueError:rejected.append(kwargs)
            else:raise ValueError('budget bypass')
        raw.append({'case':'rejected','budget_rejections':rejected,'mailbox_plain':plain,'mailbox_auto':selected})
        inputs={'fixture':'deterministic test_token10.payload; memory-only Mailbox; no corpus read'}
        codes.add('tests/test_token10.py')
    else:
        commands=fixture(n,home)
        trace=base/f'trace-{n:02d}';trace.mkdir(parents=True,exist_ok=True)
        hook='import atexit,json,os,sys\nfrom pathlib import Path\ndef done():\n root=Path(os.environ["TOKEN10_ROOT"]).resolve()\n paths=set()\n for m in list(sys.modules.values()):\n  p=getattr(m,"__file__",None)\n  if p:\n   p=Path(p).resolve()\n   if p.is_relative_to(root) and ".agent-runs" not in p.parts and p.suffix==".py":paths.add(p.relative_to(root).as_posix())\n Path(os.environ["TOKEN10_TRACE"]).write_text(json.dumps(sorted(paths)),encoding="utf-8")\natexit.register(done)\n'
        (trace/'sitecustomize.py').write_bytes(hook.encode())
        inputs={'commands':commands,'fixture_root':str(home),'cases':['large','small','rejected']}
        initial=inventory(home)
        env={**os.environ,'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1',
             'PYTHONPATH':str(trace)+os.pathsep+str(ROOT),'TOKEN10_ROOT':str(ROOT)}
        for i,command in enumerate(commands):
            pair=[]
            for compact in (False,True):
                log=trace/f'{i}-{compact}.json';env['TOKEN10_TRACE']=str(log)
                # Global argparse flags precede subcommands; prepend after executable/-m target.
                insert=5 if command[3]=='-m' else 4
                actual=command[:insert]+(['--compact'] if compact else [])+command[insert:]
                p=subprocess.run(actual,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
                text=p.stdout.decode('utf-8');stderr=p.stderr.decode('utf-8')
                pair.append({'command':actual,'stdout':text,'stderr':stderr,'exit':p.returncode,'tokens':count(text),'bytes':len(p.stdout)})
                if log.exists():codes.update(json.loads(log.read_text(encoding='utf-8')))
            if pair[0]['exit']!=pair[1]['exit']:raise ValueError('exit differs: '+dump(pair))
            if pair[0]['stdout']:
                try:a=json.loads(pair[0]['stdout']);b=json.loads(pair[1]['stdout'])
                except ValueError:
                    if pair[0]['stdout']!=pair[1]['stdout']:raise ValueError('non-JSON output changed')
                else:
                    if dump(a)!=dump(b):raise ValueError('JSON values/types differ')
            elif pair[1]['stdout']:raise ValueError('unexpected compact stdout')
            if pair[0]['stderr']!=pair[1]['stderr']:raise ValueError('stderr changed')
            raw.append({'case':inputs['cases'][i],'before':pair[0],'after':pair[1]})
        final=inventory(home)
        if initial!=final:raise ValueError('CLI changed readonly fixture')
        inputs['before_sha256']=initial;inputs['after_sha256']=final
    # Freeze full actual fixture bytes, not a mutable ignored path reference.
    with zipfile.ZipFile(out/'fixture.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(home.rglob('*')):
            if p.is_file():archive.write(p,p.relative_to(home).as_posix())
    for m in list(sys.modules.values()):
        p=getattr(m,'__file__',None)
        if p:
            p=Path(p).resolve()
            if p.is_relative_to(ROOT) and '.agent-runs' not in p.parts and p.suffix=='.py':codes.add(p.relative_to(ROOT).as_posix())
    ranks=hashlib.sha256()
    for token,rank in sorted(encoding._mergeable_ranks.items(),key=lambda p:p[1]):
        ranks.update(len(token).to_bytes(4,'big'));ranks.update(token);ranks.update(rank.to_bytes(4,'big'))
    write(out/'inputs.json',inputs);write(out/'raw.json',raw)
    write(out/'environment.json',{'python':sys.version,'platform':platform.platform(),'sqlite':sqlite3.sqlite_version,
        'tiktoken':tiktoken.__version__,'encoding':encoding.name,'ranks_sha256':ranks.hexdigest(),
        'pattern':encoding._pat_str,'special_tokens':encoding._special_tokens,'newline':repr(os.linesep),
        'tokenizer_binary':{p.name:sha(p.read_bytes()) for p in Path(tiktoken.__file__).parent.glob('*.pyd')}})
    plan=json.loads((out/'validation_plan.json').read_bytes())
    contract={'result_id':out.name,'producer_task_id':f'produce-{n:02d}','producer_actor':'/root',
        'manifest_path':str(out.relative_to(ROOT)/'manifest.json').replace('\\','/'),
        'validation_plan':ref(out/'validation_plan.json'),'scope':plan['scope']}
    metrics=[]
    for row in raw:
        for kind in ('before','after'):
            value=row.get(kind)
            if n==1 and isinstance(value,str):tokens=row[kind+'_tokens'];size=row[kind+'_bytes']
            elif isinstance(value,dict):tokens=value['tokens'];size=value['bytes']
            else:continue
            metrics.extend([{'name':row['case']+':'+kind+':tokens','value':tokens,'unit':'o200k_base text tokens'},
                            {'name':row['case']+':'+kind+':bytes','value':size,'unit':'UTF-8 bytes'}])
    write(out/'manifest.json',{'schema_version':'experiment-result/v1',**contract,'run_id':out.name,
        'code_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()+'+bound-dirty',
        'execution':{'command':[f'python -X utf8 scripts/measure_token10.py --round {n} --measure'],
            'environment_description':'Windows binary UTF-8 subprocesses (round01 direct payload plus real Mailbox), pinned tokenizer; no model calls',
            'seeds':['deterministic-public-v1'],'repeats':1},
        'artifacts':{'code':[ref(ROOT/p) for p in sorted(codes)],'inputs':[ref(out/'inputs.json'),ref(out/'fixture.zip')],
            'config':[ref(out/'config.json')],'raw_data':[ref(out/'raw.json'),ref(out/'tests.txt')],
            'outputs':[ref(out/'inputs.json')],'environment':[ref(out/'environment.json')]},'metrics':metrics})
    write(out/'contract.json',contract)
    print(dump({'round':n,'status':'pending-independent-validation','code_files':len(codes)}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--round',type=int,choices=range(1,11),required=True)
    parser.add_argument('--prepare',action='store_true');parser.add_argument('--measure',action='store_true');args=parser.parse_args()
    out=ROOT/f'agent_doc/results/token10-20261021-{args.round:02d}'
    if args.prepare:prepare(args.round,out)
    if args.measure:measure(args.round,out)
