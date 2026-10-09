"""Six meaningful synthetic claims through the real mailbox; no padding."""
import hashlib
import json
from pathlib import Path
from agent_runtime.communication import Mailbox
from agent_runtime.handoff_encoding import decode_basis_payload
from scripts.token_probe import dump,digest

def prepare(root,base,private):
    relative=base.relative_to(root).as_posix()
    dump(base/'artifact.json',{'kind':'synthetic fixture only','margin':0.5,'unit':'score'})
    artifact={'id':'A1','path':relative+'/artifact.json','sha256':digest(base/'artifact.json')}
    def claim(cid,status,parents=(),assumptions=()):
        return {'id':cid,'status':status,'depends_on':list(parents),'artifact_ids':['A1'],
                'knowledge_ids':[],'memory_ids':[],'assumptions':list(assumptions)}
    unknown={'name':'independent measurement completed','status':'unknown','evidence_ids':[]}
    invalid={'name':'revision still current','status':'unsatisfied','evidence_ids':['A1']}
    claims=[claim('C_BASE','supported'),claim('C_CHAIN','supported',['C_BASE']),
            claim('C_MEASURE','candidate',['C_CHAIN'],[unknown]),
            claim('C_REJECT','rejected',['C_BASE'],[invalid]),
            claim('C_REVIEW','candidate',['C_MEASURE']),
            claim('C_RELEASE','candidate',['C_REVIEW','C_REJECT'])]
    record={'schema_version':1,'run_id':'claims-fixture','role':'code','input_version':'v1','status':'completed',
            'limitations':[],'artifacts':[artifact],'knowledge_refs':[],'memory_refs':[], 'evidence_claims':claims,
            'checks':[{'criterion':'synthetic structure only','status':'pass','artifact_ids':['A1']}],
            'tasks':[{'task_id':'T1','status':'done','evidence':['A1']}]}
    dump(base/'handoff.json',record)
    plan={'schema_version':1,'run_id':'claims-fixture','input_version':'v1',
          'routes':[{'sender':'code','recipient':recipient,'task_id':'T1','kind':'artifact'}
                    for recipient in ('baseline-reader','table-reader')]}
    request={'schema_version':1,'input_version':'v1','tasks':[{'task_id':'T1'}],
             'required_claim_ids':['C_CHAIN'],'context_max_chars':4000}
    dump(base/'mailbox-plan.json',plan);dump(base/'consumer-request.json',request)
    ref={'id':'handoff','path':relative+'/handoff.json','sha256':digest(base/'handoff.json')}
    event={'event_id':'E1','run_id':'claims-fixture','input_version':'v1','sender':'code','task_id':'T1','kind':'artifact',
           'summary':'Synthetic pending/rejected/ancestor fixture','action':'Classify, do not execute','refs':[ref]}
    dump(base/'event.json',event)
    box=Mailbox(private/('claims-fixture-'+base.name+'.sqlite'),plan,root)
    seq=box.publish(event)['seq']
    ordinary=box.prepare_context('baseline-reader',seq,request)['payload']
    table=box.prepare_context('table-reader',seq,{**request,'context_format':'claims-table/v1'})['payload']
    assert decode_basis_payload(table)==json.loads(ordinary)
    prefix='For this supplied synthetic handoff, which claims are ready?\n'
    guidance=('If evidence_claims is a table, map columns to row values; otherwise read objects. '
              'A claim is ready only if status is supported, every ancestor is supported and all assumptions are satisfied. '
              'All other claims are blocked. Return JSON with sorted ready and blocked IDs, input_version, '
              'and the exact SHA256 of artifact A1. No tools, no execution.\n')
    prompts={'baseline':prefix+guidance+ordinary,'candidate':prefix+guidance+table}
    props={'ready':{'type':'array','items':{'type':'string'}},'blocked':{'type':'array','items':{'type':'string'}},
           'input_version':{'type':'string'},'artifact_sha256':{'type':'string'}}
    schema={'type':'object','properties':props,'required':list(props),'additionalProperties':False}
    dump(base/'output-schema.json',schema)
    oracle={'ready':['C_BASE','C_CHAIN'],'blocked':['C_MEASURE','C_REJECT','C_RELEASE','C_REVIEW'],
            'input_version':'v1','artifact_sha256':artifact['sha256']}
    return schema,prompts,oracle
