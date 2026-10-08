"""Public development oracle/demo. Not a production GPU implementation.

All containment comparisons use exact Fraction.from_float, not tolerances.
The caller explicitly assumes correctly-rounded binary64 scalar +/* with
adjacent nextafter and gradual underflow. Platform probes are diagnostics only.
"""
from fractions import Fraction as F
import itertools
import json
import math
from pathlib import Path
import random
import sys
import time

BASE = Path(__file__).resolve().parent


def finite(x):
    if type(x) is not float or not math.isfinite(x):
        raise ValueError('finite stored binary64 float required')
    return x


def expand(x):
    finite(x)
    lo, hi = math.nextafter(x, -math.inf), math.nextafter(x, math.inf)
    finite(lo); finite(hi)  # Range failure is inconclusive, never a tight bound.
    return lo, hi


def add(a, b):
    return expand(a[0] + b[0])[0], expand(a[1] + b[1])[1]


def mul(a, b):
    products = [x * y for x in a for y in b]
    for x in products: finite(x)
    return expand(min(products))[0], expand(max(products))[1]


def dot_interval(xs, ys, *, ieee_assumed=False):
    if not ieee_assumed:
        raise ValueError('arithmetic premise unknown; keep/fallback')
    if len(xs) != len(ys):
        raise ValueError('dimension mismatch')
    out = (0.0, 0.0)
    for x, y in zip(xs, ys):
        finite(x); finite(y)
        out = add(out, mul((x, x), (y, y)))
    return out


def exact_dot(xs, ys):
    return sum((F.from_float(x) * F.from_float(y) for x, y in zip(xs, ys)), F(0))


def naive(xs, ys):
    out = 0.0
    for x, y in zip(xs, ys): out = out + x * y
    return out


def encloses(bounds, exact):
    return F.from_float(bounds[0]) <= exact <= F.from_float(bounds[1])


def coarse_intervals(q, keys, selected, *, ieee_assumed=False):
    if not ieee_assumed: raise ValueError('arithmetic premise unknown')
    if not selected or len(set(selected)) != len(selected):
        raise ValueError('nonempty distinct coordinate set required')
    if any(type(j) is not int or not 0 <= j < len(q) for j in selected):
        raise ValueError('coordinate index')
    for x in q: finite(x)
    omitted = [j for j in range(len(q)) if j not in selected]
    qmax = max((abs(q[j]) for j in omitted), default=0.0)
    scores = []
    for key in keys:
        if len(key) != len(q): raise ValueError('dimension mismatch')
        for x in key: finite(x)
        coarse = dot_interval([q[j] for j in selected], [key[j] for j in selected], ieee_assumed=True)
        # Reusable per-key sum bound in a real consumer; recomputed in this demo.
        key_sum = (0.0, 0.0)
        for j in omitted: key_sum = add(key_sum, (abs(key[j]), abs(key[j])))
        rho = 0.0 if qmax == 0.0 else mul((qmax, qmax), (key_sum[1], key_sum[1]))[1]
        scores.append(add(coarse, (-rho, rho)))
    return scores


def safe_candidates(intervals, k):
    if type(k) is not int or not 1 <= k <= len(intervals):
        raise ValueError('1<=k<=N required')
    for lo, hi in intervals:
        finite(lo); finite(hi)
        if lo > hi: raise ValueError('invalid interval')
    tau = sorted((a for a, b in intervals), reverse=True)[k-1]
    return [i for i, (lo, hi) in enumerate(intervals) if hi >= tau], tau


def main():
    started = time.perf_counter()
    rng = random.Random(20261008)
    tiny = math.nextafter(0.0, math.inf)
    fixed = [
        ('empty', [], []), ('zero', [0.0, -0.0], [1.0, 2.0]),
        ('cancellation', [2.0**53, 1.0, -2.0**53], [1.0]*3),
        ('half-subnormal', [tiny], [0.5]),
        ('subnormal-cancel', [tiny, tiny], [0.5, -0.5]),
        ('tie-even', [1.0, 2.0**-53], [1.0, 1.0]),
        ('signs', [-3.0, 0.25, 2.0], [0.5, -8.0, 0.0])]
    cases = list(fixed)
    for i in range(96):
        n = rng.randrange(1, 17)
        xs = [math.ldexp(rng.choice([-1.0, 1.0])*rng.random(), rng.randrange(-400, 401)) for _ in range(n)]
        ys = [math.ldexp(rng.choice([-1.0, 1.0])*rng.random(), rng.randrange(-400, 401)) for _ in range(n)]
        cases.append((f'random-{i:02}', xs, ys))
    raw = []
    for name, xs, ys in cases:
        interval = dot_interval(xs, ys, ieee_assumed=True); target = exact_dot(xs, ys)
        assert encloses(interval, target), name
        raw.append({'id':name, 'x':[x.hex() for x in xs], 'y':[y.hex() for y in ys],
                    'exact':str(target), 'interval':[x.hex() for x in interval], 'contains':True})
    # Corners are independently checked exactly; no same floating reference.
    corner_count = 0
    boxes = [(-2.0, 3.0), (0.0, tiny), (-tiny, 0.0), (1.0, math.nextafter(1.0, math.inf))]
    for a, b in itertools.product(boxes, repeat=2):
        interval = mul(a, b)
        for x, y in itertools.product(a, b):
            assert encloses(interval, F.from_float(x)*F.from_float(y))
            corner_count += 1
    # Final one-ulp padding is provably not a running error enclosure.
    xs, ys = fixed[2][1:]; estimate = naive(xs, ys); target = exact_dot(xs, ys)
    assert estimate == 0.0 and target == 1 and not encloses(expand(estimate), target)
    # Conservative relative-model gamma crosscheck with exact rational constants.
    u = F(1, 2**53); gamma = 6*u/(1-6*u)
    bound = gamma * sum((abs(F.from_float(x)*F.from_float(y)) for x,y in zip(xs,ys)), F(0))
    assert abs(F.from_float(estimate)-target) <= bound
    refusal_inputs = [
        ('overflow-product', lambda: dot_interval([sys.float_info.max], [2.0], ieee_assumed=True)),
        ('overflow-sum', lambda: dot_interval([sys.float_info.max/2]*3, [1.0]*3, ieee_assumed=True)),
        ('nonfinite', lambda: dot_interval([math.nan], [1.0], ieee_assumed=True)),
        ('dimension', lambda: dot_interval([1.0], [], ieee_assumed=True)),
        ('unknown-arithmetic', lambda: dot_interval([tiny], [0.5])),
        ('invalid-k', lambda: safe_candidates([(0.0,1.0)], 0)),
        ('invalid-interval', lambda: safe_candidates([(2.0,1.0)], 1))]
    refusals = []
    for name, call in refusal_inputs:
        try: call()
        except ValueError as exc: refusals.append({'id':name,'decision':'reject/fallback','reason':str(exc)})
        else: raise AssertionError(name)
    # Linear sensor transfer: G in siemens, V in volts, I in amperes.
    conductance = [0.125, 0.25, 0.5]; voltage = [3.0, -2.0, 1.0]
    current = exact_dot(conductance, voltage); bounds = dot_interval(conductance, voltage, ieee_assumed=True)
    assert current == F(3,8) and encloses(bounds,current)
    # But widening only the computed answer does not cover unknown input loss.
    unknown_true = F.from_float(1.0) + F(1,2**55)
    stored = float(unknown_true); assert stored == 1.0
    # Huge input loss: original1000 rounded/quantized to cached0; stored dot bound excludes original.
    assert not encloses(dot_interval([0.0],[1.0],ieee_assumed=True),F(1000))
    refusals.append({'id':'unbounded-quantization','decision':'reject original-input target','reason':'stored0 does not enclose original1000; no input error box'})
    # Software FTZ witness: flushing a min-normal*0.25 result to zero loses many ulps.
    true_subnormal = F.from_float(sys.float_info.min) / 4
    assert not encloses(expand(0.0),true_subnormal)
    refusals.append({'id':'ftz','decision':'reject RN/gradual premise','reason':'simulated flush result0 neighbors miss exact min-normal/4'})
    screenings = []
    for trial in range(24):
        q = [rng.uniform(-2,2), rng.uniform(-2,2), rng.uniform(-.01,.01), rng.uniform(-.01,.01)]
        keys = [[rng.uniform(-3,3),rng.uniform(-3,3),rng.uniform(-.1,.1),rng.uniform(-.1,.1)] for _ in range(8)]
        intervals = coarse_intervals(q,keys,[0,1],ieee_assumed=True)
        exact = [exact_dot(q,key) for key in keys]
        assert all(encloses(b,s) for b,s in zip(intervals,exact))
        candidates,tau = safe_candidates(intervals,2)
        expected = sorted(range(len(keys)),key=lambda i:(-exact[i],i))[:2]
        assert set(expected) <= set(candidates)
        recovered = sorted(candidates,key=lambda i:(-exact[i],i))[:2]; assert recovered == expected
        screenings.append({'id':f'screen-{trial:02}','q':[x.hex() for x in q], 'keys':[[x.hex() for x in key] for key in keys], 'intervals':[[x.hex() for x in b] for b in intervals], 'exact':[str(s) for s in exact], 'tau':tau.hex(),'candidates':candidates,'topk':expected,'recovered':recovered})
    # Ties must be kept; equality is never a safe discard condition.
    keep,tau=safe_candidates([(1.0,1.0),(1.0,1.0),(0.0,0.0)],1)
    assert keep==[0,1]
    data={'schema_version':'public-dot-enclosure-fixtures/v1','scope':'Conditional stored-input RN binary64 intervals; no formal/platform/GPU/model proof','seed':20261008,'dot_cases':raw,'interval_corner_checks':corner_count,'screening_cases':screenings,'refusals':refusals,'witnesses':{'terminal_ulp_estimate':estimate.hex(),'terminal_ulp_exact':str(target),'terminal_ulp_interval':[x.hex() for x in expand(estimate)],'gamma6_exact_bound':str(bound),'sensor_current_exact':str(current),'sensor_current_interval':[x.hex() for x in bounds],'sensor_units':'S * V = A','tie_keep':keep},'diagnostic_elapsed_seconds':time.perf_counter()-started,'platform_probes':{'radix2':sys.float_info.radix==2,'mantissa53':sys.float_info.mant_dig==53,'startup_rounds1':sys.float_info.rounds==1,'subnormal_preserved':sys.float_info.min/4>0.0},'limitations':['Platform probes do not authenticate all operations/rounding-mode changes','All exposed tests are public development/regression, not unseen model evaluation']}
    (BASE/'raw.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'dot_cases':len(raw),'corner_checks':corner_count,'screening_cases':len(screenings),'refusals':len(refusals),'all_exact_oracle_checks_pass':True,'seconds':data['diagnostic_elapsed_seconds']}))


if __name__ == '__main__':
    main()
