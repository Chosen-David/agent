"""Exact finite toy checks only. No model inference and no performance measurement."""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

checks=[]
def check(name, actual, expected):
    assert actual == expected, (name,actual,expected)
    checks.append({'name':name,'actual':str(actual),'expected':str(expected),'passed':True})

def corrected(p,q):
    accepted=[F(0)]*len(p)
    reject=F(0)
    for i,qi in enumerate(q):
        if qi==0: continue
        a=min(F(1),p[i]/qi)
        accepted[i]+=qi*a
        reject+=qi*(1-a)
    residual=[max(F(0),pi-qi) for pi,qi in zip(p,q)]
    z=sum(residual)
    assert z==reject
    if z==0: return accepted,accepted,reject,None
    r=[x/z for x in residual]
    return [a+reject*ri for a,ri in zip(accepted,r)],accepted,reject,r

p=[F(3,5),F(2,5)];q=[F(9,10),F(1,10)]
y,accepted,reject,r=corrected(p,q)
check('two_token_corrected_output',y,p)
check('two_token_accepted_mass',accepted,[F(3,5),F(1,10)])
check('two_token_rejection_mass',reject,F(3,10))
check('two_token_residual',r,[F(0),F(1)])
check('wrong_resample_from_target',[a+reject*pi for a,pi in zip(accepted,p)],[F(39,50),F(11,50)])
check('greedy_output',[F(1),F(0)],[F(1),F(0)])
assert [F(1),F(0)]!=p
for i,j in product(range(6),repeat=2):
    pp=[F(i,5),1-F(i,5)];qq=[F(j,5),1-F(j,5)]
    check(f'binary_grid_p{i}_q{j}',corrected(pp,qq)[0],pp)
check('truncated_draft_support',corrected(p,[F(1),F(0)])[0],p)
check('equal_distributions_skip_residual',corrected(p,p)[3],None)

gamma=8;alpha=F(9,10);cost_step=gamma*F(1,5)+4;cost_batch=F(1,5)+4

def prefix_length(bits):
    n=0
    for b in bits:
        if not b: break
        n+=1
    return n

iid=[]
for bits in product((False,True),repeat=gamma):
    pr=F(1)
    for b in bits: pr*=alpha if b else 1-alpha
    iid.append((bits,pr))
perfect=[((True,)*8,F(9,10)),((False,)*8,F(1,10))]
disjoint=[((True,)*8,F(1,5))]
for j in range(8):
    bits=[True]*8;bits[j]=False;disjoint.append((tuple(bits),F(1,10)))

def expectation(dist):
    return sum(prob*(prefix_length(bits)+1) for bits,prob in dist)
for name,dist in [('iid',iid),('correlated',perfect),('disjoint_failures',disjoint)]:
    check(name+'_total_probability',sum(prob for _,prob in dist),F(1))
    check(name+'_each_marginal',[sum(pr for bits,pr in dist if bits[j]) for j in range(8)],[alpha]*8)
    tails=1+sum(sum(pr for bits,pr in dist if all(bits[:j])) for j in range(1,9))
    check(name+'_tail_sum',expectation(dist),tails)
check('iid_E_L',expectation(iid),sum(alpha**i for i in range(9)))
check('correlated_E_L',expectation(perfect),F(41,5))
check('disjoint_failures_E_L',expectation(disjoint),F(27,5))
check('per_token_draft_cost',cost_step,F(28,5))
check('batch_draft_cost',cost_batch,F(21,5))
assert expectation(disjoint)/cost_step<1
assert F(9)/cost_step<4 and F(9)/cost_batch<4

metrics={
 'expected_tokens_geometric':float(expectation(iid)),
 'speedup_per_token_draft':float(expectation(iid)/cost_step),
 'speedup_per_batch_draft':float(expectation(iid)/cost_batch),
 'upper_bound_per_token_draft':float(F(9)/cost_step),
 'upper_bound_per_batch_draft':float(F(9)/cost_batch),
 'committed_over_proposed_90pct_E_L':8.2,
 'committed_over_proposed_90pct_speedup_per_token_draft':float(F(41,5)/cost_step),
 'committed_over_proposed_90pct_speedup_per_batch_draft':float(F(41,5)/cost_batch),
 'same_marginal_correlated_E_L':float(expectation(perfect)),
 'same_marginal_disjoint_failures_E_L':float(expectation(disjoint)),
 'same_marginal_disjoint_failures_speedup':float(expectation(disjoint)/cost_step),
 'allowed_extra_overhead_T_for_any_gain_geometric':float(expectation(iid)-cost_step),
}
result={'status':'passed','check_count':len(checks),'scope':'Exact rational finite examples; no GPU, inference, install, statistical benchmark or formal proof','metrics':metrics,'checks':checks}
path=Path(__file__).parent/'evidence'/'example-checks.json';path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','check_count','scope','metrics']},ensure_ascii=False,indent=2))
