"""Public deterministic development checks, not a formal proof or model benchmark."""
import argparse
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path
from time import perf_counter


def probability(p):
    if not p or any(x < 0 for x in p) or sum(p) != 1:
        raise ValueError('nonnegative normalized nonempty probability required')


def condition(p, event):
    probability(p)
    if len(event) != len(set(event)) or any(i < 0 or i >= len(p) for i in event):
        raise ValueError('unique legal event indices required')
    a = sum((p[i] for i in event), F(0))
    if a <= 0:
        raise ValueError('positive event mass required')
    return tuple(p[i] / a if i in event else F(0) for i in range(len(p)))


def tv(p, q):
    return sum((abs(x-y) for x,y in zip(p,q)), F(0)) / 2


def kl(q, p):
    terms = []
    for x,y in zip(q,p):
        if x:
            if not y:
                return math.inf
            terms.append(float(x)*math.log(float(x/y)))
    return math.fsum(terms)


def lse(xs):
    if not xs:
        return -math.inf
    m = max(xs)
    return m + math.log(math.fsum(math.exp(x-m) for x in xs))


def mass_from_logs(u,v):
    if u == -math.inf:
        raise ValueError('empty/zero event')
    if v == -math.inf:
        return 1.0
    z = u-v
    return 1/(1+math.exp(-z)) if z >= 0 else math.exp(z)/(1+math.exp(z))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    out=Path(args.output);base=Path(__file__).parent
    cfg=json.loads((base/'validation_plan.json').read_text())['case_config']
    n,total=cfg['n'],cfg['integer_weight_sum'];tol=cfg['float_absolute_tolerance']
    raw=[];counts={};maximum=0.0;start=perf_counter()
    def record(kind, **kw):
        counts[kind]=counts.get(kind,0)+1;raw.append({'kind':kind,**kw})
    vectors=[tuple(F(x,total) for x in w) for w in itertools.product(range(total+1),repeat=n) if sum(w)==total]
    events=[tuple(i for i in range(n) if mask>>i&1) for mask in range(1,1<<n)]
    for pi,p in enumerate(vectors):
        for qi,q in enumerate(vectors):
            for event in events:
                a=sum(p[i] for i in event);b=sum(q[i] for i in event)
                if not a or not b:
                    bad=p if not a else q
                    try: condition(bad,event)
                    except ValueError: pass
                    else: raise AssertionError('zero event accepted')
                    record('zero_event_refusal',p=pi,q=qi,event=event);continue
                delta=tv(p,q);actual=tv(condition(p,event),condition(q,event));bound=min(F(1),delta/max(a,b))
                assert actual<=bound
                record('exact_tv',p=pi,q=qi,event=event,delta=str(delta),a=str(a),b=str(b),actual=str(actual),bound=str(bound))
    for pi,p in enumerate(vectors):
        if not all(p): continue
        for event in events:
            a=sum(p[i] for i in event);pc=condition(p,event)
            assert abs(kl(pc,p)+math.log(float(a)))<=tol
            record('projection_minimum',p=pi,event=event,error=abs(kl(pc,p)+math.log(float(a))))
            for qi,q in enumerate(vectors):
                if any(q[i] for i in range(n) if i not in event):continue
                err=abs(kl(q,p)-(kl(q,pc)-math.log(float(a))));maximum=max(maximum,err);assert err<=tol
                record('kl_decomposition',p=pi,q=qi,event=event,error=err)
            if a<1:assert math.isinf(kl(p,pc));record('forward_kl_infinite',p=pi,event=event)
    for eps in [F(1,10),F(1,10**20)]:
        p=(eps,F(0),1-eps);q=(F(0),eps,1-eps);event=(0,1)
        assert tv(condition(p,event),condition(q,event))==tv(p,q)/max(sum(p[i] for i in event),sum(q[i] for i in event))==1
        record('sharp_amplification',epsilon=str(eps),conditional_tv='1',global_tv=str(eps))
    badcases=[((F(1),),()),((F(1),),(0,0)),((F(1),),(1,)),((F(-1),F(2)),(0,)),((F(1,2),),(0,)),((),())]
    for p,event in badcases:
        try:condition(p,event)
        except ValueError:pass
        else:raise AssertionError('invalid input accepted')
        record('invalid_input_refusal',p=list(map(str,p)),event=event)
    assert math.isinf(kl((F(1),F(0)),(F(0),F(1))))
    record('zero_atom_kl_infinite')
    c=(F(4,5),F(1,5));event=(0,1)
    for a in [F(1,10),F(9,10)]:
        p=(a*c[0],a*c[1],1-a);assert condition(p,event)==(*c,F(0))
        assert p[0]==a*c[0]
        record('sensor_same_conditional_different_global',accepted=str(a),conditional_alarm=str(c[0]),joint_alarm=str(p[0]))
    cases=[([20.,0.],(1,)),([1000.,999.,-1000.],(0,1)),([-1000.,-1001.,1000.],(0,1)),([0.,0.],(0,)),([20.,0.],(0,1))]
    for xs,event in cases:
        u=lse([xs[i] for i in event]);v=lse([xs[i] for i in range(len(xs)) if i not in event]);m=max(xs)
        direct=math.fsum(math.exp(xs[i]-m) for i in event)/math.fsum(math.exp(x-m) for x in xs)
        recovered=mass_from_logs(u,v);err=abs(recovered-direct);maximum=max(maximum,err);assert err<=tol
        record('stable_normalizer',logits=xs,event=event,mass=recovered,direct=direct,error=err)
    far=mass_from_logs(0,20);assert far<1e-8
    record('near_far_counterexample',candidate_far_fraction=1,global_far_mass=far)
    assert condition((F(0),F(1)),(0,1))==(F(0),F(1))
    record('all_support_identity')
    elapsed=perf_counter()-start
    out.parent.mkdir(parents=True,exist_ok=True)
    rawpath=out.with_name(out.stem+'_raw_cases.json');rawpath.write_text(json.dumps(raw,indent=2)+'\n')
    out.write_text(json.dumps({'status':'producer-pending-independent-review','case_count':len(raw),'counts':counts,'max_float_absolute_error':maximum,'exact_violations':0,'elapsed_seconds':elapsed,'timing_scope':'perf_counter CPU arithmetic only, no performance comparison','raw_data':str(rawpath),'development_only':True},indent=2)+'\n')
    print(out.read_text())


if __name__=='__main__':main()
