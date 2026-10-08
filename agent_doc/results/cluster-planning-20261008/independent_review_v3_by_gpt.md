# V3 acceptance invalidated before publication

New evidence independently reproduced by `/root/cluster_result_review`: a 20,001-byte JSON array at depth10000 exits1 with an uncaught decoder RecursionError under frozen CLI SHA4876dbdb234e38634e40d4e0795a385b200cfec81fe9a5409865c103a2a708fe. Depth2000 rejection passed but did not cover this C decoder boundary. `independent_depth10000.json` and `.stdout/.stderr` preserve actual input and raw failure. The v3 snapshot and passing finite tests remain historical observations; the prior acceptance is rescinded and v3 must not be published/consumed. Versioned v4 parser-error repair and retest is required.

Prior report as originally written follows, retained for history only:

# Independent actual-code and result review: CLUSTER-01 v3

Decision: **usable-with-scope** for the frozen v3 deterministic CPU planner fixtures, CLI, local artifact verifier, and repository regression evidence. Manifest SHA256: `ae6b3ab7150559eb372b38ae5cd6da1e65ca9f7fd093722bb47e55703a434098`. This accepts advisory planning within the stated assumptions; it does not accept remote execution or a performance benefit.

Actual reviewer: `independent-review`, fresh-context collaboration identity `/root/cluster_result_review`, dispatched by `/root` through the actual collaboration interface. The producer identity is `root-implementation`. The review was performed by this separate actual invocation, with code inspection, independent cases and reruns, rather than producer pass JSON. This is not an authenticated deployed Engine/ReviewSession identity or a running supervisor.

## V2 rejection and versioned recovery

V2 was rejected because `_real` converted a valid JSON integer `10**309` through `math.isfinite` before checking its upper bound. The original archived CLI exits 1 with traceback and empty stdout. Exact original code SHA, malformed fixture and raw failure remain preserved in `independent_v2_reproducer.json`, `independent_v2_huge_integer.json`, `independent_v2_cli_failure.stderr`, `independent_review_v2_by_gpt.md`, `independent_validation_v2.json`, and the producer's `failed_v2/` archive. V2 is never accepted. The historical hash-matching snapshot is failure reproduction evidence only.

The producer's bounded v3 repair checks type and numeric bounds before `isfinite`; large positive/negative integers now reject without float conversion. The actual reviewed planner SHA is `4912d4970c31e87999a4b5913e7185b4ada42c324c829b61d508554c34a18c9f`. Nineteen producer tests include time/runtime/startup/link huge-integer rejection. The frozen v3 acceptance explicitly requires this case, and both independently rerun targeted tests and the separately written CLI case pass. The reviewer did not edit implementation code.

## Actual code and independent cases

The real planner, CLI, tests, example, workflow, main orchestrator entry, frozen plan/DAG/validation/manifest, environment, and raw outputs were inspected. Input contracts reject unknown fields, duplicate identities, bool/numeric confusion, nonfinite/stale snapshots, unsupported MIG, cycles and source hash mismatches. Candidate enumeration is capped with `search-limit`; a cap is not reported as mathematical infeasibility. A failed gang does not debit resources. GPU UUIDs are exclusive within the wave, and CPU/RAM/disk are debited only after complete admission. Dependencies need prior independently verified IDs; placing a parent in this wave never makes its child ready. All code paths reviewed produce advice or verify local bytes; none reserve resources, submit jobs, fetch artifacts or execute plan fields.

Thirteen independently authored cases passed. They include exhaustive small CPU capacities 0..8, a failing local two-GPU gang followed by a feasible single GPU task, cross-host fabric mismatch, prior-versus-current dependency status, exact expiry/future/nonfinite rejection, absent sources with and without matching destination cache, source SHA mismatch, exact candidate limit versus overflow, RAM/disk/single-GPU memory rejection, empty work, zero-byte local verification and parent-directory symlink rejection, huge integer CLI rejection, and fixture arithmetic/resource invariants. These cases use explicit expected outputs and resource arithmetic, not a copy of candidate generation.

The transfer oracle is `.001 + 2^20 / 2^30 = 0.0019765625` seconds. Independent expected costs are 26.003953125 seconds for distributed-eval, 21.0019765625 for large-eval and 26.0019765625 for small-eval. Each allocation charges `2^30 + 2^20 = 1074790400` disk bytes, 2 CPU slots and 8GiB RAM. Four GPU UUIDs are unique across the fixture wave. The values match raw CLI output exactly. Estimates are not hardware timings; serial staging ignores cross-task network contention.

## Reruns and integrity

After the final manifest was frozen, this invocation independently ran:

| Check | Observed result |
|---|---|
| Targeted cluster suite | 19 tests, OK |
| Independent final discriminatory cases | 13 tests, OK |
| CLI frozen fixture | exit0; JSON identical to producer v3; three placements, unverified join blocked |
| Entire repository suite | 832 tests, OK, skipped8 |
| Reader suite | 3 tests, OK |

Raw logs are `independent_*_v3.stdout/stderr`, with final cases in `independent_cases_final_v3.*`, commands/timing in `independent_execution_v3.json`, and explicit oracle in `independent_reference_costs_v3.json`. Earlier unsuffixed independent reruns happened while the producer applied the repair; they are retained but not used as frozen-v2 acceptance. All current manifest artifact hashes and validation-plan identity were independently checked through `_snapshot` at the actual absolute project root before and after reruns. Producer failure evidence remains retained. Frozen manifest counts agree with actual raw summaries. Local check execution stayed within the assigned 180-second budget; no remote/cloud/GPU actions occurred.

The prior-result search record is partial and explicitly rejects reuse; no old pass label substitutes for these checks. V3's producer, verifier and publication consumer bind the same result contract. Guide files were read only. TASK/detail remain under the main writer's ownership. This report makes no new stable requirement or authorization decision.

## Research boundaries and remaining limits

This invocation independently opened five primary sources and checked recommendation boundaries: NCCL M2N v1 layout/topology separation, the multi-model scheduler paper's model/hardware dependence and single-request/single-interruption restrictions, SkyPilot fleet visibility, Kueue manager/worker admission/status flow, and NVIDIA's July2025 topology article body. These are bounded design inspirations; none supplies a measured planner speedup, deployed API, or token saving. Actual source/read/failure details are retained in `independent_source_checks.json`.

The exact Ray resources page repeatedly returned internal error/HTTP429 and GitHub source fallback was disabled. Its live version label was not re-attested by this result reviewer. The earlier distinct actual `/root/cluster_plan_review` independently opened all six primary pages and recorded the logical/physical resource boundary. The current result acceptance covers the planner's explicit advisory boundary and does not depend on installing Ray or on its current version number.

Limits: trusted inventory/cache/verified-ID authenticity is assumed; stale snapshots are rejected but capacity is not a live lease. No host, driver, runtime estimate, network measurement or artifact fixture SHA is presented as authenticated physical data. There is no cross-process reservation, fairness, optimal scheduling, full intra-GPU topology search, contention model, or immutable cache publication. Local verification cannot stop same-user post-verification writes. CPU fixtures and finite adversarial cases are not a universal bug-free guarantee. Remote adapters, GPU/rank correctness, throughput/makespan, actual token saving and model quality remain untested and outside this receipt.
