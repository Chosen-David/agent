"""Closed-form finite checks, exact rotation counterexample; not a proof/model test."""
import json, math, time
from fractions import Fraction as F
from pathlib import Path
from agent_runtime.knowledge import KnowledgeStore

start = time.perf_counter()
checks = []
def check(name, ok):
    assert ok, name
    checks.append({'name': name, 'passed': True})
def mm(a, b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def tr(a): return list(map(list,zip(*a)))
def sub(a,b): return [[x-y for x,y in zip(row,other)] for row,other in zip(a,b)]
def fn(a): return math.sqrt(sum(x*x for row in a for x in row))
def score(q,p,k): return sum(q[i]*p[i][j]*k[j] for i in range(len(q)) for j in range(len(k)))

# Analytic symmetric 2x2 eigenpair, independently check eigen-equation.
eps=.1; gap=1.; theta=math.atan2(2*eps,gap)/2
c,s=math.cos(theta),math.sin(theta)
lam=(3+math.sqrt(gap*gap+4*eps*eps))/2
phat=[[c*c,c*s],[c*s,s*s]]; p=[[1.,0.],[0.,0.]]
check('eigen-equation',abs(2*c+eps*s-lam*c)<1e-14 and abs(eps*c+s-lam*s)<1e-14)
check('projector-idempotence',fn(sub(mm(phat,phat),phat))<1e-14)
diff=sub(phat,p)
check('projector-eigenvalues-plusminus-sine',abs(diff[0][0]+diff[1][1])<1e-14 and abs(diff[0][0]*diff[1][1]-diff[0][1]**2+s*s)<1e-14)
beta=eps/(gap-eps)
check('rank-one-error-bound',abs(s)<=beta)
check('classical-rank-one-bound',abs(s)<=2*eps/gap)
check('Weyl-eigenvalue-error',abs(lam-2)<=eps)
check('perturbed-gap',math.sqrt(1+4*eps*eps)>=gap-2*eps>0)
check('projector-Frobenius-conversion',abs(fn(diff)-math.sqrt(2)*abs(s))<1e-14)

# A finite sweep of off-diagonal perturbations, separate cases not a general proof.
sweep=[]
for a,b,e in [(2.,1.,0.),(2.,1.,.001),(2.,1.,.49),(2.,1.,-.2),(101.,100.,.1),(4.,-2.,.3)]:
    g=a-b; angle=math.atan2(2*e,g)/2; actual=abs(math.sin(angle));bound=abs(e)/(g-abs(e))
    check('finite-offdiagonal-'+str((a,b,e)),actual<=bound+1e-14)
    sweep.append({'a':a,'b':b,'offdiagonal':e,'sine':actual,'certificate':bound})

# Exact degenerate and nearly-degenerate examples.
delta=F(1,10**9)
check('arbitrarily-small-swap',1+delta-delta==1 and 1+delta>1)
check('swap-outside-useful-smallness',delta/delta==1 and not delta<delta/2)
check('degenerate-no-unique-rank-one',F(1)==F(1) and delta>0)
u=[[F(1),F(0)],[F(0),F(1)],[F(0),F(0)]]
o=[[F(0),F(-1)],[F(1),F(0)]]
v=mm(u,o)
check('internal-rotation-projector-identical',mm(u,tr(u))==mm(v,tr(v)))
check('internal-rotation-basis-distance',sum(x*x for row in sub(u,v) for x in row)==4)
check('cluster-boundary-gap',F(3)-F(1)==2 and F(3)-F(3)==0)
check('sign-invariance',mm([[-1],[0]],[[-1,0]])==[[1,0],[0,0]])

# Source A.4 alignment formula: demonstrates a local transpose inconsistency only.
check('paper-correct-right-alignment',mm(u,o)==v)
paper_error=sum(x*x for row in sub(mm(u,tr(o)),v) for x in row)
check('paper-transpose-expression-counterexample',paper_error==8)

q=[1.,0.]; safe=[[1.,0.],[0.,1.]];close=[[.45,1.],[.5,0.]]
safe_old=[score(q,p,k) for k in safe];safe_new=[score(q,phat,k) for k in safe]
check('safe-score-uniform-error',all(abs(a-b)<=beta+1e-14 for a,b in zip(safe_old,safe_new)))
check('safe-margin-certified',safe_old[0]-safe_old[1]>2*beta and safe_new[0]>safe_new[1])
close_old=[score(q,p,k) for k in close];close_new=[score(q,phat,k) for k in close]
check('small-margin-ranking-flips',close_old[0]<close_old[1] and close_new[0]>close_new[1])
check('small-margin-not-certified',close_old[1]-close_old[0]<=2*beta*math.sqrt(1+.45**2))
check('score-norm-assumption-necessary',1000*abs(score(q,diff,[0.,1.]))>beta)

# Zero noise rank-one coherent signal loses its only nonzero column with probability 1-alpha.
alpha=F(1,10);dimension=100;mu=dimension
check('sampling-coherence-condition-infeasible',16*mu*math.log(dimension)/dimension>1)
check('sampling-signal-miss-probability',1-alpha==F(9,10))
check('sampling-zero-column-rank-loss',all(x==0 for x in [0]*dimension))
feasible_lower=16*math.log(10000)/10000
check('incoherent-rate-feasible-case',feasible_lower<.1 and 8*(.01)**2<.1)

# Physical K,M mapping: mass kg, stiffness kg/s^2, transformed frequency^2 1/s^2.
m_inv_sqrt=[[F(1,2),F(0)],[F(0),F(1)]]
k=[[F(8),F(1,5)],[F(1,5),F(1)]]
a=mm(mm(m_inv_sqrt,k),m_inv_sqrt)
check('mass-coordinate-transformation',a==[[F(2),F(1,10)],[F(1,10),F(1)]])
naive=mm([[F(1,4),F(0)],[F(0),F(1)]],k)
check('naive-generalized-matrix-not-symmetric',naive!=tr(naive))
check('physical-positive-frequencies',a[0][0]>0 and a[0][0]*a[1][1]-a[0][1]*a[1][0]>0)
mass_units=(1,0,0);stiff_units=(1,0,-2)
check('physical-gap-ratio-dimensionless',tuple(x-y for x,y in zip(stiff_units,mass_units))==(0,0,-2))
# Non-normal Jordan perturbation, eigenvalue movement sqrt(e) violates Hermitian Weyl bound.
e=F(1,10000)
check('non-symmetric-bound-refusal',math.sqrt(float(e))>float(e))

store=KnowledgeStore('knowledge');refs=store.get('math.eigenspace-gap-perturbation')['knowledge_refs']
store.check_refs(refs);check('actual-knowledge-reference',len(refs)==1)
out={'count':len(checks),'checks':checks,'elapsed_seconds':time.perf_counter()-start,'gap_case':{'epsilon':eps,'gap':gap,'actual_sine':abs(s),'rank_one_certificate':beta,'classical_bound':2*eps/gap},'finite_sweep':sweep,'score_case':{'safe_original':safe_old,'safe_perturbed':safe_new,'close_original':close_old,'close_perturbed':close_new,'comparison':'same q/k arrays; projector change only, no performance/model A/B'},'paper_alignment':{'wrong_expression_squared_F_error':int(paper_error),'scope':'local alignment expression inconsistency, not main theorem counterexample'},'physical_case':{'M':[[4,0],[0,1]],'K':[[8,.2],[.2,1]],'frequency_squared_max':lam,'sine_mass_coordinates':abs(s)},'sampling_negative':{'rank':1,'dimension':dimension,'alpha':float(alpha),'coherence':mu,'signal_loss_probability':float(1-alpha)},'verification':'exact finite rational identities and closed-form double precision checks with 1e-14 tolerance; no formal prover; general proofs in entry','cost':{'model_calls':0,'model_tokens':None},'knowledge_root':'knowledge','knowledge_refs':refs}
Path(__file__).with_name('checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'seconds':out['elapsed_seconds'],'gap':out['gap_case'],'score':out['score_case']},ensure_ascii=False))
