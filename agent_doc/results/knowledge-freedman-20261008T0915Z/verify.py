"""Finite synthetic development checks, not a proof or a production verifier."""
from collections import defaultdict
from fractions import Fraction as F
import json
import math
from pathlib import Path


def bound(x, v, r):
    if not (x >= 0 and v > 0 and r > 0):
        raise ValueError('require x>=0, v>0, R>0')
    return math.exp(-x*x/(2*(v+r*x/3)))


def adaptive_tree(n, x, cap):
    live = {(F(0), F(0)): F(1)}
    hit = F(0)
    max_mean_error = F(0)
    for _ in range(n):
        nxt = defaultdict(F)
        for (s, v), mass in live.items():
            a = F(1, 2) if s > 0 else F(1)
            branches = [(a, F(1, 3)), (-a/2, F(2, 3))]
            mean = sum(d*p for d,p in branches)
            variance = sum(d*d*p for d,p in branches)
            max_mean_error = max(max_mean_error, abs(mean))
            assert mean == 0 and max(d for d,p in branches) <= 1
            assert variance == a*a/2
            for d,p in branches:
                ns,nv=s+d,v+variance
                if ns >= x and nv <= cap:
                    hit += mass*p
                else:
                    nxt[ns,nv] += mass*p
        live=nxt
        assert hit+sum(live.values()) == 1
    return hit, max_mean_error


def varying_budget(n):
    live={0:1};hit=0
    for t in range(1,n+1):
        nxt=defaultdict(int);hit *= 2
        for s,c in live.items():
            for ns in (s-1,s+1):
                if ns >= 2 and (ns-2)**2 >= 6*t:
                    hit += c
                else:
                    nxt[ns] += c
        live=nxt
        assert hit+sum(live.values()) == 2**t
    return F(hit,2**n)


def main():
    checks=[]
    for n in (4,8,12):
        for x,cap in ((F(1),F(1)),(F(2),F(3)),(F(5,2),F(4))):
            p,err=adaptive_tree(n,x,cap);b=bound(float(x),float(cap),1)
            assert float(p) <= b
            checks.append({'kind':'adaptive_positive','n':n,'x':str(x),'v':str(cap),'probability_exact':str(p),'bound_float':b,'conditional_mean_error':str(err)})
    p=varying_budget(1024)
    assert p > F(1,20) and math.exp(-3)<.05
    checks.append({'kind':'reject_varying_budget','n':1024,'probability_exact':str(p),'probability_float':float(p),'false_bound':math.exp(-3),'integer_predicate':'s>=2 and (s-2)^2>=6*n'})
    fake=bound(2,.01,1);assert .25>fake
    checks.append({'kind':'reject_empirical_variance','actual_probability':.25,'false_bound':fake,'true_V2':2,'empirical_variance_on_pp':0})
    fake=bound(99,99,1);assert .01>fake
    checks.append({'kind':'reject_one_sided_flip','actual_probability':.01,'false_bound':fake,'correct_negative_R':99})
    r,v,delta=1,4,.05;L=math.log(1/delta);x=r*L/3+math.sqrt(2*v*L+(r*L/3)**2)
    assert math.isclose(bound(x,v,r),delta,rel_tol=1e-12)
    assert math.isclose(bound(10*x,100*v,10*r),delta,rel_tol=1e-12)
    checks.append({'kind':'threshold_and_units','R':r,'v':v,'delta':delta,'x':x,'scaled_same_bound':True})
    invalid=0
    for args in ((-1,1,1),(1,0,1),(1,1,0)):
        try:bound(*args)
        except ValueError:invalid+=1
    assert invalid==3
    checks.append({'kind':'invalid_domain','rejected':invalid})
    out={'scope':'finite synthetic development checks; floating exponent comparisons not formal proof','checks':checks,'count':len(checks),'passed':True}
    Path(__file__).with_name('checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'count':len(checks),'passed':True,'varying_budget_probability':float(p)}))

if __name__=='__main__':main()
