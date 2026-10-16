# Independent manual v3 review — usable-with-scope

Reviewer: separately dispatched agent_schema_result_verify. Reviewed only Agent MEM-CHECK-SCHEMA-06, baseline 06ed701b30fc6f83c554f1f240b1f05122d387e3. TwoLevel remains paused. This is manual independent evidence, not a managed ReviewSession approval or publication authorization. No production source/test edits, model/API/GPU/network calls or v2 evidence modifications were made.

The fixed candidate passes the unchanged two-primary performance gates and the scoped correctness checks below. V1 and v2 remain rejected historical candidates. This review applies to the separately authorized correctness-only repair in repair-plan-v3.json; it does not retroactively extend the initial two-candidate plan or reset a managed budget. No fourth candidate was evaluated.

## Binding and implementation

Candidate source SHA256: `6daa9f90425763bfc03287b4a68d3dee3dde36068115d9f4791112c50ad65580`.
Candidate schema test SHA256: `88053d49cdd74adf9836dc992a9de5a047c184135a20a5a835de6f318d3fbfb3`.
Exact copies: candidate-v3.py and test-candidate-v3.py. integrity.json binds actual source, project_docs/handoff_basis dependencies, relevant tests, frozen parent plan, versioned repair plan, harness, raw producer/independent data, correctness/validity probes and logs. Both raw records' candidate/baseline source hashes match the inspected snapshot/pinned Git baseline. The producer raw record is separately copied to producer-measurement-v3.json.

Re-read the repair plan, actual implementation diff and entire new schema test file. The only source difference from v2 is comparing row_factory to the captured `_BUILTIN_SQLITE_ROW` reference and defining that reference. This closes the observed mutable sqlite3.Row guard bypass without changing traversal/hydration/timing fixtures. The v2 reproducer now produces identical successful baseline/candidate packets when a replaced global row factory drops document_dependencies while hydrating an ancestor. The new producer regression independently targets the same failure.

The shared reader retains row fetch/missing-ID error → scope JSON → schema existence query → document snapshot read/decode → dependency query ordering. Cache state is populated only following a successful schema query; false is distinguished from unknown. The shared DFS retains status/document checks before checked-set insertion, lazy sorted dependency order, one visit per reachable entry including cycles/shared ancestors, and caller-requested root order/retention. Nothing in handoff_basis changed: required check still precedes subset validation; supplied check, known refs and pending expansions remain separate validation opportunities. `_get`, direct `_check` and insertion remain uncached. The public fast path requires exact ledger/connection, owned transaction, built-in factories and unchanged entry points; customized routes fall back.

## Correctness and preserved validity checks

`independent_check.py` executed 329 complete pinned-baseline differential comparisons, with zero mismatches. Coverage: 300 seeded random graphs (shared/cyclic graphs, statuses, multiple ordered roots); 1500-deep chain; dependency-first requested roots; unknown IDs and malformed/duplicate/non-list refs; malformed or unexpected scope/document JSON; document/content/source/scope UTF-8 corruption; inactive statuses and first-error priority; legacy absent document table; missing entries/dependencies/snapshot column. Comparisons include full returned packets or exception class and exact message. Raw cases are retained in correctness.json; baseline is loaded from pinned Git bytes rather than copied candidate logic.

Independent property probes also pass:

- Native optimized diamond hydrates n3,n1,n0,n2, performs one schema lookup and preserves error-before-schema ordering for unknown ID/malformed scope. Instrumenting the helper preserves fast-path eligibility.
- Direct _get observes same-connection DDL, and direct _check remains uncached.
- Fallback query counts/sentinel dispatch cover class and instance _connect, subclass ledger, replaced sqlite3.connect, SQLite Connection subclass, nonstandard row/text factories, autocommit, class _get/_check, instance _check and replaced document validator.
- Original global sqlite3.Row callback/DDL reproducer now agrees with baseline. This fix is asserted explicitly in correctness.json, rather than inferred from a passing producer test.
- validity_probe.py uses the original document validator and a Python profiler (no validator replacement, so fast path remains eligible). All four bound entries receive real document validation. Nested caller mutation of document metadata is isolated across calls; actual TASK content change is rejected; failed malformed-scope traversal followed by repair revalidates successfully. validity.json retains observations.
- Independently ran 52 tests across tests.test_memory_check, tests.test_memory_schema_check, tests.test_project_memory and tests.test_handoff_basis: all pass. These cover path/error guards, fresh caller objects, ancestor correction, document changes, fail/retry, override behavior, cross-call schema changes and handoff validity/freshness. Logs retained. Full repository regression is a separate parent obligation.

These observations establish preservation of explicit validity operations within tested paths; packet equality alone is not being used as proof that validations ran.

## Performance replication and raw-data integrity

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python .agent-runs/memory-schema-20261016/reviewer-v3/measure-independent.py`.

The independent harness matches the frozen producer harness except private output/baseline paths and parent-plan read location. No fixture, algorithm, threshold, seed, pair count or timing scope changed. Timing completed before independent correctness tests; parent was explicitly notified to keep CPU tests idle, then sent a timing-done message. Same local machine; Python/SQLite/platform/CPU and affinity details are retained in integrity.json. Other ambient system interference cannot be ruled out.

| Fixture | Producer v3 reduction | Independent reduction |
| --- | ---: | ---: |
| chain512 | 15.01% | 13.94% |
| legacy512 | 12.16% | 11.22% |
| one | -8.16% | 2.40% |
| wide64 | 7.27% | 15.14% |
| roots128 | 12.13% | 8.79% |

Both independent primary medians exceed the frozen 10% threshold. All controls satisfy no more than 15% regression; the producer one-node regression of 8.16% is retained, not discarded. Disagreement in small-control gain magnitude indicates noise/workload sensitivity; no claim of universal gain is warranted.

All 21 before/after samples per fixture retained, three warmups per arm, seeded AB/BA schedule, five full public checks per sample. Each complete check includes path validation, connection/transaction setup, full hydration, status/document/dependency validation and return. Setup, equality checks and GC are outside timing symmetrically. Inputs and SQLite bytes match between producer and independent fixture creation. Database unchanged and complete-output equality markers hold. Recomputed all raw medians/reductions, seeded schedules, sample counts, positive finite ns/check units and IQRs; all agree. Details in integrity.json. The comparison uses ratio of per-arm medians as prospectively specified; no later statistical gate is substituted.

## Six criteria and acceptance scope

| Criterion | Verdict | Evidence |
| --- | --- | --- |
| implementation | pass within scope | Exact source review, immutable Row repair, native validity observation, fallback traces and unit.log. |
| reference_boundary | pass within scope | 329 pinned-baseline comparisons, graph/error/UTF-8/schema cases and original Row repro in correctness.json. |
| data_integrity | pass | Source/dependency/raw hashes, all 21 pairs, matching fixtures/refs/input and DB hashes in integrity.json. |
| numerical_sanity | pass | Positive finite ns/check samples, independently recomputed summaries/gates and IQRs. |
| measurement_validity | pass within scope | Full public call, frozen symmetric warmup/batching, randomized paired arm order, timing isolated from tests. |
| reproducibility | pass within scope | Independent protocol replication passes both primaries and controls; independent semantic/property/unit probes pass. |

Manual scoped acceptance: v3 ordinary owned SQLite MemoryLedger.check behavior and measured warm local synthetic complete-check latency for exactly these fixtures on this machine. This is not certification for arbitrary monkeypatching/reentrancy, concurrent hostile filesystem changes, cold disk latency, other workloads/hardware, production deployment or scientific truth of memory content. The method intentionally changes schema-query trace cardinality on the ordinary path. No model KV, QA, token, TTFT, cash-cost or end-to-end model-performance benefit is established. Parent must bind any full regressions/publication to this exact source; changes invalidate this snapshot's acceptance. No managed runtime trust receipt is asserted.
