# Independent candidate/result review v5

Verdict: usable-with-scope for adopting the exact isolated v5 candidate, pending production source equivalence and required repository regressions. Independent hosted reviewer read original search/_context/_unknown and executed full serial rerun plus separate API boundary comparison. This file is manual hosted review evidence, not a deployed ResultValidationHandler/ReviewSession acceptance receipt.

## Checks

- implementation — PASS. Candidate preserves show(), record validation, revocation check, haystack/scoring, per-record errors, result sorting, limits/partial/strategy, and exact context equality. Lazy eligibility computation stays inside first usable record's try block. Iterative classifier uses exact builtin types and exact str dict keys; unsupported contexts and subclasses/instance show overrides retain original per-record expression. The one-time context_checked marker is set only after successful classification/evaluation.
- reference_boundary — PASS within checked API scope. reviewer-boundaries.py compared entire return or exact exception type/message across 18 independent cases: missing/empty registries, known/None/incomplete/nested unknown, accepted tuple, dict/scalar/key subclasses, non-JSON set/NaN, deeply nested valid JSON with early unknown short circuit, instance show mutation, subclass fallback, actual revoked/corrupt/broken-only records. Earlier unguarded candidate defect retained in reviewer-empty-subclass.json; v5 fixes it.
- data_integrity — PASS. Producer raw-v5-serial.json and independent-v5.json have identical full baseline/candidate source strings, helper, corpus hashes, and all case returns. All 11 pairs per six cases retained; each observed complete return checked against baseline expected. 143 record.json hashes frozen before/after; scan contains 223 directories including 80 invalid/missing-record errors per case, all retained. No samples/errors omitted. v2/v3/v4 are historical iteration data; only v5 serial data supports acceptance.
- numerical_sanity — PASS. All timings finite positive milliseconds from perf_counter_ns. Independently recomputed medians/reductions from raw pairs agree. Large-corpus and large-math exceed fixed 10% improvement gate in both serial rounds; controls show no >10% regression. Small improvements near noise are not claimed as reliable benefits.
- measurement_validity — PASS for warm-cache local CPU filesystem search. Whole public search invocation including file validation/revocation checks is timed, one warmup per variant, alternating ordering for 11 pairs. Independent timer ran after producer completed. Large-context differences exceed observed timing spread; control differences overlap noise. No cold-cache/model/token/task-quality/end-to-end conclusion is supported.
- reproducibility — PASS. Independent full script rerun produced 41.18% and 38.71% large-context median reductions versus producer 41.93% and 38.53%, with all returns identical. Independent 18-case boundary run completed. Production integration and broader regressions remain root-owned and pending at this review.

## Independent serial observations

| Context | Baseline ms | Candidate ms | Median reduction |
|---|---:|---:|---:|
| large-corpus | 159.341 | 93.721 | 41.18% |
| large-math | 149.296 | 91.497 | 38.71% |
| medium-batch | 95.126 | 90.664 | 4.69% |
| none | 94.462 | 93.583 | 0.93% |
| incomplete | 97.180 | 97.128 | 0.05% |
| unknown | 92.106 | 91.114 | 1.08% |

## Limitations

Synchronous caller context must not be concurrently mutated; original API has no snapshot guarantee. Scope is this Python/CPU/checkout corpus with warm OS cache, query `result source context`, limit=3, max_scan=250. Registry-wide complete returned data matched despite existing errors; these measurements do not validate the underlying historical experiments. No universal correctness, new paper-read count, model token/quality improvement, live runtime deployment, or statistical certainty for tiny control changes is claimed.
