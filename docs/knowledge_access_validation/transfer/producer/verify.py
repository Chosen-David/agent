"""Exact checks for synthetic cooling and a finite-trend counterexample."""
from fractions import Fraction as F
import json

checks = []


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)


ambient, initial, factor, tolerance = F(20), F(36), F(3, 4), F(1, 100)


def cooling(x):
    return ambient + factor * (x - ambient)


x, t, history = initial, 0, []
while True:
    y = cooling(x)
    residual = abs(y-x)
    error = abs(y-ambient)
    certificate = factor * residual / (1-factor)
    check(f"invariant interval at update {t+1}", ambient <= y <= initial)
    check(f"closed-form value at update {t+1}", y == ambient + (initial-ambient)*factor**(t+1))
    check(f"returned error equals posterior certificate at update {t+1}", error == certificate)
    history.append({"t":t,"current_C":x,"returned_C":y,"residual_C":residual,"returned_error_C":error})
    if residual <= tolerance:
        break
    x, t = y, t+1

check("first qualifying t is 21", t == 21)
check("previous residual exceeds tolerance", history[-2]["residual_C"] > tolerance)
check("stopping residual meets tolerance", residual <= tolerance)
check("returned value error is at most 0.03 C", error <= F(3,100))
check("generic old-point threshold would be 0.04 C", tolerance/(1-factor)==F(4,100))

# Temperature differences are invariant under the Celsius-to-Kelvin offset.
offset = F("273.15")
kelvin_x, kelvin_ambient = x + offset, ambient + offset
kelvin_y = kelvin_ambient + factor*(kelvin_x-kelvin_ambient)
check("Kelvin update agrees with Celsius update", kelvin_y == y+offset)
check("residual unchanged by temperature offset", abs(kelvin_y-kelvin_x)==residual)

# An observed disagreement history, normalized to [0,1], admits two futures.
prefix = [F(1,50)*factor**j for j in range(4)]
for j in range(3):
    check(f"exact 25 percent disagreement decrease round {j+1}", prefix[j+1]/prefix[j]==factor)
check("observed final disagreement is below 0.01", prefix[-1] < tolerance)
rebound = F(1)
continue_decrease = factor * prefix[-1]
check("rebound violates extrapolated 0.75 reduction", rebound > continue_decrease)

# Even a fixed continuous self-map of [0,1] can interpolate the observed
# three transitions and then rebound. Linear interpolation between these
# ordered nodes stays in [0,1], while the first and last nodes are fixed.
nodes = [(F(0),F(0)), (prefix[3],F(1)), (prefix[2],prefix[3]),
         (prefix[1],prefix[2]), (prefix[0],prefix[1]), (F(1),F(1))]
check("interpolation nodes ordered", all(a[0]<b[0] for a,b in zip(nodes,nodes[1:])))
check("node outputs in invariant interval", all(0<=v<=1 for _,v in nodes))
node_map = dict(nodes)
check("same fixed map realizes observed prefix", all(node_map[prefix[j]]==prefix[j+1] for j in range(3)))
check("same fixed map then rebounds", node_map[prefix[-1]]==rebound)
local_lipschitz_ratio = abs(node_map[prefix[2]]-node_map[prefix[3]]) / abs(prefix[2]-prefix[3])
check("observations do not establish uniform contraction", local_lipschitz_ratio > 1)
check("two fixed points contradict uniqueness", node_map[F(0)]==0 and node_map[F(1)]==1)

result = {
    "status":"passed", "checks_passed":len(checks), "checks":checks,
    "arithmetic":"Exact fractions.Fraction; decimal displays are approximate",
    "cooling":{
        "first_stopping_t":t,"returned_index":t+1,
        "previous_residual_C":history[-2]["residual_C"],
        "observed_residual_C":residual,"observed_residual_decimal_C":float(residual),
        "returned_C":y,"returned_decimal_C":float(y),
        "actual_returned_error_C":error,"actual_returned_error_decimal_C":float(error),
        "threshold_certificate_C":factor*tolerance/(1-factor),
        "observed_residual_certificate_C":certificate,
    },
    "discussion_counterexample":{
        "normalized_disagreement_prefix":prefix,
        "compatible_next_values":{"continued_decrease":continue_decrease,"rebound":rebound},
        "continuous_piecewise_linear_self_map_nodes":nodes,
        "violating_pair_lipschitz_ratio":local_lipschitz_ratio,
        "status":"synthetic countermodel, not an observation of actual agents",
    },
    "scope":"Finite exact numerical checks supplement the proof; no physical or production experiment, no formal proof assistant, no performance claim."
}
print(json.dumps(result,indent=2,default=str))
