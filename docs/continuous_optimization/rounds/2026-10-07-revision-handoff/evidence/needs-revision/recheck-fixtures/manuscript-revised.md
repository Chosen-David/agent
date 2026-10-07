# Cache-guided batching for request processing

Synthetic working manuscript; these CPU timings are invented fixtures, not a real benchmark.

## Abstract
For the invented CPU timing fixtures, the candidate has 30% lower mean latency for the small synthetic workload (100 ms baseline versus 70 ms candidate), but 20% higher mean latency for the large synthetic workload (200 ms versus 240 ms). These percentages use the baseline mean as denominator and describe only these fixtures; reliability, accuracy equivalence, statistical significance, and deployment generalization remain unevaluated.

## Method
The candidate batches repeated requests and reuses cached parse results. Both versions use the same request stream; cache invalidation and hit rate were not measured.

## Results
Table 1 lists three timing trials per workload in milliseconds. Small requests improve and large requests regress. There are no accuracy or statistical-significance measurements.

**Table 1. Invented CPU timing fixtures from measurements.csv (milliseconds).**

| Workload | Trial | Baseline (ms) | Candidate (ms) |
| --- | --- | --- | --- |
| small | 1 | 100 | 70 |
| small | 2 | 102 | 72 |
| small | 3 | 98 | 68 |
| large | 1 | 200 | 240 |
| large | 2 | 204 | 244 |
| large | 3 | 196 | 236 |

Across the three trials per workload, mean latency falls from 100 to 70 ms for small requests and rises from 200 to 240 ms for large requests. Relative mean latency change is 100 × (candidate mean − baseline mean) / baseline mean: −30% for small and +20% for large. These descriptive fixture values do not establish reliability or deployment performance.


## Limitations
Only two synthetic workload sizes are provided; no production deployment is evaluated.

## Background
Batching can amortize fixed overhead but may add waiting time. This conceptual background is unchanged by corrections to timing claims.
