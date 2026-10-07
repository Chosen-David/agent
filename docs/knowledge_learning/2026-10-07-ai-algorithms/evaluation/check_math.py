#!/usr/bin/env python3
"""Exact CPU checks for independent speculative sampling review; stdlib only.
Finite enumeration is not a formal proof or an independent statistical sample.
Run: python check_math.py --output math_results.json
"""
from fractions import Fraction as F
from itertools import product
from collections import defaultdict
from pathlib import Path
import argparse, json, hashlib, datetime

ZERO,ONE=F(0),F(1)
def dist(*xs): return tuple(F(x) for x in xs)
def simplex(k,den):
    if k==1:
        yield (F(den,den),); return
    for xs in product(range(den+1),repeat=k-1):
        if sum(xs)<=den: yield tuple(F(x,den) for x in (*xs,den-sum(xs)))
def validate(p):
    if not p or any(x<0 for x in p) or sum(p)!=1: raise ValueError('not a distribution')
def parts(p,q):
    validate(p);validate(q)
    if len(p)!=len(q): raise ValueError('alphabet mismatch')
    accepted=tuple(min(a,b) for a,b in zip(p,q))
    alpha=sum(accepted); z=ONE-alpha
    residual=None if not z else tuple(max(a-b,ZERO)/z for a,b in zip(p,q))
    return accepted,alpha,residual

def kernel(p,q,actual=None,wrong_target_fallback=False):
    """Enumerate actual draw + accept/reject; q is distribution used in ratios."""
    actual=q if actual is None else actual
    validate(actual); _,_,r=parts(p,q)
    out=[ZERO]*len(p)
    for x,mass in enumerate(actual):
        if not mass: continue  # never divide by q on an impossible proposal
        if not q[x]: raise ValueError('actual proposal outside declared q support')
        a=min(ONE,p[x]/q[x]);out[x]+=mass*a
        if a<1:
            fallback=p if wrong_target_fallback else r
            if fallback is None: raise ValueError('rejected with zero correction mass')
            for y,ry in enumerate(fallback): out[y]+=mass*(1-a)*ry
    return tuple(out)

def sequence_distribution(p,q,n,gamma):
    """Enumerate draft paths, coins, correction, discarded suffix, and restart.
    All probability tables are keyed by the actual emitted prefix.
    Draft suffix after a rejection is ignored; correction ends this block.
    """
    calls=0
    def block(h,left):
        nonlocal calls
        calls+=1
        k=min(gamma,left)
        paths={():ONE}
        for _ in range(k):
            new=defaultdict(F)
            for path,mass in paths.items():
                for x,prob in enumerate(q[h+path]):
                    if prob:new[path+(x,)]+=mass*prob
            paths=new
        outputs=defaultdict(F)
        for path,pathmass in paths.items():
            survived=pathmass
            for i,x in enumerate(path):
                ph=h+path[:i]; pi,qi=p[ph],q[ph]
                a=min(ONE,pi[x]/qi[x])
                if a<1:
                    r=parts(pi,qi)[2]
                    for y,ry in enumerate(r):
                        if ry:outputs[path[:i]+(y,)]+=survived*(1-a)*ry
                survived*=a
                if not survived:break
            if survived:
                if k==left: outputs[path]+=survived
                else:
                    for y,py in enumerate(p[h+path]):
                        if py:outputs[path+(y,)]+=survived*py
        assert sum(outputs.values())==1
        return outputs
    def advance(h,left):
        if not left:return {h:ONE}
        result=defaultdict(F)
        for new,mass in block(h,left).items():
            for final,prob in advance(h+new,left-len(new)).items():result[final]+=mass*prob
        return dict(result)
    return advance((),n),calls

def target_sequences(p,n):
    paths={():ONE}
    for _ in range(n):
        nxt=defaultdict(F)
        for h,mass in paths.items():
            for x,prob in enumerate(p[h]):
                if prob:nxt[h+(x,)]+=mass*prob
        paths=nxt
    return dict(paths)

def prefix_length(bits):
    for i,b in enumerate(bits):
        if not b:return i+1
    return len(bits)+1

def expected_length(joint):return sum(m*prefix_length(b) for b,m in joint.items())
def tails(joint):
    gamma=len(next(iter(joint)))
    return [ONE]+[sum(m for b,m in joint.items() if all(b[:i])) for i in range(1,gamma+1)]
def correlated_joint(gamma):return {tuple([0]*gamma):F(1,2),tuple([1]*gamma):F(1,2)}
def chain_joint(alphas):
    # Independent Bernoulli construction is just one joint realizing these conditional rates.
    return {bits:prod(a if b else 1-a for b,a in zip(bits,alphas)) for bits in product((0,1),repeat=len(alphas))}
def prod(xs):
    r=ONE
    for x in xs:r*=x
    return r

def stringify(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):stringify(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [stringify(v) for v in x]
    return x

def main():
    rows=[]
    def record(name,details):rows.append({'family':name,'status':'pass','details':stringify(details)})
    # One family: exhaustive small rational grid, explicitly not 784 independent trials.
    grid=list(simplex(3,6)); zeros=full=disjoint=0
    for p,q in product(grid,repeat=2):
        m,a,r=parts(p,q)
        assert a==1-sum(abs(x-y) for x,y in zip(p,q))/2
        assert kernel(p,q)==p
        assert sum(kernel(p,q))==1
        zeros+=any(x==0 for x in q)
        if r is None:
            full+=1;assert p==q
        else:assert sum(r)==1 and all(x>=0 for x in r)
        disjoint+=a==0
    record('finite-simplex-kernel',{'alphabet':3,'grid_denominator':6,'distributions':len(grid),'ordered_pairs':len(grid)**2,'proposal_zero_support_pairs':zeros,'full_acceptance_pairs':full,'disjoint_support_pairs':disjoint})
    p,q=dist('1/2','1/3','1/6'),dist('1/4','1/2','1/4')
    m,a,r=parts(p,q);assert a==F(3,4) and r==(1,0,0)
    record('three-symbol-worked-case',{'p':p,'q':q,'accepted_mass':m,'alpha':a,'residual':r,'output':kernel(p,q)})
    p,q=dist('1/2','1/2',0),dist(0,'1/2','1/2')
    assert kernel(p,q)==p and parts(p,q)[2]==(1,0,0)
    p_same=dist(0,'2/5','3/5');assert parts(p_same,p_same)[2] is None
    record('zero-support-and-alpha-one',{'missing-proposal-support-output':kernel(p,q),'equal-distributions-residual':None})
    p,q=dist('3/4','1/4'),dist('1/2','1/2');actual=dist(1,0)
    wrong=kernel(p,q,actual);fixed=kernel(p,actual)
    assert wrong==(1,0) and wrong!=p and fixed==p
    record('actual-proposal-mismatch-counterexample',{'target':p,'reported_q':q,'actual_q':actual,'wrong_output':wrong,'corrected_output':fixed})
    p,q=dist('3/4','1/4'),dist('1/4','3/4')
    wrong=kernel(p,q,wrong_target_fallback=True);assert wrong==dist('5/8','3/8') and wrong!=p
    record('unmodified-target-fallback-counterexample',{'target':p,'wrong_output':wrong,'correct_output':kernel(p,q)})
    p=dist('3/5','2/5');greedy=dist(1,0)
    assert greedy!=p and kernel(greedy,greedy)==greedy
    record('greedy-stochastic-target-boundary',{'stochastic_target':p,'greedy_output':greedy,'valid_greedy_target':greedy})
    head_joint={bits:F(1,4) for bits in product((0,1),repeat=2)};target={(0,0):F(1,2),(1,1):F(1,2)}
    assert head_joint!=target and sum(v for (a,b),v in head_joint.items() if a!=b)==F(1,2)
    selected=defaultdict(F)
    for path,m in head_joint.items():selected[max(path)]+=m
    assert tuple(selected[i] for i in (0,1))==dist('1/4','3/4')
    record('mtp-and-tree-selection-counterexamples',{'independent-head-joint':head_joint,'correlated-target':target,'tree-selected-proposal':dict(selected)})
    # 729 conditional p/q tree pairs, for each two block lengths. Count separately from task families.
    hs=[(),(0,),(1,)];values=[ZERO,F(1,2),ONE];num=0
    for ps in product(values,repeat=3):
        p={h:(x,1-x) for h,x in zip(hs,ps)}
        for qs in product(values,repeat=3):
            q={h:(x,1-x) for h,x in zip(hs,qs)}
            target=target_sequences(p,2)
            for gamma in (1,2):
                result,_=sequence_distribution(p,q,2,gamma);assert result==target
            num+=1
    # A non-symmetric three-token table exercises first/second rejection, bonus, correction/restart.
    hs=[()]+[(x,) for x in (0,1)]+list(product((0,1),repeat=2))
    pv=map(F,['1/3','3/4','1/5','2/3','1/4','4/5','1/2'])
    qv=map(F,['2/3','1/4','4/5','1/3','3/4','1/5','1/2'])
    p={h:(x,1-x) for h,x in zip(hs,pv)};q={h:(x,1-x) for h,x in zip(hs,qv)}
    result,calls=sequence_distribution(p,q,3,2);target=target_sequences(p,3);assert result==target
    record('short-autoregressive-sequence-enumeration',{'binary-depth1-target-proposal-table-pairs':num,'block_lengths_per_pair':[1,2],'non-symmetric-three-token-output':result,'three-token-enumerated-block_calls':calls})
    joint=correlated_joint(3);ts=tails(joint);expect=expected_length(joint)
    naive=sum(F(1,2)**i for i in range(4));assert expect==sum(ts)==F(5,2) and naive==F(15,8)
    anti={(1,0):F(1,2),(0,1):F(1,2)}
    assert expected_length(anti)==F(3,2)!=F(7,4)
    record('marginal-vs-conditional-acceptance',{'correlated_tails':ts,'correct_mean':expect,'iid-from-marginals-wrong':naive,'anticorrelated_mean':expected_length(anti)})
    alphas=dist('1/2','3/4','2/3') # A tuple of rates, not a distribution.
    joint=chain_joint(alphas);ts=tails(joint);expect=expected_length(joint)
    assert expect==sum(ts)==F(17,8) and ts==[ONE,F(1,2),F(3,8),F(1,4)]
    # Exhaust every binary event law on 3 events with mass denominator 2 (36 laws).
    event_vectors=list(product((0,1),repeat=3));event_laws=0
    for mass in simplex(8,2):
        law={b:m for b,m in zip(event_vectors,mass) if m}
        assert expected_length(law)==sum(tails(law));event_laws+=1
    zero_law={(0,0,0):ONE};assert tails(zero_law)==[ONE,ZERO,ZERO,ZERO]
    record('conditional-tail-identity',{'conditional_rates':alphas,'tails':ts,'expected_length':expect,'arbitrary_event_laws':event_laws,'zero-survival-tails':tails(zero_law)})
    good_cost=3*F(2)+F(10);bad_cost=3*F(2)+F(20);baseline=F(10)
    assert good_cost/expect==F(128,17) and baseline*expect/good_cost==F(85,64)
    assert bad_cost/expect==F(208,17) and baseline*expect/bad_cost==F(85,104)<1
    # When cost is random, average per-round L/C is not long-run reward/cost.
    rounds=[(F(1),F(1)),(F(3),F(9))]
    mean_round_rate=sum(l/c for l,c in rounds)/2;renewal_rate=sum(l for l,c in rounds)/sum(c for l,c in rounds)
    assert mean_round_rate==F(2,3) and renewal_rate==F(2,5)
    record('cost-and-renewal-boundaries',{'constant_round_cost_ms':good_cost,'ms_per_token':good_cost/expect,'speed_factor':baseline*expect/good_cost,'slower_verifier_speed_factor':baseline*expect/bad_cost,'mean_round_rate_wrong_for_aggregate':mean_round_rate,'aggregate_reward_cost':renewal_rate})
    raw=F(4);actual=F(1);speed=baseline*actual/good_cost
    eos_expect=sum(F(1,2)**i for i in range(4));assert eos_expect==F(15,8) and speed==F(5,8)
    record('terminal-budget-and-eos-clipping',{'unclipped_output_count':raw,'one-token-request_useful_output':actual,'one-token-request-speed':speed,'eos-half_capped4_expected_output':eos_expect,'cost_model':'3 paid draft calls plus batch verification even if output is clipped'})
    result={'schema_version':1,'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'12 logical check families; exact finite rational enumeration, not formal proof, not independent statistical trials, not model/GPU or production performance.','families':rows,'family_count':len(rows),'all_passed':all(x['status']=='pass' for x in rows),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'families':len(rows),'passed':result['all_passed'],'output':str(args.output)},ensure_ascii=False))
if __name__=='__main__':main()
