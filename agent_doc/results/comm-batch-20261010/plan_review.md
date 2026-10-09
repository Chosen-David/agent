# COMM-BATCH-01 independent plan review

**Revise — cycle 1 of 2.** Exact full DAG SHA-256: `1f67dfba2fd12d8a0589b7a93891d4e3362952aca2e308efd6984f0f68593dba`. One blocking finding; no benchmarks or functional tests were run.

All 24 frozen input hashes match actual files. Canonical TASK/detail snapshots match, HEAD is the frozen base, and live communication source equals the frozen baseline.

- **intent: pass.** Current delegated user authorization permits bounded safe communication upgrades and direct main publication. New API is explicit opt-in, baseline retained unless frozen evidence gates pass; no SGLang or human-guide writes.
- **guide: pass.** GUIDE.md is actually empty. Guide README is read-only governance, not a fabricated project requirement. Canonical TASK/index and COMM-BATCH-01 detail byte-match frozen snapshots. Advice is non-authority; no task-specific advice adopted.
- **assumptions: pass.** Static extraction preserves ordinary publish validation, SQL, transaction, duplicate checks and outputs. Batch uses one call-local connection and transaction, never r20 persistent connection. Atomic reference executes original publish with only borrowed connection/nested BEGIN suppression and no nested commit, with finally cleanup and outer rollback/close. Sequential versus atomic failure distinction is explicit.
- **prior_results: pass.** Actual prior search is retained with 96 scans, partial=true and missing-record errors; not claimed exhaustive. Route/ACK historical negatives and r20 ProgrammingError failures are preserved, not reused as current batch gain data. Shared public harnesses are source reuse only. No applicable knowledge card is adopted.
- **acceptance: fail.** Success thresholds, safety gates, deferred CLI8 and native contracts are sound, but benchmark.py writes raw only at successful completion. A thrown assertion discards completed/partial sample evidence and trace, violating preserve-all-failures and data_integrity. Versioned exception-safe evidence retention is required before dispatch.
- **risk: pass.** Bounded 1..100 atomic API makes failure rollback and visibility explicit. Filesystem checks under write lock and unbounded artifact-time are disclosed; no deployment fairness/LLM/network/token or novelty claim. Thread/idempotency, duplicate-reference/routes, cumulative budgets, rollback and independent reader-visibility oracles remain mandatory before adoption. Exact candidate publication requires independent integration acceptance and fresh expected-head non-force readback.
- **resources: pass.** One candidate, zero performance/tuning retries, root plus one independent 31-sample replay, 900 CPU seconds including integration, two review cycles total. Current cycle is one. Unsupported tmux/backend is disclosed, actual synchronous host only; no Engine/ReviewSession/supervisor installed claim. Resource accounting and authentic host invocation records remain execution obligations.

## Blocking finding BATCH-PLAN-01

Location: `agent_doc/results/comm-batch-20261010/benchmark.py: run(), result accumulation and final out/raw.json write`.

Output directory/raw.json are created only after all correctness assertions and all shapes finish. An exception in public output/state equality, ACK, SQL tracing, or a later sample loses every completed timing/ACK sample and partial trace when TemporaryDirectory exits. A whole exception log is insufficient to preserve actual raw failure data or audit previously attempted samples. This conflicts with preserve-all-failures and the frozen data_integrity protocol, even though adoption is blocked on failure.

Before any benchmark work, create the unique output namespace. Persist raw result incrementally or in a finally/exception handler, including phase/case/repeat/order, every attempted/completed timing/ACK sample, partial returned outputs and outside-timing trace collected so far, and exception metadata. Mark an interrupted run incomplete/invalid and re-raise; do not accept it as a measured negative performance result, retry, tune thresholds, or overwrite prior evidence. Preserve enough fixture state/evidence for the failed boundary without requiring arbitrary sensitive temp files. Apply the new frozen harness hash through a versioned full DAG and plan snapshot and request cycle 2 before any measurements.

Static review in cycle 2 checks early output creation and exception-safe checkpointing. During authorized execution, preserve any actual failure evidence; a low-impact deliberately failing instrumentation check may be used before timed cohorts if recorded as a harness check rather than an extra performance retry. Native validator must confirm attempted sample coverage and no adoption on incomplete output.

## Full execution notes

- Approval is a static plan opinion, not host authorization, a trusted ReviewSession receipt, measured gain, result acceptance, or installed supervision. Host must bind the real independent invocation and retain this complete feedback.
- Keep source/import dependency hashes and cumulative CPU accounting in executed manifests. Independent validator must review and run its own atomic-reference invalid fixture and reader-concurrency visibility oracle; existing producer seven tests do not replace those preregistered checks.
- Integration validator should distinguish already accepted upstream 31-pair performance data from fresh integration test data; the shared six-domain protocol text does not authorize a second tuning/replay loop.
- Knowledge no-hit output lacks query text; the plan snapshot states transaction/atomic/batching query and no refs adopted. Reviewer separately ran the explicit local query SQLite transaction atomic batching; five lexical sqlite-only mathematical hits are unrelated to SQLite transaction semantics and rejected. No new knowledge requirement is inferred.
- External research statements are background mechanism analogies only. Reviewer did not independently reproduce external papers or web facts, and they cannot substitute for actual local evidence. The inaccurate research wording that context manager closes is corrected by actual source: connect has explicit finally db.close().
- The existing 25-test helper replaces module Mailbox for in-process tests, while its CLI subprocesses run the live baseline before adoption. Report this mixed coverage precisely; actual candidate CLI8 and full integrated tests remain required before publication, as preregistered.

Full feedback SHA-256: `5f5df048080548882d23631f72a7f994cb05c4a51171493d241be86c2085e430`. JSON preserves the complete finding, seven checks, actual input hashes and additional read references.

This opinion does not authenticate host identity, accept results, authorize tools, or install Engine/ReviewSession/supervision. Do not dispatch measurements under this failed cycle-1 acceptance check.
