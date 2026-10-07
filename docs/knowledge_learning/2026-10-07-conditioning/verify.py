"""Exact finite certificates and binary64 counterexamples, not a formal proof/model A/B."""
import json, time
from fractions import Fraction as F
from pathlib import Path

started=time.perf_counter(); checks=[]; cases=[]
def check(name, ok):
    assert ok, name
    checks.append(dict(name=name,passed=True))
def vn(x): return max(map(abs,x))
def mn(a): return max(sum(map(abs,row)) for row in a)
def mv(a,x): return [sum(v*w for v,w in zip(row,x)) for row in a]
def mm(a,b): return [[sum(v*w for v,w in zip(row,col)) for col in zip(*b)] for row in a]
def sub(x,y): return [a-b for a,b in zip(x,y)]
def inv(a):
    aa,b=a[0];c,d=a[1];det=aa*d-b*c
    if not det: raise ValueError('singular')
    return [[d/det,-b/det],[-c/det,aa/det]]
def mat(rows): return [[F(x) for x in row] for row in rows]
def finite(name,a,x,y):
    b=mv(a,x);r=sub(b,mv(a,y));an=mn(a);bn=vn(b);yn=vn(y);h=mn(inv(a));k=an*h
    den=an*yn+bn;eta=vn(r)/den if den else F(0);err=vn(sub(x,y));E=h*vn(r)
    check(name+':absolute',err<=E)
    if bn: check(name+':relative',err/vn(x)<=k*vn(r)/bn)
    if bn and k*eta<1: check(name+':joint',err/vn(x)<=2*k*eta/(1-k*eta))
    if yn:
        j=max(range(len(y)),key=lambda j:abs(y[j]));v=[F(0)]*len(y);v[j]=F(1 if y[j]>0 else -1)
        da=[[an/den*ri*vj for vj in v] for ri in r];db=[-bn/den*ri for ri in r]
        check(name+':attainment-equation',sub(mv(da,y),db)==r)
        check(name+':attainment-norms',mn(da)==eta*an and vn(db)==eta*bn)
    elif bn:
        check(name+':zero-y',eta==1 and sub([F(0)]*len(b),[-z for z in b])==r)
    else: check(name+':zero-system',eta==0 and err==0)
    i=max(range(len(y)),key=lambda j:y[j]);j=1-i;cert=y[i]-y[j]>2*E
    if cert: check(name+':ranking',x[i]>x[j])
    cases.append(dict(name=name,eta=str(eta),kappa=str(k),actual_error=str(err),error_bound=str(E),ranking_certificate=cert))
    return eta,k,E,r

a=mat([[2,0],[0,1]]);x=[F(1),F(2)];y=[F(101,100),F(199,100)]
eta,k,E,r=finite('well-conditioned',a,x,y)
check('positive-ranking-certificate',y[1]-y[0]>2*E)
for c in [F(1,10**20),F(10**20),F(-7)]:
    ee,kk,EE,_=finite('scale-'+str(c),[[c*v for v in row] for row in a],x,y)
    check('scaling-invariance-'+str(c),(ee,kk,EE)==(eta,k,E))
eps=F(1,10**8);bad=mat([[1,1],[1,1+eps]])
eta,k,E,r=finite('tiny-residual-wrong-ranking',bad,[F(1),F(2)],[F(3),F(0)])
check('small-residual-not-small-error',vn(r)==2*eps and eta<F(1,10**8) and E>4)
check('wrong-ranking-and-refusal',not F(3)>2*E and F(3)>0 and F(1)<F(2))
finite('zero-b',a,[F(0),F(0)],[F(1),F(-1)])
finite('zero-y',a,x,[F(0),F(0)])
finite('both-zero',a,[F(0),F(0)],[F(0),F(0)])
# Finite inverse certificates; q=1 is a refusal boundary, not proof of singularity.
for scale in [F(1),F(3,4),F(1,2)]:
    b=[[scale*v for v in row] for row in inv(a)]
    ba=mm(b,a);t=[[F(i==j)-ba[i][j] for j in range(2)] for i in range(2)];q=mn(t)
    check('inverse-bound-'+str(scale),q<1 and mn(inv(a))<=mn(b)/(1-q))
b2=[[2*v for v in row] for row in inv(a)];ba2=mm(b2,a)
check('q-one-must-refuse',mn([[F(i==j)-ba2[i][j] for j in range(2)] for i in range(2)])==1)
# Exact boundary has a tied true ranking; strictness cannot be weakened.
ty=[F(2),F(0)];tx=[F(1),F(1)];te=vn(sub(ty,tx))
check('ranking-equality-boundary',ty[0]-ty[1]==2*te and tx[0]==tx[1])

L=mat([[2,-1],[-1,2]]);volts=[F(2,3),F(1,3)];approx=[volts[0]+F(1,100),volts[1]-F(1,100)]
_,_,E,r=finite('grounded-electric-network',L,volts,approx)
check('kirchhoff-source',mv(L,volts)==[F(1),F(0)])
check('voltage-units-and-bound',mn(inv(L))==1 and vn(r)==F(3,100) and E==F(3,100))
check('voltage-order-preserved',approx[0]-approx[1]>2*E and volts[0]>volts[1])
ungrounded=mat([[1,-1],[-1,1]])
try: inv(ungrounded)
except ValueError: check('singular-premise-rejected',True)
else: raise AssertionError('singular not rejected')
check('zero-residual-nonunique-potential',mv(ungrounded,[F(1),F(0)])==mv(ungrounded,[F(101),F(100)])==[F(1),F(-1)])
check('gauge-error-arbitrarily-large',vn(sub([F(101),F(100)],[F(1),F(0)]))==100)

# Input rounding may hide a nonzero residual of the exact intended system.
tiny=F(1,2**54);af=mat([[1,1],[1,1+tiny]]);xf=[F(1),F(2)];yf=[F(3),F(0)]
rf=sub(mv(af,xf),mv(af,yf));afloat=[[float(v) for v in row] for row in af];bf=[float(v) for v in mv(af,xf)]
check('binary64-input-rounding',afloat[1][1]==1.0 and bf[1]==3.0)
check('printed-zero-is-not-exact-residual',sub(bf,mv(afloat,[3.0,0.0]))==[0.0,0.0] and vn(rf)==2*tiny)

# Paper Algorithm3.2 specialized to a diagonal example, no speed/general stability claim.
e=2.0**-54; inner=lambda rhs:[rhs[0]/e,rhs[1]]
yy=inner([1.0,1.0]);z=inner([1.0,0.0]);beta=1.0+z[0];theta=yy[0]/beta
sm=[yy[0]-z[0]*theta,yy[1]]
w=inner([1.0-theta,1.0]);theta1=(w[0]-theta)/beta;msm=[w[0]-z[0]*theta1,w[1]]
sm_r=vn([1-(1+e)*sm[0],1-sm[1]]);msm_r=vn([1-(1+e)*msm[0],1-msm[1]])
check('SM-cancellation-counterexample',sm==[0.0,1.0] and sm_r==1.0)
check('MSM-finite-recovery',msm==[1.0,1.0] and msm_r==0.0)
check('MSM-true-error-still-bounded',abs(F.from_float(msm[0])-1/(1+tiny))<=tiny)
out=dict(schema_version=1,scope='Finite exact arithmetic/structure checks only; not general proof, model A/B or independent unseen tests.',passed=len(checks),checks=checks,cases=cases,physical_units={'A':'siemens','b':'ampere','H':'ohm','E':'volt'},recent_experiment={'SM':sm,'MSM':msm,'binary64_residuals':[sm_r,msm_r],'inner_solves':[2,3],'scope':'one contrived input, intended exact updated matrix error checked separately; no universal stability or timing claim'},seconds=time.perf_counter()-started,model_calls=0,formal_prover='not run',quality_AB='not run')
Path(__file__).with_name('checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['passed','seconds','model_calls','quality_AB']}))
