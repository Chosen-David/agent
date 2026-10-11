"""Fixed different-owner host validation; reads native originals, no inference."""
import sys,subprocess,os
from copy import deepcopy
from common import *
sys.path.insert(0,str(R))
from agent_runtime.token_usage import short_appserver_usage
from agent_runtime.maintenance_gate import MaintenanceGate,MaintenanceOutcome
from agent_runtime.result_validation import validate_result_plan

def verify(root,manifest,plan):
    assert Path(root)==R
    frozen=read(B/'freeze.json')
    for path,expected in frozen['hashes'].items():assert sha(R/path)==expected,path
    inv=read(B/'source-inventory.json')
    for row in inv['files']:assert sha(R/row['path'])==sha(R/row['archive_path'])==row['sha256']
    assert manifest['artifacts']['code']==[{'path':x['archive_path'],'sha256':x['sha256']} for x in inv['files']]
    assert sha(EXE)==read(B/'config.json')['binary_sha256']
    assert sha(Path.home()/'.codex/config.toml')==read(B/'config.json')['user_config_sha256']
    assert read(B/'dispatch.json')['freeze_sha256']==sha(B/'freeze.json')
    assert read(B/'dispatch.json')['max_paid_calls']==plan['controls']['max_invocations']==3
    assert plan['controls']['retries']==0
    assert read(B/'report.json')==REPORT and read(B/'oracle.json')==ORACLE
    text=(B/'prompt.txt').read_text(encoding='utf-8');assert text==prompt(REPORT) and len(text)<=1500
    assert read(B/'external-events.json')=={'advice_inventory_sha256':'fixed-fixture-v1','due':False,'evidence_version':'pending-v1'}
    settings=read(B/'settings.json');assert settings['config']==read(R/'agent_doc/results/token-007-skills-20261010/profiles.json')['candidate']['config_overrides']
    names=('baseline1','baseline2','candidate1');threads=read(B/'threads.json');catalogs=read(B/'tool-catalogs.json')
    assert tuple(threads)==names and set(catalogs)==set(names)
    controls=[{k:v for k,v in threads[n].items() if k!='thread'} for n in names]
    assert controls[0]==controls[1]==controls[2]
    ids=[threads[n]['thread']['id'] for n in names];assert len(set(ids))==3
    rows=[];instruction_text=[]
    for name in names:
        t=threads[name];tid=t['thread']['id']
        assert t['model']=='gpt-6.1-sol' and t['reasoningEffort']=='high' and t['cwd']==str(R)
        assert t['approvalPolicy']=='never' and t['sandbox']=={'type':'readOnly','networkAccess':False}
        assert catalogs[name]==catalogs[names[0]] and not any(s['tools'] for s in catalogs[name])
        raw=(P/(name+'.original.rpc.jsonl')).read_bytes();red=read(B/(name+'.redaction.json'))
        assert hashlib.sha256(raw).hexdigest()==red['original_sha256']
        original=[json.loads(s) for s in raw.decode().splitlines()];public=[];removed=[]
        for line in raw.decode().splitlines():
            e=json.loads(line)
            if e.get('method')=='account/rateLimits/updated':
                h=hashlib.sha256(line.encode()).hexdigest();removed.append(h);e={'method':'private/rateLimits-notification','params':{'raw_sha256':h}}
            public.append(json.dumps(e,ensure_ascii=False))
        assert (B/(name+'.rpc.jsonl')).read_bytes()==('\n'.join(public)+'\n').encode() and removed==red['removed_line_sha256']
        assert not any(e.get('method')=='model/rerouted' for e in original)
        starts=[e['params']['turn'] for e in original if e.get('method')=='turn/started' and e['params'].get('threadId')==tid];assert len(starts)==1
        usage=short_appserver_usage(original,tid,starts[0]['id']);rows.append({'name':name,**usage})
        assert usage['total_tokens']<=25000
        answers=[e['params']['item']['text'] for e in original if e.get('method')=='item/completed' and e['params'].get('threadId')==tid and e['params']['item']['type']=='agentMessage']
        assert len(answers)==1 and json.loads(answers[0])==ORACLE==read(B/(name+'.answer.json'))
        history=read(B/(name+'.history.json'));assert len(history)==1 and history[0]['status']=='completed'
        quota=read(B/(name+'.quota.json'));assert quota['ordinary_allowed'] and all(0<=w['usedPercent']<90 for w in quota['windows'])
        instruction_text.append(envelopes(P/(name+'.rollout.private.jsonl'),text))
    assert instruction_text[0]==instruction_text[1]==instruction_text[2] and len(instruction_text[0])>=4
    assert rows==read(B/'usage.json')['observations']
    b=rows[0]['total_tokens']+rows[1]['total_tokens'];c=rows[2]['total_tokens'];spent=b+c;assert b>c and spent<=75000
    assert read(B/'outcome.json')=={'status':'pending-independent-validation','baseline_total':b,'candidate_total':c,'saving_tokens':b-c,'total_spent':spent}
    assert {m['name']:m['value'] for m in manifest['metrics']}=={'baseline_total':b,'candidate_total':c,'saving':b-c,'paired_spend':spent}
    expected=[{'request':n,'decision':{'action':'wait_for_verification','publish':False},'outcome':'handled'} for n in names]+[{'request':None,'decision':{'action':'wait_for_verification','publish':False},'outcome':'unchanged'}]
    assert read(B/'trace.json')==expected
    # Separate replay supplies its own controlled observer/clock and records
    # exact invocations rather than trusting producer's trace/ACK flag.
    invoked=[];event={'version':1}
    def callback(report):invoked.append(deepcopy(report));return MaintenanceOutcome('handled')
    gate=MaintenanceGate(callback,lambda:{'project_root':str(R),'run_id':REPORT['run_id'],'events':event},project_root=R,run_id=REPORT['run_id'],max_quiet_seconds=300,clock=lambda:0)
    report=deepcopy(REPORT);assert gate(report).status=='handled';report['updated_at']=2;assert gate(report).status=='unchanged';assert len(invoked)==1
    event['version']=2;assert gate(report).status=='handled';assert len(invoked)==2
    cpu=subprocess.run([sys.executable,'-X','utf8','-m','unittest','tests.test_maintenance_gate','-q'],cwd=R,capture_output=True,text=True,encoding='utf-8',timeout=60)
    (B/'independent-tests.log').write_bytes((cpu.stdout+cpu.stderr).encode());assert cpu.returncode==0 and 'Ran 10 tests' in cpu.stderr
    validate_result_plan(read(B/'task-chain.json'))
    dump(B/'independent-control.json',{'actor':'host-maintenance10-reviewer','pid':os.getpid(),'native_controls_exact':True,'instruction_texts_exact':True,'tools_exact':True,'independent_callback_replay':[1,1,2],'tests_passed':10,'baseline_total':b,'candidate_total':c,'saving_tokens':b-c,'paid_spend':spent,'scope':manifest['scope']})
    bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
    for group in manifest['artifacts'].values():
        for item in group:assert ref(R/item['path'])==item;bindings[item['path']]=item['sha256']
    review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(B/'manifest.json'),'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':manifest['scope'],
        'verifier':{'actor':'host-maintenance10-reviewer','source':'fixed pre-dispatch-bound independent host process; no inference','run_id':'TOK-010-verify','method':'native originals/provider usage/full observable controls, independent gate replay and10 CPU tests','independent':True},
        'limitations':['One fixed two-observation unchanged fixture, not long-context/full project supervision or cash savings.','Only explicit trusted adapter wrapping benefits; observer completeness and handled outcome quality are host obligations.','Pending/errors/restarts and quiet-expiry reawaken; no scheduler/verifier/lease/timeout removed.','Research/root chat/development/static review excluded from measured three-request spend; service internal prompt assembly unobservable.'],
        'checks':{key:{'verdict':'pass','reason':criterion['acceptance'],'evidence':[ref(B/'independent-control.json'),ref(B/'independent-tests.log')]} for key,criterion in plan['criteria'].items()}}
    dump(B/'independent-review.json',review)
    return review
