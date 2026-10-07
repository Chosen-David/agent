# Combined v3 corpus adoption

## Frozen scope

The complete `knowledge/` corpus and the packaged knowledge mirror match remote `f9898dfbd23e9bad7897643b54a419d8c88135bd` byte for byte. Snapshot: `cb76af83360932f5e397065af4449bf39474b4cd99f684ef68ffa474e51228db`. There are 80 metadata records: 78 published and two existing candidates. All 158 entry files from tested v2 tree `a922965b886c38d95dbcb94d2e65f4aee338f6ae` remain unchanged; the only additional pair is the matrix-concentration card.

Both holdout registries were read before scientific entry access. All four reserved records are unchanged. Source metadata has no exact registered DOI/URL collision. Reserved target contents were not opened; metadata checks do not establish absence of every form of semantic leakage.

Existing AIK and matrix reports, publication records and result artifacts were preserved byte-exact from remote. Old native result records remain immutable.

## Fresh checks

- Targeted index tests: 10/10 passed, including exact published-ID indexing, candidate exclusion and the standalone plugin path.
- Both existing candidates remain blocked by ordinary `get`, file search, SQLite search and the SQLite document ID set.
- AIK: the same 12 frozen development questions were run with both backends. Default context remains 21/24; explicit AI-algorithms domain remains 23/24. The 8-entry/20,000-character budget is unchanged.
- Default failures remain files A12 and SQLite A03/A12. Domain failure remains SQLite A12. These are failures, not successful automatic recovery.
- The new matrix card changes four default query rank/context rows and one domain raw-rank row. No AIK target-hit regression was observed. Full row differences are retained in the result summary.
- Four matrix development queries on both backends exactly match the upstream result IDs, context IDs, budgets, status and recall/rank metrics: 8/8 target hits.
  All eight matrix contexts have `context_status=partial`; 8/8 establishes target presence only, not complete contextual or prerequisite closure.

The fresh checks use standard-library Python and SQLite FTS5. They make no model-quality, unseen-test, scientific-proof, GPU, latency, token-cost, deployment or production-benefit claim.

## Historical reuse and inherited reporting discrepancy

The matrix report and tests summary say 21 old development queries, but the actual `regression.json`, `baseline-latest-main.json` and `concurrent-main-check.json` contain eight cases per backend. Seven are positive cases and one is a no-hit negative control. Mean raw Recall@3 is 0.8095238095; bounded-context recall is 1.0 for the positive cases. The raw physical-model miss and partial cross-entry recall remain visible.

This adoption uses only that demonstrated eight-case-per-backend scope. Upstream text is retained as published and the discrepancy is documented here. The earlier AIK 116 legacy-query/backend pairs cover the 77-published-card corpus before the matrix addition; they are historical evidence, not a new complete-catalog result on 78 published cards. No full legacy-catalog run or full integration suite was duplicated by this worker.

## Result and acceptance

The new native result is `doc/results/combined-corpus-v3-20261007/`. Its contract, manifest, raw query rows, command logs, corpus identity map, candidate checks, before/after dependencies and summary are preserved there. Native registration is `pending`; an independent release reviewer must inspect implementation, bindings and actual results before any consumer claims scoped acceptance.

Frozen manifest SHA-256: `073b6da43ed49874707617253b6d04b76f5e9cf0a864d53dee35be3391c29dda`.

A setup-only producer assertion initially expected the new card in an incorrect subdirectory. It failed before tests or query measurements. The failed log is preserved; only the producer's expected path was corrected. `dependency-preflight-supplement.json` also identifies transitive implementation files that must be bound by the independent current-result wrapper; the native manifest and record were not rewritten.
