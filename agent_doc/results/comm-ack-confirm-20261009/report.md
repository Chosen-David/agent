# ACK retry one-shot confirmation — 2026-10-09

**Outcome: rejected for adoption; runtime remains exact baseline.** This is a valid negative result, not a communication performance upgrade. The producer100-event primary median increased0.301802→0.308165ms (+0.006363ms). Removing the redundant UPDATE reduced logical SQLite changes1→0 and VM callbacks170→141, but the frozen BOTH-cohort latency gate failed. No repeated benchmark or relaxed threshold was used. The independent cohort passing does not override the failed producer cohort.

Baseline main `f044ef39413f2adb47cf720d3a8f58ed6666f861`; candidate only returns for a canonical identical stored receipt after validation/budget/BEGIN IMMEDIATE/run lookup/immutable conflict checks. This is ordinary redundant-write elimination, no claimed scientific novelty. Prior COMM20-r10 negative remains intact.

| Cohort | Events | Routes | Baseline ms | Candidate ms | Ratio | Primary improvement gate* | Public guards |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| producer | 100 | 1 | 0.301802 | 0.308165 | 0.9794 | no | pass |
| producer | 20000 | 1 | 0.328562 | 0.298187 | 1.1019 | yes | pass |
| producer | 100 | 1000 | 0.320297 | 0.312177 | 1.0260 | yes | pass |
| independent | 100 | 1 | 0.486377 | 0.453319 | 1.0729 | yes | pass |
| independent | 20000 | 1 | 0.299821 | 0.292591 | 1.0247 | yes | pass |
| independent | 100 | 1000 | 0.310183 | 0.313755 | 0.9886 | no | pass |

*First two shapes are mandatory primaries; third shape's improvement value is descriptive only. Each cohort has31 alternating public-method pairs after3warmups. Adoption requires both primaries in both cohorts to pass the frozen operation-reduction+latency-nonregression or1.25x+.05ms branch, plus all public guards. Complete guard medians, ranges, reopen/migration diagnostics and SQL traces are in independent_decision.json/raw.json. Database storage matches. Identical DDL makes maintenance timings diagnostic; no cold-start gain claimed.

Checks:25 existing candidate communication/usage tests in each cohort;61 independent public list/byte/trust properties,57 ACK properties and2 existing regressions on each frozen source. ACK properties include all statuses, key reordering, invalid/conflicting/missing/cross-run receipts, concurrent initial ACK and repeats, transaction release/reopen/counters. Six independent code/data checks are usable-with-scope. ValidationSHA `2be9a00303b25d60a87cf1604ea5426d776eabc5f21693a424326bfbf9157d4b` was authenticated through actual fresh host child `/root/ack_verify` and registered natively; this hash alone is not proof of identity or correctness.

Preserved failures: original plan review v1 requested consistent Boolean/input pins, approved v2 fixes both before measurement. Independent validator initially expected COMMIT inside a trace whose callback is removed before context exit; attempt1 failure/log and correction note remain. Only the diagnostic assertion was corrected, with no performance replay or gate change. Exact replay samples and frozen manifest unchanged.

Scope: local shared-CPU warm-cache SQLite/filesystem envelope workloads. Logical UPDATE/total_changes is not physical disk I/O, transmitted bytes, token savings or wall-clock throughput. BEGIN IMMEDIATE and connection cost remain. No LLM/task-quality/network/billing/remote-deployment/GPU claims. Since candidate is not adopted, no new full-suite integration run was necessary and no previous full-suite result is presented as current. No deployed tmux/monitor backend is available or claimed.

Source screening: research.md / screening_followup.md / post_negative_screening.md record primary papers dated2026-10-02/03/05, author GitHub/official SQLite/AWS engineering sources, exact reading scope and mismatches. MASBench motivates paired outcome+cost evaluation; Coda needs an inference/KV serving layer; Copies or Sources suggests provenance-aware quality testing; scalar distributed optimization assumptions do not match artifact envelopes. After the negative result, bilateral compression-cost paper was examined: sender/receiver and repair costs must stay separate, and early task failure cannot count as savings. No author result is imported as a repository gain.

Next eligible research: task-grounded outcome/cost fixtures with complete denominators and explicit cost units; exact batching with independently specified failure/atomicity semantics. These are untested hypotheses, not completed upgrades or authorization to omit messages. Current bounded confirmation is complete after verified evidence publication/readback; broad continuous communication optimization remains active. Human-only guide and SGLang unchanged.
