from pathlib import Path
from fractions import Fraction as F
import json,random,time,platform,sys
D=Path(__file__).parent;cfg=json.loads((D/'config.json').read_text());rng=random.Random(cfg['seed']);start=time.perf_counter();rows=[];assertions=0
for case in range(cfg['cases']):
 n=case%7;x=[F(0),F(0)];y=[F(rng.randint(-3,3),10) for _ in range(2)];e0=max(map(abs,y));B=e0;gains=[];defects=[];stages=[]
 for l in range(n):
  a=[F(rng.randint(-4,4),2) for _ in range(2)];b=[F(rng.randint(-3,3),10) for _ in range(2)];c=[F(rng.randint(-3,3),10) for _ in range(2)]
  x=[a[j]*x[j]+c[j] for j in range(2)];y=[a[j]*y[j]+c[j]+b[j] for j in range(2)]
  L=max(map(abs,a));eps=max(map(abs,b));B=L*B+eps;e=max(abs(y[j]-x[j]) for j in range(2));assert e<=B;assertions+=1;gains.append(L);defects.append(eps);stages.append({'a':list(map(str,a)),'b':list(map(str,b)),'c':list(map(str,c)),'error':str(e),'bound':str(B)})
 product=F(1);expanded=F(0)
 for l in reversed(range(n)):expanded+=product*defects[l];product*=gains[l]
 expanded+=product*e0;assert expanded==B;assertions+=1
 rows.append({'case':case,'n':n,'e0':str(e0),'stages':stages,'expanded':str(expanded)})
# Scalar signed affine exact examples; documented nonlinear boundary constructions.
boundaries={'early_error':str(10*F(1,100)),'late_error':str(F(1,100)),'cancellation_error':'0','cancellation_bound':str(F(1,5)),'point_jacobian_false_bound':'0','square_actual':str(F(1,10)**2),'square_segment_bound':str(F(1,5)*F(1,10)),'teacher_false_bound':'0','teacher_actual':str(100*F(1,10)),'relative_drift_before':'1','relative_drift_after':str(F(2,100)),'absolute_drift_before':'1','absolute_drift_after':'2'}
assert F(boundaries['square_actual'])>0;assert F(boundaries['teacher_actual'])>0;assert F(boundaries['early_error'])>F(boundaries['late_error']);assertions+=3
contractions=[]
for rho in [F(0),F(1,2),F(1),F(2)]:
 for n in range(7):
  eps=F(1,10);e0=F(1,5);v=e0
  for _ in range(n):v=rho*v+eps
  closed=rho**n*e0+(n*eps if rho==1 else eps*(1-rho**n)/(1-rho));assert v==closed;assertions+=1;contractions.append({'rho':str(rho),'n':n,'value':str(v)})
raw={'cases':rows,'boundaries':boundaries,'contractions':contractions};(D/'raw.json').write_text(json.dumps(raw,separators=(',',':'))+'\n');(D/'summary.json').write_text(json.dumps({'cases':len(rows),'contraction_cases':len(contractions),'assertions':assertions,'elapsed_seconds':time.perf_counter()-start,'scope':cfg['scope']},indent=2)+'\n');(D/'environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'arithmetic':'Fraction rational exact; no floating norms','model_calls':0,'GPU_calls':0,'formal_checks':0},indent=2)+'\n')
