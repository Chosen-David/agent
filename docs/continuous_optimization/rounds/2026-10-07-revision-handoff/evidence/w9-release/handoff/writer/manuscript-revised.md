# Synthetic manuscript: Selective execution — corrected working draft

This is a synthetic fixture, not a published paper or a report of new experiments. This bounded revision uses only the supplied manuscript and measurements.csv; no external citations are supplied or added. All performance statements below describe the supplied single-run CPU records.

## Abstract

The supplied synthetic records describe replacement of a selected kernel under the same CPU process and input configuration. End-to-end latency changes from 100 to 80 ms for the small workload, from 120 to 100 ms for the medium workload, and from 200 to 220 ms for the large workload. The corresponding baseline-to-candidate speedup ratios are 1.25×, 1.20×, and approximately 0.90909×: the small and medium records have latency reductions of 20.0% and approximately 16.7%, while the large record has a 10.0% latency regression. Separately timed kernel-only latency changes from 20 to 10 ms, a 2.00× kernel-only speedup. The kernel is already included in the end-to-end paths, so its timing must not be added to end-to-end timing or its speedup presented as an end-to-end result. Each value represents one run without independent repeats. Variance and output quality were not measured, and no GPU measurement was made. These descriptive observations establish neither repeatable performance improvement nor quality preservation or a uniform gain across workloads.

## Method and measurement scope

The supplied method replaces a selected kernel. All supplied measurements use the same CPU process and input configuration. The available evidence does not specify the kernel implementation, CPU model, software configuration, warmup procedure, run ordering, or timing-instrumentation details; this draft does not invent them. No GPU measurement has been made.

The measurements comprise three end-to-end baseline/candidate pairs and one independently timed kernel-only pair. The kernel-only pair is included in the end-to-end paths; these timing scopes must remain separate. Each numerical value represents a single run, with no independent repeats. We calculate the descriptive speedup ratio as baseline latency divided by candidate latency, and latency change as 100 × (candidate latency − baseline latency) / baseline latency. A ratio below one indicates increased latency. The arithmetic below is a re-expression of the supplied records, not a new benchmark.

## Results

Table 1 reports all supplied rows, including the negative result. Latencies are in milliseconds; ratios and percentages are derived from the two latency columns. Positive latency change means a regression. Rounded percentages do not express statistical precision.

| Workload | Scope | Baseline (ms) | Candidate (ms) | Speedup ratio | Latency change |
|---|---|---:|---:|---:|---:|
| small | end_to_end | 100 | 80 | 1.25× | −20.0% |
| medium | end_to_end | 120 | 100 | 1.20× | −16.7% |
| large | end_to_end | 200 | 220 | 0.90909× | +10.0% |
| kernel | kernel_only | 20 | 10 | 2.00× | −50.0% |

In these single-run CPU records, the small and medium workloads have lower candidate latency, while the large workload has higher candidate latency. Thus the records do not support a claim of 2× end-to-end speedup on every workload or absence of regression. The 2.00× ratio applies only to the separately timed kernel pair. The available evidence does not establish why the large workload regresses or how the kernel change contributes to each end-to-end difference; no overhead decomposition or causal mechanism is inferred.

## Evidence limits

There are no independent repeats, so the supplied values do not permit an estimate of run-to-run variance or support a confidence interval, a significance claim, or a repeatability claim. Absence of such evidence does not establish that the observed differences are noise or that the methods are equivalent. Output quality was not measured, so correctness or quality preservation is not established. CPU observations provide no GPU performance evidence. No conclusion about unmeasured workloads, configurations, or hardware is asserted.

## Appendix A: Retained regression disclosure and scope consistency

The original Appendix A already disclosed that the large workload regresses from 200 ms to 220 ms. That disclosure is retained here; this revision corrects the inconsistent abstract and scopes its conclusions, rather than repairing an alleged hidden or omitted result. The large-workload speedup ratio is 200/220 = 10/11 ≈ 0.90909×, and the latency increase is (220 − 200)/200 = 10.0%. For consistency with the abstract and Results, the other end-to-end ratios are 100/80 = 1.25× for small and 120/100 = 1.20× for medium. The kernel-only ratio is 20/10 = 2.00×, not an end-to-end ratio; it is never added to an end-to-end latency. Quality and variance remain unmeasured, there are no independent repeats, and no GPU measurement has been made.
