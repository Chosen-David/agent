"""Public exact event witnesses; no Gaussian probability simulation or formal proof."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D, localcontext, ROUND_CEILING
import json,time,hashlib
B=Path(__file__).resolve().parent
cfg=json.loads((B/'cases.json').read_text());start=time.perf_counter();out=[]
def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def add(a,b,sign=1):return [x+sign*y for x,y in zip(a,b)]
def mat(A,x):return [dot(r,x) for r in A]
def emit(id,values):out.append({'id':id,'values':values,'passed':True})
A=[[F(1),F(0)],[F(0),F(4,5)]];u=[F(1),F(0)];v=[F(0),F(1)];eps=F(2,5)
for x in [add(u,v),add(u,v,-1)]:assert abs(dot(mat(A,x),mat(A,x))-dot(x,x))<=eps*dot(x,x)
assert dot(mat(A,u),mat(A,v))==dot(u,v)==0
emit('polarization-positive',{'norm2_original':'2','norm2_projected':'41/25','relative':'9/50','dot_error':'0'})
z=[F(0),F(0)];assert mat(A,z)==z and dot(z,u)==0;emit('zero-vector',{'score':'0'})
v=[-a for a in u];assert add(u,v)==z;assert dot(mat(A,u),mat(A,v))==-1;emit('opposite-vectors',{'sum_norm2':'0','dot':'-1'})
s=[F(1),F(0)];hat=[F(9,10),F(1,10)];E=F(1,10);assert s[0]-s[1]>2*E and hat[0]>hat[1];emit('strict-margin-preserved',{'gap':'1','bound':'1/5'})
s=[F(1,5),F(0)];hat=[F(1,10)]*2;assert s[0]-s[1]==2*E and hat[0]==hat[1];emit('equality-can-tie',{'gap':'1/5','proxy':['1/10','1/10']})
s=[F(1,20),F(0)];hat=[F(-1,20),F(1,10)];assert all(abs(a-b)<=E for a,b in zip(s,hat)) and s[0]>s[1] and hat[0]<hat[1];emit('no-margin-can-flip',{'scores':list(map(str,s)),'proxy':list(map(str,hat))})
P=[[F(1),F(1)]];x=[F(1),F(-1)];assert mat(P,x)==[0] and dot(x,x)==2;emit('adaptive-kernel',{'rank':'1','input_norm2':'2','sketch_norm2':'0','unit_normalization':'x/sqrt(2), independent-input premise fails'})
g=[F(1),F(0)];p=mat(P,g);true=F(1);approx=p[0]*p[0]/100;assert dot(g,g)==dot(p,p)==1 and approx==F(1,100);emit('inverse-not-preserved',{'F_diagonal':['1','99'],'true':'1','projected':'1/100','gradient_geometry_exact':True})
u=[F(3,5),F(4,5)];v=[F(1),F(0)];terms=[]
for sign in [1,-1]:
 x=add(u,v,sign);e=dot(mat(A,x),mat(A,x))-dot(x,x);assert abs(e)<=eps*dot(x,x);terms.append(e)
err=dot(mat(A,u),mat(A,v))-dot(u,v);assert err==(terms[0]-terms[1])/4 and abs(err)<=eps;emit('finite-event-norm-to-score',{'unit_norms':[str(dot(u,u)),str(dot(v,v))],'errors':list(map(str,terms)),'score_error':str(err),'bound':str(eps)})
with localcontext() as c:
 c.prec=60;e=D(1)/5;d=D(1)/20;Q=1;N=1024;constant=e*e/4-e*e*e/6;ratio=(D(4*Q*N)/d).ln()/constant;m=int(ratio.to_integral_value(rounding=ROUND_CEILING));failure=D(4*Q*N)*(-D(m)*constant).exp();assert m==1306 and failure<=d and m>128
 emit('dimension-bound-vacuous',{'m':m,'d':128,'Q':Q,'N':N,'epsilon':'1/5','delta':'1/20','c':str(constant),'failure_upper_decimal':str(failure),'status':'Decimal sanity only, not certified interval rounding'})
assert [a['id'] for a in out]==cfg['cases'];(B/'raw.json').write_text(json.dumps({'schema':'public-rational-checks/v1','cases_sha256':hashlib.sha256((B/'cases.json').read_bytes()).hexdigest(),'records':out,'elapsed_seconds':time.perf_counter()-start,'scope':'Finite exact event implications and witnesses; no statistical coverage or general proof from samples'},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'cases':len(out),'passed':len(out)}))
