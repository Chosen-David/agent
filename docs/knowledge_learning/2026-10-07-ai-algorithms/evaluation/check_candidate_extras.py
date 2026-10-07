#!/usr/bin/env python3
"""Post-freeze supplemental checks for candidate-specific claims, not blind tests."""
from fractions import Fraction as F
from itertools import permutations,product
from collections import defaultdict
from pathlib import Path
import json,hashlib
from check_math import simplex,parts,kernel,stringify

base=Path(__file__).parent
rows=[]
# Independent derivation for point-proposal elimination.
def eliminate(p,order):
    output=[F(0)]*len(p);mass=F(1);u=p
    for c in order:
        if not mass:break
        output[c]+=mass*u[c];mass*=1-u[c]
        if mass:
            z=1-u[c];u=tuple(F(0) if i==c else x/z for i,x in enumerate(u))
    for i,x in enumerate(u):output[i]+=mass*x
    return tuple(output)
orders=[perm for k in range(4) for perm in permutations(range(3),k)]
for p,order in product(simplex(3,6),orders):assert eliminate(p,order)==p
rows.append({'family':'deterministic-candidate-elimination','status':'pass','probability_grid_count':28,'candidate_orders':len(orders),'configurations':28*len(orders),'includes_empty_order_and_zero_mass':True})
p=(F(3,5),F(3,10),F(1,10));q=(F(1,5),F(1,2),F(3,10))
assert kernel(p,q)==p
assert kernel(p,q,wrong_target_fallback=True)==(F(11,25),F(21,50),F(7,50))
assert eliminate(p,(1,2))==p
rows.append({'family':'candidate-worked-examples','status':'pass','wrong_fallback':kernel(p,q,wrong_target_fallback=True),'elimination_output':eliminate(p,(1,2))})
def length(a,g):return sum(a**i for i in range(g+1))
a,c,g=F(4,5),F(1,10),4
assert length(a,g)==F(2101,625)
assert length(a,g)/(g*c+1)==F(2101,875)
assert length(a,g)/(g*c+4)==F(191,250)
assert length(F(1,2),20)/(20*F(1,10)+1)<F(2,3)
settings=0
for a,c in product([F(i,5) for i in range(6)],[F(i,5) for i in range(11)]):
    if a>c:assert length(a,1)/(1+c)>1
    for g in range(1,21):
        if a<=c:assert length(a,g)<=g*c+1
    settings+=1
rows.append({'family':'candidate-cost-examples-and-threshold','status':'pass','alpha_cost_settings':settings,'horizons_checked':list(range(1,21)),'positive_speed':F(2101,875),'negative_speed':F(191,250),'proof_scope':'Threshold proof reviewed algebraically: sum(alpha**i,i=1..gamma)<=gamma*alpha, gamma=1 gives sufficiency. Finite checks supplement, not prove, the universal statement.'})
# Seeing a current coin before selecting a proposal is an independent counterexample.
# p=(1/2,1/2). U<=1/2: pick 0, accept. U>1/2: pick 1,
# reject with that same U then fallback to 0. Output always 0.
peeked_output=(F(1),F(0));assert peeked_output!=(F(1,2),F(1,2))
rows.append({'family':'lookahead-at-acceptance-coin-counterexample','status':'pass','target':(F(1,2),F(1,2)),'wrong_output':peeked_output,'scope':'Confirms need for candidate choice independent of current acceptance coin; not an allegation about the cited runtime.'})
result={'schema_version':1,'scope':'Four supplemental post-candidate-review families. Not frozen blind tasks, not formal proof, no upstream/runtime execution.','all_passed':True,'families':rows,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(base/'candidate_extra_results.json').write_text(json.dumps(stringify(result),ensure_ascii=False,indent=2)+'\n')
print('4 supplemental families passed')
