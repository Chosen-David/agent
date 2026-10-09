"""Frozen public exact identities and one actual binary64 SM witness; no production solver."""
from fractions import Fraction as F
from pathlib import Path
import json,time,sys,hashlib
B=Path(__file__).resolve().parent;start=time.perf_counter();cfg=json.loads((B/'cases.json').read_text());records=[]
def mm(A,C):return [[sum((a*b for a,b in zip(row,col)),F(0)) for col in zip(*C)] for row in A]
def tr(A):return list(map(list,zip(*A)))
def add(A,C,sign=1):return [[a+sign*b for a,b in zip(row,col)] for row,col in zip(A,C)]
def eye(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def inv(A):
 n=len(A);M=[list(map(F,row))+ident for row,ident in zip(A,eye(n))]
 for j in range(n):
  p=next((i for i in range(j,n) if M[i][j]),None)
  if p is None:raise ValueError('singular matrix')
  M[j],M[p]=M[p],M[j];pivot=M[j][j];M[j]=[v/pivot for v in M[j]]
  for i in range(n):
   if i!=j:
    factor=M[i][j];M[i]=[a-factor*b for a,b in zip(M[i],M[j])]
 return [row[n:] for row in M]
def update(A,U,V):
 Ai=inv(A);Z=mm(Ai,U);T=mm(tr(V),Ai);S=add(eye(len(U[0])),mm(tr(V),Z));Si=inv(S)
 return add(Ai,mm(mm(Z,Si),T),-1),S
def serial(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,list):return [serial(a) for a in x]
 if isinstance(x,dict):return {k:serial(v) for k,v in x.items()}
 return x
def emit(id,values):records.append({'id':id,'values':serial(values),'passed':True})
A=[[F(2),F(1)],[F(0),F(3)]];U=[[F(1)],[F(2)]];V=[[F(2)],[F(-1)]];rhs=[[F(3)],[F(4)]];C=add(A,mm(U,tr(V)));Ci,S=update(A,U,V);assert C==[[4,0],[4,1]] and S==[[F(2,3)]] and Ci==inv(C);sol=mm(Ci,rhs);assert sol==[[F(3,4)],[F(1)]];emit('rankone-general',{'B':C,'S':S,'solution':sol})
Z=[[F(0)],[F(0)]];Ci,S=update(A,Z,V);assert Ci==inv(A) and S==[[1]];emit('zero-update',{'S':S,'inverse':Ci})
A=eye(2);U=[[F(1),F(1)],[F(0),F(0)]];Ci,S=update(A,U,U);assert S==[[2,1],[1,2]] and Ci==[[F(1,3),0],[0,1]];emit('rankdeficient-factors',{'S':S,'inverse':Ci})
A=[[F(0),F(0)],[F(0),F(1)]];U=[[F(1)],[F(0)]];C=add(A,mm(U,tr(U)));assert C==eye(2)
try:update(A,U,U)
except ValueError:emit('singular-base',{'B_invertible':True,'decision':'reject A inverse formula'})
else:raise AssertionError('singular base accepted')
A=eye(2);V=[[-F(1)],[F(0)]];C=add(A,mm(U,tr(V)))
try:update(A,U,V)
except ValueError:emit('zero-capacitance',{'beta':'0','B':C,'decision':'reject singular update'})
else:raise AssertionError('singular update accepted')
A=[[F(2),F(0)],[F(0),F(3)]];Ci,S=update(A,U,U);assert inv(Ci)==[[3,0],[0,3]];emit('spd-add',{'B':inv(Ci),'beta':S[0][0]})
V=[[-a[0]] for a in U];Ci,S=update(A,U,V);assert S==[[F(1,2)]] and inv(Ci)==[[1,0],[0,3]];emit('spd-downdate',{'a':'1/2','beta':S[0][0],'B':inv(Ci)})
A=eye(2);U=[[F(2)],[F(0)]];V=[[-a[0]] for a in U];Ci,S=update(A,U,V);assert S==[[-3]] and Ci==[[F(-1,3),0],[0,1]];emit('indefinite-invertible',{'a':'4','B':inv(Ci),'decision':'reject positive-definite interpretation'})
A=[[F(2),F(0)],[F(0),F(3)]];U=[[F(1)],[F(2)]];Ci,S=update(A,U,U);assert Ci==[[F(7,17),F(-2,17)],[F(-2,17),F(3,17)]];h=[[F(1)],[F(1)]];y=F(2);hn=add(h,[[y],[2*y]]);sol=mm(Ci,hn);assert sol==mm(inv(add(A,mm(U,tr(U)))),hn);emit('ridge-stream',{'C_new':inv(Ci),'h_new':hn,'solution':sol,'beta':S[0][0]})
assert sys.float_info.radix==2 and sys.float_info.mant_dig==53
u=float(2**54);y=1.0;z=u;alpha=1.0;beta=1.0+z;theta=alpha/beta;xhat=y-z*theta;exact=F(1,2**54+1);Bexact=F(2**54+1);r=F(1)-Bexact*F.from_float(xhat);eta=abs(r)/(abs(Bexact)*abs(F.from_float(xhat))+1)
assert beta==u and theta==2.0**-54 and xhat==0 and exact>0 and eta==1
emit('binary64-cancellation',{'A':'1','u':str(2**54),'beta_float_hex':beta.hex(),'theta_hex':theta.hex(),'xhat_hex':xhat.hex(),'exact_solution':exact,'actual_residual_exact':r,'normalized_residual':eta,'forward_relative_error':abs(F.from_float(xhat)-exact)/exact,'direct_on_rounded_B_hex':(1.0/beta).hex(),'condition_A':'1','condition_true_B':'1','scope':'actual Python binary64 order; not MSM, GPU or universal stability test'})
assert [r['id'] for r in records]==cfg['cases'];(B/'raw.json').write_text(json.dumps({'schema':'public-inverse-checks/v1','cases_sha256':hashlib.sha256((B/'cases.json').read_bytes()).hexdigest(),'records':records,'elapsed_seconds':time.perf_counter()-start,'scope':cfg['scope']},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'cases':len(records),'passed':len(records),'binary64_wrong_solution':xhat,'binary64_backward_diagnostic':str(eta)}))
