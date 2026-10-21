import sys, os, json, hashlib, zipfile, sqlite3, tempfile
from pathlib import Path
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'.agent-runs/memory-index96-deps')]
os.environ['TIKTOKEN_CACHE_DIR']=str(ROOT/'.agent-runs/memory-index96-token-cache')
os.environ['PYTHONDONTWRITEBYTECODE']='1'
OUT=Path(__file__).parent
BASE=ROOT/'agent_doc/results/token10-20261021-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def same(a,b):return dump(a)==dump(b)
def reject(fn):
    try:fn()
    except ValueError:return
    raise AssertionError('expected ValueError')
def write(p,v):p.write_bytes((dump(v)+'\n').encode('utf-8'))
m=json.loads((BASE/'manifest.json').read_bytes())
c=json.loads((BASE/'contract.json').read_bytes())
bindings={c['validation_plan']['path']:c['validation_plan']['sha256']}
for refs in m['artifacts'].values():
    for r in refs:bindings[r['path']]=r['sha256']
for path,h in bindings.items():assert sha(ROOT/path)==h,path
import tiktoken
assert tiktoken.__version__=='0.12.0'
enc=tiktoken.get_encoding('o200k_base')
count=lambda s:len(enc.encode(s,disallowed_special=()))
env=json.loads((BASE/'environment.json').read_bytes())
ranks=hashlib.sha256()
for token,rank in sorted(enc._mergeable_ranks.items(),key=lambda p:p[1]):
    ranks.update(len(token).to_bytes(4,'big'));ranks.update(token);ranks.update(rank.to_bytes(4,'big'))
assert ranks.hexdigest()==env['ranks_sha256']
COLS=['id','status','depends_on','artifact_ids','knowledge_ids','memory_ids','assumptions']
MEM=['id','kind','content','source','scope','evidence','status','created_at','document_refs','deps']
def restore(text):
    p=json.loads(text);fmt=p.pop('context_format',None)
    if fmt:
        assert fmt in ('claims-table/v1','basis-tables/v1')
        for key,cols in [('evidence_claims',COLS)]+([('memory_entries',MEM)] if fmt=='basis-tables/v1' else []):
            table=p[key];assert table['columns']==cols
            p[key]=[dict(zip(cols,row,strict=True)) for row in table['rows']]
    return p
def options(value):
    opts=[dump(value)]
    a=deepcopy(value)
    if all(set(x)==set(COLS) for x in a['evidence_claims']):
        a['context_format']='claims-table/v1'
        a['evidence_claims']={'columns':COLS,'rows':[[x[k] for k in COLS] for x in value['evidence_claims']]}
        opts.append(dump(a))
        if all(set(x)==set(MEM) for x in value['memory_entries']):
            a['context_format']='basis-tables/v1'
            a['memory_entries']={'columns':MEM,'rows':[[x[k] for k in MEM] for x in value['memory_entries']]}
            opts.append(dump(a))
    return opts
from agent_runtime.handoff_encoding import choose_basis_payload,decode_basis_payload
raw=json.loads((BASE/'raw.json').read_bytes());observed=[];checks=0
for row in raw[:2]:
    value=restore(row['before']);opts=options(value)
    assert opts==row['candidates']
    best=min(enumerate(opts),key=lambda x:(count(x[1]),len(x[1]),x[0]))[1]
    assert row['after']==best and choose_basis_payload(value,count)==(best,count(best))
    for side in ('before','after'):
        assert count(row[side])==row[side+'_tokens']
        assert len(row[side].encode())==row[side+'_bytes']
        assert same(restore(row[side]),value)
    observed.append({'case':row['case'],'candidate_tokens':[count(x) for x in opts],
                     'before':count(row['before']),'after':count(row['after'])})
    checks+=1
value=restore(raw[0]['before'])
for n in (0,1,2):
    v={k:x[:n] for k,x in value.items()};original=deepcopy(v);opts=options(v)
    for counter in (count,len,lambda s:7):
        expected=min(enumerate(opts),key=lambda x:(counter(x[1]),len(x[1]),x[0]))[1]
        text,t=choose_basis_payload(v,counter)
        assert text==expected and t==counter(text) and same(restore(text),v)
        assert same(decode_basis_payload(text),v) and same(v,original)
        assert choose_basis_payload(v,counter,max_chars=len(text),max_tokens=t)==(text,t)
        checks+=1
for bad in (None,lambda s:True,lambda s:-1,lambda s:1.5,lambda s:float('nan')):
    reject(lambda:choose_basis_payload(value,bad));checks+=1
for cap in ({'max_chars':1},{'max_tokens':1}):reject(lambda:choose_basis_payload(value,count,**cap));checks+=1
unknown=deepcopy(value);unknown['evidence_claims'][0]['future']={'type':[True,1,1.0,None]}
text,_=choose_basis_payload(unknown,count);assert same(json.loads(text),unknown);checks+=1
home=Path(tempfile.mkdtemp(prefix='fixture-replay-',dir=OUT))
with zipfile.ZipFile(BASE/'fixture.zip') as z:
    assert all(not Path(p).is_absolute() and '..' not in Path(p).parts for p in z.namelist())
    z.extractall(home)
from agent_runtime.communication import Mailbox
from agent_runtime.project_memory import MemoryLedger
plan=json.loads((home/'plan.json').read_bytes())
# Frozen Mailbox DB binds its original root. Rebuild only the delivery envelope
# in a fresh DB at the isolated root, retaining exact artifact/memory bytes.
with sqlite3.connect(home/'mail.sqlite') as db:event=json.loads(db.execute('SELECT body FROM communication_events WHERE seq=1').fetchone()[0])
box=Mailbox(home/'replay.sqlite',plan,home);box.publish(event)
request={'schema_version':1,'input_version':'v1','tasks':[{'task_id':'T1'}],
         'knowledge_refs':[],'memory_refs':['m3'],'memory_required':True,'knowledge_required':False,
         'context_format':'auto-lossless/v1'}
from agent_runtime.handoff_basis import make_token_counter
counter=make_token_counter('o200k_base')
selected=box.prepare_context('auto',1,request,token_counter=counter,max_chars=200000)
assert same(selected,raw[2]['mailbox_auto'])
assert same(restore(selected['payload']),json.loads(raw[2]['mailbox_plain']['payload']))
assert [e['id'] for e in restore(selected['payload'])['memory_entries']]==['m0','m1','m2','m3']
for kwargs in ({'max_chars':1},{'max_tokens':1}):reject(lambda:box.prepare_context('auto',1,request,token_counter=counter,**kwargs))
reject(lambda:box.prepare_context('auto',1,request))
reject(lambda:box.prepare_context('auto',1,{**request,'context_max_tokens':1},token_counter=counter))
MemoryLedger(home).correct('m0','m0-new','corrected','synthetic:independent','boundary check')
reject(lambda:box.prepare_context('auto',1,request,token_counter=counter))
assert any(x['recipient']=='auto' for x in box.impact())
observed.append({'case':'real Mailbox','plain_tokens':count(raw[2]['mailbox_plain']['payload']),
                 'auto_tokens':count(selected['payload']),'closure_entries':4,
                 'missing_counter_rejected':True,'immutable_request_rejected':True,'correction_stale_rejected':True})
for path,h in bindings.items():assert sha(ROOT/path)==h,path
obs={'result_id':m['result_id'],'independent_checks':checks,'rows':observed,
     'source_review':['handoff_encoding.choose_basis_payload: three complete candidates, bounded strict decode, counter exact int, token/char/order minimum',
     'handoff_basis.basis_context: existing authority/dependency/tokenizer/request budget gates precede encoding; default non-auto branch unchanged',
     'communication.prepare_context -> consume_handoff immutable request/provenance validation -> basis_context; correction rechecks actual ledger'],
     'hashes_before_after_equal':True,'tokenizer_ranks_sha256':ranks.hexdigest(),
     'replay_root_note':'Archived Mailbox DB correctly rejected relocation (plan/root binding). Replay rebuilt exact frozen envelope in a fresh isolated Mailbox, retaining artifact and ledger bytes; original DB was not rebound.'}
write(OUT/'observations.json',obs)
archive='agent_doc/results/token10-20261021-01/independent/'
evidence=[{'path':archive+f,'sha256':sha(OUT/f)} for f in ('observations.json','reproduce.py')]
reasons={
 'implementation':'Read changed two product files and actual validation/context/consumer dependency path; hashes of all 12 bound code files unchanged before and after checks.',
 'reference_boundary':'Independent literal-column table oracle preserves exact JSON scalar types; enumerated real-token, character and constant-counter choices; empty/singleton, unknown fields, invalid/missing counter and dual caps checked; Mailbox request immutability and stale correction rejected.',
 'data_integrity':'Read all three raw cases, all candidates, complete fixture zip and all manifest bindings; fresh isolated Mailbox replay equals frozen auto output and complete four-entry closure.',
 'numerical_sanity':'Recounted all recorded token and UTF-8 byte metrics; 1929 to1929 negative control and74 to11 small-payload gain; actual Mailbox387 to369. Finite integer metrics.',
 'measurement_validity':'Pinned actual tiktoken0.12.0/o200k_base ranks match environment; complete candidate headers/text counted, only local payload comparison, no timing/model accounting claim.',
 'reproducibility':'Independent script replayed choices and frozen Mailbox fixture with same output before isolated correction; all original bound bytes unchanged.'}
review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(BASE/'manifest.json'),
 'artifact_hashes':bindings,'validation_plan_sha256':c['validation_plan']['sha256'],'scope':m['scope'],
 'verifier':{'actor':'/root/token10_verifier','independent':True,'source':'native independent agent tools and source review',
             'run_id':'token10-review-01-v1','method':'manual source/data review plus independently written oracle/counter/isolated Mailbox replay'},
 'limitations':['Synthetic bounded payload and memory-only Mailbox fixtures; no knowledge corpus, live model, QA, cost or universal correctness claim.',
                'Large forced-basis comparison is unchanged; strict gain demonstrated by complete empty/small payload and local Mailbox pair.',
                'Root-bound archived Mailbox cannot be directly relocated; independently replayed its exact envelope and unchanged artifact/ledger bytes in a fresh isolated Mailbox.'],
 'checks':{k:{'verdict':'pass','reason':v,'evidence':evidence} for k,v in reasons.items()}}
write(OUT/'review.json',review)
print(dump({'status':'usable-with-scope','checks':checks,'files':{f:sha(OUT/f) for f in ('review.json','observations.json','reproduce.py')}}))
