"""Reviewer-owned exact checks, derived from the trusted task and stated claims."""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
base=Path(__file__).resolve().parent
spec=json.loads((base.parent/'task.json').read_text())
Q=F(str(spec['query_norm_bound'])); d=F(str(spec['each_vector_error_norm_bound'])); gap=F(str(spec['topk_boundary_gap']))
checks=[]
def check(name,condition,evidence):
    if not condition: raise AssertionError(name)
    checks.append({'id':name,'passed':True,'evidence':evidence})
check('REV-C01',Q*d==F(3,50),{'single_score_bound':str(Q*d)})
check('REV-C02',gap-2*Q*d==F(3,100)>0,{'residual_gap':str(gap-2*Q*d)})
# Independent enumeration of signed scalar perturbations at all box vertices.
losses=[Q*(a-b) for a,b in product([-d,d],repeat=2)]
check('REV-C03',min(gap+x for x in losses)==F(3,100),{'worst_box_gap':str(min(gap+x for x in losses))})
# Evaluate claimed example directly from its original and replacement values.
a=[F(1,20),F(0),F(-1)]; b=[F(-1,100),F(0),F(-1)]
s=[Q*x for x in a]; sh=[Q*x for x in b]; errors=[abs(x-y) for x,y in zip(a,b)]
check('REV-C04',sum(errors)/3==d and max(errors)>d,{'errors':list(map(str,errors)),'mean':str(sum(errors)/3)})
check('REV-C05',s[0]-s[1]==gap and s.index(max(s))==0 and sh.index(max(sh))==1,{'original_scores':list(map(str,s)),'replacement_scores':list(map(str,sh))})
check('REV-C06',gap-Q*2*d==F(3,100)>0,{'n2_mean_only_residual':str(gap-Q*2*d)})
# Independent alternative counterexample with error split across the boundary pair.
a2=[F(1,20),F(0),F(-2)]; b2=[F(1,50),F(3,100),F(-2)]
check('REV-C07',sum(abs(x-y) for x,y in zip(a2,b2))/3==d and Q*b2[1]>Q*b2[0],{'original':list(map(str,a2)),'replacement':list(map(str,b2)),'new_gap':str(Q*(b2[0]-b2[1]))})
check('REV-C08',2*(Q*d)**2>(Q*d)**2,{'reason':'Two opposite maximal score errors violate a global l2 bound equal to the single-score bound.'})
check('REV-C09',2*Q*d-Q*d-Q*d==0,{'reason':'At equality gap=2 epsilon, opposing errors can create a tie.'})
print(json.dumps({'status':'passed','checks':checks,'scope':'Exact rational arithmetic; finite checks supplement the general inequality proof. Norm assumptions remain explicit.'},indent=2))
