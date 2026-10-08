"""Public development checks for a declared supported product-law objective."""
from fractions import Fraction as F
from pathlib import Path
import itertools, json, time, math
import numpy as np
BASE=Path(__file__).resolve().parent

def scalar(v): return F(str(v))
def score(q,H,k): return sum((q[i]*H[i][j]*k[j] for i in range(len(q)) for j in range(len(k))),F())
def states(amplitudes): return [tuple(F(s)*F(a) for s,a in zip(signs,amplitudes)) for signs in itertools.product([-1,1],repeat=len(amplitudes))]
def exact_risk(qs,ks,E): return sum((score(q,E,k)**2 for q in qs for k in ks),F())/(len(qs)*len(ks))
def moment(vs): return [[sum((v[i]*v[j] for v in vs),F())/len(vs) for j in range(len(vs[0]))] for i in range(len(vs[0]))]
def trace_risk(E,S,T):
 return sum((E[i][j]*E[a][b]*S[i][a]*T[j][b] for i in range(len(E)) for a in range(len(E)) for j in range(len(E[0])) for b in range(len(E[0]))),F())
def encoded(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,(np.integer,np.floating)):return x.item()
 if isinstance(x,dict):return {k:encoded(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [encoded(v) for v in x]
 return x

def solve(U,a,V,b,H,r):
 """Numerical prototype with declared orthonormal support bases, not rank detection."""
 if any(np.iscomplexobj(x) for x in [U,a,V,b,H]):raise ValueError('real inputs required')
 U,a,V,b,H=[np.asarray(x,dtype=float) for x in [U,a,V,b,H]]
 if H.ndim!=2 or U.ndim!=2 or V.ndim!=2 or a.ndim!=1 or b.ndim!=1:raise ValueError('shapes')
 m,n=H.shape
 if U.shape!=(m,len(a)) or V.shape!=(n,len(b)):raise ValueError('support dimensions')
 if any(not np.all(np.isfinite(x)) for x in [U,a,V,b,H]):raise ValueError('finite')
 if type(r) is not int or not 0<=r<=min(m,n):raise ValueError('rank')
 if np.any(a<=0) or np.any(b<=0):raise ValueError('strictly positive declared support scales')
 if not np.allclose(U.T@U,np.eye(len(a)),atol=1e-10,rtol=0) or not np.allclose(V.T@V,np.eye(len(b)),atol=1e-10,rtol=0):raise ValueError('orthonormal support')
 # Range checks reject unsupported floating-point outcomes, not prove accuracy.
 def finite(x,label):
  if not np.all(np.isfinite(x)):raise ValueError('nonfinite '+label)
 try:
  with np.errstate(over='raise',invalid='raise',divide='raise'):
   finite(1/a,'reciprocal q scale');finite(1/b,'reciprocal k scale')
   core=U.T@H@V;finite(core,'restricted matrix')
   C=a[:,None]*core*b[None,:];finite(C,'weighted matrix')
   W,s,Z=np.linalg.svd(C,full_matrices=False)
   for x,label in [(W,'left SVD'),(s,'singular values'),(Z,'right SVD')]:finite(x,label)
   count=min(r,len(s));Cr=(W[:,:count]*s[:count])@Z[:count,:];finite(Cr,'truncated matrix')
   M=U@((Cr/a[:,None])/b[None,:])@V.T;finite(M,'lift')
   tail=float(np.sum(s[count:]**2));finite(tail,'tail square')
 except (FloatingPointError,np.linalg.LinAlgError) as e:
  raise ValueError('numerical range/decomposition failure: '+str(e)) from e
 return {'C':C,'Cr':Cr,'M':M,'s':s,'tail':tail}

def main():
 start=time.perf_counter(); exact=[]; floated=[]
 patterns=[([0,1,2],[3,0,1]),([1,0,0],[0,2,0]),([0,0,0],[1,2,3]),([1,1,0],[1,1,0]),([1,2,3],[3,2,1]),([0,2,0],[0,3,0])]
 for pi,(qa,ka) in enumerate(patterns):
  qs,ks=states(qa),states(ka);S,T=moment(qs),moment(ks)
  for hi,h in enumerate([[1,2,3],[3,-1,0],[0,0,0]]):
   H=[[F(h[i]) if i==j else F() for j in range(3)] for i in range(3)]
   weights=[F(qa[i]**2*ka[i]**2*h[i]**2) for i in range(3)]
   order=sorted(range(3),key=lambda i:(-weights[i],i))
   for r in range(4):
    chosen=set(order[:r]);M=[[H[i][j] if i==j and i in chosen and qa[i]*ka[i]!=0 else F() for j in range(3)] for i in range(3)]
    E=[[H[i][j]-M[i][j] for j in range(3)] for i in range(3)]
    risk=exact_risk(qs,ks,E);target=sum((weights[i] for i in order[r:]),F());assert risk==trace_risk(E,S,T)==target
    # Non-diagonal rank-one trial checks the probability trace identity independently.
    A=[F(1),F(-2),F(3)];B=[F(2),F(1),F(-1)];trial=[[H[i][j]-A[i]*B[j] for j in range(3)] for i in range(3)]
    tr=exact_risk(qs,ks,trial);assert tr==trace_risk(trial,S,T)
    if r>=1:assert tr>=target
    exact.append({'id':f'e{pi}-{hi}-{r}','q_amplitudes':qa,'k_amplitudes':ka,'H':H,'r':r,'M':M,'exact_risk':risk,'tail_target':target,'trial_risk':tr})
 rng=np.random.default_rng(20261008)
 for case in range(48):
  m,n=4,5;p,q=case%5,(case//5)%6
  U=np.linalg.qr(rng.normal(size=(m,m)))[0][:,:p];V=np.linalg.qr(rng.normal(size=(n,n)))[0][:,:q]
  a=np.arange(1,p+1,dtype=float);b=np.arange(1,q+1,dtype=float);H=rng.normal(size=(m,n));r=case%3
  out=solve(U,a,V,b,H,r);M=out['M'];C=out['C'];Cr=out['Cr'];L=(U*a)@U.T;R=(V*b)@V.T
  loss=float(np.linalg.norm(L@(H-M)@R,'fro')**2);lift_error=float(np.linalg.norm(L@M@R-U@Cr@V.T,'fro'))
  assert abs(loss-out['tail'])<=1e-9*max(1.,out['tail']) and lift_error<=1e-9*max(1.,float(np.linalg.norm(C)))
  # Four MP equations for the explicitly represented square roots.
  Li=(U/a)@U.T;Ri=(V/b)@V.T
  mp=max(float(np.linalg.norm(X@Y@X-X)) for X,Y in [(L,Li),(Li,L),(R,Ri),(Ri,R)])
  assert mp<=1e-9*max(1.,float(np.linalg.norm(L)),float(np.linalg.norm(R)))
  P=U@U.T;Q=V@V.T;N=rng.normal(size=(m,n));N=N-P@N@Q
  invisible=float(np.linalg.norm(L@N@R));inner=float(np.sum(M*N));assert invisible<=1e-9*max(1.,float(np.linalg.norm(L))*float(np.linalg.norm(R))) and abs(inner)<=1e-9*max(1.,float(np.linalg.norm(M))*float(np.linalg.norm(N)))
  floated.append({'id':f'f{case}','U':U,'a':a,'V':V,'b':b,'H':H,'r':r,'C':C,'Cr':Cr,'M':M,'loss':loss,'tail':out['tail'],'lift_error':lift_error,'mp_error':mp,'N':N,'invisible_error':invisible,'orthogonal_inner':inner,'note':'N may increase rank; no rank-feasible optimality claimed for arbitrary additions'})
 assert sum(x['tail']>1e-10 for x in floated)>=6, 'positive noncoordinate truncation coverage'
 # Physical linear sensor mapping: gains dimensionless, voltages V, H conductance S.
 av=[F(1),F(2),F(0)];bv=[F(1),F(0),F(3)];H=[[F(2 if i==0 else 5 if i==1 else 7) if i==j else F() for j in range(3)] for i in range(3)]
 M=[[av[i]*bv[j]/25 for j in range(3)] for i in range(3)];qs=[tuple(u*x for x in av) for u in [F(-1),F(1)]];ks=[tuple(v*x for x in bv) for v in [F(-2),F(2)]];E=[[H[i][j]-M[i][j] for j in range(3)] for i in range(3)]
 assert exact_risk(qs,ks,E)==0
 c=[F(2),F(-1),F(0)];N=[[c[i]*bv[j] for j in range(3)] for i in range(3)]
 Nplus=[[M[i][j]+N[i][j] for j in range(3)] for i in range(3)];norm=lambda X:sum((v*v for row in X for v in row),F());assert exact_risk(qs,ks,[[H[i][j]-Nplus[i][j] for j in range(3)] for i in range(3)])==0 and norm(Nplus)>norm(M)
 shift=score([F(0),F(1),F(0)],E,[F(0),F(1),F(0)]);assert shift==5
 # Concrete discriminating misuse witnesses, not model refusal measurements.
 paired_true=F(1,2);paired_proxy=F(1,4);assert paired_true!=paired_proxy
 centered_true=F(36);centered_wrong=F(0);assert centered_true!=centered_wrong
 tiny=F(1,10**6);tiny_risk=exact_risk([(F(0),tiny),(F(0),-tiny)],[(F(1),F(0)),(F(-1),F(0))],[[F(),F()],[F(10**6),F()]]);assert tiny_risk==1
 assert F(1,10**12)/F(1,10**6)==F(1,10**6)
 # Ridge lambda=1 picks unobserved component10 instead of observed component1: original risk0 vs1.
 ridge=solve(np.eye(2),[2**.5,1.],np.eye(2),[2**.5,1.],np.diag([1.,10.]),1);assert np.allclose(ridge['M'],np.diag([0.,10.]))
 tie=solve(np.eye(2),[1,1],np.eye(2),[1,1],np.eye(2),1);assert abs(tie['tail']-1)<=1e-12
 refusals=[]
 tests=[('negative-rank',np.eye(2),[1,1],np.eye(2),[1,1],np.eye(2),-1),('fractional-rank',np.eye(2),[1,1],np.eye(2),[1,1],np.eye(2),.5),('bool-rank',np.eye(2),[1,1],np.eye(2),[1,1],np.eye(2),True),('excess-rank',np.eye(2),[1,1],np.eye(2),[1,1],np.eye(2),3),('zero-declared-positive',np.eye(2),[1,0],np.eye(2),[1,1],np.eye(2),1),('negative-scale',np.eye(2),[1,-1],np.eye(2),[1,1],np.eye(2),1),('not-orthonormal',np.ones((2,2)),[1,1],np.eye(2),[1,1],np.eye(2),1),('nonfinite',np.eye(2),[1,1],np.eye(2),[1,1],np.array([[math.nan,0],[0,1]]),1),('shape',np.eye(2),[1],np.eye(2),[1,1],np.eye(2),1)]
 tests += [('scale-overflow',np.eye(2),[1e308,1],np.eye(2),[1e308,1],np.eye(2),1),('weighted-overflow',np.eye(2),[2,1],np.eye(2),[2,1],np.diag([1e308,1]),1),('svd-overflow',np.eye(2),[1,1],np.eye(2),[1,1],np.full((2,2),1.7e308),1),('tail-overflow',np.eye(2),[1,1],np.eye(2),[1,1],np.diag([1e155,1e155]),1),('reciprocal-overflow',np.eye(2),[1e-320,1],np.eye(2),[1,1],np.ones((2,2)),1)]
 for name,*args in tests:
  try:solve(*args)
  except ValueError as e:refusals.append({'id':name,'reason':str(e)})
  else:raise AssertionError(name)
 from unittest.mock import patch
 with patch.object(np.linalg,'svd',side_effect=np.linalg.LinAlgError('injected nonconvergence')):
  try:solve(np.eye(2),[1,1],np.eye(2),[1,1],np.eye(2),1)
  except ValueError as e:refusals.append({'id':'svd-nonconvergence','reason':str(e),'kind':'explicitly injected failure path, not observed backend failure'})
  else:raise AssertionError('svd nonconvergence guard')
 raw={'seed':20261008,'exact_cases':exact,'float_cases':floated,'sensor':{'q':qs,'k':ks,'H':H,'M':M,'invisible_N':N,'M_plus_N':Nplus,'risk':F(),'min_norm_squared':norm(M),'alternative_norm_squared':norm(Nplus),'support_shift_error':shift,'units':'q dimensionless; k V; H/M S; score A; MSE A^2'},'counterexamples':{'paired_true':paired_true,'independent_proxy':paired_proxy,'noncentral_true':centered_true,'centered_wrong':centered_wrong,'tiny_eigenvalue_discarded_true_risk':tiny_risk,'ridge_M':ridge['M'],'ridge_original_risk':1,'support_optimal_original_risk':0,'tie_tail':tie['tail'],'inverse_noise_amplification':{'sqrt_eigenvalue':1e-6,'whitened_error':1e-12,'lifted_error':1e-6}},'refusals':refusals,'diagnostic_seconds':time.perf_counter()-start,'tolerance':'1e-9 scaled absolute/relative for float fixtures, exact Fraction equality separately','limitations':['Finite sample checks not proof','Support bases supplied, no population rank estimation','Finite output is no accuracy guarantee for arbitrarily ill-conditioned scales; nonfinite/decomposition outcomes rejected','No model/token/GPU/e2e benchmark; all cases public development']}
 (BASE/'raw.json').write_text(json.dumps(encoded(raw),ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'exact_cases':len(exact),'float_cases':len(floated),'refusals':len(refusals),'diagnostic_seconds':raw['diagnostic_seconds']}))
if __name__=='__main__':main()
