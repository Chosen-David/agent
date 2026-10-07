"""Original finite-rational examples; no model, upstream import, or performance run."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
checks = []


def check(name, ok, detail):
    if not ok:
        raise AssertionError(name)
    checks.append({'name': name, 'passed': True, 'detail': detail})


def kernel(p, q):
    """Enumerate probability mass, not random samples or a production sampler."""
    assert sum(p) == sum(q) == 1 and all(x >= 0 for x in (*p, *q))
    accepted = tuple(qx * min(F(1), px / qx) if qx else F(0) for px, qx in zip(p, q))
    rejection = 1 - sum(accepted)
    raw = tuple(max(F(0), px-qx) for px, qx in zip(p, q))
    assert sum(raw) == rejection
    if not rejection:
        return accepted, F(1), None
    residual = tuple(x / rejection for x in raw)
    output = tuple(a + rejection*r for a, r in zip(accepted, residual))
    return output, 1-rejection, residual


p = (F(3,5), F(3,10), F(1,10))
q = (F(1,5), F(1,2), F(3,10))
out, alpha, residual = kernel(p,q)
check('three_token_mass_balance', out == p and alpha == F(3,5) and residual == (1,0,0),
      {'output': list(map(str,out)), 'acceptance': str(alpha), 'residual': list(map(str,residual))})
bad = tuple(min(px,qx) + (1-alpha)*px for px,qx in zip(p,q))
check('unmodified_target_fallback_is_biased', bad == (F(11,25),F(21,50),F(7,50)) and bad != p,
      {'wrong_output': list(map(str,bad))})

grid = [tuple(F(x,6) for x in (a,b,6-a-b)) for a in range(7) for b in range(7-a)]
for pi,qi in product(grid,repeat=2):
    oi,ai,ri = kernel(pi,qi)
    assert oi == pi
    assert ai == 1-sum(abs(x-y) for x,y in zip(pi,qi))/2
    if ri is not None:
        assert sum(ri) == 1
check('all_grid_pairs_exactness_and_tv', True,
      {'distributions': len(grid), 'pairs': len(grid)**2, 'grid_denominator': 6, 'vocabulary': 3})

out,alpha,residual=kernel((F(0),F(1)),(F(1),F(0)))
check('disjoint_support_allowed', out==(0,1) and alpha==0 and residual==(0,1), 'q need not cover target support')
out,alpha,residual=kernel(p,p)
check('equal_distributions_skip_zero_residual', out==p and alpha==1 and residual is None, 'No 0/0 branch evaluated')

def eliminate(p, candidates):
    """Original deterministic-proposal probability enumeration."""
    u = list(p)
    reach = F(1)
    emitted = [F(0)]*len(p)
    for token in candidates:
        if not reach:
            break
        emitted[token] += reach*u[token]
        reject = 1-u[token]
        reach *= reject
        if not reject:
            break
        u = [F(0) if i==token else x/reject for i,x in enumerate(u)]
    for i,x in enumerate(u):
        emitted[i] += reach*x
    return tuple(emitted)

check('deterministic_tree_candidate_elimination', eliminate(p,[1,2])==p,
      'Fixed order b,c; successive point-proposal residuals recover p')
check('greedy_does_not_recover_stochastic_target', (F(1),F(0)) != (F(3,5),F(2,5)),
      'Matching argmax is a different distributional assertion')

def expected_tokens(worlds):
    result = F(0)
    for probability, flags in worlds:
        prefix = 0
        for flag in flags:
            if not flag:
                break
            prefix += 1
        result += probability*(1+prefix)
    return result

corr=expected_tokens([(F(1,2),(0,0)),(F(1,2),(1,1))])
ind=expected_tokens([(F(1,4),flags) for flags in product([0,1],repeat=2)])
anti=expected_tokens([(F(1,2),(0,1)),(F(1,2),(1,0))])
check('same_marginal_different_prefix_yield', (corr,ind,anti)==(2,F(7,4),F(3,2)),
      {'correlated': str(corr), 'independent': str(ind), 'exclusive': str(anti)})

def tokens(alpha,gamma):
    return sum(alpha**i for i in range(gamma+1))

n=tokens(F(4,5),4)
fast=n/(4*F(1,10)+1)
slow=n/(4*F(1,10)+4)
check('verification_cost_reverses_gain', n==F(2101,625) and fast>1 and slow<1,
      {'tokens': str(n), 'ideal_speed_ratio': str(fast), 'costly_verify_ratio': str(slow),
       'ideal_speed_ratio_decimal': float(fast), 'costly_verify_ratio_decimal': float(slow)})
short=tokens(F(1,2),1)/(1+F(1,10))
long=tokens(F(1,2),20)/(1+20*F(1,10))
check('longer_draft_can_lose', short==F(15,11) and long<F(2,3),
      {'short_speed_ratio': str(short), 'long_speed_ratio': str(long)})
check('acceptance_one_endpoint', tokens(F(1),4)==5, 'Finite sum avoids geometric 0/0')
check('equal_alpha_cost_endpoint', tokens(F(1,5),1)/(1+F(1,5))==1 and
      all(tokens(F(1,5),g)/(1+g*F(1,5))<1 for g in range(2,21)),
      'gamma=1 ties; tested gamma 2..20 loses, general result proved in text')

# Averages of per-cycle ratios differ from total reward / total cost.
cycles=[(F(1),F(1)),(F(3),F(9))]
pooled=sum(l for l,c in cycles)/sum(c for l,c in cycles)
mean_ratio=sum(l/c for l,c in cycles)/len(cycles)
check('pooled_rate_not_mean_cycle_ratio', pooled==F(2,5) and mean_ratio==F(2,3),
      {'pooled':str(pooled),'mean_cycle_ratio':str(mean_ratio)})

result={'schema_version':1,'kind':'finite-rational-example-checks','status':'passed',
        'checks':checks,'named_check_count':len(checks),
        'scope':'Original deterministic rational probability/cost examples only; not model sampling, GPU, latency, formal proof, or upstream runtime verification.',
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'named_checks':len(checks),'grid_pairs':len(grid)**2}))
