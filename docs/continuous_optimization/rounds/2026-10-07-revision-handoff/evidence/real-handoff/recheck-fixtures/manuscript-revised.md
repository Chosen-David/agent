# Cache-guided batching for request processing

Synthetic working manuscript; these CPU timings are invented fixtures, not a real benchmark.

## Abstract
In the supplied synthetic fixtures, our cache-guided batching candidate has a mean processing time of 70 ms versus 100 ms for the baseline on the small workload (30% lower time), and 240 ms versus 200 ms on the large workload (20% higher time). Percent time reduction is defined as (baseline mean − candidate mean) / baseline mean × 100%; the large-workload reduction is therefore −20%. These descriptive timing differences do not establish reliability, accuracy, statistical significance, or performance on real benchmarks.

## Method
The candidate batches repeated requests and reuses cached parse results. Both versions use the same request stream; cache invalidation and hit rate were not measured.

## Results
Table 1 lists three timing trials per workload in milliseconds. Small requests improve and large requests regress. There are no accuracy or statistical-significance measurements.

Table 1. Supplied synthetic timing trials from measurements.csv; all times are in milliseconds.

| Workload | Trial | Baseline (ms) | Candidate (ms) |
| --- | --- | --- | --- |
| small | 1 | 100 | 70 |
| small | 2 | 102 | 72 |
| small | 3 | 98 | 68 |
| large | 1 | 200 | 240 |
| large | 2 | 204 | 244 |
| large | 3 | 196 | 236 |

## Limitations
Only two synthetic workload sizes are provided; no production deployment is evaluated.

## Background
Batching can amortize fixed overhead but may add waiting time. This conceptual background is unchanged by corrections to timing claims.
