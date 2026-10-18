# FTS-BATCH-21 independent code/result review

Verdict: **usable-with-scope; retain the candidate for final regression and publication checks**.

Reviewer: actual fresh-context host agent `/root/fts21_result_verify`, distinct from producer
`/root`; review performed 2026-10-18 through the available collaboration host. This document
is manual independent evidence, not a native ReviewSession or experiment-validation receipt.
The reviewer changed no implementation, benchmark, task plan, or human guide.

Scope: exact 128-ID batched deletion in both `knowledge_index.py` copies versus Git baseline
`8cf78b709f49e4ecaa3030b57a341940c3f780a1`; the frozen 33-case local CPU benchmark and
the explicitly listed independent reruns. All six required checks pass within this scope.
This does not certify arbitrary workloads, all SQLite versions, global bug freedom, or model QA.
Full repository/Reader regression and remote publication remain the main agent's separate gates.

## Six required checks

| Criterion | Verdict | Independent observations and evidence |
| --- | --- | --- |
| implementation | pass | Read both complete source copies, actual diff, benchmark, existing and final new tests, and CLI imports in `knowledge.py`. Copies are byte-identical. Only deletion statements change: generated placeholders bind IDs, batch size is at most 128, table names are fixed, all deletions remain before the unchanged insertion loop, and the original transaction/exception behavior and engine/schema identifiers remain. `independent-raw.jsonl` binds actual source and shared dependency hashes. |
| reference_boundary | pass | Reference is the unchanged index module loaded from the fixed Git commit, not a rewritten copy of the new deletion algorithm. The harness compares complete return dictionaries, every logical row of entries/meta, full docs/chunks rows including rowids, and complete output dictionaries for all five fixed queries on every warm and measured pair. The 33 cases cover no-op, single/64 updates, all/delete/rebuild, 127/128/129 boundaries, mixed changes, and migration. Independent replay covered small/no-op, bulk400, mixed130, migration130 and fresh empty creation. The 257-ID unit test injects failure after all deletion batches and proves full logical-state rollback. The migration replay also injects failure after transactional DDL, checking rollback to the old-engine seed. |
| data_integrity | pass | Independently parsed all 34 lines: one environment record plus exactly 33 unique size/mode cases and 462 positive timed calls. Reconstructed all three input corpora, every target, all six ordinary/migration seed hashes, chunk counts and content-byte counts; they match the producer records exactly. Verified candidate/baseline source hashes, seven samples per case, pair IDs 0–6, exact alternating AB/BA labels, and no duplicate/missing cases. `benchmark.stderr` is empty. Evidence: producer raw hash and `producer_raw_audit` in independent raw. |
| numerical_sanity | pass | Recomputed all 66 medians directly from the 462 raw times, every speedup and threshold, and all 33 pass flags. Every time is finite and strictly positive, in milliseconds. All four required bulk cases beat the 15% median reduction threshold; all remaining cases satisfy `candidate <= max(baseline*1.15, baseline+0.5ms)`. Independently retained per-case min/max dispersion; no outlier deletion or aggregation across workloads. |
| measurement_validity | pass | Inspected the timer around the full `build_index` call, including connection, initialization checks, transaction, tokenization/insertion and close/commit, with corpus preparation and identical seed-file copies outside timing for both implementations. One untimed pair precedes seven alternating pairs. Snapshot/query parity checks run outside the timer. Reviewer did only static/read work while producer timing ran; independent timing started only after the producer exited, and main postponed full regression until independent timing finished. No CPU pinning or external-host isolation is claimed. |
| reproducibility | pass | Independently executed four seven-pair cases (size1 no-op/single; size400 all/delete), two one-pair semantic cases (size130 mixed/migration), fresh-empty baseline/candidate parity, and all 16 targeted tests. All semantic and rollback comparisons pass. Bulk400 replay again clears 15%; small cases clear the nonregression allowance. Raw replay samples and test output are preserved in the independent files. |

## Main measurements and replay

All values below are full-call wall milliseconds; each performance row uses seven pairs.

| Case | Producer baseline median | Producer candidate median | Reduction | Independent replay baseline → candidate |
| --- | ---: | ---: | ---: | ---: |
| synthetic400 all update | 149.520908 | 55.574974 | 62.83% | 158.307278 → 58.231806 |
| synthetic400 all delete | 112.608321 | 13.233337 | 88.25% | 118.758277 → 14.740653 |
| synthetic1600 all update | 1551.894541 | 223.239415 | 85.62% | Not rerun; all raw/configuration/seed checks performed |
| synthetic1600 all delete | 1499.420518 | 60.153719 | 95.99% | Not rerun; all raw/configuration/seed checks performed |

Independent small size1 medians: no-op 2.547729 → 2.820917ms, single update
3.433995 → 2.902914ms. These support the frozen tolerance, not a claim that every small
operation is faster. Producer real-corpus no-op and single-update medians are respectively
10.77% and 8.40% slower; both remain within the predeclared bound. Producer real-corpus
all-update/delete reductions are 29.68%/48.18%. Do not present only the bulk gains as
universal improvement. Full per-case ranges and all original samples remain available.

Environment recorded by the producer: Python 3.12.14, SQLite 3.53.1,
Linux 6.18.55 x86_64/glibc2.39, Intel Xeon Platinum 8573C, nine visible CPUs,
`PYTHONHASHSEED=0`. Independent replay used the same checkout/runtime/hashseed.

## Dependencies and test robustness

- The baseline `exec` imports current `agent_runtime.knowledge` and `project_docs`, just as
  the candidate does. Both dependencies were verified unchanged against the fixed baseline;
  their hashes are bound below. Their imports on this path are standard-library modules.
  This is a controlled shared dependency, not a comparison against a separately installed
  historical environment.
- The benchmark intentionally requires Git plus the historical commit object, the real
  knowledge corpus, SQLite FTS5, and Linux `lscpu` for its CLI environment record.
  The benchmark source and dependencies are therefore part of reproducibility conditions.
- Initial new unit tests called `paired()` and therefore depended on historical Git data.
  Reviewer raised that robustness issue; producer replaced the dependency before final
  targeted regression. The final unit tests import only pure fixture/state helpers and do
  not call `baseline()`/Git. They check two delete statements for 129 IDs, direct 257-ID
  rollback, full logical-state equality, deletion-to-empty and no-op empty behavior.
  The benchmark still independently supplies historical-reference parity. Initial producer
  test logs are historical and are not substituted for the final 16-test independent pass.
- `size=115` in real-corpus records means total source records, not 115 published documents.
  Real `b127/b128/b129` cases are consequently capped by the available published records;
  exact boundary coverage comes from the synthetic400/1600 cases. Synthetic records have
  four sections each; 400/1600 therefore contain 1600/6400 chunks. Real data include varied
  section counts and nonempty multilingual query coverage. No synthetic Agent accuracy
  or model-learning gain is inferred.

## Reproduction and evidence bindings

Producer command: `PYTHONHASHSEED=0 python scripts/benchmark_knowledge_index.py`
(defaults are sizes 0/400/1600, eleven modes and seven pairs).

Independent replay invocation after importing the frozen benchmark module:

```python
for size, mode, repeats in [(1, 'noop', 7), (1, 'single', 7),
                            (400, 'all', 7), (400, 'delete', 7),
                            (130, 'mixed', 1), (130, 'migration', 1)]:
    print(json.dumps(benchmark_knowledge_index.paired(size, mode, repeats)))
```

Run the above under `PYTHONHASHSEED=0` from the repository root. Independent raw also
contains the fresh-empty state/query digests and final checked file-hash mapping. The
targeted test command and exit status are preserved in `independent-targeted.log`.

| Artifact | SHA-256 |
| --- | --- |
| producer raw.jsonl | `534064f7b8cda65b0b28970f91d600bbe78383a58043741ebf6a7f2d85ffb145` |
| independent-raw.jsonl | `64c09884c16b8ad4339213c7a694491f3747f3bd6585cdeb9ae8ad6f49ff63f2` |
| independent-targeted.log | `64596de0b5e12920c43d273172f54c5275121384ee99a9930590c4f9f8f52281` |
| independent-knowledge.log | `263a2cc0075265aad8188a0d9badc966c32859986249553ead148a1a6337ee2d` |
| both candidate index modules | `5266ec9a760ecd34419b2bc0b574a199d2901daee7f217b7f627ca2ba95a9e7e` |
| baseline index module | `44d5bb19eaa1bb9f7527348d60eae2b3a13c2feb445d0bb35680949da4678058` |
| benchmark script | `f00ac39e0d11db085d050c11e2baf82f68ce1ed20ae71c7e2a122748651dd8a4` |
| agent_runtime/knowledge.py | `0f83bb00568a0e26eaf0b49d73dab1d6f958acebd1e95d749c6bb8cc9a1014b7` |
| agent_runtime/project_docs.py | `a2712d093f4012350f6654401a15aa1d22e442d6993482025996b63183477a57` |
| final tests/test_knowledge_index_batch.py | `251a1d73b5851a135a0bed2011c763bc3752cbfc81fdf022ffeb3d2a03e7bade` |
| tests/test_knowledge_index.py | `49f58cd38e0979313e9ccc15bf8f493eed72ca41c7b0c1c80256430d6e490bcd` |
| stable Plan before `## Progress` | `dccf1a6924323246ecabe84fc367e174db15bac99f0e29e0a6e3ef2fbd575c24` |

Knowledge access: actual file-backend query `SQLite incremental deletion batching transaction`
returned three unrelated cards; all were rejected as implementation justification, with no
adopted knowledge refs. Snapshot and hit identities are preserved in independent-knowledge.log.
Prior-result applicability and manual plan-review scope were checked in the existing plan and
plan-review record; neither old pass labels nor unrelated results substitute for this rerun.

## Remaining limitations

The data support bounded local full-index-maintenance speedups, not statistical significance,
performance on unseen hardware/storage or every workload, byte-identical SQLite shadow-table
layout, or correctness beyond the tested/reference-reviewed contract. Logical rows and query
results—not physical database bytes after each transition—are the semantic equivalence target.
Physical seed bytes were nevertheless regenerated and verified exactly. Full regression,
publication authorization, fetch/integration and remote readback are not certified here.

No open implementation, numerical, parity, or threshold blocker was found. Any future change
to the bound implementation, harness, corpus, dependencies or measurement conditions requires
new scoped verification; progress-only task edits do not silently expand this acceptance.

## Producer report consistency follow-up

After the performance review, independently read producer `report.md` and `research.md`.
All 33 displayed rows match the original raw medians, speedups and candidate min/max values
exactly at the stated display precision (programmatically checked; evidence in
`independent-report-check.log`). The report correctly retains real small-case slowdowns,
caps its claims to local subsystem measurements and distinguishes synthetic from Agent QA.
Source, benchmark and final-test hashes remain unchanged. Checked report SHA-256:
`2e96976b1990ef76dadbdccc9abdc979af6b11378de6daeb07ba7952046448c9`.
Checked research-note SHA-256:
`866c378c236c58c5d3eaf15636e8c29682f1f4de948b623e7a7c5a1d8d8dfdc9`.
This follow-up checks numerical/code-claim consistency and evidence boundaries, not a new
independent reading/validation of the external papers discussed by the producer.

## Final integration/regression follow-up

Independently read the complete final logs and current integration diff after the main agent
completed regression. `full.log` records **1271 tests in 124.061s, OK (skipped=8)**;
its progress markers independently count 1263 passes plus eight skips. `reader.log` records
**three tests in 1.605s, OK**, with all three named Reader cases passing. Skipped tests are
not represented as executed passes. These are inspected producer regression outputs, not
a claim that the reviewer independently repeated the full suite; the reviewer separately
ran the 16 targeted tests recorded above.

Final source copies remain byte-identical and their hashes, the benchmark hash, both
targeted-test hashes and producer raw hash still equal the earlier bindings. The current
production diff remains only the previously reviewed deletion batching; CODEMAP addition
accurately maps the implementation, tests and evidence. `git diff --check` passes.

- `full.log` SHA-256: `9c50a02a021e13af6892329a2214f2c5b8bcb40626f4a720ca33b351c6d92ef8`.
- `reader.log` SHA-256: `793e2e22722a82563653af8a75343ca461b1d82d0eceee718f608c3eb3e66de9`.

Verdict extension: **final integration and available regression evidence accepted within
the same scope**. No remaining code/result/regression blocker was found. Ordinary publication
authorization, latest-remote integration and post-push readback remain outside this review;
any code-changing integration requires targeted revalidation.
