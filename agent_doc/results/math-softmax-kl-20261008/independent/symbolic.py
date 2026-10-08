from fractions import Fraction as F
from pathlib import Path
import json
I=Path(__file__).parent;D=I.parent
p=list(map(F,['1/10','2/10','3/10','4/10']));e=list(map(F,[-2,1,4,0]))
H=[[int(i==j)*p[i]-p[i]*p[j] for j in range(4)] for i in range(4)]
pair=sum(p[i]*p[j]*(e[i]-e[j])**2 for i in range(4) for j in range(i))
assert pair==F(json.loads((D/'raw.json').read_text())['rational_variance'])
assert all(sum(r)==0 for r in H)
assert sum(e[i]*H[i][j]*e[j] for i in range(4) for j in range(4))==pair
assert sum((e[i]+17)*H[i][j]*(e[j]+17) for i in range(4) for j in range(4))==pair
# Exact rank by row reduction, independent of spectral assertion.
a=[r[:] for r in H];rank=0
for c in range(4):
 pivot=next((r for r in range(rank,4) if a[r][c]),None)
 if pivot is None:continue
 a[rank],a[pivot]=a[pivot],a[rank];z=a[rank][c];a[rank]=[v/z for v in a[rank]]
 for r in range(4):
  if r!=rank:
   z=a[r][c];a[r]=[u-z*v for u,v in zip(a[r],a[rank])]
 rank+=1
assert rank==3
assert [[F(1)-F(1)*F(1)]]==[[0]]
# Mask case is genuinely outside the finite-logit domain and KL is infinite.
mask_p=[F(1,2),F(1,2)];mask_q=[F(1),F(0)]
assert any(a>0 and b==0 for a,b in zip(mask_p,mask_q))
(I/'symbolic-result.json').write_text(json.dumps({'status':'pass','exact_pairwise_variance':str(pair),'Fisher_rank':rank,'row_sums_zero':True,'gauge_direction_invariance':True,'n1_Fisher_zero':True,'mask_support_infinite_KL':True},indent=2)+'\n')
