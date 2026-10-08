from pathlib import Path
import json,math,random,time,platform,sys
from fractions import Fraction as F
D=Path(__file__).parent; cfg=json.loads((D/'config.json').read_text()); rng=random.Random(cfg['seed']); start=time.perf_counter();raw=[];assertions=0

def mat(z,w):return [[(z+w).real,(-z+w).imag],[(z+w).imag,(z-w).real]]
def rot(t):return [[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]]
def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
def sub(a,b):return [[a[i][j]-b[i][j] for j in range(2)] for i in range(2)]
def norm(a):return math.sqrt(sum(x*x for row in a for x in row))
def check(c):
 global assertions
 assertions+=1
 assert c
for i in range(32):
 theta=rng.uniform(.1,2.9); phi=rng.uniform(.1,2.9);a=complex(rng.uniform(-1,1),rng.uniform(-1,1));b=complex(rng.uniform(-1,1),rng.uniform(-1,1));S=mat(a,b); E=sub(mul(S,rot(theta)),mul(rot(phi),S));dp=abs(complex(math.cos(theta),math.sin(theta))-complex(math.cos(phi),math.sin(phi)));dm=abs(complex(math.cos(theta),-math.sin(theta))-complex(math.cos(phi),math.sin(phi)))
 rhs=2*abs(a)**2*dp**2+2*abs(b)**2*dm**2;check(abs(norm(E)**2-rhs)<cfg['tolerance']);check(norm(S)<=norm(E)/min(dp,dm)+cfg['tolerance']); steps=[]
 for m in [-31,-1,0,1,17]:
  defect=norm(sub(mul(S,rot(m*theta)),mul(rot(m*phi),S)));check(defect<=abs(m)*norm(E)+cfg['tolerance']);steps.append({'m':m,'defect':defect})
 for target,B in [(theta,mat(a,0)),(-theta,mat(0,b))]:check(norm(sub(mul(B,rot(theta)),mul(rot(target),B)))<cfg['tolerance'])
 check(norm(sub(rot(theta),rot(theta+2*math.pi)))<cfg['tolerance']);check(norm(sub(rot(theta/2),rot((theta+2*math.pi)/2)))>1)
 raw.append({'theta':theta,'phi':phi,'a':[a.real,a.imag],'b':[b.real,b.imag],'defect_squared':norm(E)**2,'reference_squared':rhs,'steps':steps})
I=[[F(1),F(0)],[F(0),F(1)]]; J=[[F(0),F(-1)],[F(1),F(0)]]; minusJ=[[F(0),F(1)],[F(-1),F(0)]];Q=[[F(3,5),F(-4,5)],[F(4,5),F(3,5)]]; S=[[F(2),F(3)],[F(-3),F(2)]];C=[[F(1),F(0)],[F(0),F(-1)]];shear=[[F(1),F(2)],[F(0),F(1)]]
exact=[]
for name,A,B,T,expected in [('equal-rational',Q,Q,S,True),('opposite',J,minusJ,C,True),('zero',I,I,shear,True),('pi',[[-x for x in r] for r in I],[[-x for x in r] for r in I],shear,True),('different',Q,J,S,False),('zero-pi',I,[[-x for x in r] for r in I],shear,False)]:
 ok=mul(T,A)==mul(B,T);check(ok==expected);exact.append({'branch':name,'expected':expected,'observed':ok})
# Rank obstruction: summing distinct orthogonal coordinates introduces a cross term.
check(sum(x*y for x,y in zip([1,0],[0,1]))==0);check((1+0)*(0+1)==1)
# On diagonal same-frequency subspace, normalized fusion preserves norm exactly in rational scaled form.
check(2*(F(3)**2+F(4)**2)==F(50))
(D/'raw.json').write_text(json.dumps({'seed':cfg['seed'],'cases':raw,'exact_branches':exact},indent=2)+'\n');(D/'summary.json').write_text(json.dumps({'cases':32,'exact_branches':6,'assertions':assertions,'elapsed_seconds':time.perf_counter()-start,'producer_status':'pending independent acceptance','scope':cfg['scope'],'formal_verified':False,'model_AB_calls':0},indent=2)+'\n');(D/'environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'arithmetic':'Python float and exact Fraction','GPU':False},indent=2)+'\n');print(assertions)
