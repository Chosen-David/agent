"""Known fixed CPU producer/reviewer entry; no model backend or inference."""
import hashlib,json,sys,subprocess,platform,os
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R))
REL='agent_doc/results/token-010-maintenance-cpu-r3-20261011';B=R/REL
def read(name):return json.loads((B/name).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(name,value):(B/name).write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())
def ref(name):return {'path':REL+'/'+name,'sha256':sha(B/name)}

def checks(mode):
    p=subprocess.run([sys.executable,'-m','unittest','tests.test_maintenance_gate','-v'],cwd=R,capture_output=True,text=True,encoding='utf-8',timeout=60)
    (B/(mode+'-tests.log')).write_bytes((p.stdout+p.stderr).encode())
    assert p.returncode==0 and 'Ran 10 tests' in p.stderr
    from agent_runtime.maintenance_gate import MaintenanceGate,MaintenanceOutcome
    calls=[];event={'code':'v1','due':False};clock=[0]
    def handle(report):calls.append(report);return MaintenanceOutcome('handled')
    gate=MaintenanceGate(handle,lambda:{'project_root':str(R),'run_id':'independent-cpu','events':event},project_root=R,run_id='independent-cpu',max_quiet_seconds=5,clock=lambda:clock[0])
    report={'run_id':'independent-cpu','updated_at':1,'source_error':None}
    actual=[gate(report).status];report['updated_at']=2;actual.append(gate(report).status)
    event['due']=True;actual.append(gate(report).status)
    report['source_error']='missing evidence';actual.append(gate(report).status)
    clock[0]=5;actual.append(gate(report).status)
    assert actual==['handled','unchanged','handled','handled','handled'] and len(calls)==4
    value={'actor':'native-maintenance-cpu-producer' if mode=='producer' else 'host-maintenance-cpu-reviewer','pid':os.getpid(),
           'platform':platform.platform(),'python':platform.python_version(),'tests_passed':10,'gate_calls':len(calls),'trace':actual,'model_calls':0}
    dump(mode+'-checks.json',value)
    return value

def verify(root,manifest,plan):
    assert Path(root)==R and read('producer-checks.json')['actor']=='native-maintenance-cpu-producer'
    for row in read('source-inventory.json')['files']:
        assert sha(R/row['path'])==sha(R/row['archive_path'])==row['sha256']
    actor=checks('independent');assert actor['pid']!=read('producer-checks.json')['pid']
    assert actor['trace']==read('producer-checks.json')['trace']
    from agent_runtime.result_validation import validate_result_plan
    validate_result_plan(read('task-chain.json'))
    bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
    for group in manifest['artifacts'].values():
        for item in group:assert sha(R/item['path'])==item['sha256'];bindings[item['path']]=item['sha256']
    assert {x['name']:x['value'] for x in manifest['metrics']}=={'tests_passed':10,'model_calls':0}
    review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(B/'manifest.json'),'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':manifest['scope'],
        'verifier':{'actor':'host-maintenance-cpu-reviewer','source':'fixed host CPU entry, separately executed in WSL','run_id':'TOK-010-CPU-verify','method':'source/archive hashes, independent event/deadline trace,10 actual CPU tests','independent':True},
        'limitations':['CPU boundaries only, no model usage/quality/token savings or live adapter deployment.','Trusted observer event completeness and real handled acknowledgements remain host obligations.','Independent Windows/Linux CPU checks do not establish long-running tmux survival or whole-project behavior.'],
        'checks':{key:{'verdict':'pass','reason':criterion['acceptance'],'evidence':[ref('independent-checks.json'),ref('independent-tests.log')]} for key,criterion in plan['criteria'].items()}}
    dump('independent-review.json',review);return review

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='producer':
        assert not (B/'producer-checks.json').exists();print(json.dumps(checks(mode)))
    elif mode=='verify':
        assert not (B/'acceptance.json').exists()
        manifest=read('manifest.json');plan=read('validation-plan.json');review=verify(R,manifest,plan)
        from agent_runtime.result_store import ResultStore
        def fixed(root,m,p):
            assert Path(root)==R and m==manifest and p==plan
            for path,expected in review['artifact_hashes'].items():assert sha(R/path)==expected
            return review
        accepted=ResultStore(R).register(read('contract.json'),verifier=fixed)['record']['validation_at_registration']
        dump('acceptance.json',accepted);assert accepted['status']=='usable-with-scope',accepted['errors']
        print(json.dumps({'status':accepted['status'],'scope':accepted['scope'],'tests':10,'model_calls':0}))
    else:raise ValueError('known producer/verify modes only')
