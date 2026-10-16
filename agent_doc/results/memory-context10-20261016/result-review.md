# Independent result review: MEM-CONTEXT-10

Verdict: **usable-with-scope** for frozen final production source, pending owner full-repository/Reader regression and normal atomic main publication/readback. No managed ReviewSession receipt or installed supervisor is asserted.

## Inspected implementation

Read real basis_context caller and MemoryLedger private closure, _walk, check and connection lifecycle. Existing initial check_handoff_basis stays first, including required-memory omission/error gates. Final payload sorts the full validated closure, retains full entry fields, dependency IDs, selected claims and known-ID reuse behavior. Default public check still retains only requested roots; no cross-call cache or schema migration added. Closure private helper runs only for exact built-in ledger/check/get/walk/connect/document checker/sqlite connector/Row identity; fake ledgers and customized paths retain generation checks. The later guard amendment is correctness-driven and supersedes v1 evidence; reviewer/preguard-* is retained, not promoted as final-source timing.

## Actual independent validation

- reviewer/verify.py ran52 complete packet differential/boundary groups:35 randomized shared DAG/multiroot/known-ID cases; missing/required error precedence; stale/scope-JSON/document-JSON/document-contract corruption; character budget; custom check/get/check/walk; fake ledger full output and observable call equality; explicit diamond/shared ancestor, selected claim roots, valid source document and stale source document even when known.
- reviewer/boundaries.py ran10 guard/snapshot groups: altered connect/document checker/sqlite connector/Row, subclass and four per-instance hooks return None before accessing invalid refs. A real WAL writer commits ancestor stale status after helper root hydration; same helper transaction returns old coherent active snapshot, next helper call fails stale. No stale result retained across calls.
- Independently executed current six unit regressions, all pass. Owner test-first log is separate producer evidence; no additional failure count inferred here.
- Complete immutable-state packet equality is runtime checked in every measured sample; raw stores packet hashes, not whole serialized packets. Prior check output/error semantics compared using isolated original baseline memory and handoff globals.

## Independent measurement and frozen gate

Executed same complete basis_context protocol sequentially after final producer measurement exited:21 randomized AB/BA pairs per scenario,3 warmup pairs, seed81610, full validation/connection/hydration/serialization inside wall timer. Setup, expected equality/hash outside timer. Reviewer uses separate temporary fixtures from same recipe; each arm of a pair uses identical actual DB and full input hash. Timestamps make independently constructed DB hashes differ across producer/reviewer; this is a reproduction of recipe, not a false claim identical cross-run bytes. No data trimming, affinity/frequency changes, model/API/GPU usage or outlier filtering.

| Scenario | Baseline median ns | Candidate median ns | Reduction |
| --- | ---: | ---: | ---: |
| chain96 | 63245211 | 3743069 | 94.081656% |
| shared96 | 34845736 | 3811772 | 89.061009% |
| small3 | 1514331 | 1282018 | 15.340966% |
| no_memory | 20931 | 20941 | -0.047776% |

Both deep chain/shared primaries exceed frozen25% reduction; small and no-memory controls each remain within15% regression. Owner and reviewer raw168samples each were independently recomputed for cardinality/pair/arm/order/input/output hashes and frozen thresholds; source hashes match each other and current files. First/second primaries are synthetic chain variants, not unrelated production populations or statistical significance evidence.

## Boundaries and costs

Only complete local warm CPU basis_context assembly is supported. No model KV storage/serving, end-to-end Agent task quality, token-volume reduction, TTFT or production request throughput claim. Payload bytes/content remain equal; this removes repeated graph reads, not memory content. New helper retains the closure because complete context requires it; ordinary check low-peak behavior remains unchanged. There is extra root hydration/read transaction for dependent contexts; frozen small/no-memory controls bound only those measured cases.

The new helper has one SQLite read snapshot, **not the entire basis_context**: initial basis checks and known-memory checks remain separate transactions, and document file checks are outside SQLite transactional protection. Concurrent writes can change which failure is observed relative to baseline multitransaction interleavings; immutable same-state equivalence is the guarantee under test. It does not add hostile filesystem race protection or a cross-store atomic snapshot.

## Final frozen SHA256

- `agent_runtime/handoff_basis.py`: `43b6c6d0c281d833d22f32d9497e4d46947957b7620297592dfc82b49781d15a`
- `agent_runtime/project_memory.py`: `e1182d697f12e8e25b2457cc5510a3d1a409e383aff9dc61aa3b53463c26ba4c`

Evidence: reviewer/verification.json, boundaries.json, tests.log, raw.json, summary.json and their exact scripts. Owner full-suite/Reader/-O result must be reviewed before release; reviewer did not independently rerun full suite.
