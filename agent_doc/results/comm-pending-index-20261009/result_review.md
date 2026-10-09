# Independent result review — COMM-PERF-01

Decision: **usable-with-scope**; all final manifest/artifact bindings verified. The independently executed quiet run satisfies all three frozen improvement gates. No second candidate is needed to establish this narrowly scoped result.

Reviewer: actual Work collaboration context `/root/comm_review`, separate from producer `/root`. Independent benchmark process session30312 completed successfully. All six cases ran using the frozen plan and the inspected metadata-only harness revision; the producer stated no other heavy work would run. This is a manual host verification, not an authenticated runtime-service deployment.

## Independent measurements

| Case | Baseline median µs | Candidate median µs | Speedup | VM steps baseline → candidate | File growth bytes |
| --- | ---: | ---: | ---: | --- | ---: |
| small | 541.441 | 524.626 | 1.032× | 1828 → 1416 | 4096 |
| default_backlog | 1364.433 | 430.043 | 3.173× | 11450 → 816 | 12288 |
| large_backlog | 8575.754 | 484.557 | 17.698× | 110700 → 1416 | 20480 |
| drained | 6969.502 | 345.077 | 20.197× | 110100 → 116 | 0 |
| multi_run | 3039.400 | 2374.364 | 1.280× | 27826 → 53016 | 1130496 |
| other_run_pending | 3116.979 | 2550.800 | 1.222× | 27601 → 52616 | 1126400 |

The default_backlog, large_backlog and drained cases each exceed80% VM-step reduction and2× median speedup. Multi-run VM work worsens despite lower measured latency; this rules out any universal query-work improvement claim. The recipient index does not partition pending entries by run. No claim is made for unseen scales, workloads, SQLite versions or concurrent writers.

## Actual independent checks

- Read the complete additive source diff, relevant existing/new tests, original harness and metadata-only revision. Message contracts and all inbox query semantics remain unchanged.
- Executed all six cases independently with31 paired polls,31 paired publishes and31 paired ACKs per case,5 warmups, alternating order and separate VM instrumentation. Full output: `raw/independent-quiet.json`.
- Independently regenerated all event tuples and fixture SHA-256 values from the plan, two-byte artifact digest and deterministic construction. Checked case order/config equality, pending counts, every sample count/positive integer value, exact median and nearest-rank p95, speedup/reduction summaries and semantic-equivalence assertions.
- All VM counts, query plans and fixture digests exactly reproduce the first run. All actual per-arm PRAGMA values agree: journal_mode=delete, synchronous=2, page_size=4096, cache_size=-2000. Read-window timestamps are present and ordered.
- Independently executed `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p test_communication.py -v` after benchmarking:16 tests,0.233s,OK. Covers migration, sparse/interleaved runs, recipient independence, FIFO/limits, invalid input, retry, immutable receipts, reference changes and budgets.
- Read the full-suite outcome:854 tests,1 failure,8 skips (845 passes). Its stale generated `code-reading_execution.md` failure also appears in the preserved clean-baseline reproduction log. The relevant sync test/script/reference have no diff from the pinned baseline. This is an existing repository limitation; the broad suite is not reported as fully passing.
- Independently read `/proc/cpuinfo`, os.cpu_count/sched_getaffinity, platform and SQLite version; these match environment.json:Xeon Platinum8573C,9 logical/available CPUs,SQLite3.53.1,Linux6.18.44/glibc2.39.

## Costs and limitations

Full public-operation costs remain visible rather than being inferred from query speed:

| Case | Publish median candidate/baseline | ACK median candidate/baseline | First candidate open ms |
| --- | ---: | ---: | ---: |
| small | 1.173 | 1.058 | 0.733 |
| default_backlog | 0.853 | 0.756 | 1.728 |
| large_backlog | 1.051 | 1.122 | 6.541 |
| drained | 1.015 | 1.199 | 5.827 |
| multi_run | 0.978 | 0.929 | 20.755 |
| other_run_pending | 1.113 | 1.079 | 18.847 |

These are observed ratios from one31-pair set, not stable universal write-cost bounds. First-open includes complete Mailbox initialization and index creation; it is a single observation, not isolated index-build timing. File growth may be zero when SQLite reuses free pages, and is not the index logical byte size. Multi-run cases grow the database file by about1.13MB.

The first run overlaps a full test suite and its wall-clock timings are exploratory only. The quiet independent run provides the accepted local latency observations; exact VM work/semantics match both. External host interference cannot be globally excluded. Samples are synthetic warm-cache local polls, no model/token/end-to-end quality, GPU, cloud automation execution or remote/tmux deployment evidence.

Finite tests and review support usable-with-scope acceptance only, never an absolute bug-free guarantee. Final verification.json must bind the finalized manifest and every artifact; changing code, data, protocol or bound summary requires revalidation.

Independent raw SHA-256: `7a024b80a4777e71981835671c8fd5b68e49f878014e45d854b540fb61ddc64e`.
Harness SHA-256: `c9df7dcc141cf460fbdf20c3ff142dd5cdd99621b8b181395d1000f8aafff2ab`.
Candidate SHA-256: `13c24e39159ce8199db36210f7653f2bbc6fbfc83bf753d9da2df993c9440bec`.
Plan SHA-256: `8d8ae18d169d51a9d4f1553d7c743d1c6c65d050c79a01258bda7f9ef9eb3c37`.

## Final binding and publication review

Manifest SHA-256: `3b5894a95e7241f85e0936b47db425455c54302b2e0dfd7ee60c80a7a20a6a26`. Every declared artifact and validation-plan hash was re-read and verified using `_snapshot`; archived baseline source bytes exactly match both the pinned git object and executed baseline hash. All24 manifest metrics and units, and every measurement_summary field, were independently compared with quiet raw data. The summary’s historical pending flag is not an acceptance proof; this independent review/verification supplies the final scoped acceptance. Report.md numerical tables and cost/limitation disclosures were checked against raw data. No broad-suite-full-pass or live deployment claim is accepted.
