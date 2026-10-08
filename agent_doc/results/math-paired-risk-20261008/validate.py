"""Public exact paired-law checks; no general rank optimizer or model trial."""
from fractions import Fraction as F
from pathlib import Path
import json, itertools, time
BASE=Path(__file__).resolve().parent
def dot(x,y):return sum((a*b for a,b in zip(x,y)),F())
def vec(E):return [E[i][j] for j in range(len(E[0])) for i in range(len(E))]
def score(q,E,k):return sum((q[i]*E[i][j]*k[j] for i in range(len(q)) for j in range(len(k))),F())
def risk(law,E):return sum((p*score(q,E,k)**2 for q,k,p in law),F())
def outer(x,y):return [[a*b for b in y] for a in x]
def moment(law):
 z=[([kj*qi for kj in k for qi in q],p) for q,k,p in law];d=len(z[0][0])
 return [[sum((p*x[i]*x[j] for x,p in z),F()) for j in range(d)] for i in range(d)]
def product(law):
 m,n=len(law[0][0]),len(law[0][1]);S=[[sum((p*q[i]*q[j] for q,k,p in law),F()) for j in range(m)] for i in range(m)];T=[[sum((p*k[i]*k[j] for q,k,p in law),F()) for j in range(n)] for i in range(n)]
 return [[T[j][l]*S[i][h] for l in range(n) for h in range(m)] for j in range(n) for i in range(m)]
def quadratic(D,x):return sum((x[i]*D[i][j]*x[j] for i in range(len(x)) for j in range(len(x))),F())
def grad(law,E):return [[sum((p*score(q,E,k)*q[i]*k[j] for q,k,p in law),F()) for j in range(len(E[0]))] for i in range(len(E))]
def sub(A,B):return [[a-b for a,b in zip(x,y)] for x,y in zip(A,B)]
def det2(A):return A[0][0]*A[1][1]-A[0][1]*A[1][0]
def unit(n,i):return [F(int(j==i)) for j in range(n)]
def encoded(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:encoded(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [encoded(v) for v in x]
 return x
def main():
 start=time.perf_counter();paired=[]
 for i in range(2):
  for u,v in itertools.product([-1,1],repeat=2):paired.append(([u*x for x in unit(2,i)],[v*x for x in unit(2,i)],F(1,8)))
 independent=[(unit(3,i),unit(2,j),F(1,6)) for i in range(3) for j in range(2)]
 weak=[(unit(2,i),unit(2,j),F(1 if i==j else 4,10)) for i in range(2) for j in range(2)]
 laws={'paired-zero-cross-covariance':paired,'independent-nonsquare':independent,'weak-dependent-SPD':weak};records=[]
 for name,law in laws.items():
  assert sum(p for q,k,p in law)==1 and all(p>0 for q,k,p in law)
  D,D0=moment(law),product(law);m,n=len(law[0][0]),len(law[0][1])
  for case in range(12):
   E=[[F((case+2*i+3*j)%7-3) for j in range(n)] for i in range(m)];V=[[F((case+3*i+j)%5-2) for j in range(n)] for i in range(m)]
   a=risk(law,E);b=quadratic(D,vec(E));assert a==b
   G=grad(law,E);Dv=[dot(row,vec(E)) for row in D];assert vec(G)==Dv
   h=F(1,1000);plus=[[E[i][j]+h*V[i][j] for j in range(n)] for i in range(m)];minus=[[E[i][j]-h*V[i][j] for j in range(n)] for i in range(m)]
   derivative=(risk(law,plus)-risk(law,minus))/(2*h);assert derivative==2*dot(vec(G),vec(V))
   proxy=quadratic(D0,vec(E));delta=max(sum(abs(D[i][j]-D0[i][j]) for j in range(len(D))) for i in range(len(D)))
   # These D,D0 are diagonal; the max diagonal absolute error is exact spectral norm.
   assert all(D[i][j]==D0[i][j]==0 for i in range(len(D)) for j in range(len(D)) if i!=j)
   assert abs(a-proxy)<=delta*dot(vec(E),vec(E))
   if name=='independent-nonsquare':assert D==D0 and a==proxy
   if name=='weak-dependent-SPD':assert F(2,5)*proxy<=a<=F(8,5)*proxy
   records.append({'id':name+'-'+str(case),'law':law,'E':E,'direction':V,'D':D,'D0':D0,'risk':a,'quadratic':b,'proxy':proxy,'gradient':G,'derivative':derivative,'delta':delta})
 H=[[F(2),F(0)],[F(0),F(1)]];M0=[[F(2),F(0)],[F(0),F(0)]];M1=[[F(2),F(2)],[F(1),F(1)]]
 assert det2(H)==2 and det2(M0)==det2(M1)==0
 assert risk(paired,sub(H,M0))==F(1,2) and risk(paired,sub(H,M1))==0
 assert quadratic(product(paired),vec(sub(H,M0)))==F(1,4) and quadratic(product(paired),vec(sub(H,M1)))==F(5,4)
 cross=[[sum((p*q[i]*k[j] for q,k,p in paired),F()) for j in range(2)] for i in range(2)];assert cross==[[F(),F()],[F(),F()]]
 X=[[F(1),F(1)],[F(1),F(1)]];Y=[[F(1),F(2)],[F(2),F(1)]];assert det2(X)==0 and det2(Y)==-3
 eta=F(3,5);D,D0=moment(weak),product(weak);assert max(abs(D[i][i]/D0[i][i]-1) for i in range(4))==eta
 candidates=[M0,M1,[[F(),F()],[F(),F(1)]],[[F(),F()],[F(),F()]]]
 for M in candidates:assert det2(M)==0 and risk(weak,sub(H,M0))<=4*risk(weak,sub(H,M))
 sensor=[(unit(2,i),[F(3 if i==0 else 5)*x for x in unit(2,i)],F(1,2)) for i in range(2)]
 assert risk(sensor,sub(H,M0))==F(25,2) and risk(sensor,sub(H,M1))==0
 raw={'exact_cases':records,'rank_witness':{'law':paired,'H':H,'proxy_optimal_M':M0,'paired_feasible_M':M1,'proxy_losses':[F(1,4),F(5,4)],'paired_losses':[F(1,2),F()],'zero_cross_covariance':cross,'eta':F(1),'eta_lt_one_certificate':'not applicable'},'whitening_rank_witness':{'X':X,'whitening_diagonal':[1,2,2,1],'reshaped_Y':Y,'det_X':0,'det_Y':-3},'relative_certificate':{'law':weak,'eta':eta,'factor':4,'tested_rank1_candidates':candidates,'claim':'General proof is in card; finite menu is no global paired optimizer'},'sensor':{'law':sensor,'H':H,'proxy_M':M0,'paired_M':M1,'losses_A_squared':[F(25,2),F()],'units':'q dimensionless gain, k volt, H/M siemens, response ampere, risk A^2'},'heavy_tail':'Analytical only: q=k=n with p_n=(1/zeta(4))/n^4 has finite second moments but infinite fourth-score moment; no finite numerical enumeration proves divergence','diagnostic_seconds':time.perf_counter()-start,'limitations':['Exact finite public development fixtures, not proof or model test','No generic eigensolver, moment estimator or global paired rank optimizer','η certificate is known-distribution analytic diagonal case, not estimated population certificate','No unused/model/token/GPU/e2e measurement']}
 (BASE/'raw.json').write_text(json.dumps(encoded(raw),ensure_ascii=False,indent=2)+'\n');print(json.dumps({'exact_cases':len(records),'diagnostic_seconds':raw['diagnostic_seconds']}))
if __name__=='__main__':main()
