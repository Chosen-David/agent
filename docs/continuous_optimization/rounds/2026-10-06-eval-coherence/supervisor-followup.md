# User-prioritized supervisor follow-up, wake w2

2026-10-06 user asks about slow-task diagnosis, per-task TASK attribution and remembered commit/push. Fresh fetch confirms HEAD = origin/main = e8ee3dca5dc8cd076fc031dd4510dabde214e046. Existing dirty work matches all16 w1 checkpoint hashes; checkpoint-w1.json preserves that checkpoint. No implementation changes existed before this follow-up.

The batch is retained, not reset. Two completed papers still apply to verification/termination and outcome correctness. CO-020 material-preflight implementation is deferred behind the user's explicit runtime concern; no prior experiment or paper is discarded. Publication still requires ten-paper synthesis and final-candidate actual-role gates.

## Preregistered local change and acceptance

Observed source: Engine.tick increments attempts for each claim, then treats pending and retry alike for exhaustion. Its claim loop starts at plan index0 every tick. Thus a polling task can exhaust retry allowance or dominate later independent tasks.

Counterfactual tests: with explicit waiting policy and max_attempts1, a legitimate pending then complete task currently fails after its first poll; with waiting task first and independent quick task second, two due ticks claim the first twice. Preserve failing tests before patching.

Mechanism: opt-in immutable wait_policy separates bounded observation polls from failed action attempts; keep legacy plans unchanged, never reopen exhausted records or refund unknown/crashed side effects. Respect both maximum polls and elapsed waiting time; expiration blocks for diagnosis, never reports success or kills external work. A persisted rotating claim cursor gives due independent tasks a turn. Main-owned progress reports expose counters, waiting/diagnosis flags and task_refs to the existing maintain callback.

Metrics/threshold: both demonstrated bugs fixed; normal pending beyond max_attempts can complete within wait budget; independent due task is served by second tick; retry/exception/expired lease still consume attempts; poll/time bounds block, never pass; duplicate/early tick and reopen preserve bounds/fairness. Legacy tasks keep existing semantics. No new unbounded loops, privileged backend, process killing or automatic algorithm switch.

Acceptance: targeted controlled-clock SQLite tests covering normal/limit/restart/cancel/fairness/legacy; existing runtime/manifest/supervisor tests, then full program regressions as affected shared core. These are program tests with synthetic handlers, not model tasks or production speed evidence. Source/task definitions for eventual model release must be rebound to the final candidate; prior model results cannot cover these changes.

Bounded scope for this follow-up: runtime waiting/fairness foundation and concrete status exposure. Task-change provenance and staged publication are separate pending deliverables, not silently claimed as implemented. Diagnose->hypothesis->same-input correctness/performance comparison->adopt/retain requires a real trusted host adapter and explicit remaining budget. Neither this record nor a maintain function reference starts such an adapter.

Main publish authorization applies only to this repository after all release gates. No commit/push merely because a task finished, no SGLang change, no automatic force push. Further source and ten-paper research continues from w1, not recounted.

## Observed w2 results and limits

Baseline log `evidence/waiting-baseline.log` preserved: 11 tests with 15 subtest failures and 3 errors; normal-wait and fairness counterfactuals failed. Candidate initial waiting suite 11/11 passed. Full run first found one partial-snapshot compatibility error among371 tests; retained log, fixed missing counters as unknown. Next full run372 tests364passed8skipped. Independent reviewer then found cancellation/reconciliation diagnostics overriding terminal guidance and elapsed diagnostics delayed until next poll. Both were fixed with three additional regressions. Final full run375 tests367passed8skipped,28.048s; reader3/3. These are deterministic program tests, not model A/B or acceleration benchmarks. See all w2 logs and initial/follow-up independent review reports.

Unpublished files: core bounded waiting/fairness, manifest TASK-linked execution observations, opt-in draft/template policy, supervision workflow and generated plugin reference, regression tests. Existing legacy plan pending semantics remain unchanged. No running host optimizer, per-change Git provenance service, automatic publisher, target-server tmux deployment or model-quality gain is claimed.

Latest user steering puts research writing first next wake. Diagnose paper-vs-report structure, argument and language using private sample if available; research directly relevant methods/Skills; freeze at least3 distinct complete-draft tasks including heldout before edits. Root must read full drafts and final PDFs if generated, preserve negative evidence and actual before/after outputs. Private sample is not added to this public repository. Existing task prompt was updated and read back with same schedule and enabled state; no duplicate task. Research remains2/10 and no current-candidate role/handoff executions, so no commit/push. Preserve all checkpoints and unfinished provenance/publishing work.
