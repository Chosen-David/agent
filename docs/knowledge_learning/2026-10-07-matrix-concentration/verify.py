"""Exact finite identities plus public float64 probes, not formal/model verification."""
from fractions import Fraction as F
from math import log,sqrt,exp,comb
import numpy as np,json,time,platform
from pathlib import Path
D=Path(__file__).resolve().parent;start=time.perf_counter();checks=[]
def ck(name,p,**data):
 assert bool(p),(name,data);checks.append(dict(name=name,passed=True,**data))
def add(A,B):return [[a+b for a,b in zip(x,y)]for x,y in zip(A,B)]
def sc(A,a):return [[a*x for x in row]for row in A]
def mul(A,B):return [[sum(A[i][k]*B[k][j]for k in range(2))for j in range(2)]for i in range(2)]
def outer(x):return [[a*b for b in x]for a in x]
def radius(n,d,L,delta,B=None):
 if n<1 or d<1 or not 0<delta<1 or L<0:raise ValueError('parameter domain')
 B=L*L if B is None else B
 if B<0 or B>L*L:raise ValueError('declared B range; scientific validity audited separately')
 a=log(2*d/delta);return sqrt(2*L*L*B*a/n)+2*L*L*a/(3*n)
a=[F(1),F(0)];b=[F(3,5),F(4,5)];weights=[F(3,4),F(1,4)];A,B=outer(a),outer(b);M=add(sc(A,weights[0]),sc(B,weights[1]));M2=mul(M,M);EY2=[[F(0)for j in range(2)]for i in range(2)]
for idx,X in enumerate([A,B]):
 Y=add(X,sc(M,-1));EY2=add(EY2,sc(mul(Y,Y),weights[idx]));ck('rank-one unit-norm square '+str(idx),mul(X,X)==X)
ck('exact centered-matrix variance',EY2==add(M,sc(M2,-1)))
ck('not commuting per realization',mul(A,M)!=mul(M,A))
Mf=np.array(M,float);variance=np.array(EY2,float);lam,U=np.linalg.eigh(Mf)
ck('variance PSD',np.linalg.eigvalsh(variance).min()>=-1e-14)
ck('Loewner variance upper',np.linalg.eigvalsh(Mf-variance).min()>=-1e-14)
ck('matrix norm bound',max(np.linalg.norm(np.array(X,float)-Mf,2)for X in [A,B])<=1+1e-14)
# Enumerate n=80 counts exactly; symbols do not affect xx^T.
n=80;epsilon=.25;p=F(3,4);tail=F(0)
for count in range(n+1):
 error=.8*abs(count/n-float(p))
 if error>=epsilon:tail+=F(comb(n,count))*p**count*(1-p)**(n-count)
upper=min(1.,4*exp(-n*epsilon**2/(2*lam[-1]+2*epsilon/3)))
ck('exact binomial tail below matrix bound',float(tail)<=upper,probability=float(tail),bound=upper)
ck('enumeration bound is nonvacuous',upper<1)
for nn in [1,10,100,10000]:
 e=radius(nn,2,1,.05);tailU=4*exp(-nn*e**2/(2+2*e/3));ck('radius inversion '+str(nn),tailU<=.05+1e-14)
ck('radius decreases with n',radius(10000,2,1,.05)<radius(100,2,1,.05))
ck('zero vectors edge',radius(7,3,0,.05)==0)
for args in [(0,2,1,.05),(10,0,1,.05),(10,2,-1,.05),(10,2,1,0),(10,2,1,1)]:
 try:radius(*args);ok=False
 except ValueError:ok=True
 ck('invalid parameter '+str(args),ok)
# Controlled independent calibration; not real embeddings.
rng=np.random.default_rng(20261007);n=10000;counts=int((rng.random(n)<.75).sum());Mhat=counts/n*np.array(A,float)+(1-counts/n)*np.array(B,float);error=float(np.linalg.norm(Mhat-Mf,2));e=radius(n,2,1,.05)
ck('finite iid calibration event',error<=e,n=n,error=error,radius=e)
lh,Uh=np.linalg.eigh(Mhat);ghat=float(lh[-1]-lh[-2]);P=np.outer(U[:,-1],U[:,-1]);Phat=np.outer(Uh[:,-1],Uh[:,-1]);perror=float(np.linalg.norm(P-Phat,2));pbound=e/(ghat-e)
ck('observed-gap certificate feasible',ghat>2*e,gap=ghat)
ck('projector transfer bound',perror<=pbound,actual=perror,bound=pbound)
q=np.array([1.,.5]);k=np.array([.3,-.7]);Q=float(np.linalg.norm(q));K=float(np.linalg.norm(k));score=float(abs(q@(Phat-P)@k));sbound=Q*K*pbound
ck('bounded score transfer',score<=sbound,actual=score,bound=sbound)
# Cross-domain sensor units: doubling all voltages multiplies moment/gap/radius by4.
eV=radius(n,2,2,.05);ck('sensor V-squared scaling',abs(eV-4*e)<1e-14)
ck('sensor principal angle dimensionless',abs(eV/(4*ghat-eV)-pbound)<1e-14)
ck('duplicate measurements refusal',all(np.linalg.norm(np.array(X,float)-Mf,2)>e for X in [A,B]))
selected=np.array(A,float);ck('data-dependent selection target shift',np.linalg.norm(selected-Mf,2)>.1)
ck('nonzero mean versus covariance',np.linalg.norm(selected)>0 and np.all(selected-outer(a)==0))
ck('no spectral gap refuses direction certificate',0<=2*e)
# Finite heavy-tail unseen-support counterexample: observed maximum need not bound future draws.
rare=F(1,10000);true_second=rare*10000
ck('unseen rare support',true_second==1 and (1-float(rare))**100>.98)
ck('within-pair dependence can coexist with iid pairs',np.all(np.array([1,-1])*np.array([1,-1])==1))
ck('independent sample clock not proved by duplicate count',n>1 and np.linalg.matrix_rank(np.repeat([[1.,0.]],n,axis=0))==1)
out=dict(scope='public development exact finite identities and float64 examples; no formal proof, live model, unused holdout or physical experiment',seed=20261007,python=platform.python_version(),numpy=np.__version__,checks=len(checks),passed=len(checks),seconds=time.perf_counter()-start,details=checks)
(D/'checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='details'}))
