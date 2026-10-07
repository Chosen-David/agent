"""Independent exact review of cooling and finite-prefix extrapolation."""
from fractions import Fraction as F
from pathlib import Path
import json
p=Path(__file__).resolve().parent
checks=[]
def check(label,ok,evidence):
 if not ok: raise AssertionError(label)
 checks.append({'id':label,'passed':True,'evidence':evidence})
q=F(3,4); ambient=F(20); initial=F(36); tol=F(1,100)
def T(n): return ambient+(initial-ambient)*q**n
# Determine stopping using closed form, separately from recurrence iteration.
t=next(i for i in range(100) if 4*q**i<=tol)
r=T(t)-T(t+1); result=T(t+1); err=result-ambient
check('CROSS-C01',t==21 and 4*q**(t-1)>tol and r<=tol,{'first_t':t,'returned_index':t+1,'previous_residual':str(4*q**(t-1))})
check('CROSS-C02',err==3*r and err<=F(3,100),{'residual':str(r),'returned':str(result),'error':str(err),'error_decimal':float(err)})
# Endpoint proof of image plus affine monotonicity, stated in review.
G=lambda x: ambient+q*(x-ambient)
check('CROSS-C03',G(20)==20 and G(36)==32 and 0<q<1,{'image_endpoints':[str(G(20)),str(G(36))],'factor':str(q)})
x=initial
for i in range(22): x=G(x)
check('CROSS-C04',x==result,{'recurrence_matches_closed_form':str(x)})
check('CROSS-C05',G(ambient)==ambient and tol/(1-q)==F(4,100) and q*tol/(1-q)==F(3,100),{'old_point_threshold':'0.04','returned_threshold':'0.03'})
# Both Kelvin offset and Fahrenheit scaling preserve the actual dimensionful result.
K=lambda x: x+F(27315,100)
Fa=lambda x: F(9,5)*x+32
check('CROSS-C06',K(ambient)+q*(K(T(t))-K(ambient))==K(result) and K(T(t))-K(result)==r,{'kelvin_error':str(K(result)-K(ambient))})
check('CROSS-C07',Fa(ambient)+q*(Fa(T(t))-Fa(ambient))==Fa(result) and Fa(result)-Fa(ambient)==F(9,5)*err,{'fahrenheit_threshold':str(F(9,5)*F(3,100))})
check('CROSS-C08',(T(t)-ambient)/16==q**t,{'normalized_state':str(q**t)})
# Construct a continuous piecewise-linear function from the claimed nodes;
# evaluate interpolation itself instead of only reading a node dictionary.
z=[F(1,50)*q**i for i in range(4)]
nodes=sorted([(F(0),F(0)),(z[3],F(1)),(z[2],z[3]),(z[1],z[2]),(z[0],z[1]),(F(1),F(1))])
def H(x):
 for (a,u),(b,v) in zip(nodes,nodes[1:]):
  if a<=x<=b: return u+(v-u)*(x-a)/(b-a)
 raise ValueError('outside domain')
check('CROSS-C09',all(H(z[i])==z[i+1] for i in range(3)) and H(z[3])==1,{'prefix':list(map(str,z)),'next':str(H(z[3]))})
slopes=[(v-u)/(b-a) for (a,u),(b,v) in zip(nodes,nodes[1:])]
check('CROSS-C10',all(0<=u<=1 for _,u in nodes) and all(0<=H((a+b)/2)<=1 for (a,_),(b,_) in zip(nodes,nodes[1:])) and H(0)==0 and H(1)==1,{'slopes':list(map(str,slopes)),'fixed_points':['0','1']})
ratio=abs(H(z[2])-H(z[3]))/abs(z[2]-z[3])
check('CROSS-C11',ratio==F(3173,9)>1,{'violating_lipschitz_ratio':str(ratio)})
producer=json.loads((p.parent/'producer/verification-output.json').read_text())['cooling']
check('CROSS-C12',F(producer['observed_residual_C'])==r and F(producer['returned_C'])==result and F(producer['actual_returned_error_C'])==err and producer['returned_index']==t+1,{'producer_exact_values_match_independent_computation':True})
print(json.dumps({'status':'passed','checks_passed':len(checks),'checks':checks,'scope':'Exact synthetic model and logical counterexample; finite arithmetic checks supplement algebra, no observed physical or agent experiment.'},indent=2))
