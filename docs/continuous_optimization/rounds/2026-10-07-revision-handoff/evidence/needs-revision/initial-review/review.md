# Independent scientific review

Reviewed 2026-10-06; provisional rubric (no venue supplied). Frozen manuscript SHA-256: `fe3f73113bb46c919354d844297c4ca8cf767657f02ca7d6bcb378067e1a088b`. Read all 18 manuscript lines, project.json, and all six CSV rows. The frozen research-review skill and relevant execution, workflow, and measurement contract references were loaded. No manuscript was edited.

The manuscript describes batching repeated requests and reusing cached parse results, with two synthetic workloads. Its submitted evidence is explicitly invented timing fixtures, not a real benchmark. The descriptive results support a benefit for small requests and a regression for large requests. They do not establish reliable real-world gains, accuracy preservation, significance, or causation by cache hits.

## Executed numerical check

The standard-library script `calculate.py` was run successfully; exact outputs are in `calculation-results.json` and `calculation.log`.

| Workload | Rows | Baseline mean (ms) | Candidate mean (ms) | Candidate − baseline (ms) | Latency change relative to baseline |
|---|---:|---:|---:|---:|---|
| small | 3 | 100 | 70 | −30 | 30% reduction |
| large | 3 | 200 | 240 | +40 | 20% increase |

Each small paired difference is −30 ms and each large difference is +40 ms. The small mean-ratio speedup is 1.42857×; large is 0.83333×. Percent latency reduction and speedup are distinct. Total fixture time is 900 ms baseline versus 930 ms candidate, a 3.333% increase. That pooled quantity is descriptive only: no deployment workload mixture or primary pooled estimand is specified. No p-values or confidence intervals were calculated, because invented fixture repetitions and unspecified independent units cannot support those inferences.

## Findings and disposition

- **REV-F001 (major, confirmed error, open):** Abstract line 6 claims 30% acceleration across workload sizes. Large mean latency increases 20%, contradicting both the CSV and the correct Results statement. Correct the scope and metric; the small-only 30% latency reduction remains supported descriptively.
- **REV-F002 (major, evidence gap, open):** Abstract line 6 asserts reliable gains. Synthetic timings, three row labels, no statistical or accuracy evaluation, and no independent measurement design do not support that assertion. Narrow the claim to observations in these fixtures, retaining unevaluated reliability and accuracy. No new experiment is necessary or authorized to make that correction.
- **REV-F003 (minor, reporting gap, open):** Results line 12 refers to absent Table 1. All manuscript content was checked. Include an accurate table from the existing CSV or make an accurate explicit reference to the supplied measurement file.

Full location, evidence, owner, verification, resolution options, and executable acceptance conditions are in `findings.json`. All three findings remain open. Assignment or acknowledgment is not closure; only an actual revised snapshot and original-reviewer recheck can establish resolution.

## Correct content to preserve

The explicit synthetic-data warning (line 3), same-stream method description and unmeasured cache invalidation/hit rate (line 9), small improvement/large regression and absent accuracy/statistical measurements (line 12), two-workload/no-production limitation (line 15), and conceptual batching-overhead/waiting-time background (line 18) are sound within their stated scope. The method mechanism is described, not experimentally verified; no separate defect is inferred from that description. Do not erase these correct statements or add fabricated measurements, significance tests, or citations.

## Verification and next owners

The main AI first verifies each finding against the frozen snapshot and calculations. The writing role then makes the minimal warranted correction and records the revised hash and changes. The original review role checks that actual manuscript against each original acceptance condition, including regression checks of the preserved content. `task_chain.json` encodes separate verify → resolve → recheck dependencies. Recheck is blocked until the actual revised manuscript and change record arrive.

The questions that could change the judgment are concrete: Does the new abstract limit the benefit to small synthetic requests and acknowledge the large regression? Does it avoid reliability or inferential claims unsupported by this evidence? Can a manuscript reader locate the referenced timings? These can all be answered with the existing inputs and an actual revised artifact.

Current and historical novelty, external literature, implementation correctness, real timing execution, and cache causality were not independently established. The task explicitly forbids network/install/new experiments/new citations and provides no venue; therefore no venue score, novelty objection, or acceptance probability is supplied. This bounded review has checked every scientific statement against the supplied evidence without interpreting unverified method background as a demonstrated mechanism.
