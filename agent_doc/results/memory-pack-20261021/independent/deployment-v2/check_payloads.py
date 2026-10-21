"""Independent full-payload reconstruction, BPE recount and reproducibility."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];RUN=Path(__file__).resolve().parent
SOURCE=ROOT/'agent_doc/results/memory-pack-20261021/deployment-v2'
sys.path.insert(0,str(ROOT/'.agent-runs/memory-index96-deps'))
os.environ['TIKTOKEN_CACHE_DIR']=str(ROOT/'.agent-runs/memory-index96-token-cache')
import tiktoken
import regex
CLAIMS=['id','status','depends_on','artifact_ids','knowledge_ids','memory_ids','assumptions']
MEMORY=['id','kind','content','source','scope','evidence','status','created_at','document_refs','deps']
def require(cond,reason):
    if not cond:raise AssertionError(reason)
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def dump(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def independent_decode(text):
    def unique(items):
        result={}
        for k,v in items:
            require(k not in result,'duplicate wire key');result[k]=v
        return result
    result=json.loads(text,object_pairs_hook=unique)
    fmt=result.pop('context_format',None)
    for key,columns in [('evidence_claims',CLAIMS),('memory_entries',MEMORY)]:
        if fmt=='basis-tables/v1' or (fmt=='claims-table/v1' and key=='evidence_claims'):
            table=result[key];require(set(table)=={'columns','rows'} and table['columns']==columns,'reference schema')
            require(all(len(row)==len(columns) for row in table['rows']),'reference row width')
            result[key]=[{column:deepcopy(row[i]) for i,column in enumerate(columns)} for row in table['rows']]
    return result
def expected_inputs():
    output={}
    for name,count in [('empty',0),('singleton',1),('short-32',32),('unique-32',32),('long-8',8),('unicode-8',8)]:
        memories=[];claims=[]
        for i in range(count):
            content=f'Observation {i}: retain unit and limitation.'
            if name=='long-8':content+=f' A long unique premise {i}{i}{i}.'+' original wording.'*256
            if name=='unicode-8':content=f'更正 {i}：单位需核验。\n🧠 "rows" <|endoftext|> \\路径 e\u0301'
            memories.append({'id':f'm{i}','kind':'observation','content':content,
                'source':f'fixture:source/{i}' if name=='unique-32' else 'fixture:shared-source',
                'scope':{'task_id':f'T{i}' if name=='unique-32' else 'T1'},'evidence':'verified',
                'status':['active','candidate','superseded','stale'][i%4], 'created_at':'2026-10-21T00:00:00Z',
                'document_refs':None,'deps':[f'm{i-1}'] if i else []})
            claims.append({'id':f'c{i}','status':['supported','candidate','rejected'][i%3],
                'depends_on':[f'c{i-1}'] if i else [],'artifact_ids':[],'knowledge_ids':[], 'memory_ids':[f'm{i}'],'assumptions':[]})
        output[name]={'input_version':'v1','knowledge_refs':[],'memory_refs':[e['id'] for e in memories],
            'evidence_claims':claims,'artifacts':[],'knowledge_entries':[],'memory_entries':memories}
    return output
enc=tiktoken.get_encoding('o200k_base');environment=load(SOURCE/'environment.json')
require(tiktoken.__version__==environment['tiktoken']=='0.12.0','tokenizer version')
ranks=hashlib.sha256()
for token,rank in sorted(enc._mergeable_ranks.items(),key=lambda pair:pair[1]):
    ranks.update(len(token).to_bytes(4,'big')+token+rank.to_bytes(4,'big'))
require(ranks.hexdigest()==environment['ranks_sha256'],'rank table')
require(enc._pat_str==environment['pattern'] and enc._special_tokens==environment['special_tokens'] and len(enc._mergeable_ranks)==environment['rank_count'],'encoding identity')
for name,expected in environment['tokenizer_files'].items():
    require(hashlib.sha256((Path(tiktoken.__file__).parent/name).read_bytes()).hexdigest()==expected,'tokenizer file '+name)
cache={}
def reference_tokens(text):
    result=[]
    for piece in regex.findall(enc._pat_str,text):
        raw=piece.encode('utf-8')
        if raw not in cache:
            parts=[bytes([b]) for b in raw]
            while len(parts)>1:
                best=min(range(len(parts)-1),key=lambda i:enc._mergeable_ranks.get(parts[i]+parts[i+1],float('inf')))
                if parts[best]+parts[best+1] not in enc._mergeable_ranks:break
                parts[best:best+2]=[parts[best]+parts[best+1]]
            cache[raw]=[enc._mergeable_ranks[part] for part in parts]
        result.extend(cache[raw])
    return result
checked=[]
def account(text,counts,label):
    tokens=enc.encode(text,disallowed_special=())
    require(tokens==reference_tokens(text),'independent BPE sequence '+label)
    actual={'bytes':len(text.encode('utf-8')),'chars':len(text),'tokens':len(tokens)}
    for key,value in actual.items():require(counts[key]==value,'payload accounting '+label+' '+key)
    checked.append({'label':label,'payload_sha256':hashlib.sha256(text.encode('utf-8')).hexdigest(),**actual})
    return actual
expected=expected_inputs();producer=load(SOURCE/'raw.json');rerun=load(RUN/'rerun-v2/raw.json')
require(dump(load(SOURCE/'inputs.json'))==dump(expected)==dump(load(RUN/'rerun-v2/inputs.json')),'independent fixture reconstruction')
require(dump(producer['cases'])==dump(rerun['cases'])==dump(load(SOURCE.parent/'raw.json')['cases']),'six deterministic case outputs differ from rerun or retained v1')
require([case['case'] for case in producer['cases']]==list(expected),'case coverage')
require(load(SOURCE.parent/'config.json')['formats']==['json','claims-table/v1','basis-tables/v1'],'configured formats')
metrics={};summary=[]
for origin,raw in [('producer',producer),('rerun',rerun)]:
    for case in raw['cases']:
        name=case['case'];formats=case['formats']
        require(list(formats)==['json','claims-table/v1','basis-tables/v1'],'all baselines present')
        for fmt,row in formats.items():
            require(dump(independent_decode(row['payload']))==dump(expected[name]),'reference restoration '+name+fmt)
            require(dump(json.loads(row['payload']))==row['payload'],'exact declared compact serialization')
            account(row['payload'],row,origin+':'+name+':'+fmt)
            if origin=='producer':
                for unit in ('tokens','bytes'):metrics[name+':'+fmt+':'+unit]=row[unit]
        if origin=='producer':summary.append({'case':name, 'counts':{fmt:{u:r[u] for u in ('bytes','tokens')} for fmt,r in formats.items()}})
    mailbox=raw['mailbox'];plain=mailbox['ordinary'];table=mailbox['table']
    require(dump(independent_decode(plain['payload']))==dump(independent_decode(table['payload'])),'actual Mailbox pair not equal')
    require({e['id'] for e in independent_decode(table['payload'])['memory_entries']}=={'input-v1','derived-v1'},'actual fixture ancestor coverage')
    for fmt,pack in [('json',plain),('basis-tables/v1',table)]:account(pack['payload'],pack['usage'],origin+':actualMailbox:'+fmt)
    require(mailbox['exact_budget_accepted'] is True and mailbox['one_token_short_refused'] is True,'measured budget results')
manifest=load(SOURCE/'manifest.json')
require({m['name']:m['value'] for m in manifest['metrics']}==metrics,'manifest metric mapping')
require(all(m['unit']==('UTF-8 bytes' if m['name'].endswith(':bytes') else 'o200k_base text tokens') for m in manifest['metrics']),'metric units')
short=next(case['formats'] for case in producer['cases'] if case['case']=='short-32')
require(short['basis-tables/v1']['tokens']<min(short['json']['tokens'],short['claims-table/v1']['tokens']),'fixed short-32 target failed')
result={'status':'pass','payloads_recounted':len(checked),'independent_BPE':'complete token sequences matched',
        'rank_sha256':ranks.hexdigest(),'deterministic_six_cases':'byte-for-byte equal',
        'source_raw_sha256':hashlib.sha256((SOURCE/'raw.json').read_bytes()).hexdigest(),
        'checks':checked,'cases':summary,'actual_mailbox_counts':{k:producer['mailbox'][k]['usage'] for k in ('ordinary','table')},
        'scope':'complete compact payload strings; no newline/tool/model envelope; actual Mailbox fixture is two-format comparison'}
with (RUN/'payload-checks-v2.json').open('x',encoding='utf-8') as stream:stream.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'payloads_recounted':len(checked),'cases':summary,'actual_mailbox_counts':result['actual_mailbox_counts']}))
