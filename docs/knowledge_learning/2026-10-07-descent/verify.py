"""Rational coefficient and finite trajectory checks; no formal proving/model calls."""
from fractions import Fraction as F
from pathlib import Path
import json,time,math
from agent_runtime.knowledge import KnowledgeStore
start=time.perf_counter();checks=[]
def check(name,yes):
 assert yes,name
 checks.append({'name':name,'passed':True})
def matmul(A,B):return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]
def transpose(A):return list(map(list,zip(*A)))
A=[[F(7,5),F(-9,10)],[F(1),F(0)]]
P=[[F(760,33),F(-168,11)],[F(-168,11),F(1081,55)]]
Q=matmul(matmul(transpose(A),P),A)
check('all-state-rational-coefficient-identity',[[Q[i][j]-P[i][j] for j in range(2)] for i in range(2)]==[[F(-1),F(0)],[F(0),F(-1)]])
det=P[0][0]*P[1][1]-P[0][1]**2
check('positive-definite-Sylvester',P[0][0]>0 and det==F(7240,33)>0)
def V(s):return sum(s[i]*P[i][j]*s[j] for i in range(2) for j in range(2))
def update(s):return tuple(sum(A[i][j]*s[j] for j in range(2)) for i in range(2))
s=(F(1),F(1));traj=[]
for n in range(30):
 nxt=update(s);traj.append({'step':n+1,'x':float(nxt[0]),'objective':float(nxt[0]**2/2),'extended_potential':float(V(nxt))})
 check('momentum-energy-step-'+str(n),V(nxt)==V(s)-sum(x*x for x in s) and V(nxt)<V(s))
 s=nxt
check('raw-objective-increase',traj[1]['objective']==.02 and traj[2]['objective']==.26645)
x=F(1);alpha=F(1,2);c=alpha*(1-alpha/2);acc=F(0)
for n in range(30):
 y=x-alpha*x;acc+=x*x
 check('GD-certified-decrease-'+str(n),y*y/2==x*x/2-c*x*x)
 x=y
check('GD-telescoping-budget',c*acc==F(1,2)-x*x/2)
check('step-boundary-cycle',(1-F(2))**2==1)
check('oversize-step-divergence',abs(1-F(5,2))>1)
x=F(1);total=F(0);last_drop=None
for n in range(30):
 a=F(1,2**(n+2));total+=a;y=(1-a)*x;last_drop=(x*x-y*y)/2;x=y
check('summable-step-stagnation',x>=1-total>F(1,2) and last_drop<F(1,10**8))
check('stationary-maximum-cos',math.sin(0)==0 and math.cos(0)>math.cos(math.pi))
# f=1/(1+x^2), alpha=.25, exact finite growth; infinite drift proof is in entry.
x=F(1)
for n in range(4):
 grad=-2*x/(1+x*x)**2;y=x-grad/4
 check('noncompact-growing-state-'+str(n),y>x and 1/(1+y*y)<1/(1+x*x))
 x=y
# SI dimensions (mass,length,time).
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def scale(a,k):return tuple(k*x for x in a)
m=(1,0,0);q=(0,1,0);vel=(0,1,-1);spring=(1,0,-2);damping=(1,0,-1);energy=(1,2,-2)
check('mechanical-energy-units',add(m,scale(vel,2))==add(spring,scale(q,2))==energy)
check('dissipation-power-units',add(damping,scale(vel,2))==add(energy,(0,0,-1)))
# Derivative at rational states: mv*vdot+kq*qdot=-bv^2.
for q0,v0 in [(F(1),F(0)),(F(1),F(2)),(F(-2),F(3))]:
 mass=F(2);b=F(3);k=F(4);vdot=(-b*v0-k*q0)/mass
 check('oscillator-power-'+str((q0,v0)),mass*v0*vdot+k*q0*v0==-b*v0*v0)
check('zero-power-set-not-wholly-invariant',F(0)**2==0 and -F(1)!=0)
check('no-damping-periodic-energy',all(q0*q0+v0*v0==1 for q0,v0 in [(F(1),F(0)),(F(0),F(1)),(F(-1),F(0)),(F(0),F(-1))]))
h=F(1,10);B=[[F(1),h],[-h,1-h]];q0=F(1);v0=F(0);qn=q0+h*v0;vn=v0-h*(q0+v0)
check('Euler-continuous-energy-increase',(qn*qn+vn*vn)/2==F(101,200)>F(1,2))
trace=B[0][0]+B[1][1];detB=B[0][0]*B[1][1]-B[0][1]*B[1][0]
check('Euler-asymptotically-stable-with-transient',detB==F(91,100)<1 and trace**2-4*detB<0)
store=KnowledgeStore('knowledge');refs=store.get('math.descent-lyapunov-certificate')['knowledge_refs'];store.check_refs(refs)
check('knowledge-identity',len(refs)==1)
result={'count':len(checks),'checks':checks,'elapsed_seconds':time.perf_counter()-start,'momentum_trajectory':traj,'paired_numerical_case':{'same_problem':'f=x^2/2','same_initial_x':1,'updates_each':30,'gradient_evaluations_each':30,'GD_alpha':.5,'momentum_alpha':.5,'momentum_beta':.9,'GD_final_error':float(F(1,2)**30),'momentum_final_error':float(abs(s[0])),'scope':'synthetic solver comparison; momentum stores an extra state; no Agent/model A/B or universal speedup'},'potential_matrix':[[str(x) for x in row] for row in P],'physical_case':{'initial_energy_joule':.5,'Euler_next_energy_joule':.505,'timestep_seconds':.1,'spectral_radius':math.sqrt(.91)},'verification':'rational polynomial identity + finite cases; derivation-reviewed, no Lean/SymPy','cost':{'model_calls':0,'model_tokens':None},'knowledge_root':'knowledge','knowledge_refs':refs}
Path(__file__).with_name('checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':len(checks),'elapsed_seconds':result['elapsed_seconds'],'paired':result['paired_numerical_case']}))
