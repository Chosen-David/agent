"""Independent structural oracle, random JSON properties and actual Mailbox gates."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import traceback
import types
ROOT=Path(__file__).resolve().parents[2]
RUN=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/'.agent-runs/memory-index96-deps')]
os.environ['TIKTOKEN_CACHE_DIR']=str(ROOT/'.agent-runs/memory-index96-token-cache')
tempfile.tempdir=str(RUN/'tmp');Path(tempfile.tempdir).mkdir(exist_ok=True)
from agent_runtime.handoff_encoding import encode_basis_tables,encode_claims_table,decode_basis_payload
from agent_runtime.handoff_basis import basis_context,make_token_counter
from agent_runtime.external_json import strict_json
from agent_runtime.communication import Mailbox
from agent_runtime.project_memory import MemoryLedger
CLAIMS=['id','status','depends_on','artifact_ids','knowledge_ids','memory_ids','assumptions']
MEMORY=['id','kind','content','source','scope','evidence','status','created_at','document_refs','deps']
def require(cond,reason):
    if not cond:raise AssertionError(reason)
def dump(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def typed(value):
    if isinstance(value,dict):return ('object',tuple((k,typed(v)) for k,v in sorted(value.items())))
    if isinstance(value,list):return ('array',tuple(typed(v) for v in value))
    return (type(value).__name__,dump(value))
def reference(value):
    result=deepcopy(value);result['context_format']='basis-tables/v1'
    for key,cols in [('evidence_claims',CLAIMS),('memory_entries',MEMORY)]:
        result[key]={'columns':cols[:],'rows':[[deepcopy(entry[col]) for col in cols] for entry in value[key]]}
    return result
def depth(value,level=0):
    if isinstance(value,dict):children=value.values()
    elif isinstance(value,list):children=value
    else:return -1
    return max([level]+[depth(child,level+1) for child in children if isinstance(child,(dict,list))])
def refused(fn):
    try:fn()
    except ValueError:return
    raise AssertionError('expected explicit ValueError refusal')
def minimal():return {'evidence_claims':[],'memory_entries':[dict(zip(MEMORY,['id','claim','body','source',[], 'verified','active','now',None,[]]))]}

def random_properties():
    rng=random.Random(211021)
    old_source=subprocess.check_output(['git','show','425390428f7ea9dbf5b5a4756c5d6cadcab89be3:agent_runtime/handoff_encoding.py'],cwd=ROOT)
    old=types.ModuleType('agent_runtime._independent_old_encoding');old.__package__='agent_runtime'
    exec(compile(old_source,'baseline-handoff-encoding','exec'),old.__dict__)
    def value(n=0):
        if n>2 or rng.randrange(3)==0:
            return rng.choice([None,True,False,-17,0,1,1.0,-0.0,9007199254740993,1e-200,
                               '', '中文 🧠 e\u0301','<|endoftext|>','columns rows context_format','\n\t\\"'])
        if rng.randrange(2):return [value(n+1) for _ in range(rng.randrange(4))]
        return {key:value(n+1) for key in rng.sample(['x','列名','0','rows',''],rng.randrange(5))}
    for _ in range(250):
        payload={'evidence_claims':[{k:value() for k in CLAIMS} for _ in range(rng.randrange(5))],
                 'memory_entries':[{k:value() for k in MEMORY} for _ in range(rng.randrange(7))],
                 'extra':{'context_format':'nested marker retained','value':value()}}
        before=typed(payload)
        encoded=encode_basis_tables(payload)
        require(typed(encoded)==typed(reference(payload)),'row/column constructor differs')
        require(typed(decode_basis_payload(dump(encoded)))==before,'type-sensitive roundtrip')
        require(typed(payload)==before,'encoder mutated input')
        require(dump(encode_claims_table(payload))==dump(old.encode_claims_table(payload)),'legacy encoder changed')
        require(typed(decode_basis_payload(dump(old.encode_claims_table(payload))))==typed(old.decode_basis_payload(dump(old.encode_claims_table(payload)))),'legacy decoder changed')
    payload=minimal();payload['memory_entries'][0]['document_refs']={'mutable':[1]}
    encoded=encode_basis_tables(payload);encoded['memory_entries']['rows'][0][8]['mutable'].append(2)
    require(payload['memory_entries'][0]['document_refs']=={'mutable':[1]},'output alias leaked into input')
    return {'seed':211021,'random_payloads':250,'legacy_differential_payloads':250,'type_sensitive':True}

def invalid_and_bounds():
    invalid=0
    for collection,cols in [('evidence_claims',CLAIMS),('memory_entries',MEMORY)]:
        payload=minimal();payload['evidence_claims']=[dict(zip(CLAIMS,['c','candidate',[],[],[],[],[]]))]
        for mutation in ('extra-field','missing-field','not-object'):
            bad=deepcopy(payload)
            if mutation=='extra-field':bad[collection][0]['future']='must refuse'
            elif mutation=='missing-field':bad[collection][0].pop(cols[-1])
            else:bad[collection][0]=[]
            before=typed(bad);refused(lambda:encode_basis_tables(bad));require(typed(bad)==before,'failed encoder mutated input');invalid+=1
        for mutation in ('extra-table','missing-columns','reorder','missing-row-value','extra-row-value','wrong-row-type','wrong-rows-type'):
            bad=reference(payload);table=bad[collection]
            if mutation=='extra-table':table['unknown']=True
            elif mutation=='missing-columns':table.pop('columns')
            elif mutation=='reorder':table['columns']=table['columns'][::-1]
            elif mutation=='missing-row-value':table['rows'][0].pop()
            elif mutation=='extra-row-value':table['rows'][0].append(None)
            elif mutation=='wrong-row-type':table['rows'][0]={}
            else:table['rows']={}
            refused(lambda:decode_basis_payload(dump(bad)));invalid+=1
    for raw in ('{"x":1,"x":2}','{"x":{"same":0,"same":1}}','{"context_format":"basis-tables/v2"}',
                '{"context_format":true}','{"context_format":null}','[]',
                *['{"n":'+x+'}' for x in ('NaN','Infinity','-Infinity','1e400','-1e400')]):
        refused(lambda:decode_basis_payload(raw));invalid+=1
    refused(lambda:strict_json(b'\xff'));invalid+=1
    payload=minimal();payload['memory_entries'][0]['content']=''
    room=200000-len(dump(reference(payload)))
    payload['memory_entries'][0]['content']='x'*room
    require(len(dump(encode_basis_tables(payload)))==200000,'exact character boundary refused')
    payload['memory_entries'][0]['content']+='x';refused(lambda:encode_basis_tables(payload));invalid+=1
    depth_results=[]
    for nesting in (0,1,250,251,252,253,254,255,256,257,260,400):
        payload=minimal();nested=0
        for _ in range(nesting):nested=[nested]
        payload['memory_entries'][0]['document_refs']=nested
        expected=depth(reference(payload))<=256
        if expected:require(typed(decode_basis_payload(dump(encode_basis_tables(payload))))==typed(payload),'valid depth roundtrip')
        else:refused(lambda:encode_basis_tables(payload))
        depth_results.append({'nested_arrays':nesting,'encoded_container_depth':depth(reference(payload)),'accepted':expected})
    return {'invalid_cases':invalid,'depth_boundaries':depth_results,'exact_200000_characters':'pass'}

def mailbox_gates():
    with tempfile.TemporaryDirectory(prefix='independent-mailbox-') as tmp:
        root=Path(tmp);ledger=MemoryLedger(root,create=True)
        ledger.add('base','observation','合成原文 1.0 🧠','independent:synthetic',evidence='verified')
        ledger.add('leaf','claim','dependent value','independent:synthetic',deps=['base'],evidence='verified')
        body=b'{"value":1}'
        (root/'proof.json').write_bytes(body)
        artifact={'id':'proof','path':'proof.json','sha256':hashlib.sha256(body).hexdigest()}
        record={'schema_version':1,'run_id':'independent','role':'code','input_version':'v1','status':'completed','limitations':[],
                'artifacts':[artifact],'checks':[{'criterion':'synthetic structure','status':'pass','artifact_ids':['proof']}],
                'tasks':[{'task_id':'T1','status':'done','evidence':['proof']}], 'knowledge_refs':[],'memory_refs':['leaf'],
                'evidence_claims':[dict(zip(CLAIMS,['claim','supported',[],['proof'],[],['leaf'],[]]))]}
        recipients=['ordinary','legacy','tables','bounded-chars','bounded-tokens']
        plan={'schema_version':1,'run_id':'independent','input_version':'v1','routes':[
            {'sender':'code','recipient':name,'task_id':'T1','kind':'artifact'} for name in recipients]}
        box=Mailbox(root/'mail.sqlite',plan,root)
        handoff=dump(record).encode('utf-8');(root/'handoff.json').write_bytes(handoff)
        seq=box.publish({'event_id':'E1','run_id':'independent','input_version':'v1','sender':'code','task_id':'T1',
                         'kind':'artifact','summary':'synthetic','action':'verify','refs':[{
                             'id':'handoff','path':'handoff.json','sha256':hashlib.sha256(handoff).hexdigest()}]})['seq']
        request={'schema_version':1,'input_version':'v1','tasks':[{'task_id':'T1'}],
                 'memory_required':True,'memory_refs':['leaf'],'required_claim_ids':['claim']}
        counter=make_token_counter('o200k_base')
        ordinary=box.prepare_context('ordinary',seq,request,token_counter=counter)
        legacy=box.prepare_context('legacy',seq,{**request,'context_format':'claims-table/v1'},token_counter=counter)
        table_request={**request,'context_format':'basis-tables/v1','context_tokenizer':'o200k_base'}
        table=box.prepare_context('tables',seq,table_request,token_counter=counter)
        plain=json.loads(ordinary['payload']);restored=decode_basis_payload(table['payload'])
        require(typed(restored)==typed(plain)==typed(decode_basis_payload(legacy['payload'])),'real Mailbox payload lost values')
        require({e['id'] for e in restored['memory_entries']}=={'base','leaf'},'missing memory ancestor')
        chars=len(table['payload']);tokens=counter(table['payload'])
        box.prepare_context('tables',seq,table_request,token_counter=counter,max_chars=chars,max_tokens=tokens)
        refused(lambda:box.prepare_context('tables',seq,table_request,token_counter=counter,max_chars=chars-1))
        refused(lambda:box.prepare_context('tables',seq,table_request,token_counter=counter,max_tokens=tokens-1))
        refused(lambda:box.prepare_context('bounded-chars',seq,{**table_request,'context_max_chars':chars-1},token_counter=counter,max_chars=200000))
        refused(lambda:box.prepare_context('bounded-tokens',seq,{**table_request,'context_max_tokens':tokens-1},token_counter=counter,max_tokens=tokens+100))
        refused(lambda:box.prepare_context('tables',seq,request))
        partial=basis_context(root,record,table_request,known_memory_ids=['leaf'],token_counter=counter)
        require([e['id'] for e in decode_basis_payload(partial['payload'])['memory_entries']]==['base'],'known leaf hid ancestor')
        (root/'proof.json').write_bytes(b'changed')
        refused(lambda:box.prepare_context('tables',seq,table_request,token_counter=counter))
        (root/'proof.json').write_bytes(body)
        ledger.correct('base','base2','corrected synthetic value','independent:correction','fixture correction')
        refused(lambda:box.prepare_context('tables',seq,table_request,token_counter=counter))
        refused(lambda:basis_context(root,record,table_request,known_memory_ids=['base','leaf'],token_counter=counter))
        return {'ordinary':ordinary,'legacy':legacy,'tables':table,'closure':['base','leaf'],
                'exact_caps':'pass','one_short_and_consumer_caps':'refused','immutable_request':'refused',
                'artifact_mutation':'refused','correction_and_known_reuse':'refused'}

checks=[]
for name,fn in [('random_type_reference_and_legacy',random_properties),('strict_schema_and_boundaries',invalid_and_bounds),('actual_independent_mailbox',mailbox_gates)]:
    try:checks.append({'name':name,'verdict':'pass','observations':fn()})
    except Exception:checks.append({'name':name,'verdict':'fail','traceback':traceback.format_exc()})
result={'actor':'/root/memory_index_verifier','run_id':'tok-mem-20261021-independent-v1','checks':checks,
        'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                         ['agent_runtime/handoff_encoding.py','agent_runtime/handoff_basis.py','agent_runtime/external_json.py']}}
with (RUN/'properties-v1.json').open('x',encoding='utf-8') as stream:stream.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{'name':c['name'],'verdict':c['verdict']} for c in checks]))
sys.exit(int(any(c['verdict']!='pass' for c in checks)))
