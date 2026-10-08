from pathlib import Path
import json,random,math,platform,sys
from fractions import Fraction as F
D=Path(__file__).resolve().parent
cfg=json.loads((D/'config.json').read_text());rng=random.Random(cfg['seed']);tol=cfg['tolerance'];count=0

def check(x):
 global count
 count+=1
 assert x

def soft(x):
 a=max(x);v=[math.exp(z-a) for z in x];z=math.fsum(v);return [y/z for y in v]
def lse(x):
 a=max(x);return a+math.log(math.fsum(math.exp(y-a) for y in x))
def variance(p,e):
 m=math.fsum(a*b for a,b in zip(p,e));return math.fsum(a*(b-m)**2 for a,b in zip(p,e))
def calc(s,e):
 p=soft(s);t=[x+y for x,y in zip(s,e)];q=soft(t);kl=math.fsum(a*(math.log(a)-math.log(b)) for a,b in zip(p,q));breg=lse(t)-lse(s)-math.fsum(a*b for a,b in zip(p,e));n=len(s);r=max(e)-min(e);dc=[x-math.fsum(e)/n for x in e];norm=math.fsum(x*x for x in dc);v=variance(p,e);m=math.exp(-max(max(s)-min(s),max(t)-min(t)))/n
 N=512
 f=lambda u:(1-u)*variance(soft([a+u*b for a,b in zip(s,e)]),e)
 integ=(f(0)+f(1)+math.fsum((4 if j%2 else 2)*f(j/N) for j in range(1,N)))/(3*N)
 check(abs(kl-breg)<=tol);check(abs(kl-integ)<=tol);check(kl>=-tol);check(kl<=r*r/8+tol);check(kl<=norm/4+tol);check(kl>=m*norm/2-tol);check(kl>=math.exp(-r)*v/2-tol);check(kl<=math.exp(r)*v/2+tol)
 check(abs(math.fsum(p)-1)<=tol);check(abs(math.fsum(q)-1)<=tol)
 shifted=soft([x+8 for x in t]);check(max(abs(a-b) for a,b in zip(q,shifted))<=tol)
 check(all(math.isfinite(x) for x in [kl,breg,integ,r,norm,m,v]));return dict(s=s,e=e,p=p,q=q,kl=kl,bregman=breg,path_integral=integ,R=r,centered_norm2=norm,reference_variance=v,path_floor=m)
rows=[]
for i in range(cfg['cases']):
 n=1+i%8;s=[rng.randint(-12,12)/4 for _ in range(n)];e=[rng.randint(-4,4)/4 for _ in range(n)];rows.append(dict(id=i,**calc(s,e)))
# Exact rational covariance identities independent of floating softmax.
p=[F(1,10),F(2,10),F(3,10),F(4,10)];e=[F(-2),F(1),F(4),F(0)];H=[[((p[i] if i==j else 0)-p[i]*p[j]) for j in range(4)] for i in range(4)];check(all(sum(row)==0 for row in H));qf=sum(e[i]*H[i][j]*e[j] for i in range(4) for j in range(4));ve=sum(p[i]*e[i]**2 for i in range(4))-sum(p[i]*e[i] for i in range(4))**2;check(qf==ve)
# Closed binary formula, gauge, temperature and saturation boundaries.
boundaries=[]
for a in [0,.01,.5,1]:
 r=calc([0,0],[a,-a]);check(abs(r['kl']-math.log(math.cosh(a)))<=tol);boundaries.append(dict(kind='binary-logcosh',a=a,**r))
for c in [-10,0,10]:
 r=calc([1,-1,0],[c]*3);check(abs(r['kl'])<=tol);boundaries.append(dict(kind='gauge',**r))
saturation=[]
for M in [5,10,20,30]:
 s=[M,0];e=[1,0];p=soft(s);q=soft([M+1,0]);v=math.fsum(a*(math.log(a)-math.log(b)) for a,b in zip(p,q));saturation.append(dict(M=M,kl=v,centered_norm2=.5));check(v>=-tol)
check(all(a['kl']>b['kl'] for a,b in zip(saturation,saturation[1:])))
for tau in [.5,1,2]:
 r=calc([0,0],[1/tau,-1/tau]);check(abs(r['kl']-math.log(math.cosh(1/tau)))<=tol);boundaries.append(dict(kind='temperature',tau=tau,**r))
(D/'raw.json').write_text(json.dumps(dict(cases=rows,boundaries=boundaries,saturation=saturation,rational_variance=str(ve),notes='public developer cases; changing masks/greedy excluded by mathematical premise'),indent=2)+'\n')
(D/'summary.json').write_text(json.dumps(dict(cases=len(rows),boundary_cases=len(boundaries),saturation_cases=len(saturation),assertions=count,status='producer-checks-only-pending-independent',max_integral_error=max(abs(x['kl']-x['path_integral']) for x in rows)),indent=2)+'\n')
(D/'environment.json').write_text(json.dumps(dict(python=sys.version,platform=platform.platform(),processor=platform.processor(),arithmetic='stdlib float64 + Fraction covariance',models=0,GPU=False,formal=False),indent=2)+'\n')
print('producer checks',count,'pending independent')
