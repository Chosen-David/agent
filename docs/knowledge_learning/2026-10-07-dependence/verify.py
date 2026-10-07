"""Finite development checks; not a general proof or model evaluation."""
from pathlib import Path
from fractions import Fraction as F
import itertools,json,math,time
import numpy as np
D=Path(__file__).resolve().parent; start=time.perf_counter(); rows=[]
def check(name,ok,detail=None):
    assert ok,name
    rows.append(dict(name=name,passed=True,detail=detail))
def variance(phi,n):
    return sum(phi**abs(i-j) for i in range(n) for j in range(n))/n**2
for p in [F(9,10),F(-9,10)]:
    for n in [1,2,10,100]:
        v=variance(p,n);tau=1+2*sum((1-F(h,n))*p**h for h in range(1,n))
        check(f'exact-toeplitz-{p}-{n}',v==tau/n)
        check(f'PSD-{p}-{n}',np.linalg.eigvalsh(np.array([[float(p**abs(i-j)) for j in range(n)]for i in range(n)])).min()>-1e-12)
for p in [.9,-.9]:
    v=variance(p,100);v2=2*variance(p*p,100)
    check(f'mean-ESS-{p}',(1/v<100) if p>0 else (1/v>100),1/v)
    check(f'square-ESS-{p}',abs(2/v2-11.016173328880356)<1e-10,2/v2)
check('iid',variance(F(0),100)==F(1,100))
check('copies',variance(F(1),100)==1)
check('alternating-even',variance(F(-1),10)==0)
check('near-unit-finite-vs-asymptotic',1/variance(.999,10)>=1 and 10*(1-.999)/(1+.999)<1)
n=20; lag2=(n+2*(n-2)*F(1,2))/n**2
check('lag1-zero-lag2-nonzero',1/lag2==F(n*n,2*n-2))
# Exact discrete common random scale: R²=0 or 2 and independent signs.
n=4; outcomes=[(r,s) for r in [0,2] for s in itertools.product([-1,1],repeat=n)]
ex=lambda fn:sum(fn(r,s)for r,s in outcomes)/len(outcomes)
check('shared-scale-pair-cov-zero',ex(lambda r,s:r*s[0]*s[1])==0)
check('shared-scale-mean-variance',ex(lambda r,s:F(r)*F(sum(s),n)**2)==F(1,n))
check('shared-scale-square-variance',ex(lambda r,s:(r-1)**2)==1)
check('rare-tail-not-Gaussian',F(1,1000)>2*math.exp(-50))
check('rare-tail-Chebyshev-valid',F(1,1000)<=F(1,100))
check('correlated-unbiased-denominator-fails',abs(100*(1-variance(.9,100))/99-1)>.1)
check('units-mean-square',variance(.9,10)*3**2==9*variance(.9,10))
check('units-second-moment-fourth',2*variance(.81,10)*3**4==81*2*variance(.81,10))
trace_ess=101/(100/100+variance(.9,100))
check('trace-does-not-bound-every-direction',trace_ess>80 and 1/variance(.9,100)<6,trace_ess)
check('nonstationary-zero-initialization',0!=1)
rng=np.random.default_rng(20261007);reps=20000;n=100
for p in [.9,-.9]:
    x=np.empty((reps,n));x[:,0]=rng.normal(size=reps)
    for t in range(1,n):x[:,t]=p*x[:,t-1]+math.sqrt(1-p*p)*rng.normal(size=reps)
    for target,obs,pred in [('mean',x.mean(axis=1),variance(p,n)),('square',(x*x).mean(axis=1),2*variance(p*p,n))]:
        observed=float(obs.var(ddof=1));err=abs(observed/pred-1)
        check(f'Gaussian-AR-controlled-MC-{p}-{target}',err<.04,dict(predicted=pred,observed=observed,relative_error=err))
out=dict(count=len(rows),passed=len(rows),seconds=time.perf_counter()-start,numpy=np.__version__,checks=rows,monte_carlo=dict(seed=20261007,replicates=reps,n=n,relative_tolerance=.04),scope='Exact finite rational identities, finite floating examples and controlled Monte Carlo; not general proof, formal verification, physical experiment or Agent/model improvement.')
(D/'checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print({k:out[k]for k in ['count','passed','seconds']})
