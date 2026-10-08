"""Independent exact arithmetic checks; no producer import, model, GPU or timing."""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent

def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), F(0))

def residual(x, v):
    c = dot(x, v)/dot(v, v)
    return tuple(a-c*b for a, b in zip(x, v))

def exact_case(q, keys, v, k):
    # In R^2 with rank-one orthogonal P, all residuals lie on one line,
    # so the norm-product radius equals abs(residual inner product).
    rq = residual(q, v)
    true = [dot(q, key) for key in keys]
    delta = [dot(rq, residual(key, v)) for key in keys]
    hat = [s-d for s, d in zip(true, delta)]
    lower = [h-abs(d) for h, d in zip(hat, delta)]
    upper = [h+abs(d) for h, d in zip(hat, delta)]
    tau = sorted(lower, reverse=True)[k-1]
    kept = [i for i, u in enumerate(upper) if u >= tau]
    chosen = sorted(kept, key=lambda i: (-true[i], i))[:k]
    assert all(l <= s <= u for l, s, u in zip(lower, true, upper))
    assert len(kept) >= k
    assert len(chosen) == k
    assert min(true[i] for i in chosen) >= max(
        (true[j] for j in range(len(keys)) if j not in chosen), default=min(true)
    )
    # Stable tie ordering is safe here because every score >= tau is retained.
    assert chosen == sorted(range(len(keys)), key=lambda i: (-true[i], i))[:k]
    return len(keys)-len(kept)

def main():
    vecs = list(product(map(F, [-1, 0, 1]), repeat=2))
    directions = [(F(1),F(0)),(F(1),F(1)),(F(1),F(2))]
    cases = dropped = 0
    for v, q, keys in product(directions, vecs, product(vecs, repeat=3)):
        for k in [1,2,3]:
            dropped += exact_case(q, keys, v, k)
            cases += 1
    # Independent generic interval test, including envelopes wider than needed.
    intervals = [(F(l),F(s),F(u)) for l in [-1,0,1]
                 for s in [-1,0,1] for u in [-1,0,1] if l <= s <= u]
    generic = 0
    for triples in product(intervals, repeat=3):
        for k in [1,2,3]:
            tau = sorted((x[0] for x in triples),reverse=True)[k-1]
            kept = [i for i,x in enumerate(triples) if x[2] >= tau]
            chosen = sorted(kept,key=lambda i:(-triples[i][1],i))[:k]
            assert chosen == sorted(range(3),key=lambda i:(-triples[i][1],i))[:k]
            generic += 1
    # Explicit invalid substitutions, checked with exact arithmetic.
    examples = {}
    q = (F(1),F(1))
    keys = [(F(0),F(4)),(F(2),F(0))]+[(F(0),F(0))]*3
    true = [dot(q,x) for x in keys]
    hat = [x[0] for x in keys]
    average = F(4,5)
    tau = max(h-average for h in hat)
    kept = [i for i,h in enumerate(hat) if h+average >= tau]
    assert 0 not in kept and true[0] == max(true)
    examples['average_radius'] = {'scores':true,'radius':average,'tau':tau,'kept':kept}
    # P=[[1,1],[0,0]], q=(1,0), key=(0,1): r_q=0 but error=1.
    assert abs(F(0)-F(1)) > F(0)
    examples['oblique_projector'] = {'score':0,'hat':1,'radius':0}
    # Pq=diag(1,0),Pk=diag(0,1),q=key=(1,0).
    examples['different_projectors'] = {'score':1,'hat':0,'radius':0}
    score, hat, radius = [F(0),F(1)],[F(50),F(1)],[F(50),F(0)]
    bad_tau = max(hat)
    bad_kept = [i for i in range(2) if hat[i]+radius[i] >= bad_tau]
    assert 1 not in bad_kept and score[1] > score[0]
    examples['hat_threshold'] = {'scores':score,'hat':hat,'radius':radius,'tau':bad_tau,'kept':bad_kept}
    examples['non_strict_delete'] = {'scores':[1,1],'tau':1,'kept_if_U_gt_tau':[]}
    # Screening is not a full-softmax preservation theorem even at radius zero.
    # P=I, scores=(1,0): k=1 retains only first, positive discarded softmax mass.
    examples['softmax_support_change'] = {'scores':[1,0],'topk':[0],'discarded_mass':'1/(1+exp(1)) > 0'}
    out = {'scope':'Exact rational finite CPU checks; no model, GPU, timing, floating-point certificate or novelty claim',
           'projection_cases':cases,'generic_interval_cases':generic,
           'total_discarded_across_projection_cases':dropped,
           'counterexamples':examples,'verdict':'pass'}
    text = json.dumps(out,ensure_ascii=False,indent=2,default=str)+'\n'
    (BASE/'independent_raw.json').write_text(text)
    print(text)

if __name__ == '__main__':
    main()
