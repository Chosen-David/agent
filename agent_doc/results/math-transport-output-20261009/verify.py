"""Frozen scalar development checks; exact feasible transport and dual certificates."""
import json,sys,time
from pathlib import Path
from fractions import Fraction as F
BASE=Path(__file__).resolve().parent

def probability(a):
 if any(x<0 for x in a) or sum(a)!=1:raise ValueError('nonnegative unit mass required')
def certificate(v,a,b):
 probability(a);probability(b);n=len(v);assert len(a)==len(b)==n
 order=sorted(range(n),key=lambda i:(v[i],i));left=a[:];right=b[:];pi=[[F(0) for _ in v] for _ in v];i=j=0
 while i<n and j<n:
  x,y=order[i],order[j];w=min(left[x],right[y]);pi[x][y]+=w;left[x]-=w;right[y]-=w
  if left[x]==0:i+=1
  if right[y]==0:j+=1
 assert [sum(row) for row in pi]==a and [sum(pi[i][j] for i in range(n)) for j in range(n)]==b
 c=[[abs(x-y) for y in v] for x in v];primal=sum(pi[i][j]*c[i][j] for i in range(n) for j in range(n))
 f=[F(0)]*n;cum=F(0)
 for h in range(n-1):
  x,y=order[h:h+2];cum+=a[x]-b[x];sign=(cum>0)-(cum<0);f[y]=f[x]-sign*(v[y]-v[x])
 assert all(f[i]-f[j]<=c[i][j] for i in range(n) for j in range(n))
 dual=sum((a[i]-b[i])*f[i] for i in range(n));assert dual==primal
 return {'pi':[[str(x) for x in row] for row in pi],'f':list(map(str,f)),'g':list(map(str,[-x for x in f])),'primal':str(primal),'dual':str(dual)},primal

def main():
 start=time.perf_counter();cfg=json.loads((BASE/'fixtures.json').read_text());rows=[]
 for t in cfg['cases']:
  tid=t['id']
  if tid=='T7':
   refusals=[]
   for a in t['invalid_alpha']:
    try:probability(list(map(F,a)))
    except ValueError:refusals.append(True)
    else:refusals.append(False)
   pi=[[F(x) for x in z] for z in t['invalid_pi']];a=b=list(map(F,t['beta']));marginals=[sum(z) for z in pi]==a and [sum(pi[i][j] for i in range(2)) for j in range(2)]==b
   assert all(refusals) and not marginals;rows.append({'id':tid,'invalid_probability_rejected':refusals,'invalid_marginal_rejected':not marginals,'passed':True});continue
  if tid=='T8':
   q,e,lam=map(F,[t['Q'],t['E'],t['ridge']]);true=(q*e)**2;metric=e*e*(q*q+lam);assert true==F(t['expected_true_logit_squared']) and metric==F(t['expected_ridge_metric_squared']) and metric-true==lam*e*e
   rows.append({'id':tid,'true_logit_squared':str(true),'ridge_metric_squared':str(metric),'extra_penalty':str(metric-true),'exact_equality_rejected':metric!=true,'passed':True});continue
  a,b=list(map(F,t['alpha'])),list(map(F,t['beta']));v=list(map(F,t['values']));cert,cost=certificate(v,a,b);base_error=abs(sum((a[i]-b[i])*v[i] for i in range(len(v))));tv=sum(abs(a[i]-b[i]) for i in range(len(v)))/2;dtv=(max(v)-min(v))*tv;assert base_error<=cost<=dtv
  approx=list(map(F,t.get('values_hat',t['values'])));error=abs(sum(a[i]*v[i]-b[i]*approx[i] for i in range(len(v))));perturb=sum(b[i]*abs(v[i]-approx[i]) for i in range(len(v)));assert error==F(t['expected_error']) and error<=cost+perturb
  row={'id':tid,'certificate':cert,'base_error':str(base_error),'actual_error':str(error),'DTV':str(dtv),'value_perturbation':str(perturb),'combined_bound':str(cost+perturb),'passed':True}
  if 'expected_cost' in t:assert cost==F(t['expected_cost'])
  if 'expected_DTV' in t:assert dtv==F(t['expected_DTV'])
  if 'expected_combined_bound' in t:assert cost+perturb==F(t['expected_combined_bound'])
  if tid=='T2':row['cross_domain_units']='force N; probability mass dimensionless; cost/output both N'
  if tid=='T5':
   features=list(map(F,t['features']));fc,wrongcost=certificate(features,a,b);assert wrongcost==F(t['feature_cost'])==0 and error>0;assert any(features[i]==features[j] and v[i]!=v[j] for i in range(len(v)) for j in range(len(v)))
   row.update({'feature_certificate':fc,'wrong_feature_cost':str(wrongcost),'no_finite_lipschitz_on_equal_features':True,'unverified_value_bound_rejected':True})
  rows.append(row)
 assert [x['id'] for x in rows]==['T'+str(i) for i in range(1,9)]
 dest=Path(sys.argv[1]) if len(sys.argv)>1 else BASE;dest.mkdir(parents=True,exist_ok=True);(dest/'raw.json').write_text(json.dumps({'visibility':'public finite structural math checks; not model/unseen tests','rows':rows,'exact_cases':8,'seconds':time.perf_counter()-start,'model_calls':0,'model_token_cost':'unmeasured; no model experiment'},indent=2)+'\n');print('8 exact public cases passed')
if __name__=='__main__':main()
