# Manual independent v2 result review: REJECT

Reviewer: separately dispatched agent_schema_result_verify. Scope: only Agent MEM-CHECK-SCHEMA-06, baseline 06ed701b30fc6f83c554f1f240b1f05122d387e3, candidate source SHA256 7623375d43446933955ef83d6aad1f2737a2768c0056bad594b55464c4814ce4. TwoLevel remains paused. This is independent scoped code/data review, not managed ReviewSession approval, publication authorization, or a universal correctness guarantee.

The performance data are credible for the frozen synthetic CPU fixtures, and independent replication passes the numerical gates. Implementation correctness fails the promised custom-factory fallback boundary. Do not consume v2 as an accepted optimization.

## Blocking finding

`_connect` sets `db.row_factory = sqlite3.Row` dynamically. The optimized-path gate compares `db.row_factory is sqlite3.Row`, also dynamically. Replacing the module attribute `sqlite3.Row` with a custom callable therefore satisfies the guard; this is a custom factory rather than the ordinary built-in factory promised in the frozen plan. A factory returning the original Row can execute DDL during ancestor hydration. Repro preserved in independent_check.py: when n1 is hydrated, drop document_dependencies. Pinned baseline completes check(['n3']); candidate raises MemoryError `project memory ledger unavailable: no such table: document_dependencies`. Candidate reused the earlier present-table result across a callback-induced DDL change. The promised fallback must exclude a replaced Row symbol using an immutable original identity. This is a compatibility defect, not a timing noise issue.

This reviewer made no source/test/publication edits. Parent was informed immediately and confirmed v2 rejection. Any later repair requires a separately versioned plan and new binding; v2 raw results and this rejection remain history.

## Independent execution and evidence

- Read AGENTS, decision/document/result governance, frozen plan and complete independent-plan/static review, implementation diff, candidate tests, memory regression tests, producer measure.py and both producer raw measurement versions. Prior-search.json records a partial 200-record search with errors; old memory-check03 and unrelated hits do not establish this candidate's performance. Reuse is limited to context/method, never prior pass labels.
- Ran 129 pinned-baseline differential cases: 100 seeded random graphs with cycles/shared parents/status combinations; ordered roots, dependency-first requested roots, invalid refs, unknown IDs, 1500-deep chain; malformed and non-list scope JSON, malformed document JSON/UTF-8, content/source/scope UTF-8, inactive statuses, first-error priority, legacy absent document table, missing entries/dependencies/snapshot column. All 129 ordinary output/exception class+message comparisons match. This does not negate the explicit custom Row counterexample.
- Native-path SQL trace verifies the full diamond hydration order n3,n1,n0,n2, exactly one schema query, and missing ID/malformed scope errors before any schema query. The trace patches only the new shared helper, preserving native eligibility. Direct _get sees same-connection DDL, and direct _check remains uncached. Each requested root and all ancestors are still visited/validated.
- Explicit fallback checks cover instance/class _connect, subclass ledger, replaced sqlite3.connect, SQLite Connection subclass, nonstandard row/text factories, autocommit, class _get/_check, instance _check and replaced document validator; expected uncached query counts/sentinel dispatch pass. The global sqlite3.Row replacement is the failing additional factory route above.
- Independently ran 31 tests in tests.test_memory_check, tests.test_memory_schema_check and tests.test_project_memory: all passed. These include caller mutation isolation, document edits, ancestor correction, fail/retry freshness, instance override repair and direct DDL. Tests are supporting evidence, not implementation acceptance.
- First differential setup attempt failed SQLite FK protection while attempting to drop referenced entries. Preserved correctness-attempt1.log. Only the private fixture setup was corrected to drop referencing tables first, then rerun; no candidate code changed and no failed experimental case was discarded.

## Performance/data validity

Independent command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python .agent-runs/memory-schema-20261016/reviewer/measure-independent.py`. Uses the exact frozen producer harness except output/baseline paths under reviewer and plan read from parent. No algorithm or protocol changed. Parent explicitly kept CPU tests idle during timing; timing-done message sent before correctness tests. Other system-level interference cannot be excluded.

| Fixture | Producer v2 reduction | Independent reduction |
| --- | ---: | ---: |
| chain512 | 14.03% | 16.97% |
| legacy512 | 11.99% | 12.75% |
| one | 2.91% | 5.42% |
| wide64 | 4.99% | 10.28% |
| roots128 | 10.01% | 11.53% |

Both independent primaries exceed unchanged 10% minimum; every control is below the 15% maximum regression. All 21 pairs/arm are retained. Recomputed every median reduction from raw samples in v1/v2/independent files, checked positive finite ns/check values and seeded AB/BA schedules, input/SQLite hashes, output equality and unchanged DB markers. Integrity details and relative IQRs are in integrity.json. Primary and independent input hashes match. Setup/equality/GC are outside timing; full public check including path validation, connection/transaction, full hydration/validation and return is timed in batches of five after three warmups/arm. This is a warm local synthetic SQLite complete-check metric, not disk-cold latency, model KV, QA, TTFT, tokens or production throughput.

Producer v1 binds a888edab... and remains rejected historical data due to the earlier instance override defect. Producer v2 and independent replication bind 7623375d...; exact snapshots candidate-v2.py and test-candidate-v2.py are preserved. Actual implementation dependencies and evidence hashes are recorded in integrity.json. Parent changed live source/test to v3 after v2 execution and snapshot capture but before final inventory: live source/test hashes in that inventory describe later-state v3; the exact preserved v2 snapshots bind this review. No v3 validation was performed. Frozen plan prospective chronology is supported by retained plan/review/parent events; file hashes alone do not cryptographically prove creation chronology.

## Six validity criteria

| Criterion | Verdict | Reason |
| --- | --- | --- |
| implementation | fail | Mutable sqlite3.Row identity bypasses custom factory fallback. |
| reference_boundary | fail | Independent pinned-baseline counterexample despite ordinary differential parity. |
| data_integrity | pass | 21 pairs retained, hashes/inputs/order/sample counts and raw summaries checked; v1 preserved separately. |
| numerical_sanity | pass | Positive finite ns/check samples; recomputed summaries/gates agree. |
| measurement_validity | pass within scope | Complete public call, symmetric setup/warmup, randomized pairs; synthetic/local warm-cache scope only. |
| reproducibility | mixed/fail overall | Independent performance and ordinary correctness replicate; custom factory defect also independently reproduces. |

No scoped implementation acceptance is issued. Final full repository regression and publication remain parent obligations for any repaired candidate. This snapshot is rejected and must not be represented as usable-with-scope implementation evidence. Runtime hooks beyond the explicit override boundary, hostile concurrent filesystem mutation, model integration, performance on other hardware and workloads, and arbitrary customization are not certified.
