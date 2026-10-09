# Pending inbox optimization — 2026-10-09

Independent acceptance: usable-with-scope. Added only a partial SQLite index on pending `(recipient,seq)`; query/API and stored messages are unchanged. Index builds automatically on existing databases at Mailbox initialization. ACK removes the relevant index entry without removing historical evidence.

Fixed baseline: bb5bf5b8edaebd8910f9a7af28830c668113d339. See frozen manifest/validation, independent_review.md, raw.json and independent_raw.json. Research screening and rejected transfers are in research.md; this is application of established sparse-state indexing, not a new communication algorithm.

| History | Pending | Runs | VM baseline → candidate | Inbox median ms baseline → candidate |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 1 | 101 → 116 | 0.243 → 0.315 |
| 0 | 0 | 4 | 101 → 116 | 0.231 → 0.287 |
| 0 | 5 | 1 | 205 → 201 | 0.729 → 0.708 |
| 0 | 5 | 4 | 205 → 201 | 0.592 → 0.489 |
| 1000 | 0 | 1 | 11100 → 116 | 1.455 → 0.518 |
| 1000 | 0 | 4 | 2850 → 424 | 0.773 → 0.768 |
| 1000 | 5 | 1 | 11205 → 201 | 1.417 → 0.578 |
| 1000 | 5 | 4 | 2955 → 509 | 1.063 → 0.726 |
| 20000 | 0 | 1 | 220100 → 116 | 13.095 → 0.441 |
| 20000 | 0 | 4 | 55100 → 6290 | 4.276 → 1.558 |
| 20000 | 5 | 1 | 220205 → 201 | 10.221 → 0.427 |
| 20000 | 5 | 4 | 55205 → 6375 | 3.273 → 1.379 |

At 20,000 acknowledged messages in one run with five pending deliveries, the full public inbox median fell 10.221 → 0.427 ms (23.9× in this fixture), while SQLite VM instructions fell 220,205 → 201. Empty-history VM work increases 101 → 116; small-case timing can regress. All samples/ranges are retained, with wall-time outliers up to 174.7 ms. Shared CPU, warm cache and no affinity mean no universal latency promise. Other-run pending traffic remains a scaling limitation.

Frozen write/ACK non-degradation and <10 s migration acceptance passed. Maximum producer median added write/ACK cost 0.445 ms; maximum tested migration 13.774 ms. No production traffic distribution, concurrent migration, network, model/task-quality, token or end-to-end benefit was measured.

Checks: focused suite 56 passed; independent targeted suite 73 passed plus 192 oracle/boundary comparisons. Full required repository suite ran 853 tests: 844 passed, 8 skipped, 1 generated-reference failure. The already-stale code-reading execution copy was regenerated with the existing sync script; targeted failed test then passed and sync --check passed independently. This combination resolves the sole observed failure without claiming a second broad run. Paper-reader suite 3 passed. Failed import-path/module attempts and collapsed-other-run diagnostic remain archived and excluded from acceptance.

Reproduce:

```bash
python scripts/benchmark_communication_inbox.py --baseline agent_doc/results/comm-inbox-20261009/baseline_communication.py --out /tmp/communication-inbox-rerun.json
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
```

Result catalog registration used the controller-pinned output hash of its actual independent host child context. Persisted validation is history, not renewed authorization: subsequent consumers need current bound verification. No ManagedEngine, ReviewSession, remote model adapter or new supervisor was deployed. Plan publication review is a bounded actual separate context, not a fabricated runtime receipt.

Publication checkpoint: independent acceptance and checks complete; refresh main and ordinary push are required next. Larger inboxes, concurrent writes/migrations and actual model communication workloads remain subsequent bounded candidates, not accepted claims.
