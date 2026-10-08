# Independent final code/data review

Reviewer: `/root/result_review`; task `EK-20261008-0915`.

**Verdict: usable-with-scope for the local v4 first-section alias repair and integrated Freedman card.** This is the authorized restored-target/no-new-per-query-deterioration acceptance, not a claim that every absolute retrieval evaluator gate passes, nor evidence of commit/push or runtime deployment.

Read AGENTS, actual plan and independent plan review, implementation and tests, compare.py, evaluator and run_checks.py, raw before/after outputs, command receipts, failed v3 implementation/patch, and both independent final reports. Acceptance is based on actual code/data, not plan approval or producer status.

## Verified code and data

The only production retrieval changes are the distinct v4 engine marker and adding existing curated aliases to the first generic section's context. Later sections retain title/summary. No query/ID rule, rank-fusion weight, expected answer, evaluator threshold or excerpt selector changed. The engine marker makes old caches stale; the new test exercises rejection and rebuild. Runtime and plugin mirror are byte-identical. Independent local execution of all 11 knowledge-index tests passed in 3.126 seconds.

Independently recomputed four metrics from expected/actual/context IDs, checked query/expected identity, exact backend/case coverage and absence of duplicate case IDs, and matched context limits. Both repair-first and candidate have 168 complete comparisons against historical 38d3764, concurrent 59ad8d9 and starting 2325e3d (default context3 and supplemental context8 kept separate), with zero metric deterioration. These are overlapping recorded comparisons, not 168 distinct unseen queries. Original SQLite english-alias raw Recall@3 is restored from 0 to 1 and rank is now 1; against 38d raw recall remains 1 and reciprocal rank improves from 1/3 to 1.

The failed all-section v3 has four historical comparison rows with plural-residual context recall 1→0. Its source, patch and failed raw results remain intact. The corrected report now attributes zero regression only to v4, closing the stage-label finding.

All four phases' command-log SHA256 receipts were independently checked. Candidate full regression completed: 852 tests, 851 pass and one real-tmux opt-in skip; Reader 3/3. Five retrieval evaluator invocations still exit 1: original, original-context8, round2, round2-context8 and morphology. These inherited absolute failures are not converted into passed gates. Sync-check and diff-check independently return 0.

## Independent evidence join

Read final retrieval_unseen results: unchanged frozen cases retain baseline 7/11 and original failures; final-integrated replay is 11/11 on candidate snapshot `d8596dde2d2ad320b22e91b2c1c17208ae2007b40546e30b9ba20a7f2b0ad6f0`. Reruns are seen regression evidence. The report explicitly distinguishes the 97-card repair-first replay from the later 98-card migration/storage audit, closing the timing ambiguity. Real v2/v3/v4 cache comparisons use the same 98-card corpus; metadata matches do not fabricate body excerpts.

Read knowledge_result's final integration code, results and review: all seven checks pass, with exact scientific-body reuse, prior executed-source/history integrity, formal refs and rejection of old/mutated refs, package identity and evidence links. Input hashes independently match current files. Scientific acceptance remains the earlier fixed scalar predictable-variance-budget scope, not a new experiment, formal proof or PDF download. Original PDF byte hash remains unavailable. Formal card reference is v1 / `1fa401c6307800e52301c08f3a4528f5c0587d30c0a712c1d74512b807e65e8b`.

## Preservation and remaining work

Checked 115 protected tracked paths against HEAD: evaluation fixtures, holdout metadata, guide-related tracked paths and neuro/SGLang matches remain unchanged. New changes are the minimal retrieval implementation/tests, Freedman integration, mirrors and task/evidence records. No private research material or new model/GPU workload is involved; old neuro blocked lineage remains untouched.

HEAD and local origin/main read back as `2325e3d266aa7fb3c819cb52d6ba41db54ac5c90` at this review. No remaining blocker within the reviewed local scope. Main owner still owns completion metadata/TASK updates, final sync/check, pre-push remote refresh and any affected revalidation, ordinary push and exact remote readback. This review does not assert those future actions occurred. Evidence/code hashes and explicit failed-gate boundaries are in `final_review.json`.

Final metadata readback: additive learning_state completion record and TASK pending-publication wording accurately reflect local acceptance; old history/cursors remain. All bound code/card/evidence hashes remain current. These documentation-only updates do not require repeating the full suite.

Archive-format follow-up: original `repair-only.patch` is now losslessly stored as the UTF-8 `patch` field of `repair-only-patch.json`. Independently decoded SHA256 `13626693031f81dac1e7f5541f8f20d2c4614c89703ba9499dd07b84f4485577` exactly matches the previously reviewed patch hash. JSON-container hash is separately bound; no original review hash has been reinterpreted. The original staged whitespace failure is preserved in archive-format-check.json, and staged diff-check now passes. All other bound inputs remain byte-identical; acceptance scope is unchanged.
