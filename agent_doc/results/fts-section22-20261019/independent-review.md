# FTS-SECTION-22 independent result review

Decision: **usable-with-scope for the bounded manual engineering result**. All six frozen criteria pass. This is the fresh-context `/root/fts22_result_review` agent's actual code/data review and independent execution, not a native `ReviewSession`, authenticated runtime verifier receipt, supervisor installation, general publication authorization, or bug-free guarantee. Full repository/Reader regressions and final publication/readback remain the main agent's gates.

## Frozen target and evidence

- Repository: `/workspace/scratch/88c3234ecfbc/agent-memory`.
- Observed HEAD/baseline: `de05d95c725029cca53239f0eb6e0f63d4fb9c19`.
- Stable task prefix: `b1318599c07a88bc45f384c0a6dd382926fbd3e3e7fadc5dc2b117ab66d4232e`.
- Validation plan: `ecb9e58363d3d2071c38170ded5a91a219784b6c2bb95f7a8b6760f95dbf0808`.
- Production and mirror SHA-256, identical bytes: `8eb136aae4fab28b0f887c745e8d9e276948347a53af215e12659224b65c34d9`.
- Frozen baseline module SHA-256: `5266ec9a760ecd34419b2bc0b574a199d2901daee7f217b7f627ca2ba95a9e7e`.
- Runner SHA-256: `15350846959d84bb64d792045eced373c3a26f851db40413367671aaf7067c62`.
- Producer `raw.jsonl`: `f64e47c7a88de396f5111f92a3a0ebd5b3ec1b817bc62e8e2b4c2b552feb8207`.
- Independent `independent-raw.jsonl`: `3cf3eaf9447e62b3c57ab41f0dd476ea4d3d1ec4ab05641ba7778ac5ec8ab84e`.
- Independent arithmetic/binding audit `independent-audit.json`: `d4a36d9e6de4964850e273c568ed32ca8c6a66f80958538e3d0791f7988899aa`.
- Independent tests `independent-targeted.log`: `b6417ee5ae7aa35ddf8b702bc1a88a6b9c365600f6f4912cdfdf2ed1e5a4584c`.

`independent-audit.json` also binds the actual current corpus files, shared dependencies, test, runner, Plan/research/review, and the audit implementation. The whole task-file hash is a snapshot; ordinary later Progress additions need not match that whole-file hash, whereas the stable prefix must remain unchanged. The raw environment records Python 3.12.14, SQLite 3.53.1, Linux x86-64, Xeon Platinum 8573C and 9 visible logical CPUs.

The directory/task use the planned date 2026-10-19; observed execution actually occurred on **2026-10-18 UTC**. The independent benchmark was running by 16:14:05 UTC and its last write was 16:14:38.959 UTC. The independent targeted log last write was 16:15:19.382 UTC. These are observed tool/file times, not claims of exact launch timestamps.

## Independent execution

I first read AGENTS, decision-review, project-document and result-validation workflows, task/index entry, guide files, plan review and research notes. I inspected the actual diff, entire production module, mirrored equality, `_terms`/`get`/`ref` and CLI routing, fixture helper, new tests, existing error/isolated-CLI tests, and the complete search runner. No production, TASK, guide, or other agent-owned evidence was edited.

The main agent held its CPU tests until this review's CPU work ended. I did not launch a benchmark before its explicit RUN READY message. Commands, run sequentially from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python scripts/benchmark_knowledge_search.py --sections 1 2 256 > agent_doc/results/fts-section22-20261019/independent-raw.jsonl
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python -m unittest tests.test_knowledge_excerpt_selection tests.test_knowledge_index tests.test_knowledge_index_batch -v > agent_doc/results/fts-section22-20261019/independent-targeted.log 2>&1
PYTHONDONTWRITEBYTECODE=1 python agent_doc/results/fts-section22-20261019/independent-audit.py > agent_doc/results/fts-section22-20261019/independent-audit.json
```

All exited 0. The independent run used default words 16/512, seven pairs, five calls per sample, and automatically included all six real-corpus queries. The targeted suite ran **18 tests in 9.706 seconds**, all passing, including isolated mirrored-package CLI execution. The supplied pre-change log records the new once-per-section contract failing at `2 != 1`; I read that historical log but did not independently recreate its pre-change run.

## Six criteria

| Criterion | Verdict | Independent basis |
| --- | --- | --- |
| implementation | pass | The only production diff adds `nsmallest` and changes excerpt ranking/filtering. Each section receives one pure lexical overlap calculation. Explicit `(-overlap,start_line)` key preserves the baseline stable order without dictionary comparison; top two are selected before zero-overlap removal, exactly as before. Literal 900-character excerpt slicing and every returned field are unchanged. FTS, RRF, index schema/engine, queries, exceptions and CLI routing are untouched. Mirror bytes match. |
| reference_boundary | pass | Baseline is the complete Git-pinned module, not a rewritten helper. Every timed output is compared as the full Python JSON-shaped object against the frozen baseline; all 96 untimed combinations also pass. Independent rerun output hashes equal producer hashes. The new test covers fixed RNG, 1/2/3/16/256 sections, ties, empty content, Unicode normalization/Chinese, fences, long excerpts, alias-only and no-term queries. Existing error, stale-index, filter and isolated-CLI tests pass. This does not prove arbitrary malformed-store behavior. |
| data_integrity | pass | Primary: 14 distinct timed cases / 98 retained sample pairs; independent: 12 / 84. Both have 96 distinct boundary cases. No duplicate/missing IDs or pairs; every pair retains both arms and the exact alternating order. All repeats=7, inner=5, limit=5, seeds/source/dependency hashes agree. Real corpus has 115 records, synthetic fixtures 8. Every shared case has identical input, seed-DB, config and full-output hashes across runs; runner verifies DB bytes unchanged after read-only calls. Shared baseline imports are unchanged from the pinned commit. Current corpus file hashes are recorded. |
| numerical_sanity | pass | Independent audit recomputes every median, range, ratio and threshold from all positive finite raw milliseconds, and exactly matches stored summaries. Both target cases exceed 15% reduction in both runs; every other case satisfies `candidate <= max(1.15*baseline, baseline+0.5 ms)`. No aggregate or selected best sample is substituted. Order-specific medians and all paired reductions are additionally retained in the audit. |
| measurement_validity | pass, bounded | Timer encloses five complete `indexed_search` calls, including connection, metadata, SQL/ranking, store copies/references and excerpt construction; duration is divided by five into ms/call. Corpus construction/loading and DB build are outside both arms. Both use the same warmed store/DB/query/options; one warm pair is excluded, seven AB/BA pairs retained. Full equality checking is outside timing. This is warm-cache local function latency, not CLI process/load time, cold start, production throughput or tail latency. Known concurrent test contamination was excluded wholesale before acceptance; uncontrolled host noise remains visible. |
| reproducibility | pass | Independently executed the required real corpus plus synthetic 1/2/256 sections at both word counts with the frozen protocol. All 12 cases pass parity and their exact thresholds. Input/DB/output identities match the first accepted run. The 16-section cases were arithmetically audited in the producer data but were not performance-rerun, consistent with the frozen minimum rerun scope. |

## Measured scope and counterevidence

| Required target | Producer baseline → candidate ms/call | Reduction | Independent baseline → candidate ms/call | Reduction |
| --- | --- | --- | --- | --- |
| 1 section × 512 words | 2.646359 → 2.031931 | 23.22% | 3.257265 → 2.306472 | 29.19% |
| 2 sections × 512 words | 4.270624 → 2.794875 | 34.56% | 5.387104 → 3.445171 | 36.05% |

These are ratios of arm medians, not median paired ratios. They establish the planned local synthetic benefit. They do **not** establish a generally faster real workload: real `memory retrieval` was 3.91% slower in the producer run and 0.55% slower independently; independent `low rank`, `量纲`, and no-match were respectively 1.42%, 12.28%, and 2.84% slower, all within their frozen allowances. The no-term producer case was 29.64% slower but only about 0.040 ms worse, and the independent 1×16-word fixture was 15.68% slower but about 0.157 ms worse; these legitimately pass the predeclared absolute allowance, not a universal 15% non-regression rule.

The 256×512-word case is too noisy for a robust gain claim: producer median reduction 15.65%, independent only 2.96%; independent candidate range 267.642–408.482 ms versus baseline 271.592–365.386 ms. These distributions support only the frozen observed median non-regression gate, not improved p95, variance, or stable speedup. No additional retry was selected to improve these values.

`contended.jsonl` is preserved with hash `f404e8c3362e10841190c45de0ef2add549d272f9ba8333f9cbf6cd77e5afdd8`. It is excluded **entirely** from all acceptance arithmetic, comparisons and performance claims because of known overlapping tests, not because of its measured values. Its contents were not merged with either accepted run.

No claim is made about model/LLM quality, accuracy, semantic retrieval, a novel algorithm, GPU/TwoLevel/SGLang performance, cross-platform behavior, arbitrary corpora, independent host isolation, runtime certification, or deployment. The actual trusted runtime provider/manifest path remains outside this explicitly manual review. Passing tests and finite observations cannot certify absence of all defects.

Main may consume these scoped data after retaining the bindings and limitations, then complete full regressions and final remote synchronization/readback. Any change to production/runner/shared dependency/input/frozen protocol invalidates affected acceptance and needs explicit revalidation; new Progress text alone does not change the frozen Plan.
