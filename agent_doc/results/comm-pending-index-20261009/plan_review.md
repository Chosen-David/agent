# Independent plan review — COMM-PERF-01

Decision: **revise**. The proposed index is a reasonable bounded optimization; complete the measurement contract below before producing data. No source implementation changes or experiments were performed in this review.

Reviewed plan SHA-256: `3b30429a672821bc151c097b19a75a6966b9aa667248925cadd0087d3e4239ca`.
Project: `/workspace/scratch/54fe46ee5dc7/agent`.
Reviewer: Work collaboration context `/root/comm_review`, independently dispatched by `/root`; this written report is a manual review, not an authenticated `ReviewSession` runtime receipt. No runtime, supervisor or tmux deployment is asserted.

## Seven required checks

| Check | Verdict | Reason |
| --- | --- | --- |
| intent | pass | Reducing local durable inbox polling cost fits the delegated communication-efficiency goal. The plan excludes model quality, token and end-to-end claims. |
| guide | pass | Read `agent_doc/guide/GUIDE.md`; it is empty (SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`). No guide writes are needed or permitted. |
| assumptions | fail | ACK percentages do not specify where pending deliveries occur, which affects an ordered LIMIT query. Inbox limit and the interleaved-run workload are not fixed. The query-adjustment decision is not bounded to an explicit alternative. |
| prior_results | pass with scope | The historical selective-evidence plan actually concerns tokenizer counts and is inapplicable to SQLite backlog polling. New measurement is justified. The reported lexical search counts are planner-provided; its raw search evidence is not present in this result directory and must be preserved before publication. No old performance data are accepted. |
| acceptance | fail | Semantic invariants and quantitative targets are useful, but the required frozen six-criterion validation protocol/result bindings are absent. “Acknowledged-backlog cases” must name its precise cases before observing results. |
| risk | pass with scope | An additive partial index can increase initialization, publication, ACK and storage costs; the plan measures these. Existing-run migration and multi-run delivery independence must be checked. Current publication/ACK/ref/budget semantics should remain untouched. |
| resources | pass with scope | The declared stdlib/local-CPU/manual-host scope is appropriate. Workloads are bounded, but cap candidate rounds and identify the stop condition to prevent adaptive optimization until a favorable result. No paid model, GPU or remote deployment is authorized by this report. |

## Blocking revisions

1. **R1 — Freeze an executable, unambiguous experiment definition.** In a versioned replacement plan, name the cases to which both `>80%` VM-step reduction and `>=2x` median speedup apply. Pin `limit`, pending/ACK placement, targeted recipient, event sizes, interleaved run count/event count and pending placement, seeds (or explicitly deterministic construction), baseline revision/query, candidate index and any allowed ordered-query alternative. Use equivalent cloned input state per arm, alternating paired measurement order, independent uninstrumented timing and VM-step measurement, and preserve every repetition. Specify p95 convention. Limit this round to an explicit baseline/candidate comparison; if the hypothesis fails, retain the result and revise rather than silently moving the gate. Recheck: the plan and benchmark configuration fully determine all tested cases and the pass/fail calculation before data exists.

2. **R2 — Freeze the independent result protocol and consumer binding.** Add `experiment-validation-plan/v1` with the six required checks (implementation, reference_boundary, data_integrity, numerical_sanity, measurement_validity, reproducibility), each with procedure, acceptance and `allow_not_applicable`. Bind its actual path/hash plus result ID, producer ID/actor, manifest path and exact scope in the producer, independent verifier and publication consumer. The eventual manifest must pin real code, inputs/config, all raw repetitions, environment and outputs. Include an independent semantic reference (e.g. a straightforward Python filter/order of seeded deliveries) and old-database reopen/migration, empty inbox, limits 1/100 and validation errors, recipient independence, cross-run isolation and idempotent/immutable receipts. Recheck: the independent reviewer can determine data integrity, behavior and performance-gate outcome from frozen inputs and actual raw evidence without relying on producer pass flags. This manual workflow does not require pretending to have an Engine adapter.

The stable task Plan must reference the replacement version/hash; preserve this review and original plan bytes. A new independent review of the revised snapshot is required before measurement. No additional user permission is requested by this report.

## Read scope and exact implementation boundary

Read repository AGENTS, decision-review, project-document, dual-main and result-validation guidance; current communication workflow; the plan and COMM-PERF-01 detail; `agent_runtime/communication.py`; `tests/test_communication.py`; and the historical selective-context measurement plan. The current inbox query joins deliveries by sequence, filters run/recipient/NULL receipt and orders by event sequence. Its existing primary key is `(seq, recipient)`; the proposed pending-recipient index targets a plausible missing access path. Existing tests cover retries, per-recipient receipts, bounded FIFO, run isolation and reference validation, but do not yet demonstrate large acknowledged-history behavior or index migration.

Any later approval should cover only an additive pending-recipient/sequence index and a specifically frozen semantically equivalent ORDER BY/query adjustment, associated regression tests and stdlib benchmark/evidence/docs for this task. It does not authorize changing routes, receipts, budget checks, reference validation, scheduling, model/tool behavior, unrelated tasks or human guides. Performance conclusions must remain scoped to the measured synthetic SQLite workload and actual environment; storage/write costs and cross-run selectivity limitations must be reported even if poll targets pass.

Read bindings: source `2df62b823606ca4d0ff1059c632dc567180ba816dd126f2ecd6ed84168963a7c`; tests `f4b197526e9cc5c64b99c7bd2ec5a7c9d5110eb2ff2916636f359e1ea6e9bae4`; task detail `1b3ec60890621915b51da0c3667a4b4333f0211cdb4b2d9c17d3ab0c19f730e3`; task index `958f25ee9931ef8e9c22c1ed5d94dc1c2f9504a7bc4d356f25ee301a3156ad4c`.
