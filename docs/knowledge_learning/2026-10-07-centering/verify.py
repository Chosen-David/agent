"""Public development checks; finite identities are not a general or formal proof."""
from fractions import Fraction as F
from pathlib import Path
import itertools,json,time,platform
import numpy as np
start=time.perf_counter();rows=[]
def check(name,value,**evidence):
 assert bool(value),name
 rows.append(dict(name=name,passed=True,**evidence))
def outer(x,y):return np.outer(x,y)
def state(xs):
 if not xs:return None
 x=np.array(xs,dtype=object);n=len(x);m=sum(x)/n;s=sum([outer(v-m,v-m)for v in x]);return n,m,s
def merge(a,b):
 if a is None:return b
 if b is None:return a
 na,ma,sa=a;nb,mb,sb=b;n=na+nb;delta=mb-ma
 return n,ma+F(nb,n)*delta,sa+sb+F(na*nb,n)*outer(delta,delta)
def same(a,b):return a[0]==b[0]and np.array_equal(a[1],b[1])and np.array_equal(a[2],b[2])
xs=[tuple(map(F,x))for x in [(0,2),(2,0),(5,-1),(-1,4),(7,3)]];truth=state(xs)
for split in range(1,5):check('exact disjoint merge '+str(split),same(merge(state(xs[:split]),state(xs[split:])),truth))
a,b,c=state(xs[:1]),state(xs[1:3]),state(xs[3:]);check('exact associativity',same(merge(merge(a,b),c),merge(a,merge(b,c))));check('exact commutativity',same(merge(a,b),merge(b,a)));check('empty identity',same(merge(None,a),a));s=None
for i,x in enumerate(xs):
 s=merge(s,state([x]));check('singleton online update '+str(i),same(s,state(xs[:i+1])))
shift=[F(10**9),F(-10**9)];st=state([np.array(x)+shift for x in xs]);check('translation scatter invariance',np.array_equal(st[2],truth[2]))
n,m,S=truth;G=sum(outer(x,x)for x in xs);check('Gram identity',np.array_equal(S,G-n*outer(m,m)))
v=merge(state([[F(0)]]),state([[F(2)]]));check('between-group correction',v[2][0,0]==2);check('naive within-scatter average fails',state([[F(0)]])[2][0,0]+state([[F(2)]])[2][0,0]!=v[2][0,0]);check('one point scatter zero',a[2].sum()==0);check('unbiased denominator undefined at n1',a[0]-1==0)
# Exact expectation over all 2^3 independent equiprobable scalar observations.
U=F(0);Cn=F(0)
for draw in itertools.product([F(0),F(2)],repeat=3):
 z=state([[x]for x in draw]);U+=z[2][0,0]/2/8;Cn+=z[2][0,0]/3/8
check('iid unbiased covariance exact expectation',U==1);check('n denominator bias exact expectation',Cn==F(2,3));check('duplicate stream zero does not estimate population',state([[F(2)]]*20)[2][0,0]==0 and U==1)
# Deterministic norm bridge, no probability inference from a single sample.
mu=np.array([2.,-3.]);C=np.array([[2.,.3],[.3,1.]]);M=C+outer(mu,mu);mh=mu+np.array([.03,-.04]);Mh=M+np.array([[.02,-.01],[-.01,.04]]);Ch=Mh-outer(mh,mh);eta=np.linalg.norm(mh-mu);ep=np.linalg.norm(Mh-M,2);bound=ep+(np.linalg.norm(mh)+np.linalg.norm(mu))*eta
check('mean/second-moment error bridge',np.linalg.norm(Ch-C,2)<=bound,error=float(np.linalg.norm(Ch-C,2)),bound=float(bound))
x=np.array([[1e9+v,1e9-v]for v in [-2,-1,0,1,2]],dtype=np.float64);mean=x.mean(0);center=(x-mean).T@(x-mean);gram=x.T@x-len(x)*outer(mean,mean);online=None
for val in x:
 if online is None:online=(1,val.copy(),np.zeros((2,2)))
 else:
  n,mm,ss=online;delta=val-mm;online=(n+1,mm+delta/(n+1),ss+n/(n+1)*outer(delta,delta))
ge=float(np.linalg.norm(gram-center,2));we=float(np.linalg.norm(online[2]-center,2));check('large offset Gram loses accuracy',ge>we,gram_error=ge,online_error=we);check('float64 centered recurrence matches reference',we<1e-5);check('float32 input information already lost',np.array_equal(x.astype(np.float32),np.full_like(x.astype(np.float32),1e9)))
# Units: same affine scale sends scatter to scale^2 scatter.
scale=F(9,5);scaled=state([np.array(x)*scale+F(32)for x in xs]);check('sensor affine scale square',np.array_equal(scaled[2],truth[2]*scale**2))
check('duplicated partition changes multiset',merge(a,a)[0]==2*a[0]);check('wrong-frame direct merge fails',not np.array_equal(merge(a,state([(-v[1],v[0])for v in xs[1:]]))[2],truth[2]))
e=np.array([[1.,-1.],[-1.,1.]]);check('max to operator norm dimension factor',np.linalg.norm(e,2)==2*np.abs(e).max())
# iid Bernoulli {0,2}, population covariance 1. Full-batch U equals its own reference.
vals=[state([[v]for v in draw])[2][0,0]for draw in itertools.product([F(0),F(2)],repeat=2)]
coverage=sum(v==1 for v in vals)/len(vals)
check('estimated reference does not certify population',coverage==0,population_covariance=1,possible_sample_covariances=list(map(float,sorted(set(vals)))),zero_reference_residual_coverage=coverage)
raw=np.zeros((4096,8),dtype=np.float64);stats=8+8*8+8*8*8;check('binary statistic payload count',raw.nbytes==262144 and stats==584,raw_bytes=raw.nbytes,statistic_bytes=stats,scope='array payload only; excludes metadata/transport/serialization, no Agent measurement')
result=dict(scope='public exact finite and float examples; no formal proof, unused holdout, model or physical experiment',python=platform.python_version(),numpy=np.__version__,checks=len(rows),passed=len(rows),seconds=time.perf_counter()-start,details=rows);Path(__file__).with_name('checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print({k:result[k]for k in ['checks','passed','seconds']})
