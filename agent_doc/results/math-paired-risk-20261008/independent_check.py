from pathlib import Path
from fractions import Fraction as F
import json,hashlib,itertools,time,tempfile,sys,math
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));start=time.process_time()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def parse(x):
 if isinstance(x,list):return [parse(v) for v in x]
 if isinstance(x,dict):return {k:parse(v) for k,v in x.items()}
 if isinstance(x,str):
  try:return F(x)
  except ValueError:return x
 return x
def direct(law,E):
 return sum(p*sum(q[i]*E[i][j]*k[j] for i in range(len(q)) for j in range(len(k)))**2 for q,k,p in law)
def joint(law,m,n):
 return [[sum(p*q[i]*q[h]*k[j]*k[l] for q,k,p in law) for l in range(n) for h in range(m)] for j in range(n) for i in range(m)]
def proxy(law,m,n):
 return [[sum(p*q[i]*q[h] for q,k,p in law)*sum(p*k[j]*k[l] for q,k,p in law) for l in range(n) for h in range(m)] for j in range(n) for i in range(m)]
def subtract(A,B):return [[a-b for a,b in zip(x,y)] for x,y in zip(A,B)]
def det(A):return A[0][0]*A[1][1]-A[0][1]*A[1][0]
raw=parse(load(BASE/'raw.json'));cases=raw['exact_cases'];assert len(cases)==36 and len({c['id'] for c in cases})==36
checks=[]
for c in cases:
 law,E=c['law'],c['E'];m,n=len(E),len(E[0]);assert sum(p for q,k,p in law)==1 and all(p>0 and len(q)==m and len(k)==n for q,k,p in law)
 D=joint(law,m,n);D0=proxy(law,m,n);assert D==c['D'] and D0==c['D0'] and direct(law,E)==c['risk']==c['quadratic']
 v=[E[i][j] for j in range(n) for i in range(m)];P=sum(v[a]*D0[a][b]*v[b] for a in range(m*n) for b in range(m*n));assert P==c['proxy']
 G=[[sum(p*sum(q[a]*E[a][b]*k[b] for a in range(m) for b in range(n))*q[i]*k[j] for q,k,p in law) for j in range(n)] for i in range(m)];assert G==c['gradient']
 V=c['direction'];h=F(1,17);plus=[[E[i][j]+h*V[i][j] for j in range(n)] for i in range(m)];minus=[[E[i][j]-h*V[i][j] for j in range(n)] for i in range(m)]
 derivative=(direct(law,plus)-direct(law,minus))/(2*h);assert derivative==c['derivative']==2*sum(G[i][j]*V[i][j] for i in range(m) for j in range(n))
 # M perturbation has opposite sign to E=H-M.
 assert (direct(law,minus)-direct(law,plus))/(2*h)==-derivative
 delta=max(abs(D[a][a]-D0[a][a]) for a in range(m*n));assert delta==c['delta'] and abs(c['risk']-P)<=delta*sum(x*x for x in v)
 Z=[[F(0)]*n for _ in range(m)];assert direct(law,Z)==0 # H=M, feasible at full budget
 assert direct(law,subtract(E,Z))==c['risk'] # r=0 permits only M=0
 checks.append(c['id'])
r=raw['rank_witness'];H,M0,M1=r['H'],r['proxy_optimal_M'],r['paired_feasible_M'];assert det(H)==2 and det(M0)==det(M1)==0 and any(x for row in M0 for x in row) and any(x for row in M1 for x in row)
assert [direct(r['law'],subtract(H,M)) for M in (M0,M1)]==r['paired_losses']==[F(1,2),0]
assert r['proxy_losses']==[F(1,4),F(5,4)]
Dp=proxy(r['law'],2,2)
for M,expected in zip((M0,M1),r['proxy_losses']):
 error=subtract(H,M);v=[error[i][j] for j in range(2) for i in range(2)];assert sum(v[a]*Dp[a][b]*v[b] for a in range(4) for b in range(4))==expected
assert direct([([F(2)],[F(3)],F(1))],[[F(1)]])==36 # noncentered moment, Cov(z)=0 would fail
assert [[sum(p*q[i]*k[j] for q,k,p in r['law']) for j in range(2)] for i in range(2)]==r['zero_cross_covariance']==[[0,0],[0,0]]
assert r['eta']==1 and r['eta_lt_one_certificate']=='not applicable'
w=raw['whitening_rank_witness'];assert det(w['X'])==0 and det(w['reshaped_Y'])==-3 and all(x>0 for x in w['whitening_diagonal'])
t=raw['relative_certificate'];D=joint(t['law'],2,2);D0=proxy(t['law'],2,2);ratios=[D[a][a]/D0[a][a] for a in range(4)];assert min(ratios)==F(2,5) and max(ratios)==F(8,5) and max(abs(x-1) for x in ratios)==t['eta']==F(3,5) and (1+t['eta'])/(1-t['eta'])==t['factor']==4
for M in t['tested_rank1_candidates']:assert det(M)==0 and direct(t['law'],subtract(H,M0))<=4*direct(t['law'],subtract(H,M))
s=raw['sensor'];assert [direct(s['law'],subtract(s['H'],M)) for M in (s['proxy_M'],s['paired_M'])]==s['losses_A_squared']==[F(25,2),0]
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.knowledge_index import build_index,indexed_search
store=KnowledgeStore(ROOT/'knowledge');cfg=load(BASE/'retrieval_protocol.json');retr=load(BASE/'retrieval.json');assert retr['snapshot']==store.snapshot
assert retr['protocol_sha256']==sha(BASE/'retrieval_protocol.json') and retr['holdouts_metadata_sha256']==sha(ROOT/'knowledge/evaluation_holdouts.json')
with tempfile.TemporaryDirectory() as tmp:
 db=Path(tmp)/'independent.sqlite';build_index(store,db)
 for rec in retr['records']:
  actual=store.search(rec['query'],domain=cfg['domain'],limit=cfg['cutoff']) if rec['backend']=='files-lexical-v1' else indexed_search(store,db,rec['query'],domain=cfg['domain'],limit=cfg['cutoff'])
  assert actual==rec['result'] and [a['id'] for a in actual['results']]==rec['actual'] and rec['hit'] and cfg['expected_id'] in rec['actual']
context=store.context(store.search(cfg['queries'][0],domain=cfg['domain'],limit=1),**cfg['context']);assert context==retr['context'] and context['status']=='ready'
assert {e['id'] for e in context['entries']}=={'math.paired-bilinear-risk','math.tensor-kronecker-calculus','math.weighted-bilinear-low-rank','math.low-rank-svd'}
store.check_refs(load(BASE/'retrieval_knowledge_use.json')['knowledge_refs'])
corpus={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'knowledge').rglob('*')) if p.is_file()}
bundle=ROOT/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge';assert all((bundle/p.relative_to(ROOT/'knowledge')).read_bytes()==p.read_bytes() for p in (ROOT/'knowledge').rglob('*') if p.is_file())
assert {str(p.relative_to(bundle)) for p in bundle.rglob('*') if p.is_file()}=={str(p.relative_to(ROOT/'knowledge')) for p in (ROOT/'knowledge').rglob('*') if p.is_file()}
assert sha(Path('/workspace/scratch/1e3b490c36dd/a3-paper.pdf'))==load(BASE/'sources.json')['recent']['pdf_sha256']
result={'actor':'independent-paired-review','context':'/root/paired_result_review','case_ids':checks,'case_count':len(checks),'rank0_full_H_equals_M':'exact direct checks in every case','gradient_M_sign':'negative twice implicit operator checked with separate h=1/17','eta_boundary':'eta=1 rejected; eta=3/5 factor4 checked analytically','retrieval_records':len(retr['records']),'context_count':len(context['entries']),'snapshot':store.snapshot,'holdout_sha256':retr['holdouts_metadata_sha256'],'corpus_hashes':corpus,'bundle_byte_parity':True,'cpu_seconds':time.process_time()-start,'limitations':['All fixtures are public development checks; not unused/model tests','Proofs contextual, not formal Lean; no general optimizer or eigensolver','Timing/chars are diagnostic only']}
(BASE/'independent_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('case_ids','corpus_hashes')},ensure_ascii=False))
