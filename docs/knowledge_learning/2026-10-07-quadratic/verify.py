"""Finite/public development checks, not a formal proof or model performance test."""
from pathlib import Path
from fractions import Fraction as F
import math,json,time,itertools
import numpy as np
D=Path(__file__).resolve().parent;start=time.perf_counter();checks=[]
def check(name,ok,detail=None):
 assert ok,name
 checks.append(dict(name=name,passed=True,detail=detail))
# Exact fourth Gaussian moments on a rational covariance, independently expanded.
L=[[F(1),F(0),F(0)],[F(1,2),F(1),F(0)],[F(0),F(1,3),F(1)]]
C=[[sum(L[i][k]*L[j][k]for k in range(3))for j in range(3)]for i in range(3)]
A=[[F(2),F(1),F(0)],[F(1),F(2),F(0)],[F(0),F(0),F(1)]]
a=sum(A[i][j]*C[i][j]for i,j in itertools.product(range(3),repeat=2))
e2=sum(A[i][j]*A[k][l]*(C[i][j]*C[k][l]+C[i][k]*C[j][l]+C[i][l]*C[j][k])for i,j,k,l in itertools.product(range(3),repeat=4))
f2=sum(A[i][j]*C[j][k]*A[k][l]*C[l][i]for i,j,k,l in itertools.product(range(3),repeat=4))
check('exact-Wick-energy-variance',e2-a*a==2*f2,str(e2-a*a))
for ev in [[1],[1,1,1],[2,.5,.5],[1.5,1.5,0],[0,0]]:
 v=np.array(ev);aa=v.sum();ff=float(v@v);ll=v.max()
 if not ff:check('zero-energy',aa==0);continue
 for t in [.1,1,3,10]:
  s=math.sqrt(t)/(math.sqrt(ff)+2*ll*math.sqrt(t));log=sum(-s*x-.5*math.log1p(-2*s*x)for x in ev);major=s*s*ff/(1-2*ll*s)
  check(f'mgf-upper-{ev}-{t}',log<=major+1e-12)
  lo=sum(s*x-.5*math.log1p(2*s*x)for x in ev);check(f'mgf-lower-{ev}-{t}',lo<=s*s*ff+1e-12)
# Trace and operator clocks; same quadratic variance need not imply same tail bound.
Tp=np.full((3,3),.5);np.fill_diagonal(Tp,1);Tm=np.full((3,3),-.5);np.fill_diagonal(Tm,1)
check('same-variance-different-tail-clock',np.trace(Tp@Tp)==np.trace(Tm@Tm)==4.5 and np.linalg.norm(Tp,2)>np.linalg.norm(Tm,2))
check('iid-clocks',16**2/np.trace(np.eye(16))==16)
check('copy-clocks',16**2/np.trace(np.ones((16,16))@np.ones((16,16)))==1)
th=2+2*math.sqrt(2*10)+2*10;p=math.erfc(math.sqrt(th/4))
check('Gaussian-marginals-not-joint-tail',p>math.exp(-10),dict(actual_tail=p,invalid_bound=math.exp(-10)))
check('Gaussian-marginals-not-joint-variance',8!=4)
check('known-mean-required',np.linalg.norm(np.outer([1,0],[1,0]),2)==1)
# Fixed seeded simulation using a separate direct AR recurrence rather than sqrt(T).
rng=np.random.default_rng(2026100717);n=64;d=3;reps=12000;phi=.6;sigma=np.array([3.,1.,.3]);x=np.empty((reps,n,d));x[:,0]=rng.normal(size=(reps,d))*np.sqrt(sigma)
for j in range(1,n):x[:,j]=phi*x[:,j-1]+rng.normal(size=(reps,d))*np.sqrt((1-phi*phi)*sigma)
S=np.einsum('bni,bnj->bij',x,x)/n;T=phi**abs(np.arange(n)[:,None]-np.arange(n));f=float(np.trace(T@T));l=float(np.linalg.norm(T,2));delta=.05;t=math.log(2*9**d/delta);bound=2*sigma.max()*(2*math.sqrt(f*t)/n+2*l*t/n)
expected=2*sigma[0]**2*f/n**2;observed=float(S[:,0,0].var(ddof=1));check('controlled-AR-direction-variance',abs(observed/expected-1)<.05,dict(predicted=expected,observed=observed))
check('controlled-AR-unbiased',abs(float(S[:,0,0].mean())/sigma[0]-1)<.02)
errors=np.linalg.norm(S-np.diag(sigma),ord=2,axis=(1,2));check('finite-model-coverage',float(np.mean(errors>bound))<delta,dict(bound=bound,empirical_exceedance=float(np.mean(errors>bound)),scope='finite simulation; does not prove probability bound'))
check('bound-can-be-vacuous',bound>sigma.max(),bound)
# Larger controlled trajectory offers a usable sufficient gap diagnostic with true constants.
n2=8192;phi2=.2;tt2=n2+2*sum((n2-h)*phi2**(2*h)for h in range(1,n2));op_upper=(1+abs(phi2))/(1-abs(phi2));eps=2*3*(2*math.sqrt(tt2*t)/n2+2*op_upper*t/n2)
y=np.empty((n2,d));y[0]=rng.normal(size=d)*np.sqrt(sigma)
for j in range(1,n2):y[j]=phi2*y[j-1]+rng.normal(size=d)*np.sqrt((1-phi2*phi2)*sigma)
Sh=y.T@y/n2;err=float(np.linalg.norm(Sh-np.diag(sigma),2));w,V=np.linalg.eigh(Sh);P=np.outer(V[:,-1],V[:,-1]);perr=float(np.linalg.norm(P-np.diag([1,0,0]),2))
check('controlled-gap-premise',eps<1,dict(error_bound=eps,true_gap=2))
check('controlled-observed-matrix-error',err<=eps,err)
check('controlled-projector-certificate',perr<=eps/(2-eps),dict(error=perr,certificate=eps/(2-eps)))
# Fixed direction versus adaptive selection and units/noise amplification boundaries.
z=rng.normal(size=100);Q=float(z@z);check('same-data-rank-one-refusal',Q>1+2*math.sqrt(10)+20,Q)
check('voltage-units',np.isclose(4**2*f,16*f))
E=np.diag([1.,2.]);Tinvsqrt=np.diag([10.,1.]);check('whitening-noise-amplification',np.linalg.norm(Tinvsqrt@E,'fro')>np.linalg.norm(E,'fro'))
out=dict(count=len(checks),passed=len(checks),seconds=time.perf_counter()-start,numpy=np.__version__,seed=2026100717,checks=checks,scope='finite exact/float and controlled synthetic recurrence; no general/formal proof, unused model tests, physical or GPU experiment')
(D/'checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print({k:out[k]for k in ['count','passed','seconds']})
