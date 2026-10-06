"""Exact finite examples; no formal proof or live model evaluation."""
from fractions import Fraction as F
from pathlib import Path
import json,time
from agent_runtime.knowledge import KnowledgeStore
start=time.perf_counter(); checks=[]
def check(name,condition):
    assert condition,name
    checks.append({'name':name,'passed':True})
q=F(99,100); x=F(0); k=0; tol=F(1,50)
y=q*x+1-q
check('small-step-false-stop',abs(y-x)<tol and abs(y-1)>tol)
check('exact-next-certificate',q*abs(y-x)/(1-q)==abs(y-1))
while abs(x-1)>tol: x=q*x+1-q; k+=1
check('certified-stop-and-predecessor',k==390 and abs(x-1)<=tol and q**(k-1)>tol)
q=F(9,10); x=F(9); eta=F(1,10); y=q*x+1-eta
check('zero-computed-residual-nonzero-error',y==x and abs(x-10)==1)
check('inexact-current-and-next-bound',(abs(x-y)+eta)/(1-q)==1 and (q*abs(x-y)+eta)/(1-q)==1)
x=F(0)
for n in range(1,30):
 y=q*x+1-eta;r=abs(x-y)
 check('inexact-bound-step-'+str(n),abs(y-10)<=(q*r+eta)/(1-q))
 x=y
constant=lambda x:F(7)
check('q-zero-one-step',all(constant(x)==7 and abs(constant(x)-7)==0 for x in [F(-2),F(0),F(10)]))
identity=lambda x:x
check('q-one-no-uniqueness',identity(F(0))==0 and identity(F(1))==1 and F(0)!=F(1))
# Algebraic boundary arguments are also documented; these samples do not prove them.
check('open-domain-no-zero',F(1,2)>0)
check('self-map-failure',F(1,2)+1>1)
A=((F(1,2),F(10)),(F(0),F(1,2)))
def apply(v):return tuple(sum(A[i][j]*v[j] for j in range(2)) for i in range(2))
def inf(v):return max(map(abs,v))
def weighted(v):return max(abs(v[0])/40,abs(v[1]))
e=(F(0),F(1)); ne=apply(e)
check('nonnormal-transient-growth',inf(ne)==10 and inf(e)==1)
check('weighted-induced-row-bound',max(F(1,2)+F(10,40),F(1,2))==F(3,4))
check('weighted-step',weighted(ne)<=F(3,4)*weighted(e))
check('norm-conversion',inf(ne)<=40*weighted(ne))
q=F(1,2); x=F(0); target=1/(1+q)
for n in range(12):
 y=1-q*x;r=abs(y-x)
 check('implicit-euler-certificate-'+str(n),abs(y-target)<=q*r/(1-q))
 x=y
q=F(2); x=F(0); target=F(1,3); errors=[]
for n in range(5): x=1-q*x; errors.append(abs(x-target))
check('stable-integrator-divergent-solver',target<1 and all(b==2*a for a,b in zip(errors,errors[1:])))
store=KnowledgeStore('knowledge'); ref=store.get('math.contraction-residual-certificate')
result={'verification_level':'exact finite numerical/structure checks; derivation-reviewed; no formal proof or model A/B','checks':checks,'count':len(checks),'elapsed_seconds':time.perf_counter()-start,'model_calls':0,'model_tokens':None,'knowledge_refs':ref['knowledge_refs'],'paired_synthetic_stop':{'same_map':'.99x+.01','same_start':0,'same_tolerance':.02,'naive_steps':1,'naive_error':.99,'certified_steps':k,'certified_error':float(F(99,100)**k),'oracle_evaluations':[1,k],'claim':'finite solver comparison, not Agent A/B'},'physical_transfer':{'equation':'y_prime=-kappa*y','dimensionless_parameter':'h*kappa','convergent_solver_q':.5,'divergent_solver_q':2,'stable_integrator_amplification_at_q2':float(F(1,3))}}
Path(__file__).with_name('checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'seconds':result['elapsed_seconds'],'certified_steps':k}))
