# MEM-SCOPE-02 independent code and result verification

Verdict: **usable-with-scope** for the frozen local SQLite retrieval change and
the six synthetic warm-cache cases below. Both primary and independent samples
meet the fixed >=25% sparse-scope improvement and <=15% control-regression
criteria. No blocking finding remains within that scope.

This reviewer was invoked through a separate, fresh host collaboration context
as `memory_scope02_review`, read the repository rules and exact implementation,
and ran the commands below independently. This is not an authenticated runtime
ReviewSession, result-handler receipt, deployed monitor, or publishing authority.
The main agent owns implementation, tests, task index, reports, and publication;
this reviewer wrote only its assigned independent evidence files and the earlier
temporary plan review. Timings were explicitly serialized with the main agent.

## Frozen identity

- Reference commit: `f872166a7ce4c61e21353dad83a83729d44440ca`.
- Reference source SHA256: `5ae35f1dcad87ab759fe4aab5f7deb522c9a3ea1d01ef8118c4ca65547ef7b19`.
- Candidate `agent_runtime/project_memory.py` SHA256: `914229446d705343ef71d81c79b20b7119652a376aa180e9eff54e83a7d1d450`.
- Primary raw SHA256: `f5a2502f269a67e0aaefa69361c101989c151fdd9708d181250d7e5445b3dcbb`.
- Independent raw SHA256: `e9251abf79e242492f5061621a3c5b20feeaedc2e780e4778d66d3b248b2beee`.

The reference is the already status-optimized current baseline, not the older
eager algorithm. The benchmark loads its exact Git bytes, verifies their hash,
and constructs the reference class in a separate module namespace so its exact
`type(self) is MemoryLedger` branch remains active. Candidate bytes were checked
again after independent runs and still match the frozen hash.

## Six validation checks

1. **Implementation: pass.** Read the actual diff and full list/_get/connection
   paths. Only an existing mixed-status fast path with exact built-in str scope
   gains scope filtering. Metadata is fetched completely, all Python JSON scope
   and document decoding finishes, then status-short-circuited Python membership
   selects IDs in the preexisting created_at/ID order. Hydration and final return
   remain in the same connection/transaction. No schema, index, cache, data-write,
   API, correction, acceptance, or dependency-validation change was introduced.
   None/non-str scope keeps the prior three-column metadata and status SQL path;
   all-active, status=all, status subclasses and ledger subclasses keep fallback.
2. **Reference/boundary: pass.** `independent_check.py` independently creates
   fixtures and compares complete values or exception class-name/message against
   current f872, not just eager. All **1366 differential checks** pass. Coverage:
   every status; string/dict/list/null/numeric/bool decoded scope; T1/T10/T/empty
   membership; absent and empty matches; None/non-str/str-subclass scopes; status
   subclass and ledger subclass; full dependencies/document refs and tied order;
   old schema without document table; missing dependencies with nonempty and
   empty selections; empty database; invalid status before missing ledger I/O.
   Early selected null plus later malformed scope/document JSON preserves decode
   precedence; malformed JSON, UTF-8 BLOB and deep JSON agree. Retained candidate
   exception tracebacks permit immediate writes. Instrumented _get confirms only
   `c` is hydrated for mixed-status T10, but all a/b/c are hydrated in all-active
   fallback. Separately reran all12 retrieval tests and15 project-memory tests:
   **27 passed**, no skips. Those tests also exercise correction/acceptance and
   invalidation behavior not changed by the patch.
3. **Data integrity: pass.** Reviewed benchmark source and fixed config. All six
   result cases match config; each contains21 samples per implementation and21
   recorded paired orders, with no missing or extra label. Full packet equality
   is checked before and after each timed call outside the timing interval.
   Each before/after pair shares the same database, hash-checked after measuring.
   Primary and independent database hashes agree case-by-case, as do the frozen
   candidate/source hashes and configuration. No real user memory was used.
4. **Numerical sanity: pass.** Independently recomputed each median and
   `1-after_median/before_median` from all raw samples for both runs; stored
   aggregates agree exactly. All252 samples in each run are finite positive
   milliseconds. Both target cases return10 complete records; all-match and
   no-scope return1000, small returns8, all-active returns4, matching fixture
   construction. No sample was discarded.
5. **Measurement validity: pass within scope.** Timing uses perf_counter_ns and
   includes complete list entry, path checks, connection/transaction, all metadata
   decoding, hydration, final filtering and returned full list. Database creation,
   reference correctness comparison, sample aggregation and hash checks are
   outside the interval. Both paths warm once; fixed seed1610 randomizes each
   paired order. Primary then independent benchmark windows do not overlap each
   other or tests. Recorded before-first counts across six cases are15/8/10/6/10/14,
   with complementary after-first counts, no attempt to rebalance after results.
   Some individual timings show host noise; medians comfortably clear the fixed
   target gates and both runs meet control gates. Tiny control improvements are
   not interpreted as reliable speedups.
6. **Reproducibility: pass.** Independently executed the frozen benchmark with
   unchanged config and fresh deterministic temporary databases. Both runs have
   Python3.12.14, Clang22.1.3, SQLite3.53.1, Linux6.18.44 x86_64/glibc2.39. The
   independent measured reductions corroborate the primary result; raw samples,
   orders, environment and hashes remain in independent-raw.json. No independent
   full-repository regression was claimed; main-agent final serial regressions
   and publication/remote readback remain its responsibility.

## Independent timing

| Synthetic case | Before median ms | After median ms | Change in elapsed time |
| --- | ---: | ---: | ---: |
| Scope sparse,128 B content | 11.919134 | 4.216343 | -64.63% |
| Scope sparse,8192 B content | 23.322374 | 8.861323 | -62.01% |
| Mixed status,all scope matches | 12.720506 | 13.102424 | +3.00% |
| Mixed status,no scope filter | 13.693241 | 13.714854 | +0.16% |
| Small,8 active | 0.349559 | 0.321928 | -7.90% |
| All400 active | 3.983418 | 4.037138 | +1.35% |

Primary raw recomputation: sparse targets -67.35%/-60.94%; controls +6.60%,
-1.31%,-0.10%,+0.48%, respectively. These are distinct measurements, not copied
independent outcomes.

## Actual independent commands

```bash
PYTHONPATH=. python agent_doc/results/memory-scope02-20261016/independent_check.py
PYTHONPATH=. python scripts/bench_memory_retrieval.py --config agent_doc/results/memory-scope02-20261016/config.json --output agent_doc/results/memory-scope02-20261016/independent-raw.json
python -m unittest discover -s tests -p test_memory_retrieval.py -v
python -m unittest discover -s tests -p test_project_memory.py -v
```

Additional read-only Python checks recomputed all medians, reductions, positive
finite samples, repeat/order counts, config equality, source hashes and matching
fixture hashes directly from both JSON files. No benchmark repeat, candidate
revision, or acceptance-threshold change was requested by this reviewer.

## Limitations

This is bounded semantic and synthetic local warm-cache performance acceptance,
not a universal correctness guarantee. Existing arbitrary-corrupt-database
limitations remain: for example, malformed UTF-8 content/source on newly skipped
scope-unmatched rows need not be read, so arbitrary raw SQLite corruption may
change failure visibility. O(N) metadata reading/decoding and temporary storage
remain; this does not establish O(K) total retrieval, peak-RSS improvement, stronger
concurrent snapshot guarantees, cold-disk performance, or general workload gains.
Model KV tensors, GPU, token costs, memory QA quality and actual LLM service
integration were not exercised and are not accepted by this evidence. Historical
papers were not independently re-read in this verification round; this verdict
supports code/data claims only. Human guide content was not modified.

## Final report and task readback

Read final report.md, research-delta.md, task detail and canonical TASK entry.
The six-row timing table agrees with the raw data and this review. Both primary
and independent gates remain the original thresholds; current f872 is correctly
identified as reference. Full-object/ordering and exception claims are bounded
to valid API data and tested metadata conditions, with arbitrary-corruption,
O(N), noise and real-KV/QA exclusions retained. The local scoped completion is
distinguished from pending publication/readback and the unfinished parent KV
task. No new code/data/report consistency blocker was found.

Read checks.log, explicitly a short host output capture/transcription rather
than the complete regression log. Its reported main-agent runs are1194 tests in
68.029s,8 skips; Reader3 tests in1.580s; project-document validation exit0.
These agree with the report. They were executed by the main agent, not rerun by
this reviewer; short captured output does not provide full-test forensic detail.
The independent27 targeted tests and1366 differential checks above were actually
run by this reviewer. Frozen source remains SHA256914229446d705343ef71d81c79b20b7119652a376aa180e9eff54e83a7d1d450.

Research-delta is appropriately framed as targeted reading and deferred tensor
integration, not independent GPU reproduction or ten new full-paper reads. This
review checked that framing against code and scope, but did not independently
retrieve or verify the new remote papers or all their specific scientific claims.
The proposed discoverability registration must retain manual/unknown-runtime
trust and cannot manufacture a native result-validation receipt or certify later
reuse. Publication and actual remote byte readback remain the main agent's next
actions. This independent evidence file is now frozen.
