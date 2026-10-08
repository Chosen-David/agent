# Independent actual-code and result review: CLUSTER-01 v4

Decision: **usable-with-scope** for the frozen v4 deterministic CPU planner fixtures, CLI, local artifact verifier, and repository regression evidence. Manifest SHA256: `1386a9e7947f5b6bbafda0accd559dc80aedb438b59b4910bde099eac2e0b644`. This accepts advisory planning within the stated assumptions; it does not accept remote execution or a performance benefit.

Actual reviewer: `independent-review`, fresh-context collaboration identity `/root/cluster_result_review`, dispatched by `/root` through the actual collaboration interface. The producer identity is `root-implementation`. The review was performed by this separate actual invocation, with code inspection, independent cases and reruns, rather than producer pass JSON. This is not an authenticated deployed Engine/ReviewSession identity or a running supervisor.

## V2 rejection and versioned recovery

V2 was rejected because `_real` converted a valid JSON integer `10**309` through `math.isfinite` before checking its upper bound. The original archived CLI exits 1 with traceback and empty stdout. Exact original code SHA, malformed fixture and raw failure remain preserved in `independent_v2_reproducer.json`, `independent_v2_huge_integer.json`, `independent_v2_cli_failure.stderr`, `independent_review_v2_by_gpt.md`, `independent_validation_v2.json`, and the producer's `failed_v2/` archive. V2 is never accepted. The historical hash-matching snapshot is failure reproduction evidence only.

The producer's bounded v3 repair checks type and numeric bounds before `isfinite`; large positive/negative integers now reject without float conversion. The actual reviewed planner SHA is `4912d4970c31e87999a4b5913e7185b4ada42c324c829b61d508554c34a18c9f`. Twenty producer tests include time/runtime/startup/link huge-integer rejection. The frozen v4 acceptance explicitly requires this case, and both independently rerun targeted tests and the separately written CLI case pass. The reviewer did not edit implementation code.

V3 was also invalidated before publication after the main independently found and this reviewer independently reproduced an uncaught JSON-decoder `RecursionError` at array depth 10000 (20,001 bytes, below the 2 MiB input limit). The lower-depth 2000 case had passed and did not cover this decoder boundary. The prior finite-test acceptance and its subsequent invalidation are transparently retained as `independent_*_v3_pre_invalidation*` and `independent_*_v3*`; v3 is not publication-ready. Exact input and raw failure are `independent_depth 10000.json` and `.stdout/.stderr`. V4 catches `RecursionError` and `OverflowError` at the CLI error boundary and adds a regression. Current targeted 20 tests and the independent depth 10000 case reject cleanly as JSON invalid/exit2, with empty stderr. Reviewed CLI SHA: `80d90535bd03f576025d86e640a48d9460d469b8afb46427f9ece1329ea81334`.

## Actual code and independent cases

The real planner, CLI, tests, example, workflow, main orchestrator entry, frozen plan/DAG/validation/manifest, environment, and raw outputs were inspected. Input contracts reject unknown fields, duplicate identities, bool/numeric confusion, nonfinite/stale snapshots, unsupported MIG, cycles and source hash mismatches. Candidate enumeration is capped with `search-limit`; a cap is not reported as mathematical infeasibility. A failed gang does not debit resources. GPU UUIDs are exclusive within the wave, and CPU/RAM/disk are debited only after complete admission. Dependencies need prior independently verified IDs; placing a parent in this wave never makes its child ready. All code paths reviewed produce advice or verify local bytes; none reserve resources, submit jobs, fetch artifacts or execute plan fields.

Fourteen independently authored cases passed. They include exhaustive small CPU capacities 0..8, a failing local two-GPU gang followed by a feasible single GPU task, cross-host fabric mismatch, prior-versus-current dependency status, exact expiry/future/nonfinite rejection, absent sources with and without matching destination cache, source SHA mismatch, exact candidate limit versus overflow, RAM/disk/single-GPU memory rejection, empty work, zero-byte local verification and parent-directory symlink rejection, huge integer CLI rejection, fixture arithmetic/resource invariants, and decoder nesting at depth 10000. The reviewer also actually loaded `math.discrete-budget-allocation@1` through the knowledge CLI with the exact pinned SHA and inspected its additive fixed-menu assumptions. Coupled GPU/gang/network choices violate those assumptions, so declining its exact-DP guarantee is valid; its weak-duality theorem is not used to certify this heuristic. `independent_knowledge_pin.stdout/stderr` retain actual load evidence. These cases use explicit expected outputs and resource arithmetic, not a copy of candidate generation.

The transfer oracle is `.001 + 2^20 / 2^30 = 0.0019765625` seconds. Independent expected costs are 26.003953125 seconds for distributed-eval, 21.0019765625 for large-eval and 26.0019765625 for small-eval. Each allocation charges `2^30 + 2^20 = 1074790400` disk bytes, 2 CPU slots and 8GiB RAM. Four GPU UUIDs are unique across the fixture wave. The values match raw CLI output exactly. Estimates are not hardware timings; serial staging ignores cross-task network contention.

## Reruns and integrity

Against code/input hashes captured before and after execution and matching the final frozen manifest, this invocation independently ran:

| Check | Observed result |
|---|---|
| Targeted cluster suite | 20 tests, OK |
| Independent final discriminatory cases | 14 tests, OK |
| CLI frozen fixture | exit0; JSON identical to producer v4; three placements, unverified join blocked |
| Entire repository suite | 833 tests, OK, skipped8 |
| Reader suite | 3 tests, OK |

Raw logs are `independent_*_v4.stdout/stderr`, with final cases in `independent_cases_v4.*`, commands/timing in `independent_execution_v4.json`, and explicit oracle in `independent_reference_costs_v3.json`. Earlier unsuffixed independent reruns happened while the producer applied the repair; they are retained but not used as frozen-v2 acceptance. All current manifest artifact hashes and validation-plan identity were independently checked through `_snapshot` at the actual absolute project root before and after reruns. Producer failure evidence remains retained. Frozen manifest counts agree with actual raw summaries. Local check execution stayed within the assigned 180-second budget; no remote/cloud/GPU actions occurred.

The prior-result search record is partial and explicitly rejects reuse; no old pass label substitutes for these checks. V4's producer, verifier and publication consumer bind the same result contract. Guide files were read only. TASK/detail remain under the main writer's ownership. This report makes no new stable requirement or authorization decision.

## Research boundaries and remaining limits

This invocation independently opened five primary sources and checked recommendation boundaries: NCCL M2N v1 layout/topology separation, the multi-model scheduler paper's model/hardware dependence and single-request/single-interruption restrictions, SkyPilot fleet visibility, Kueue manager/worker admission/status flow, and NVIDIA's July 2025 topology article body. These are bounded design inspirations; none supplies a measured planner speedup, deployed API, or token saving. Actual source/read/failure details are retained in `independent_source_checks.json`.

The exact Ray resources page repeatedly returned internal error/HTTP429 and GitHub source fallback was disabled. Its live version label was not re-attested by this result reviewer. The earlier distinct actual `/root/cluster_plan_review` independently opened all six primary pages and recorded the logical/physical resource boundary. The current result acceptance covers the planner's explicit advisory boundary and does not depend on installing Ray or on its current version number.

Limits: trusted inventory/cache/verified-ID authenticity is assumed; stale snapshots are rejected but capacity is not a live lease. No host, driver, runtime estimate, network measurement or artifact fixture SHA is presented as authenticated physical data. There is no cross-process reservation, fairness, optimal scheduling, full intra-GPU topology search, contention model, or immutable cache publication. Local verification cannot stop same-user post-verification writes. CPU fixtures and finite adversarial cases are not a universal bug-free guarantee. Remote adapters, GPU/rank correctness, throughput/makespan, actual token saving and model quality remain untested and outside this receipt.
