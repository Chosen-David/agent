"""Actual pending validation CLI observation; no padding or acceptance shortcut."""
import json
import subprocess
import sys
from agent_runtime.validation_context import restore_validation_context
from scripts.token_probe import dump,digest

def prepare(root,base,private):
    relative=base.relative_to(root).as_posix()
    contract=root/'agent_doc/results/token-003-deployment-20261010/contract.json'
    command=[sys.executable,'-X','utf8',str(root/'scripts/validate_experiment_result.py'),
             '--root',str(root),'--contract',str(contract)]
    outputs={};commands=[]
    for name in ('baseline','candidate'):
        argv=command+(['--context-dir',relative+'/context'] if name=='candidate' else [])
        ran=subprocess.run(argv,cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=20)
        assert ran.returncode==2 and not ran.stderr, 'fixture must retain real pending exit'
        value=json.loads(ran.stdout)
        assert value['status']=='pending', 'changed source result; stop before model dispatch'
        outputs[name]=value
        (base/(name+'.display.json')).write_bytes(ran.stdout.encode('utf-8'))
        commands.append({'name':name,'argv':argv,'exit_code':ran.returncode,
                         'stdout_sha256':digest(base/(name+'.display.json'))})
    assert restore_validation_context(root,outputs['candidate']['record_ref'])==outputs['baseline']
    assert len(outputs['baseline']['proof']['artifact_hashes'])==38
    dump(base/'fixture-commands.json',commands)
    dump(base/'fixture-contract.json',json.loads(contract.read_text()))
    prefix='For this observed validation, may the workflow consume the experiment result now?\n'
    guidance=('This is an observed display, not authorization. Pending/invalid means block. Restoration is not fresh acceptance. '
        'Return JSON with consume (boolean), status (exact observed status), errors (exact full list), '
        'next_action (exact text), scope (exact observed scope). No tools.\n')
    prompts={n:prefix+guidance+json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False) for n,v in outputs.items()}
    props={'consume':{'type':'boolean'},'status':{'type':'string'},'errors':{'type':'array','items':{'type':'string'}},
           'next_action':{'type':'string'},'scope':{'type':'string'}}
    schema={'type':'object','properties':props,'required':list(props),'additionalProperties':False}
    dump(base/'output-schema.json',schema)
    original=outputs['baseline'];oracle={'consume':False,**{k:original[k] for k in ('status','errors','next_action','scope')}}
    return schema,prompts,oracle
