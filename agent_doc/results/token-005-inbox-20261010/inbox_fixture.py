"""Four real CLI envelopes, synthetic task semantics; no padded documents."""
import hashlib,json,subprocess,sys
from pathlib import Path
from agent_runtime.communication import Mailbox
from scripts.token_probe import dump,digest

PREFIX="For the host-selected FIG-1 task, report its observed unresolved messages."
GUIDANCE=("The host explicitly selects FIG-1 local handling, not global clearance. "
 "Other task IDs are independently coordinated by the main host. Preserve all FIG-1 kinds. "
 "A blocker is unresolved until independently verified; correction alone does not clear it. "
 "Return JSON: blocked boolean, messages in seq order with seq, kind, action copied exactly. No tools.\n")

def replay(root,base,db):
    plan=json.loads((base/'fixture-plan.json').read_text(encoding='utf-8'))
    events=json.loads((base/'fixture-events.json').read_text(encoding='utf-8'))
    box=Mailbox(db,plan,root)
    for event in events:box.publish(event)
    command=[sys.executable,'-X','utf8','-m','agent_runtime.communication','--root',str(root),
        '--db',str(db),'--plan',str(base/'fixture-plan.json'),'inbox','writer']
    observations={};commands=[]
    for name,extra in (('baseline',[]),('candidate',['--task-id','FIG-1'])):
        proc=subprocess.run(command+extra,cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=15)
        assert proc.returncode==0 and not proc.stderr,proc.stderr
        observations[name]=json.loads(proc.stdout)
        commands.append({'name':name,'argv':command+extra,'exit_code':proc.returncode,
            'stdout_sha256':hashlib.sha256(proc.stdout.encode()).hexdigest()})
    assert observations['candidate']==[r for r in observations['baseline'] if r['event']['task_id']=='FIG-1']
    assert len(observations['baseline'])==4 and len(observations['candidate'])==2
    assert all(r['receipt'] is None for r in box.status())
    return observations,commands

def prepare(root,base,private):
    refdir=base/'fixture-records';refdir.mkdir(exist_ok=True)
    cases=[('FIG-2','review','Revise the legend units from milliseconds to seconds before publishing panel 2.',
        'Panel 2 legend labels disagree with the measured seconds column; check the source units.'),
       ('FIG-1','blocker','Keep panel 1 consumption blocked until an independent reviewer validates the corrected data.',
        'Panel 1 has a stale measurement snapshot and lacks current independent validation.'),
       ('FIG-2','question','Confirm whether panel 2 should show median with IQR or individual repeat measurements.',
        'The panel 2 aggregation convention remains unresolved; main host coordinates this separate task.'),
       ('FIG-1','correction','Read the replacement panel 1 dataset and obtain fresh independent validation; retain the blocker.',
        'A replacement panel 1 dataset is available; its producer notification is not acceptance.')]
    events=[]
    for seq,(task,kind,action,summary) in enumerate(cases,1):
        path=refdir/(str(seq)+'.json')
        dump(path,{'task_id':task,'kind':kind,'finding_id':'finding-'+str(seq),
            'scope':'synthetic task-local coordination only','action':action,'note':summary})
        events.append({'event_id':'notice-'+str(seq),'run_id':'token005-inbox','input_version':'figures:v1',
            'sender':'reviewer','task_id':task,'kind':kind,'action':action,'summary':summary,
            'refs':[{'id':'finding-'+str(seq),'path':path.relative_to(root).as_posix(),'sha256':digest(path)}]})
    plan={'schema_version':1,'run_id':'token005-inbox','input_version':'figures:v1','max_events':10,
          'routes':[{'sender':'reviewer','recipient':'writer','task_id':task,'kind':kind} for task,kind,_,_ in cases]}
    dump(base/'fixture-plan.json',plan);dump(base/'fixture-events.json',events)
    db=private/'tok005-fixture.sqlite'
    assert not db.exists(),'never reuse an already dispatched fixture'
    observations,commands=replay(root,base,db)
    for name,value in observations.items():
        (base/(name+'.display.json')).write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())
    for c in commands:assert c['stdout_sha256']==digest(base/(c['name']+'.display.json'))
    dump(base/'fixture-commands.json',commands)
    messages=[{'seq':r['seq'],'kind':r['event']['kind'],'action':r['event']['action']} for r in observations['candidate']]
    oracle={'blocked':True,'messages':messages}
    props={'blocked':{'type':'boolean'},'messages':{'type':'array','items':{'type':'object',
        'properties':{'seq':{'type':'integer'},'kind':{'type':'string'},'action':{'type':'string'}},
        'required':['seq','kind','action'],'additionalProperties':False}}}
    schema={'type':'object','properties':props,'required':list(props),'additionalProperties':False}
    dump(base/'output-schema.json',schema)
    prompts={n:PREFIX+'\n'+GUIDANCE+json.dumps(v,ensure_ascii=False,indent=2) for n,v in observations.items()}
    return schema,prompts,oracle
