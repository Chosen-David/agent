from pathlib import Path
import json, hashlib, subprocess, shutil, sys, math
from reference import D as Dec, F, Z, trig, mm, dim, diag, transpose
import tiktoken

R=Path(__file__).resolve().parents[4]; D=Path(__file__).parent; P=D.parent
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((P/'manifest.json').read_text())
assert digest(P/'manifest.json')=='75679d88cc7ff93aedce91c18f71d524cc6ef55dbe93bff2edd91df57478e216'
bindings=[manifest['validation_plan']]+[x for values in manifest['artifacts'].values() for x in values]
for x in bindings: assert digest(R/x['path'])==x['sha256'], x['path']
corpus=json.loads((P/'retrieval-corpus.json').read_text())['files']
for x in corpus: assert digest(R/x['path'])==x['sha256'],x['path']
assert {x['path'] for x in corpus}=={str(p.relative_to(R)) for p in (R/'knowledge/entries').rglob('*') if p.is_file() and p.suffix in ('.json','.md')}

# A genuinely distinct reference: 75-digit trigonometric arithmetic and direct
# application to the two real basis vectors, with no producer matrix helpers.
raw=json.loads((P/'raw.json').read_text()); assert len(raw['cases'])==32
errors=[];min_gap=Dec('Infinity')
for row in raw['cases']:
    t,p=Dec(row['theta']),Dec(row['phi']);a=Z(*row['a']);b=Z(*row['b'])
    S=lambda z:a*z+b*z.conj()
    sq=lambda n:sum((S(trig(n*t)*z)-trig(n*p)*S(z)).sq() for z in [Z(1),Z(0,1)])
    e=sq(1);errors += [abs(e-Dec(row['defect_squared'])),abs(e-Dec(row['reference_squared']))]
    dp=abs(trig(t)-trig(p));dm=abs(trig(-t)-trig(p));gap=min(dp,dm);min_gap=min(min_gap,gap)
    assert (2*(a.sq()+b.sq())).sqrt()<=e.sqrt()/gap+Dec('1e-60')
    assert [step['m'] for step in row['steps']]==[-31,-1,0,1,17]
    for step in row['steps']:
        val=sq(step['m']).sqrt();errors.append(abs(val-Dec(step['defect'])))
        assert val<=abs(step['m'])*e.sqrt()+Dec('1e-60')
assert max(errors)<Dec('2e-12')
assert all(math.isfinite(x) for row in raw['cases'] for x in [row['theta'],row['phi'],row['defect_squared'],row['reference_squared'],*row['a'],*row['b']])
I=[[F(1),F(0)],[F(0),F(1)]];J=[[F(0),F(-1)],[F(1),F(0)]];Q=[[F(3,5),F(-4,5)],[F(4,5),F(3,5)]]
named={'zero':I,'pi':[[-v for v in row] for row in I],'positive':Q,'negative':transpose(Q),'quarter':J};dimensions={}
for n,A in named.items():
    for m,B in named.items():
        value=dim(A,B);expected=4 if A==B and A in [I,named['pi']] else 2 if A==B or A==transpose(B) else 0
        assert value==expected;dimensions[n+'->'+m]=value
assert len(raw['exact_branches'])==6 and [r['observed'] for r in raw['exact_branches']]==[True,True,True,True,False,False]
A=diag(Q,Q,I);B=diag(Q,I);assert dim(A,B)==8
# F=(I I)/sqrt(2): FF^T=I, F restricted to (x,x) preserves all bilinear forms;
# avoid an irrational matrix by checking G=(I I), GG^T=2I and G diag(Q,Q)=QG.
G=[row+row for row in I];assert mm(G,transpose(G))==[[2*v for v in row] for row in I]
assert mm(G,diag(Q,Q))==mm(Q,G)
for v,w in [([F(3),F(4)],[F(5),F(-2)]),([F(1),F(0)],[F(0),F(1)])]:
    V=v+v;W=w+w;GV=mm(G,[[z] for z in V]);GW=mm(G,[[z] for z in W])
    assert sum(a[0]*b[0] for a,b in zip(GV,GW))/2==sum(a*b for a,b in zip(V,W))
for t,p in [(Dec('.5'),Dec('.500000000001')),(Dec('.5'),Dec('-.500000000001'))]:
    assert min(abs(trig(t)-trig(p)),abs(trig(-t)-trig(p)))>0

# Producer replay relocates its write root under independent/, preserving bytes.
rerun=D/'rerun';rerun.mkdir(exist_ok=True)
for n in ['verify.py','config.json']:shutil.copyfile(P/n,rerun/n)
run=subprocess.run([sys.executable,str(rerun/'verify.py')],capture_output=True,text=True,check=True)
(D/'rerun.log').write_text(run.stdout+run.stderr)
assert (rerun/'raw.json').read_bytes()==(P/'raw.json').read_bytes()
summary=json.loads((P/'summary.json').read_text());again=json.loads((rerun/'summary.json').read_text())
assert {k:v for k,v in summary.items() if k!='elapsed_seconds'}=={k:v for k,v in again.items() if k!='elapsed_seconds'}
assert summary['assertions']==361 and summary['cases']==32

def cli(*args):return json.loads(subprocess.check_output([sys.executable,'-m','agent_runtime.knowledge','--root','knowledge',*args],cwd=R))
idx=D/'replay.sqlite';index=cli('index','--db',str(idx));usage=json.loads((P/'knowledge-usage.json').read_text());replays=[]
assert len(usage['retrieval'])==6
for item in usage['retrieval']:
    opts=['--index',str(idx)] if item['backend']=='sqlite' else []
    val=cli('search',item['input']['query'],'--domain',item['domain'],'--limit','3',*opts)
    assert val==item['result']
    assert val['results'][0]['id']=='math.rotation-intertwiner'
    replays.append(val)
show=cli('show','math.rotation-intertwiner')
assert show['knowledge_refs']==usage['knowledge_refs']
tokens=len(tiktoken.get_encoding('cl100k_base').encode(json.dumps(show,ensure_ascii=False)))
cost=json.loads((P/'cost.json').read_text());assert tokens==cost['body_package_cl100k_base_tokens']==2716
assert cost['retrieval_cli_calls']==8 and cost['model_AB_calls']==0 and cost['host_tokens'] is None and cost['token_saving_claim'] is False
(D/'retrieval-replay.json').write_text(json.dumps({'index':index,'replay':replays,'show':show,'tokens':tokens},ensure_ascii=False,indent=2)+'\n')
pdf=R/'.agent-runs/math-rope-intertwiner-20261008/recent.pdf'
assert digest(pdf)==json.loads((P/'research.json').read_text())['recent']['pdf_sha256']
# Check bindings again after all independent operations.
for z in bindings+corpus:assert digest(R/z['path'])==z['sha256']
result={'status':'pass','manifest_sha256':digest(P/'manifest.json'),'binding_count':len(bindings),'corpus_file_count':len(corpus),'max_75digit_reference_absolute_error':float(max(errors)),'minimum_generator_gap':float(min_gap),'rational_solution_dimensions':dimensions,'mixed_block_solution_dimension':8,'raw_byte_replay_equal':True,'producer_assertions':summary['assertions'],'retrieval_replays':6,'actual_show_cl100k_tokens':tokens,'recent_pdf_sha256':digest(pdf),'independent_python':sys.version,'reference_arithmetic':'75digit Decimal Taylor plus exact Fraction elimination','tiktoken_version':tiktoken.__version__}
(D/'check-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
