# Independent integration result review — COMM-PERF-01

Decision: **usable-with-scope**; final manifest and all declared artifact bindings independently verified. The fixed additive-index candidate passes all three frozen backlog gates against0498816. The small queue has no measured benefit.

Reviewer: actual Work collaboration context `/root/comm_review`, separate from planner/implementer `/root`. Independently launched and observed full6case quiet run in process session23904, then recomputed all data and executed affected tests. Manual host review only; no automatic ReviewSession/tmux deployment claim.

## Current integration results

| Case | Baseline median µs | Candidate median µs | Speedup | VM steps baseline → candidate | File growth bytes |
| --- | ---: | ---: | ---: | --- | ---: |
| small | 420.445 | 423.541 | 0.992690× | 1856 → 1444 | 4096 |
| default_backlog | 1072.846 | 468.431 | 2.290297× | 11478 → 844 | 12288 |
| large_backlog | 9743.258 | 678.521 | 14.359553× | 110728 → 1444 | 20480 |
| drained | 7292.756 | 388.413 | 18.775777× | 110128 → 144 | 0 |
| multi_run | 3091.412 | 2449.530 | 1.262043× | 27854 → 53044 | 1130496 |
| other_run_pending | 3001.793 | 2459.433 | 1.220522× | 27629 → 52644 | 1126400 |

All three named gates (default_backlog,large_backlog,drained) achieve>80% VM-step reduction and≥2× median speedup. The two multi-run controls retain approximately1.9× VM-work regressions and about1.13MB file growth despite lower observed latency. The index does not partition pending deliveries by run; these results cannot justify universal lower query work or cross-run scalability.

## Independent checks and integration boundary

- Verified byte-for-byte that current communication.py equals upstream0498816 after removing precisely the approved three index-DDL lines. Upstream usage initialization, counters/triggers, publish budgets and usage API remain intact in both benchmark arms.
- Read upstream ledger implementation and all9ledger-specific tests covering exact accounting, Unicode, event/byte caps, rollback, concurrent publication, old-writer upgrades and atomic migration failure/retry. Existing16communication cases cover recipient/run independence, sparse receipts, FIFO, migration, reference errors and immutable receipts/retries.
- Verified approved plan hash, unchanged workload objects and improvement gates, fixed one-candidate budget, source/harness/baseline hashes and metadata-only harness implementation. No alternative query was tested.
- Ran all six frozen cases independently with5warmups and31 alternating pairs each for full inbox, publish and ACK. VM instrumentation was separate. Exact expected inbox contents and final status/usage match both arms.
- Independently regenerated all event tuples/fixture digests from deterministic ordinal events and the two-byte artifact digest; confirmed expected pending counts, all6case configs, every31x2raw array and positive integer sample, exact median/nearest-rank p95 and ratios.
- Actual matching per-arm settings: journal_mode=delete,synchronous=2,page_size=4096,cache_size=-2000. All read windows have ordered timestamps. Host heavy work was paused for this run according to the coordinating parent; external unrelated interference cannot be fully excluded.
- Independently executed after measurement: `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p test_communication*.py -v`:25tests,0.552s,OK. Then plugin reference sync unittest:1test,0.119s,OK. Parent preserved equivalent25+1passing logs. No full-suite rerun performed; exact additive delta plus affected integration coverage did not reveal a need.
- Prior broad854test run belongs to the old snapshot and retains its8skips/1known failure; that sync failure is now fixed upstream and passes the focused check. Do not convert this into a claim that a new full854test run passed.

## Costs

| Case | Publish median candidate/baseline | ACK median candidate/baseline | First candidate open ms |
| --- | ---: | ---: | ---: |
| small | 1.073 | 0.858 | 0.804 |
| default_backlog | 0.892 | 1.020 | 4.099 |
| large_backlog | 1.108 | 1.004 | 7.782 |
| drained | 1.053 | 1.013 | 5.326 |
| multi_run | 1.173 | 1.006 | 21.621 |
| other_run_pending | 1.194 | 1.156 | 20.034 |

Ratios are observations from one31-pair set, not stable overhead bounds. First-open is one full-constructor observation, not an isolated index-build distribution. File growth can reuse SQLite free pages; zero growth does not mean zero index storage.

## Scope and historical evidence

This result concerns six deterministic synthetic local SQLite workloads and the exact0498816+index source snapshot. No model/token/network/GPU/end-to-end quality or remote service claim is supported. Latency magnitudes vary with host noise, versions and workload. Finite testing/review supports usable-with-scope only, never universal bug freedom.

The earlier comm-pending-index-20261009 raw data, manifest and review remain historical against their original source hashes. No historical pass was copied to authorize this source: the concurrent usage ledger changed initialization/write behavior and motivated this separate integration run. The current full rerun reproduces the prior qualitative backlog benefit and multi-run limitation without treating old numerical speedups as current results.

Current source SHA-256: `c02b577228f9625e7bcb641e7be1448c2733b8de480c574efcc11617b327ebad`.
Current baseline source SHA-256: `eecfe2b16a40d6118db8d7c99f9a89311eaaf491a55a51b6ac65c924d2ae115e`.
Frozen harness SHA-256: `c9df7dcc141cf460fbdf20c3ff142dd5cdd99621b8b181395d1000f8aafff2ab`.
Plan SHA-256: `7a29da1164388485f2daf48ed4ddc1d629e56352f212bb7f58034163a577e704`.
Independent raw SHA-256: `d8b8d44e2a4e30bd98a639b91824bee3dc25535a8650dbfe5d1c3119d509c987`.

## Final binding

Manifest SHA-256: `f712719dda9410fc81ee225af703c6ea2687b4a4d616e1d795cfe1f7f733d12b`. Native `_snapshot` re-read every declared code/input/config/raw/output/environment and validation-protocol hash. Actual archived baseline is byte-identical to the0498816 git object; archived candidate is byte-identical to executed current source. All24manifest metrics/units, all summary fields and both six-row publication tables (poll/VM and write/ACK/first-open/file costs) match independent raw recomputation. Final report clearly distinguishes current25+1tests from the historical full-suite outcome, small-control non-improvement and multi-run VM regression. No blocking publication finding remains within the declared scope.
