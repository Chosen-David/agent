from pathlib import Path
from fractions import Fraction as F
from itertools import product
import json,hashlib,subprocess,sys,shutil,tiktoken
R=Path(__file__).resolve().parents[4];D=Path(__file__).parent;B=D.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
M=json.loads((B/'manifest.json').read_text());before=sha(B/'manifest.json');refs=[r for group in M['artifacts'].values() for r in group]+[M['validation_plan']]
for r in refs:assert sha(R/r['path'])==r['sha256'],r['path']
raw=json.loads((B/'raw.json').read_text());cfg=json.loads((B/'config.json').read_text());count=0

def joint(k,n):
 d={'':F(1)}
 for t in range(n):
  nxt={}
  for h,m in d.items():
   v=F(k[h]);assert 0<=v<=1
   nxt[h+'0']=m*(1-v);nxt[h+'1']=m*v
  d=nxt
 return d

def tv(p,q):return sum(max(F(0),p[x]-q[x]) for x in p)

def cdf_coupling(p,q):
 # interval overlaps under a single U; binary distributions in same token order
 P=[F(0),p[0],F(1)];Q=[F(0),q[0],F(1)]
 return [[max(F(0),min(P[a+1],Q[b+1])-max(P[a],Q[b])) for b in range(2)] for a in range(2)]

assert len(raw['cases'])==cfg['cases']==48
assert [r['case'] for r in raw['cases']]==list(range(48))
words=prefixes=0
for row in raw['cases']:
 n=row['n'];p=joint(row['P'],n);q=joint(row['Q'],n);dist=tv(p,q)
 assert {k:str(v) for k,v in p.items()}==row['pjoint'];assert {k:str(v) for k,v in q.items()}==row['qjoint'];assert dist==F(row['tv'])
 assert sum(p.values())==sum(q.values())==1;assert dist==sum(abs(p[k]-q[k]) for k in p)/2
 assert dist==1-sum(min(p[k],q[k]) for k in p)
 # exhaustive event optimization on small n (up to 8 outcomes)
 if n<=3:assert max(abs(sum((p[x]-q[x]) for j,x in enumerate(p) if mask>>j&1)) for mask in range(1<<len(p)))==dist
 eps=[];mus=[];hy=[q]
 for t in range(n):
  pp=joint(row['P'],t);dif={h:abs(F(row['P'][h])-F(row['Q'][h])) for h in pp};eps.append(max(dif.values()));mus.append(sum(pp[h]*dif[h] for h in pp))
  H={h:(row['P'][h] if len(h)<=t else row['Q'][h]) for h in row['P']};hy.append(joint(H,n))
  assert tv(hy[-1],hy[-2])==mus[-1]
  for h in pp:
   a=F(row['P'][h]);b=F(row['Q'][h]);mat=cdf_coupling([1-a,a],[1-b,b])
   assert [sum(v) for v in mat]==[1-a,a];assert [sum(mat[j][k] for j in range(2)) for k in range(2)]==[1-b,b]
   assert mat[0][1]+mat[1][0]==dif[h];prefixes+=1
 survival=F(1)
 for e in eps:survival*=1-e
 assert eps==list(map(F,row['epsilon']));assert mus==list(map(F,row['P_prefix_mean']))
 assert F(row['product_bound'])==1-survival;assert F(row['mean_bound'])==min(1,sum(mus))
 assert dist<=1-survival<=min(1,sum(eps));assert dist<=min(1,sum(mus));assert F(row['ratio_identity'])==dist
 reward=lambda s:F(s.count('1'),n) if n else F(0)
 assert abs(sum(reward(s)*(p[s]-q[s]) for s in p))==F(row['reward_gap'])<=dist
 # Nonunit reward span, tight event reward and constant reward.
 ev={s for s in p if p[s]>q[s]};f={s:F(-7)+(F(11) if s in ev else F(0)) for s in p}
 assert sum(f[s]*(p[s]-q[s]) for s in p)==11*dist
 assert sum(F(19)*(p[s]-q[s]) for s in p)==0
 words+=len(p);count+=1
assert words==504 and prefixes==456
# Exact endpoint, null-prefix, arbitrarily small greedy and arbitrary coupling fixtures.
assert tv({'0':F(1),'1':F(0)},{'0':F(0),'1':F(1)})==1
assert tv({'0':F(1,2),'1':F(1,2)},{'0':F(1,2),'1':F(1,2)})==0
complement=[[F(0),F(1,2)],[F(1,2),F(0)]]
assert sum(complement[a][b] for a in range(2) for b in range(2) if a!=b)==1
# KL infinity is an exact support condition rather than floating log overflow.
p=[F(1),F(0)];q=[F(9,10),F(1,10)];assert any(q[i]>0 and p[i]==0 for i in range(2))
assert tv(dict(enumerate(p)),dict(enumerate(q)))==F(1,10)
for b in raw['boundaries']:
 if b['name']=='sharp-product':assert F(b['tv'])==1-F(9,10)**b['n']
 if b['name']=='unmeasured-prefix':assert F(b['observed_prefix_0_tv'])==0 and F(b['joint_tv'])==F(1,2)
 if b['name']=='greedy-flip':assert F(b['probability_tv'])==F(1,500000) and F(b['greedy_output_tv'])==1
 if b['name']=='EOS-absorbing':
  p=joint(b['P'],4);q=joint(b['Q'],4);assert tv(p,q)==F(b['tv']);assert all(v==0 for s,v in {**p,**q}.items() if '10' in s)
# General nonbinary maximal coupling formula, including zero residual.
for p,q in [([F(3,5),F(3,10),F(1,10)],[F(1,5),F(1,2),F(3,10)]),([F(1),F(0),F(0)],[F(0),F(1),F(0)]),([F(1,3)]*3,[F(1,3)]*3)]:
 c=[min(a,b) for a,b in zip(p,q)];a=sum(c)
 mat=[[ (c[i] if i==j else F(0)) + ((p[i]-c[i])*(q[j]-c[j])/(1-a) if a<1 else F(0)) for j in range(3)] for i in range(3)]
 assert [sum(v) for v in mat]==p;assert [sum(mat[i][j] for i in range(3)) for j in range(3)]==q
 assert sum(mat[i][j] for i in range(3) for j in range(3) if i!=j)==1-a
# Frozen producer rerun in isolated verifier directory; original files remain immutable.
T=D/'rerun';T.mkdir(exist_ok=True)
for f in ['verify.py','config.json']:shutil.copyfile(B/f,T/f)
run=subprocess.run([sys.executable,str(T/'verify.py')],capture_output=True,text=True,check=True);(D/'rerun.log').write_text(run.stdout+run.stderr)
assert (T/'raw.json').read_bytes()==(B/'raw.json').read_bytes()
summ=json.loads((B/'summary.json').read_text());rs=json.loads((T/'summary.json').read_text())
for key in ['cases','joint_words','coupling_prefixes','assertions','scope']:assert summ[key]==rs[key]
# Corpus byte integrity and actual retrieval/token rerun.
corpus=json.loads((B/'retrieval-corpus.json').read_text())['files'];actual=sorted(str(p.relative_to(R)) for p in (R/'knowledge/entries').rglob('*') if p.is_file() and p.suffix in ['.json','.md'])
assert sorted(r['path'] for r in corpus)==actual
for ref in corpus:assert sha(R/ref['path'])==ref['sha256']
def cli(*args):return json.loads(subprocess.check_output([sys.executable,'-m','agent_runtime.knowledge','--root','knowledge',*args],cwd=R))
show=cli('show','math.sequence-tv-coupling');tokens=len(tiktoken.get_encoding('cl100k_base').encode(json.dumps(show,ensure_ascii=False)))
assert tokens==json.loads((B/'cost.json').read_text())['body_package_cl100k_base_tokens']==3903
usage=json.loads((B/'knowledge-usage.json').read_text());db=D/'owned-search.sqlite';cli('index','--db',str(db));retrieval=[]
for r in usage['retrieval']:
 res=cli('search',r['input']['query'],'--domain',r['domain'],'--limit','3',*(['--index',str(db)] if r['backend']=='sqlite' else []))
 assert res==r['result'];retrieval.append({'backend':r['backend'],'query':r['input']['query'],'rank1':res['results'][0]['id']})
for p in D.glob('owned-search.sqlite*'):p.unlink()
for r in refs:assert sha(R/r['path'])==r['sha256']
assert sha(B/'manifest.json')==before
out={'status':'pass','cases':count,'joint_words':words,'binary_coupling_prefixes':prefixes,'event_exhaustion':'n<=3','hybrid_adjacent_tv':'equal to true P-prefix expectation on every step','reward':'span11 tight event; constant span0','support_and_coupling':'KL(Q||P) infinity support witness, complement mismatch1 at TV0, ternary maximal tests','producer_raw_rerun_sha256':sha(T/'raw.json'),'corpus_files':len(corpus),'tokens':tokens,'retrieval':retrieval,'manifest_sha256':before,'frozen_unchanged':True}
(D/'check-result.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps(out,ensure_ascii=False))
