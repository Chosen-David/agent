"""Exact rational checks for the specified dot-product/top-k task; standard library only."""
from fractions import Fraction as F
import json


def report(q, original, replacement, k):
    scores = [q * x for x in original]
    changed_scores = [q * x for x in replacement]
    errors = [abs(x - y) for x, y in zip(original, replacement)]
    rank = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    changed_rank = sorted(range(len(scores)), key=lambda i: changed_scores[i], reverse=True)
    return {
        "q": q,
        "n": len(original),
        "k": k,
        "original_vectors_1d": original,
        "replacement_vectors_1d": replacement,
        "vector_errors": errors,
        "mean_vector_error": sum(errors) / len(errors),
        "original_scores": scores,
        "replacement_scores": changed_scores,
        "original_boundary_gap": scores[rank[k-1]] - scores[rank[k]],
        "original_topk_zero_based": sorted(rank[:k]),
        "replacement_topk_zero_based": sorted(changed_rank[:k]),
    }


epsilon = F(3) * F("0.02")
remaining_gap = F("0.15") - 2 * epsilon
assert epsilon == F("0.06")
assert remaining_gap == F("0.03") > 0

# An attained worst-case cross-boundary loss under the per-vector bound.
uniform = report(F(3), [F("0.05"), F(0)], [F("0.03"), F("0.02")], 1)
assert max(uniform["vector_errors"]) == F("0.02")
assert uniform["original_boundary_gap"] == F("0.15")
assert uniform["original_topk_zero_based"] == uniform["replacement_topk_zero_based"]
assert uniform["replacement_scores"][0] - uniform["replacement_scores"][1] == remaining_gap

# A mean <=0.02 permits concentrated error and a strict top-1 reversal.
mean = report(F(3), [F("0.05"), F(0), F(-1)], [F("-0.01"), F(0), F(-1)], 1)
assert mean["mean_vector_error"] == F("0.02")
assert mean["original_boundary_gap"] == F("0.15")
assert mean["original_topk_zero_based"] == [0]
assert mean["replacement_topk_zero_based"] == [1]
assert mean["replacement_scores"][1] > mean["replacement_scores"][0]

# The mean-only problem has a useful n=2 exception: total error <=0.04.
mean_n2_pair_loss_bound = F(3) * 2 * F("0.02")
assert F("0.15") - mean_n2_pair_loss_bound == F("0.03") > 0

print(json.dumps({
    "status": "passed",
    "assertions_passed": 12,
    "arithmetic": "fractions.Fraction; exact rational one-dimensional Euclidean examples",
    "per_score_error_bound": epsilon,
    "uniform_guaranteed_cross_boundary_gap": remaining_gap,
    "uniform_attained_bound_example": uniform,
    "mean_only_counterexample": mean,
    "mean_only_n2_pair_loss_bound": mean_n2_pair_loss_bound,
    "scope": "Numerical examples verify arithmetic; the general certificate is the proof in answer.md. No performance or formal-proof claim."
}, indent=2, default=str))
