"""Independent exact-rational and Decimal references; no producer imports."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
from itertools import product
import json,subprocess,sys,hashlib
D=Path(__file__).resolve().parent.parent;O=D/'independent'
raw=json.loads((D/'raw.json').read_text());cfg=json.loads((D/'config.json').read_text())
nchecks=0
for row in raw['deterministic']:
 mu,hat,rr,c,ch=(list(map(F,row[k])) for k in ['mu','hat','radii','cost','cost_hat'])
 h=row['feasible'];oracle=sorted(h,key=lambda i:mu[i])[0];best=sorted(h,key=lambda i:hat[i])[0]
 accepted=[i for i in h if hat[i]-hat[best]<=F(cfg['eta'])]
 assert accepted==row['accepted'];assert [[i,str(mu[i]-mu[oracle])] for i in accepted]==row['regrets']
 assert all(abs(mu[i]-hat[i])<=F(cfg['r']) and abs(mu[i]-hat[i])<=rr[i] for i in range(len(mu)))
 for i in accepted:
  assert mu[i]-mu[oracle]<=2*F(cfg['r'])+F(cfg['eta'])
  assert mu[i]-mu[oracle]<=rr[i]+rr[oracle]+F(cfg['eta']);nchecks+=2
 safe=[i for i in range(len(c)) if ch[i]<=F(2,5)];slack=[i for i in range(len(c)) if c[i]<=F(3,10)]
 assert safe==row['safe'] and slack==row['slack'];assert set(slack)<=set(safe);assert all(c[i]<=F(1,2) for i in safe)
 if safe:
  pick=min(safe,key=lambda i:hat[i]);comp=min(safe,key=lambda i:mu[i]);assert mu[pick]-mu[comp]<=2*F(cfg['r']);nchecks+=1
mins=[];outcome_count=0;exhaustive_profiles=0
with localcontext() as ctx:
 ctx.prec=70
 for row in raw['binomial']:
  n=row['n'];dd=F(row['delta']);delta=Decimal(dd.numerator)/Decimal(dd.denominator)
  rad=((Decimal(6)/delta).ln()/Decimal(2*n)).sqrt()
  assert abs(Decimal(str(row['radius']))-rad)<Decimal('1e-15')
  # recurrence reference avoids producer combination-factor path
  pmf=[F(3,4)**n]
  for k in range(n):pmf.append(pmf[-1]*F(n-k,k+1)/3)
  assert sum(pmf)==1
  fail=F(0);regfail=F(0);sep=[]
  for item,mass in zip(row['outcomes'],pmf):
   k=item['k'];dev=abs(F(k,n)-F(1,4));dv=Decimal(dev.numerator)/Decimal(dev.denominator)
   bad=dv>rad;sep.append(abs(dv-rad));assert F(item['mass'])==mass and F(item['deviation'])==dev and item['event_failure']==bad
   # exact tie rule: candidate0 wins whenever k<=n/2; candidate1 otherwise
   winner=int(2*k>n);reg=F(1,2) if winner else F(0)
   assert item['winner']==winner and F(item['regret'])==reg
   if bad:fail+=mass
   if Decimal(reg.numerator)/Decimal(reg.denominator)>2*rad:regfail+=mass
   outcome_count+=1
  assert fail==F(row['failure_probability'])<=dd and regfail==F(row['regret_failure_probability'])<=dd
  assert min(sep)>Decimal('1e-10');assert abs(Decimal(str(row['threshold_margin']))-min(sep))<Decimal('1e-15');mins.append(str(min(sep)))
  if n<=8:
   probability=F(0)
   for xs in product([0,1],repeat=n):
    k=sum(xs);deviation=abs(F(k,n)-F(1,4));value=Decimal(deviation.numerator)/Decimal(deviation.denominator)
    if value>rad:probability+=F(1,4)**k*F(3,4)**(n-k)
   assert probability==fail;exhaustive_profiles+=1
counter=raw['counterexamples'];assert F(counter['adaptive_singleton']['true_loss_lower'])==1-F(100,10000)
a=counter['mean_not_hard_cost'];assert sum(F(p)*v for p,v in zip(a['probabilities'],a['cost_values']))==a['mean'];assert F(a['single_run_violation'])==F(1,100)
subprocess.run([sys.executable,str(D/'verify.py'),'--out',str(O/'rerun')],check=True)
assert (O/'rerun/raw.json').read_bytes()==(D/'raw.json').read_bytes()
record={'status':'pass','deterministic_rows':len(raw['deterministic']),'independent_regret_assertions':nchecks,'binomial_profiles':len(raw['binomial']),'outcomes':outcome_count,'exhaustive_sequence_profiles':exhaustive_profiles,'min_decimal_threshold_margin':str(min(map(Decimal,mins))),'threshold_precision_digits':70,'rerun_raw_byte_identical':True,'counterexamples':'memorizers/replication/shift/cost-mean reviewed; some are analytic fixtures rather than sampled experiments','limitations':['Public developer fixtures, no holdout or model/GPU/performance claim','Decimal finite threshold agreement is not formal real-arithmetic certification','General theorem reviewed informally, not formal proof']}
(O/'checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
