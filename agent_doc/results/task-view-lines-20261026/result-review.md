# TASK-VIEW-LINES-01 independent result review

Decision: **usable-with-scope** for the two local correctness repairs and the named bounded regression coverage. No blocking findings. SYSTEM-99 remains open; publication and native CI acceptance are separate.

Reviewer `/root/task_view_lines_review_2120`, 2026-10-26, independently executed one new regression invocation after rereading the actual final source, tests, CLI entry points, runner, full production/CI diff, SYSTEM-99 Version39 phaseW/progress, report, baseline/fixed metadata and representative raw failure blocks. This review owns only this file, independent.log and independent.json. It did not change production, tests, TASK, guide or producer evidence.

## Implementation and original-code evidence

The actual production diff matches the approved Version2 repair exactly: task_context imports and iterates existing physical_lines with keepends=True; advice_context imports that same helper and constructs its decoded line list with keepends=True. The shared project_docs helper is unchanged. No alternate parser, fence-policy change, prompt_context edit, schema change, budget relaxation, source-hash relaxation or new write path was introduced. Advice source CRLF formatting is preserved. The only CI changes are adding the two existing test-module invocations to the existing installation matrix.

Fresh source review confirms why this repair works: physical_lines consumes CR/LF/CRLF only and preserves all original terminators with keepends=True; task parsing already uses that helper. The view's remaining state machine and TASK_PATTERN consume the same physical source lines after the fix. Advice heading discovery and slicing now index those physical lines rather than invented Unicode-separated fragments. Existing explicit selection, stale-source, ambiguity/comment/fence, scope and budget checks remain in place. Import execution and actual CLI subprocess coverage passed in the independent run.

Independently obtained Git object bytes using `git show 06937b3d:PATH` and compared SHA-256 to baseline.json for both original production files and project_docs. All three match exactly, and baseline before/after maps agree. Baseline test hashes match the final pre-execution approved fixture hashes; fixed before/after maps also agree and match the current independently bound runtime/test/CLI bytes.

The original task source SHA is `d03ac5314bac5df15e0892d2fa9fa9854a138ef6dcdcc75d621766c9d8b34870`; original advice SHA is `1cdbf1eede0b18cc483ab38e9b4888b15dc20dad393012ccd416fa73d2d9c6b0`. Accepted fixed task SHA is `41b1f2aafe1c25a0e1b6b421d97a5818a26cb5f72678a961c95192a5d1670564`; fixed advice SHA is `f1f84c448b411e52e38fc133d504cf38cd8aad4e00b15861125e608d0735efd8`.

Raw baseline output confirms 19 methods, 88 failing subcases and 24 error subcases. Independent parsing of all failure/error block headers gives:

| Failure family | Failing subcases | Error subcases |
| --- | ---: | ---: |
| Task CLI literal constraints | 8 | 0 |
| Task invented fence | 8 | 0 |
| Task global instruction suffix | 8 | 0 |
| Task selected/unselected titles | 24 | 0 |
| Advice CLI headings/view | 16 | 0 |
| Advice API, plain suffix | 24 | 0 |
| Advice API, pseudo-fence | 0 | 24 |

Every error block is the expected fake_fence=True case ending in `ValueError: unterminated code fence; use full source`. Representative actual diffs show an OLD-shaped literal global suffix missing, an actual unselected task retained after an invented fence, an unselected title tail left behind, and advice leading text cut at FAKE_LEADING. Advice CLI cases return successful JSON before failing the preservation assertion, confirming silent omission rather than a command/encoding failure. Baseline API/CLI assertions fail at leading_text first; therefore baseline output does not separately observe the later selected-section assertion in those same cases. The selected-section defect follows from inspected heading slicing; fixed tests directly verify its complete content and positions. Counts are subcases, not 112 separate bugs.

## Independent execution and integrity

The sole new verifier invocation ran the same eight named modules as the producer fixed round in a subprocess with outer timeout=120; CLI children retain timeout=15. It used Python 3.12.14, `-B`, unittest discovery and an independently constructed command rather than executing the producer runner. Exact command, executable, full before/after hashes and observed output byte lengths are preserved in independent.json; full raw output is independent.log.

Observed result: **103 methods passed, no skips, no failures/errors, exit 0, no timeout, stderr empty**. All bound files were unchanged across the verifier run. Bound files include the two consumers, shared helper, both CLI scripts, eight test modules, CI, SYSTEM-99, TASK index, report, runner, plan/review, raw baseline/fixed logs and metadata, and both guide files. No guide diff exists.

Evidence hashes:

| Evidence | SHA-256 |
| --- | --- |
| independent.log | `07371fd8eb526e4f0ad66e62617cc7097dcd4ef4212de8decc099d27d253739b` |
| independent.json | `0fb4e17fde67c9459fb2a31627d8f8062f80a3690d5d5796f49a68cbf901fec2` |

The six new methods retain the independent original-chunk preservation oracle from plan review. They cover eight nonphysical separators, three physical line endings, EOF without newline, fake task/H2/fence suffixes, selected/unselected titles, exact text and source positions, actual UTF-8 JSON CLI output under conflicting parent encoding, and unchanged input bytes. Existing adjacent tests cover parser/document/Markdown/context-output rejection and transport contracts. Root report and SYSTEM-99 phaseW correctly limit their claims; raw fixed.log also ends with 103 tests/OK. No evidence of an oracle being weakened after the old failure was found.

## Scope and remaining limitations

This acceptance supports correct literal text preservation and physical line/section mapping for the exercised task/advice view cases and named local adjacent regressions. It does not establish universal Markdown correctness or discover every possible parser edge case. The current fence grammar is deliberately retained. The review does not claim an authenticated runtime ReviewSession receipt or external deployment.

Actual Ubuntu/Windows × Python3.10/3.12 results for the newly added CI commands were not available in this review; the verifier ran one Linux Python3.12 environment. CI configuration is a future coverage commitment, not native-matrix success. The original-code baseline was inspected and its bytes checked against Git, not rerun by this verifier. This round has no fullsuite, exhausted PID/ALIAS/role/Codex/wire gate retries, model benchmark, token/cost measurement or performance claim. Unittest durations and different suite sizes are not a speed comparison. Guide files and the unrelated evidence zip remain outside write scope. Existing SYSTEM-99 fullsuite, real-host/task-quality and other unresolved boundaries remain unresolved, and paper counts are not incremented or certified here.

Root may record this scoped independent acceptance and proceed with the already authorized ordinary publication checks. Any substantive change to bound production/tests or acceptance scope requires affected checks and renewed independent review; ordinary closure Progress updates must retain these actual frozen input versions and limitations.
