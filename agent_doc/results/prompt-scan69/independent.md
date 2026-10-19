# PROMPT-SCAN-69 independent review

Verdict: **usable-with-scope**. Reviewer: separate host context
`/root/prompt_scan69_review`; implementation/data author is `/root`.
This is independent code/data review and a serial measurement reproduction, not
a claim that a persistent supervisor, authenticated DAG adapter, or CI was installed.

## Frozen identity and implementation

Baseline: `38a6451306dba93fcf40d4c23391876471682891`.
The complete baseline module was loaded using `git show`, not reconstructed by
reversing selected candidate lines. Reviewed production diff changes only the
two-line marker-location list comprehension in `_span`. All matching positions
are still collected; no early exit, cache, file-reading, fence/comment, output,
hash, error, or budget behavior was edited.

`^` with `re.MULTILINE` has the same start-of-string/preceding-LF condition as the
original predicate. The escaped fixed marker contains no newline and cannot
overlap itself, so finditer's non-overlap traversal loses no eligible position.
Non-LF Unicode separators must not gain marker-start status.

| Artifact | SHA-256 |
| --- | --- |
| Baseline prompt_context.py bytes | `303c762d2345e12e0f6d955b15288e3400d8a7c2b6c19f8ab23282c9bd73d92b` |
| Candidate agent_runtime/prompt_context.py | `a897b5ac60584f07be47de7f163c7993a7b93654a9a0737e34923a1f3584b618` |
| scripts/benchmark_prompt_scan.py | `9034e8b33e3ece5e3f8683ae78b8489ddfb4eab875f8f86de7e645118166b822` |
| tests/test_prompt_scan.py | `d0cf03945e9569cd038bb6e9a3084e482d9be8a56e309ea6863cbcfebdacfe55` |
| benchmark.json | `c640727d655482b7c5267f57bc11f9c9467e56e794feab41450f945b71abd249` |
| independent-benchmark.json | `c91282151df5a46ce86f947ea8a63395c5fa36d0a0151495ddfb2c3088bbf572` |

## Independent correctness checks

The reviewer executed an independent inline Python probe (host process session
56877, exit 0), without changing production code, tests, or the benchmark:

- 6,160 full `_span` baseline/candidate comparisons: 6,000 deterministic random
  token assemblies (`random.Random(691901)`, 1–19 tokens), plus 160 structured
  fence/comment/separator cases. Tokens included the complete marker, a partial
  marker, LF, CR, CRLF, NEL, U+2028, U+2029, NUL, emoji, backtick/tilde fences,
  HTML comments, whitespace and a different CJK section boundary. Structured
  cases additionally covered VT and FF. All identical.
- 3,870 complete compose comparisons: each of the three input files was replaced
  independently with 13 valid, non-LF, inline, duplicated-marker, comment,
  outer-fence, missing-marker and differing-policy texts. Every nonempty entry
  permutation and both dedup values were checked; successful cases also used
  exact output character length minus one, equal, and plus one caps. Successful
  results were compared as ordered, UTF-8 JSON bytes, and failures as exception
  type plus exact message. All identical.
- Nine invalid-argument comparisons: caps 0, -1, 1000001, True, 1.0, None;
  empty, unknown and duplicate entry selections. All identical.
- Six invalid-file comparisons: invalid UTF-8 and 1,000,001-byte input, applied
  separately to every entry file. All identical.

This is 10,045 held-out comparisons, in addition to the benchmark's 300 complete
compose comparisons. The inline probe also reconstructed all four benchmark
fixtures, independently verified all twelve recorded file hashes/byte and
character lengths, checked the candidate-source hash, and recalculated every
reported median, improvement and nonregression decision from the seven samples.

## Independent serial performance reproduction

After the main process reported the full regression job finished, the reviewer
ran `python scripts/benchmark_prompt_scan.py` once, serially (host process session
35857, exit 0). Complete raw output is preserved in
[independent-benchmark.json](independent-benchmark.json), separate from and
without overwriting the original measurement. Both runs used the same script,
baseline, candidate, all input hashes and frozen gates. Independent raw medians
and gates were recalculated after saving the file.

| Scenario | Original before/after ms | Independent before/after ms | Independent reduction |
| --- | ---: | ---: | ---: |
| Actual repository triple entry | 3.646024 / 1.097385 | 3.399433 / 0.829347 | 75.60% |
| Each source plus 50K prefix | 16.693009 / 2.868701 | 18.077050 / 2.739644 | 84.84% |
| Missing canonical marker | 0.464806 / 0.127587 | 0.500007 / 0.116085 | 76.78% |
| Repeated canonical marker | 0.458935 / 0.132520 | 0.488678 / 0.126921 | 74.03% |

All four original and repeated nonregression gates pass:
`candidate_median - baseline_median <= max(0.05 * baseline_median, 50000 ns)`.
The actual-source primary metric exceeds the frozen 10% improvement threshold
in both runs. Each recorded sample is one twenty-call batch mean, and the summary
is the median of seven batch means; these are not individually timed call medians.
Each side has five warmup calls, then seven alternating-order rounds of twenty
calls. No samples were dropped or additional tuning loops run.

Both sides use **max_chars=1000000**, not the default 100000. The enlarged fixture
adds 50000 ASCII characters plus LF to each original file, giving 55174, 64150
and 64652 characters; it is not a default-cap large-file success claim. Timing
includes the complete in-process compose operation, read/hash/scan/assembly and
exception handling wrapper, but not CLI startup, fixture creation or equality
assertions. The assertion outside each timed batch checks the final call; the
separate full-output differential checks provide additional correctness coverage.

## Regression, guide and acceptance boundary

Read `tests.txt`: producer-reported prompt suite 20 passed in normal and `-O`
modes, Reader 3 passed, full suite 1310 ran with 8 skips and otherwise passed.
The independent reviewer did not repeat the full suite; these are inspected
producer logs, distinct from the independent held-out checks and performance run.
`git diff --check` passes. `git diff BASE -- agent_doc/guide` is empty.
GUIDE.md is empty (SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`);
guide README hash is
`f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261`.
No guide files were written.

Implementation, reference-boundary, data-integrity, numerical-sanity,
measurement-validity and scoped reproducibility checks pass. The measured claim
is restricted to this CPU/Python environment, warm-cache in-process complete
assembly and the four frozen fixtures. Scheduler noise is visible; no statistical
significance, cold-cache, process startup, RSS, peak memory, GPU, model-task
quality, token savings or full application latency claim is supported.

Previous prompt-read67 memory data and content-copy60 measurements are not used
as speed evidence. Partial prior-result search is not an exhaustive search.
Finite differential testing is not a universal bug-free guarantee. Ordinary
main publication, latest-remote integration, protected-path check and remote
SHA/tree readback remain the main owner's responsibility. Any relevant source,
input, benchmark or acceptance change requires rechecking this scoped verdict.
