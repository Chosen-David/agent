# Final inbox integration — 2026-10-09

Independent result acceptance: usable-with-scope. Publication baseline is concurrent main0498816, which adds an exact transactional usage ledger. The only additional runtime delta remains a partial pending-recipient index. This fresh result replaces comm-inbox-20261009 as current performance evidence; that original run remains unmodified historical evidence.

| History | Pending | Runs | VM baseline → index | Inbox median ms baseline → index |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 1 | 129 → 144 | 0.300 → 0.388 |
| 0 | 0 | 4 | 129 → 144 | 0.269 → 0.292 |
| 0 | 5 | 1 | 233 → 229 | 0.327 → 0.462 |
| 0 | 5 | 4 | 233 → 229 | 0.438 → 0.389 |
| 1000 | 0 | 1 | 11128 → 144 | 0.676 → 0.307 |
| 1000 | 0 | 4 | 2878 → 452 | 0.412 → 0.329 |
| 1000 | 5 | 1 | 11233 → 229 | 0.719 → 0.345 |
| 1000 | 5 | 4 | 2983 → 537 | 0.514 → 0.399 |
| 20000 | 0 | 1 | 220128 → 144 | 10.286 → 0.437 |
| 20000 | 0 | 4 | 55128 → 6318 | 3.424 → 1.370 |
| 20000 | 5 | 1 | 220233 → 229 | 9.589 → 0.509 |
| 20000 | 5 | 4 | 55233 → 6403 | 3.665 → 1.436 |

At20k acknowledged-history plus5pending one-run: 9.589→0.509ms (18.8× fixture median), 220233→229 VM steps. Empty inbox:10.286→0.437ms. Index benefit is isolated against ledger-enabled main, not credited with the concurrent ledger improvement. Maximum added median publish/ACK cost0.126ms and measured index upgrade9.418ms. Migration timing starts from a ledger-enabled database; combined pre-ledger upgrade is functionally tested in the ledger suite but no combined timing claim is made.

All21paired producer samples and independent5paired samples retained; three warmups, connection/JSON included, VM profiling separately. Exact12-case matrix,192independent reference checks,73targeted+9ledger tests and full862tests OK (8skipped); reader prior3tests pass and its source unchanged. No universal speedup: empty/tiny cases can cost more; unrelated-run pending rows and sorting remain; warm filesystem cache/shared CPU/no affinity; no real traffic, contention, network, model-quality, token or end-to-end benefit claim.

Direct SQL fixture INSERTs are accounted by the new ledger triggers; independent direct UTF-8 count/byte scans verified this. Event/ACK/budget/evidence/knowledge semantics and public API are retained. No SGLang, roles, marketplace or model runtime changes. New protocol/services deferred after source screening in ../comm-inbox-20261009/research.md.

Reproduce: `python scripts/benchmark_communication_inbox.py --baseline agent_doc/results/comm-inbox-integration-20261009/baseline_communication.py --out /tmp/inbox-integration.json`. See frozen manifest.json/contract.json/validation.json, independent_review.md and plan_review.md. Actual independent host context output was pinned by controller at registration; persisted proof alone does not authorize later reuse. No runtime supervisor/ReviewSession installed.

Publication checkpoint: ready for fresh main synchronization, non-force push and remote SHA readback. Both concurrent improvements preserved. This bounded result does not conclude the ongoing communication research objective.
