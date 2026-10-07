"""Reviewer-authored finite algebra checks. No upstream code, model, or GPU execution."""
from fractions import Fraction as F
from itertools import product, permutations
from collections import defaultdict
import json

simplex=[(F(a,4),F(b,4),F(4-a-b,4)) for a in range(5) for b in range(5-a)]
counts={}
for p,q in product(simplex,repeat=2):
    acc=[q[i]*min(1,p[i]/q[i]) if q[i] else F(0) for i in range(3)]
    z=1-sum(acc)
    residual=[max(F(0),p[i]-q[i]) for i in range(3)]
    assert z==sum(residual)
    if z:
        out=[acc[i]+z*(residual[i]/z) for i in range(3)]
    else:
        assert p==q
        out=acc
    assert tuple(out)==p
    assert sum(acc)==1-sum(abs(p[i]-q[i]) for i in range(3))/2
counts['single_token_distribution_pairs']=len(simplex)**2

orders=[order for k in range(4) for order in permutations(range(3),k)]
for p,order in product(simplex,orders):
    u=list(p);survival=F(1);out=[F(0)]*3
    for x in order:
        if not survival:break
        out[x]+=survival*u[x]
        survival*=1-u[x]
        if not survival:break
        u[x]=0
        z=sum(u)
        assert z>0
        u=[v/z for v in u]
    out=[out[x]+survival*u[x] for x in range(3)]
    assert tuple(out)==p
counts['deterministic_elimination_distribution_orders']=len(simplex)*len(orders)

# Enumerate one-token draft blocks to a 2-token stopped output with history-specific laws.
def stopped_chain(p,q):
    answer=defaultdict(F)
    def visit(h,mass):
        if len(h)>=2:
            answer[h[:2]]+=mass
            return
        ph,qh=p[h],q[h]
        z=sum(max(F(0),a-b) for a,b in zip(ph,qh))
        for x in range(3):
            acc=min(ph[x],qh[x])
            if acc:
                if len(h)==1:
                    visit(h+(x,),mass*acc)
                else:
                    for y,v in enumerate(p[h+(x,)]):
                        if v:visit(h+(x,y),mass*acc*v)
        if z:
            for x in range(3):
                r=max(F(0),ph[x]-qh[x])/z
                if r:visit(h+(x,),mass*z*r)
    visit((),F(1))
    return answer
p={(): (F(1,2),F(1,3),F(1,6)), (0,):(F(0),F(1,4),F(3,4)), (1,):(F(1),F(0),F(0)), (2,):(F(1,3),)*3}
q={(): (F(0),F(1),F(0)), (0,):(F(1),F(0),F(0)), (1,):(F(0),F(0),F(1)), (2,):(F(1,2),F(1,2),F(0))}
actual=stopped_chain(p,q)
expected={(x,y):p[()][x]*p[(x,)][y] for x,y in product(range(3),repeat=2)}
assert all(actual.get(s,F(0))==v for s,v in expected.items())
assert sum(actual.values())==1
counts['autoregressive_stopped_joint_coordinates']=9

for a,c,g in product([F(n,8) for n in range(9)],[F(n,8) for n in range(9)],range(1,21)):
    L=sum(a**j for j in range(g+1)); cost=1+g*c
    if a<=c:assert L<=cost
    if g==1:assert (L>cost)==(a>c)
counts['cost_grid_cases']=9*9*20
assert sum(F(4,5)**j for j in range(5))/F(22,5)==F(191,250)==F('0.764')
counts['corrected_example']=str(F(191,250))
counts['status']='passed'
counts['scope']='Finite exact-rational checks of reviewer-authored semantics; no upstream execution or performance validation.'
print(json.dumps(counts,indent=2))
