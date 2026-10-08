# Freedman continuation and direct retrieval repair

Task: EK-20261008-0915, continuing the archived candidate and all failed history. Start2325e3d; historical gates38d3764 and59ad8d9 retained. Scientific/content and integrated frozen-case reviews have completed; final global review and publication receipts are recorded separately.

## Change and failed alternative

Document retrieval already indexed curated aliases, but section retrieval omitted them. This deprived metadata-only cross-language matches of a reciprocal-rank-fusion lane. The first all-section alias variant (v3) restored english-alias but regressed plural-residual context recall1→0. Its exact implementation, patch, logs and full comparisons are retained. It is rejected for publication.

The retained v4 variant indexes each entry’s aliases once on its first generic section, retaining original title/summary context elsewhere. A distinct engine identity forces old caches to rebuild. RRF, queries, expected answers and thresholds are unchanged; no ID/query-specific rule. Body excerpts still require literal body/heading matches, so metadata-only retrieval does not fabricate an excerpt.

Repair-first (v4, without Freedman) and candidate (v4, with Freedman) each have168 matched historical/current comparisons with no raw/context/MRR/no-hit deterioration. Comparisons preserve default context3 and supplemental historical context8 separately. Original english-alias/sqlite raw Recall@3 restored0→1 and now ranks first; relative to38d its raw recall remains1 and MRR improves1/3→1.

## Scientific scope and independent checks

Freedman scientific Markdown is byte-identical to the reviewed09:15 candidate. Only JSON status and verification links change for integration. Original source/derivation review is reused within the fixed scalar predictable-variance-budget scope; no new PDF-download or formal-proof claim. The original raw source hash remains unavailable following403. Strong refs and packaging passed the separate seven-check independent integration review. Old neuro candidate and exhausted audit lineage are unchanged and unrelated.

Frozen independent tests retain their baseline7/11 and all4 failures. v3 and v4 regression reruns are not new unseen successes. See independent_review.md for exact corpus snapshots and final integrated verdict, and integration_review.md for scientific/content/refs validation. The original09:15 checks, case repairs and failures remain in their immutable directory.

## Commands and measurements

Baseline required validate/sync/sync-check/index/full-tests/reader-tests all exited0:851 tests,850 passed/1 opt-in tmux skip; reader3/3. Candidate corresponding commands exited0:852 tests,851 passed/1 opt-in tmux skip; reader3/3. Required original and round2 accept-context evaluators and morphology sqlite-required evaluator all still exit1 because inherited failures remain. These absolute evaluator gates are not claimed passed; acceptance is the authorized zero-new-per-query-deterioration criterion with the original regression restored.

At default context3, files metrics are unchanged. SQLite mean raw Recall@3: original .666667→.809524; round2 .625→.75; morphology .25→.75. Means do not replace per-query acceptance. Raw timings, MRR, context results, index build times and command exits are retained in phase JSON/logs and metrics-summary.json. No production performance inference is made.

Independent cache audit builds a real archived v3 cache, verifies v4 rejects it, rebuilds all98 published records and then updates0/unchanged98. Every767 section context is checked. On the same integrated corpus, fresh cache sizes: v2 2940928 bytes, v3 3137536, v4 2961408. Extra20480 bytes over v2 is a corpus-specific measurement, not a general bound.

No runtime supervisor/tmux deployment, model/GPU experiment, private source publication, SGLang modification or human-guide change. Final review and publication receipts must be read before treating this local result as pushed.

## Final local decision

Independent final_review.md joins code/data, science/refs and integrated frozen-case evidence: usable-with-scope; no remaining local acceptance blocker. Ordinary main push, remote SHA readback and hosted CI visibility remain publication operations. Repository contains no tracked GitHub Actions workflows; required hosted checks cannot be inferred from that absence.
