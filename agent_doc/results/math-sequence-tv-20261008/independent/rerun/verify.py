from pathlib import Path
from fractions import Fraction as F
from itertools import product
import json,random,time,sys,platform
D=Path(__file__).parent;cfg=json.loads((D/'config.json').read_text());rng=random.Random(cfg['seed']);start=time.perf_counter();rows=[];assertions=0

def joint(k,n):
 out={}
 for word in product('01',repeat=n):
  s=''.join(word);v=F(1)
  for t,a in enumerate(s):p=F(k[s[:t]]);v*=p if a=='1' else 1-p
  out[s]=v
 return out

def tv(p,q):return sum(abs(p[s]-q[s]) for s in p)/2
for i in range(cfg['cases']):
 n=i%6;P={};Q={};eps=[];mu=[];couplingchecks=0
 for t in range(n):
  ds=[];expected=F(0)
  for word in product('01',repeat=t):
   h=''.join(word);p=F(rng.randint(0,10),10);q=F(rng.randint(0,10),10);P[h]=str(p);Q[h]=str(q);p0=[1-p,p];q0=[1-q,q];common=list(map(min,p0,q0));alpha=sum(common);mat=[[F(0),F(0)],[F(0),F(0)]]
   for a in range(2):
    for b in range(2):mat[a][b]=(common[a] if a==b else F(0))+((p0[a]-common[a])*(q0[b]-common[b])/(1-alpha) if alpha<1 else F(0))
   assert [sum(row) for row in mat]==p0;assert [sum(mat[a][b] for a in range(2)) for b in range(2)]==q0;assert mat[0][1]+mat[1][0]==abs(p-q);assertions+=3;couplingchecks+=1
   prob=F(1)
   for j,a in enumerate(h):v=F(P[h[:j]]);prob*=v if a=='1' else 1-v
   d=abs(p-q);ds.append(d);expected+=prob*d
  eps.append(max(ds));mu.append(expected)
 pjoint=joint(P,n);qjoint=joint(Q,n);distance=tv(pjoint,qjoint);survival=F(1)
 for e in eps:survival*=1-e
 bound=1-survival;meanbound=min(F(1),sum(mu));identity=sum(pjoint[s]*max(F(0),1-qjoint[s]/pjoint[s]) for s in pjoint if pjoint[s]>0);rewardgap=abs(sum((F(s.count('1'),n) if n else F(0))*(pjoint[s]-qjoint[s]) for s in pjoint))
 assert sum(pjoint.values())==sum(qjoint.values())==1;assert distance<=bound<=min(F(1),sum(eps));assert distance<=meanbound;assert distance==identity;assert rewardgap<=distance;assertions+=5
 rows.append({'case':i,'n':n,'P':P,'Q':Q,'pjoint':{s:str(v) for s,v in pjoint.items()},'qjoint':{s:str(v) for s,v in qjoint.items()},'tv':str(distance),'epsilon':list(map(str,eps)),'P_prefix_mean':list(map(str,mu)),'product_bound':str(bound),'mean_bound':str(meanbound),'ratio_identity':str(identity),'reward_gap':str(rewardgap),'coupling_prefixes':couplingchecks})
# Explicit boundary kernels, exact event gaps; no sampled-model refusal claims.
boundaries=[]
for n in [0,1,2,4]:
 e=F(1,10);p={};q={}
 for t in range(n):
  for w in product('01',repeat=t):h=''.join(w);p[h]='0';q[h]=str(e)
 d=tv(joint(p,n),joint(q,n));assert d==1-(1-e)**n;assertions+=1;boundaries.append({'name':'sharp-product','n':n,'tv':str(d)})
p={'':'1/2','0':'0','1':'0'};q={'':'1/2','0':'0','1':'1'};d=tv(joint(p,2),joint(q,2));assert d==F(1,2);assertions+=1;boundaries.append({'name':'unmeasured-prefix','observed_prefix_0_tv':'0','joint_tv':str(d)})
e=F(1,1000000);d=tv({'0':F(1,2)+e,'1':F(1,2)-e},{'0':F(1,2)-e,'1':F(1,2)+e});assert d==2*e;assertions+=1;boundaries.append({'name':'greedy-flip','probability_tv':str(d),'greedy_output_tv':'1'})
# EOS=1 is absorbing. Kernels at every prefix containing1 deterministic1.
p={};q={}
for t in range(4):
 for w in product('01',repeat=t):h=''.join(w);p[h]='1' if '1' in h else '1/2';q[h]='1' if '1' in h else '3/5'
P=joint(p,4);Q=joint(q,4);assert all(v==0 for s,v in P.items() if '10' in s);assertions+=1;boundaries.append({'name':'EOS-absorbing','tv':str(tv(P,Q)),'P':p,'Q':q})
raw={'cases':rows,'boundaries':boundaries};(D/'raw.json').write_text(json.dumps(raw,separators=(',',':'))+'\n');(D/'summary.json').write_text(json.dumps({'cases':len(rows),'joint_words':sum(len(r['pjoint']) for r in rows),'coupling_prefixes':sum(r['coupling_prefixes'] for r in rows),'assertions':assertions,'elapsed_seconds':time.perf_counter()-start,'scope':cfg['scope']},indent=2)+'\n');(D/'environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'arithmetic':'Fraction exact finite binary trees','model_calls':0,'GPU_calls':0,'formal_checks':0},indent=2)+'\n')
