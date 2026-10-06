"""Finite table checks, rational probabilities and double log2. Not model A/B."""
from fractions import Fraction as F
from collections import defaultdict
from pathlib import Path
import json,math,time
from agent_runtime.knowledge import KnowledgeStore
start=time.perf_counter();checks=[]
def check(name,condition):
 assert condition,name
 checks.append({'name':name,'passed':True})
def close(a,b):return abs(a-b)<1e-12
def entropy(p):return -sum(float(a)*math.log2(float(a)) for a in p if a)
def kl(p,q):
 if any(a and not b for a,b in zip(p,q)):return math.inf
 return sum(float(a)*math.log2(float(a/b)) for a,b in zip(p,q) if a)
def joint(rows,left,right):
 out=defaultdict(F)
 for x,p in rows:out[(left(x),right(x))]+=p
 return dict(out)
def mi(j):
 a=defaultdict(F);b=defaultdict(F)
 for (u,v),p in j.items():a[u]+=p;b[v]+=p
 return sum(float(p)*math.log2(float(p/(a[u]*b[v]))) for (u,v),p in j.items() if p)
def accuracy(j):
 cols=defaultdict(dict)
 for (target,s),p in j.items():cols[s][target]=p
 return sum(max(col.values()) for col in cols.values())
rows=[((u,v),F(1,4)) for u in [0,1] for v in [0,1]]
Y=lambda x:x[0]^x[1];good=Y;bad=lambda x:x[0];full=lambda x:x
metrics={}
for name,fn in [('full',full),('task_bit',good),('first_bit',bad)]:
 j=joint(rows,Y,fn);metrics[name]={'target_information_bits':mi(j),'optimal_accuracy':float(accuracy(j)),'representation_entropy_bits':entropy([sum(p for (y,s),p in j.items() if s==t) for t in set(s for y,s in j)])}
check('full-task-information',close(metrics['full']['target_information_bits'],1))
check('task-bit-sufficient',close(metrics['task_bit']['target_information_bits'],1) and accuracy(joint(rows,Y,good))==1)
check('first-bit-loses-task',close(metrics['first_bit']['target_information_bits'],0) and accuracy(joint(rows,Y,bad))==F(1,2))
check('equal-one-bit-budget',metrics['task_bit']['representation_entropy_bits']==metrics['first_bit']['representation_entropy_bits']==1)
check('task-shift-reverses',close(mi(joint(rows,bad,good)),0) and close(mi(joint(rows,bad,bad)),1))
# Enumerate posterior equality rather than infer it from accuracy.
def posterior_map(j):
 totals=defaultdict(F)
 for (y,t),p in j.items():totals[t]+=p
 return {t:{y:p/totals[t] for (y,s),p in j.items() if s==t} for t in totals}
post=posterior_map(joint(rows,Y,good))
check('posterior-equality-good',all(post[good(x)].get(Y(x))==1 for x,p in rows))
post_bad=posterior_map(joint(rows,Y,bad))
check('posterior-mismatch-bad',any(post_bad[bad(x)].get(Y(x))!=1 for x,p in rows))
p=[F(2,5),F(1,10),F(1,10),F(2,5)];q=[F(1,4)]*4
K_same_ratio=[[1,0],[0,1],[0,1],[1,0]];K_loss=[[1,0],[1,0],[0,1],[0,1]]
K_noise=[[F(3,4),F(1,4)],[F(1,4),F(3,4)],[F(1,2),F(1,2)],[F(2,3),F(1,3)]]
def process(a,K):return [sum(a[x]*F(K[x][t]) for x in range(len(a))) for t in range(len(K[0]))]
def posterior_gap(p,q,K):
 pt,qt=process(p,K),process(q,K)
 return sum(float(pt[t])*kl([p[x]*F(K[x][t])/pt[t] for x in range(len(p))],[q[x]*F(K[x][t])/qt[t] for x in range(len(q))]) for t in range(len(pt)) if pt[t])
check('same-channel-rows-valid',all(sum(map(F,row))==1 and min(row)>=0 for K in [K_same_ratio,K_loss,K_noise] for row in K))
check('likelihood-group-equality',close(kl(p,q),kl(process(p,K_same_ratio),process(q,K_same_ratio))))
check('merged-evidence-loss',kl(p,q)>0 and kl(process(p,K_loss),process(q,K_loss))==0)
check('stochastic-KL-chain',close(kl(p,q),kl(process(p,K_noise),process(q,K_noise))+posterior_gap(p,q,K_noise)))
check('stochastic-DPI',kl(process(p,K_noise),process(q,K_noise))<=kl(p,q)+1e-12)
check('support-singular-input',math.isinf(kl([F(1),F(0)],[F(0),F(1)])))
check('constant-compression-zero',kl([F(1)],[F(1)])==0)
check('different-channel-counterexample',kl([F(1,2)]*2,[F(1,2)]*2)==0 and math.isinf(kl(process([F(1,2)]*2,[[1,0],[1,0]]),process([F(1,2)]*2,[[0,1],[0,1]]))))
side=[((y,0,y),F(1,2)) for y in [0,1]]
check('side-info-Markov-failure',close(mi(joint(side,lambda x:x[0],lambda x:x[1])),0) and close(mi(joint(side,lambda x:x[0],lambda x:x[2])),1))
# Conditional decoder cross-entropy identity, not measured mutual information.
a=[F(3,4),F(1,4)];b=[F(1,2),F(1,2)]
ce=-sum(float(p)*math.log2(float(q)) for p,q in zip(a,b))
check('NLL-conditional-entropy-plus-mismatch',close(ce,entropy(a)+kl(a,b)))
# A single coarse decision can have equal risk despite changed posterior.
# Y=1 has posterior .6/.8 depending on X, always same MAP action1.
coarse=[((0,0),F(1,5)),((1,0),F(3,10)),((0,1),F(1,10)),((1,1),F(2,5))]
jx=dict(coarse);jt={(0,0):F(3,10),(1,0):F(7,10)}
check('equal-risk-not-posterior-sufficient',accuracy(jx)==accuracy(jt) and mi(jx)>0 and mi(jt)==0)
store=KnowledgeStore('knowledge');refs=store.get('math.data-processing-task-sufficiency')['knowledge_refs'];store.check_refs(refs)
check('versioned-refs-valid',len(refs)==1)
result={'checks':checks,'count':len(checks),'metrics':metrics,'kl_bits':{'input':kl(p,q),'sufficient_group':kl(process(p,K_same_ratio),process(q,K_same_ratio)),'lossy_group':kl(process(p,K_loss),process(q,K_loss)),'stochastic':kl(process(p,K_noise),process(q,K_noise))},'elapsed_seconds':time.perf_counter()-start,'cost':{'model_calls':0,'model_tokens':None,'probability_table_rows':4,'compressed_fixed_width_bits':1,'original_fixed_width_bits':2},'verification':'finite numerical/structure only; exact probabilities, float log2 tolerance1e-12; no formal proof or model A/B','knowledge_root':'knowledge','knowledge_refs':refs}
Path(__file__).with_name('checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':len(checks),'elapsed_seconds':result['elapsed_seconds'],'metrics':metrics}))
