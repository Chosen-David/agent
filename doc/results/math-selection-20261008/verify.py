"""Public finite developer checks; no model, Monte Carlo, formal proof or production API."""
import json,random,math,platform,sys,time,argparse
from fractions import Fraction as F
from pathlib import Path

def check(out):
 D=Path(__file__).parent;cfg=json.loads((D/'config.json').read_text());out.mkdir(parents=True,exist_ok=True);rng=random.Random(cfg['seed']);r=F(cfg['r']);eta=F(cfg['eta']);rows=[];count=0;t=time.perf_counter()
 for case in range(cfg['deterministic_cases']):
  mu=[F(rng.randint(0,100),100) for _ in range(cfg['candidates'])];hat=[x+F(rng.randint(-10,10),100) for x in mu]
  feasible=[i for i in range(len(mu)) if rng.randrange(2)] or [0]
  optimum=min(mu[i] for i in feasible);emp_min=min(hat[i] for i in feasible)
  accepted=[i for i in feasible if hat[i]<=emp_min+eta]
  regrets=[]
  for i in accepted:
   excess=mu[i]-optimum;assert excess<=2*r+eta;count+=1;regrets.append([i,str(excess)])
  # Heterogeneous bounds do NOT replace r_selected+r_oracle by min(radius).
  radii=[abs(x-y)+F(rng.randrange(3),100) for x,y in zip(mu,hat)];oracle=min(feasible,key=lambda i:mu[i])
  for i in accepted: assert mu[i]-mu[oracle]<=radii[i]+radii[oracle]+eta;count+=1
  costs=[F(rng.randrange(101),100) for _ in mu];s=F(1,10);cost_hat=[x+F(rng.randint(-10,10),100) for x in costs];budget=F(1,2)
  safe=[i for i,x in enumerate(cost_hat) if x+s<=budget];slack=[i for i,x in enumerate(costs) if x<=budget-2*s]
  assert all(costs[i]<=budget for i in safe);assert set(slack)<=set(safe);count+=2
  rows.append({'case':case,'mu':list(map(str,mu)),'hat':list(map(str,hat)),'feasible':feasible,'accepted':accepted,'regrets':regrets,'radii':list(map(str,radii)),'cost':list(map(str,costs)),'cost_hat':list(map(str,cost_hat)),'safe':safe,'slack':slack})
 # All possible counts of Z~Bernoulli(1/4), candidate losses Z,1-Z,1/2 share same sample.
 tails=[];p=F(cfg['p']);M=3
 for n in cfg['binomial_n']:
  for delta_text in cfg['delta']:
   delta=F(delta_text);rad=math.sqrt(math.log(2*M/float(delta))/(2*n));fail=F(0);bad_regret=F(0);minsep=1.;outcomes=[]
   for k in range(n+1):
    mass=math.comb(n,k)*p**k*(1-p)**(n-k);mu=[p,1-p,F(1,2)];hat=[F(k,n),1-F(k,n),F(1,2)];deviation=abs(F(k,n)-p);sep=abs(float(deviation)-rad);minsep=min(minsep,sep);assert sep>1e-10;count+=1
    violates=float(deviation)>rad
    if violates:fail+=mass
    winner=min(range(M),key=lambda i:(hat[i],i));regret=mu[winner]-min(mu)
    if float(regret)>2*rad:bad_regret+=mass
    outcomes.append({'k':k,'mass':str(mass),'deviation':str(deviation),'event_failure':violates,'winner':winner,'regret':str(regret)})
   assert fail<=delta and bad_regret<=delta;count+=2
   tails.append({'n':n,'delta':delta_text,'radius':rad,'failure_probability':str(fail),'regret_failure_probability':str(bad_regret),'threshold_margin':minsep,'outcomes':outcomes})
 # Refusal fixtures: a data-created singleton memorizer, replicated sample, mean vs one-run bound.
 n=100;single_r=math.sqrt(math.log(40)/(2*n));N=10000;mem_risk_lower=F(N-n,N)
 assert float(mem_risk_lower)>single_r;assert .5>single_r;count+=2
 counter={'adaptive_singleton':{'population_size':N,'calibration_n':n,'empirical_loss':0,'true_loss_lower':str(mem_risk_lower),'incorrect_singleton_radius':single_r,'reason':'candidate function zero on observed IDs and one elsewhere; candidate not frozen'},'replicated_documents':{'n':n,'Z_p':'1/2','all_rows_equal_Z':True,'deviation':'1/2','naive_radius':single_r,'failure_probability':1},'mean_not_hard_cost':{'cost_values':[0,100],'probabilities':['99/100','1/100'],'mean':1,'budget':1,'single_run_violation':'1/100'},'empty_accepted_set':{'action':'return no certified candidate; do not pick least bad and claim safety'},'zero_width':{'radius':0,'strict_failure_test':'>0 not >=0','failure_probability':0},'distribution_shift':{'frozen_loss':'Z','calibration_P_Z1':0,'deployment_P_Z1':1,'calibration_risk':0,'deployment_risk':1}}
 raw={'deterministic':rows,'binomial':tails,'counterexamples':counter}
 (out/'raw.json').write_text(json.dumps(raw,ensure_ascii=False,separators=(',',':'))+'\n');(out/'summary.json').write_text(json.dumps({'deterministic_cases':len(rows),'exact_binomial_profiles':len(tails),'assertions':count,'elapsed_seconds':time.perf_counter()-t,'scope':cfg['scope']},indent=2)+'\n');(out/'environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'arithmetic':'stdlib Fraction exact counts/probability; binary64 log/sqrt only thresholds, separated >1e-10; no formal certification','hardware':'host CPU; no model/GPU'},indent=2)+'\n')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,default=Path(__file__).parent);check(a.parse_args().out)
