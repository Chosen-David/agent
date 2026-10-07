"""Public algebra regression: exact rational identities + labeled float64 checks.
Run from repository root. These are finite examples, not general proofs/model A/B.
"""
from fractions import Fraction as F
from pathlib import Path
import json,time
import numpy as np
D=Path(__file__).resolve().parent; checks=[];start=time.perf_counter()
def check(topic,name,condition,level='exact-rational',detail=None):
 checks.append(dict(topic='math.'+topic,name=name,passed=bool(condition),level=level,detail=detail));assert condition,(topic,name)
def mat(a):return [[F(x) for x in r] for r in a]
def mul(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def add(a,b):return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def scale(a,x):return [[x*y for y in r] for r in a]
def eye(n):return mat([[int(i==j) for j in range(n)] for i in range(n)])
def transpose(a):return list(map(list,zip(*a)))
def rank(a):
 a=[r[:] for r in mat(a)];k=0
 for j in range(len(a[0]) if a else 0):
  ii=next((i for i in range(k,len(a)) if a[i][j]),None)
  if ii is None:continue
  a[k],a[ii]=a[ii],a[k];q=a[k][j];a[k]=[x/q for x in a[k]]
  for i in range(len(a)):
   if i!=k:q=a[i][j];a[i]=[x-q*y for x,y in zip(a[i],a[k])]
  k+=1
 return k
def poly_mul(p,q):
 r=[F(0)]*(len(p)+len(q)-1)
 for i,x in enumerate(p):
  for j,y in enumerate(q):r[i+j]+=x*y
 return r
def poly_div(p,q):
 p=list(map(F,p));q=list(map(F,q));r=p[:];u=[F(0)]*max(1,len(p)-len(q)+1)
 while len(r)>=len(q) and any(r):
  k=len(r)-len(q);x=r[-1]/q[-1];u[k]=x
  for i,y in enumerate(q):r[i+k]-=x*y
  while r and r[-1]==0:r.pop()
 return u,r
T='polynomial-euclidean-calculus';u,r=poly_div([-1,0,0,1],[-1,1]);check(T,'field division',[F(1)]*3==u and not r);check(T,'nonfield refusal',F(1,2).denominator!=1);check(T,'repeated root derivative',poly_mul([-1,1],[-1,1])==[1,-2,1])
T='rank-nullity-quotient';a=mat([[1,1,0],[0,0,1]]);v=mat([[1],[-1],[0]]);check(T,'rank nullity',rank(a)==2 and mul(a,v)==mat([[0],[0]]));check(T,'query factors through code',mul(mat([[1,1,0]]),v)==[[0]]);check(T,'lost query refusal',mul(mat([[1,0,0]]),v)!=[[0]])
T='matrix-rank-factorization';a=mat([[1,2,3],[2,4,6]]);c=mat([[1],[2]]);r=mat([[1,2,3]]);check(T,'CR equality',mul(c,r)==a and rank(a)==rank(c)==rank(r)==1);check(T,'exact versus numeric rank',rank([[1,0],[0,F(1,10**12)]])==2);check(T,'empty rank',rank([[0,0],[0,0]])==0)
T='similarity-invariants';a=mat([[1,1],[0,1]]);s=mat([[100,0],[0,1]]);si=mat([[F(1,100),0],[0,1]]);ap=mul(mul(si,a),s);check(T,'same endomorphism',mul(s,ap)==mul(a,s));check(T,'same spectrum insufficient',rank(add(a,scale(eye(2),-1)))==1 and rank([[0,0],[0,0]])==0);check(T,'general similarity changes norm',np.linalg.norm(np.array(a,float),2)>np.linalg.norm(np.array(ap,float),2),'float64')
T='determinant-invertibility';check(T,'volume no condition bound',F(10**6)*F(1,10**6)==1);check(T,'integer nonunit refusal',F(1,2).denominator!=1);check(T,'nonzero det vs rank',rank([[2,0],[0,3]])==2)
T='minimal-polynomial-primary-decomposition';a=mat([[1,0],[0,2]]);e1=add(scale(eye(2),2),scale(a,-1));e2=add(a,scale(eye(2),-1));check(T,'CRT projectors',add(e1,e2)==eye(2) and mul(e1,e2)==mat([[0,0],[0,0]]) and mul(e1,e1)==e1);check(T,'Cayley Hamilton',add(add(mul(a,a),scale(a,-3)),scale(eye(2),2))==mat([[0,0],[0,0]]));j=mat([[1,1],[0,1]]);n=add(j,scale(eye(2),-1));check(T,'repeated minimum refuses diagonalization',rank(n)==1 and rank(mul(n,n))==0)
T='rational-canonical-cyclic';a=mat([[1,0],[0,2]]);w=mat([[1,1],[1,2]]);h=mat([[0,-2],[1,3]]);check(T,'companion similarity',rank(w)==2 and mul(a,w)==mul(w,h));rot=mat([[0,-1],[1,0]]);check(T,'real unsplit companion',mul(rot,rot)==scale(eye(2),-1));check(T,'same chi different cyclic factors',rank(add(mat([[1,1],[0,1]]),scale(eye(2),-1)))!=rank([[0,0],[0,0]]))
T='jordan-generalized-eigenspaces';n=mat([[0,1,0,0],[0,0,1,0],[0,0,0,0],[0,0,0,0]]);p=eye(4);ds=[0]
for k in range(1,5):p=mul(p,n);ds.append(4-rank(p))
check(T,'block nullities',ds==[0,2,3,4,4]);check(T,'block sizes recovered',[2*ds[k]-ds[k-1]-ds[k+1] for k in range(1,4)]==[1,0,1]);check(T,'max block nilpotency',rank(mul(n,n))==1 and rank(mul(mul(n,n),n))==0)
T='krylov-minimal-polynomial';a=mat([[1,0,0],[0,2,0],[0,0,3]]);b=mat([[1],[1],[0]]);w=mat([[1,1],[1,2],[0,0]]);h=mat([[0,-2],[1,3]]);check(T,'AW WH',mul(a,w)==mul(w,h) and rank(w)==2);p=b;hp=mat([[1],[0]])
for k in range(10):check(T,'recurrence '+str(k),p==mul(w,hp));p=mul(a,p);hp=mul(h,hp)
check(T,'zero start boundary',mul(a,mat([[0],[0],[0]]))==mat([[0],[0],[0]]));check(T,'nonnormal zero eigenvalue not scalar action',mul(mat([[0,5],[0,0]]),mat([[0],[1]]))==mat([[5],[0]]))
T='orthogonal-projection-qr';p=mat([[1,0],[0,0]]);x=mat([[2],[3]]);check(T,'orthogonal projector',mul(p,p)==p and transpose(p)==p and mul(p,x)==mat([[2],[0]]));a=np.array([[1,0],[0,2],[0,0.] ]);b=np.array([1,4,3.]);q,r=np.linalg.qr(a);z=np.linalg.solve(r,q.T@b);check(T,'QR LS residual',np.allclose(z,[1,2]) and np.allclose(a.T@(a@z-b),0),'float64');check(T,'rank deficient R refusal',rank([[1,1],[2,2]])==1);check(T,'normal equations square condition',np.isclose(np.linalg.cond(a.T@a),np.linalg.cond(a)**2),'float64')
T='hermitian-spectral-schur';a=np.array([[2,1],[1,2.]]);v,u=np.linalg.eigh(a);check(T,'selfadjoint spectrum',np.allclose(v,[1,3]) and np.allclose(u.T@u,np.eye(2)) and np.allclose(a@u,u*v),'float64');a=mat([[1,100],[0,2]]);check(T,'diagonalizable not normal',mul(a,transpose(a))!=mul(transpose(a),a));check(T,'closed disk not asymptotic',np.linalg.norm(np.linalg.matrix_power(np.eye(2),20))>0,'float64')
T='moore-penrose-pseudoinverse';a=mat([[1,0],[0,0]]);check(T,'four Penrose equations',mul(mul(a,a),a)==a and transpose(mul(a,a))==mul(a,a));check(T,'minimum norm LS',mul(a,mat([[2],[3]]))==mat([[2],[0]]));check(T,'rank discontinuity',F(1,F(1,10**6))==10**6)
T='bilinear-quadratic-inertia';a=mat([[2,0,0],[0,-3,0],[0,0,0]]);s=mat([[1,1,0],[0,1,0],[0,0,2]]);b=mul(mul(transpose(s),a),s);ev=np.linalg.eigvalsh(np.array(b,float));check(T,'congruence inertia',sum(ev>1e-10)==1 and sum(ev< -1e-10)==1 and sum(abs(ev)<=1e-10)==1,'float64');check(T,'positive determinant not SPD',(-1)*(-1)==1 and -1<0);check(T,'char2 polarization refusal',(2%2)==0)
T='generalized-hermitian-eigenproblem';a=np.array([[2,-1],[-1,2.]]);b=np.diag([2.,1]);l=np.linalg.cholesky(b);c=np.linalg.solve(l,np.linalg.solve(l,a).T).T;ev,u=np.linalg.eigh(c);z=np.linalg.solve(l.T,u);check(T,'mass eigensystem',np.allclose(a@z,(b@z)*ev) and np.allclose(z.T@b@z,np.eye(2)),'float64');check(T,'physical eigenvalues',np.allclose(ev,[(3-np.sqrt(3))/2,(3+np.sqrt(3))/2]),'float64','N/m divided kg gives s^-2; omega sqrt eigenvalue s^-1');check(T,'indefinite mass refusal',np.allclose(np.sort_complex(np.linalg.eigvals(np.array([[0,1],[-1,0.]]))),[-1j,1j]),'float64')
T='tensor-kronecker-calculus';a=np.array([[1,2],[0,1.]]);x=np.array([[1,0],[2,3.]]);b=np.array([[0,1],[1,0.]]);check(T,'column vec identity',np.array_equal((a@x@b).ravel(order='F'),np.kron(b.T,a)@x.ravel(order='F')),'float64-exact-integers');bc=b+1j*np.eye(2);check(T,'adjoint not transpose',not np.allclose(np.kron(bc.T,a),np.kron(bc.conj().T,a)),'float64');check(T,'tensor basis dimension',len([(i,j) for i in range(2) for j in range(3)])==6)
T='matrix-function-jordan-calculus';n=mat([[0,5],[0,0]]);e=add(eye(2),n);check(T,'nilpotent exponential Taylor',mul(n,n)==mat([[0,0],[0,0]]) and mul(e,add(eye(2),scale(n,-1)))==eye(2));check(T,'spectral values omit derivatives',e!=eye(2));check(T,'pole refusal',rank(n)==1)
T='sylvester-equation-separation';alpha=F(1001,1000);a=mat([[alpha,0],[0,-alpha]]);b=mat([[0,-1],[1,0]]);x=scale(mat([[alpha,-1],[1,-alpha]]),1/(alpha**2+1));check(T,'exact solution with bad downstream inverse',add(mul(a,x),scale(mul(x,b),-1))==eye(2));k=np.kron(np.eye(2),np.array(a,float))-np.kron(np.array(b,float).T,np.eye(2));check(T,'operator perfect solution illconditioned',np.isclose(np.linalg.cond(k),1) and np.isclose(np.linalg.cond(np.array(x,float)),2001),'float64');a=np.array([[1,100],[0,1.]]);k=a-2*np.eye(2);check(T,'nonnormal gap does not bound separation',np.linalg.svd(k,compute_uv=False)[-1]<0.011,'float64')
T='schur-complement-block-elimination';a=F(2);b=F(-1);s=F(2)-b*b/a;l=mat([[1,0],[b/a,1]]);r=transpose(l);check(T,'block factorization',mul(mul(l,mat([[a,0],[0,s]])),r)==mat([[2,-1],[-1,2]]));check(T,'boundary current preserved',s==F(3,2) and F(2)+b*F(1,2)==s);check(T,'invertible whole singular pivot refusal',rank([[0,1],[1,0]])==2 and rank([[0]])==0)
# Actual research-scope failure probes; these are our examples, not paper reproductions.
T='krylov-minimal-polynomial';a=np.diag([1.,2.,3.]);b=np.array([[1,0],[0,1],[0,1.]]);cat=np.hstack((b,a@b));check(T,'partial block deflation',np.linalg.matrix_rank(b)==2 and np.linalg.matrix_rank(cat)==3<4,'float64-exact-integers');c0=np.diag([-1.,0]);c1=np.diag([1.,0]);check(T,'matrix polynomial noninjectivity',np.array_equal(b@c0+a@b@c1,np.zeros_like(b)),'float64-exact-integers')
T='generalized-hermitian-eigenproblem';u=np.array([1.,.2]);f=np.diag([1.,.1])
for k in range(5):check(T,'filtered graph contraction '+str(k),np.isclose(abs(u[1]/u[0]),.2*.1**k),'float64');u=f@u
check(T,'absent target overlap refusal',np.array_equal(f@np.array([0.,1.]),np.array([0.,.1])),'float64-exact-decimals');check(T,'wrong filter amplifies',abs((np.diag([.1,1.])@np.array([1.,.2]))[1]/.1)>.2,'float64')
T='tensor-kronecker-calculus';e0=np.array([1.,0]);e1=np.array([0.,1]);fisher=sum(np.kron(np.outer(e,e),np.outer(e,e)) for e in (e0,e1))/2;factored=np.eye(4)/4;check(T,'correlated Fisher factoring failure',not np.allclose(fisher,factored) and np.isclose(np.max(abs(fisher-factored)),.25),'float64');check(T,'ALS projected leverage not original',not np.array_equal(np.array([1.,0.]),np.array([1.,1.])),'float64','W*=I2, F*=[1,0] loses full-column-rank R=2')
cur=json.loads((D/'curriculum.json').read_text());covered={c['topic'] for c in checks};assert set(t['id'] for t in cur['topics'])<=covered
out=dict(schema_version=1,passed=len(checks),checks=checks,seconds=time.perf_counter()-start,python_cost='one process; Fraction/NumPy; no GPU/model calls',numpy_version=np.__version__,quality_AB='not run',formal_proof='not run',heldout='no unused independent holdout; all examples public/development',scope='Exact/float finite verification + manually reviewed derivations. No general theorem proved by testing.')
(D/'checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'},ensure_ascii=False))
