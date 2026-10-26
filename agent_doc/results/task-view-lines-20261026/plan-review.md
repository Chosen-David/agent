# TASK-VIEW-LINES-01 independent plan review

Decision: **approve**, limited to the exact TASK view candidate below. No blocking findings. This is a static implementation/test-plan review before production edits or regression execution; it is not result acceptance, a live host deployment claim, or an authenticated runtime ReviewSession receipt.

Reviewer: independently dispatched `/root/task_view_lines_review_2120`, 2026-10-26. PROJECT_ROOT and WORKFLOW_ROOT both `/workspace/scratch/6416f20dc59b/agent-run-1303`. Assigned write ownership is only this file. Reviewed AGENTS.md, project_document_workflow.md, result_validation_workflow.md, dual_main_workflow.md, the exact plan, original runtime, parser/helper, CLI, candidate tests, portable CI, guide inventory, TASK index and relevant SYSTEM-99 stable Plan. GUIDE.md is present and empty; README.md describes human ownership. Neither guide file was changed.

## Frozen review inputs

| Input | SHA-256 |
| --- | --- |
| `agent_doc/results/task-view-lines-20261026/plan.md` | `99222f65ca85d7428123334a5d8c3b72aefadf99522c3b8cc97224f5bf7f2447` |
| `tests/test_task_context.py` | `0696e59cfa1e7eb790e51e4a5ff7fca1ec5f9d230cbee357430d38f81052b3f6` |
| Original `agent_runtime/task_context.py` | `d03ac5314bac5df15e0892d2fa9fa9854a138ef6dcdcc75d621766c9d8b34870` |
| `agent_runtime/project_docs.py` | `456bbe40a5ca731e7ab311a4435838252627c9447d66e88b51ee082cd361e92c` |

SYSTEM-99 currently says Version38/phaseV. Version39/phaseW is a proposed stable-plan update, not an already published or executed version. Preserve the former version and failed evidence when recording that change. This review covers the exact import/iterator change proposed here, the candidate regression source, and adding its test module to existing portable CI. Any production expansion requires a new review object.

## Static defect and repair assessment

`parse_requirements(..., canonical=True)` iterates `physical_lines(text)`. That helper recognizes only CR, LF and CRLF, retaining all other separators as content. `task_view` instead enumerates `text.splitlines(keepends=True)`, which also recognizes VT, FF, FS, GS, RS, NEL, LS and PS. The view then applies TASK_PATTERN and fence transitions to invented source lines that the canonical parser never recognized.

The candidate's instruction fixture is a concrete static counterexample: `Correction stays` followed by a nonphysical separator and an OLD-shaped checkbox suffix is one non-task physical line for canonical parsing. The original view splits it and removes the suffix when selecting NOW, silently losing literal global text. A literal prefix followed by the separator and a backtick fence similarly becomes an invented opener, causing the original view to retain real omitted rows. Separators within actual selected/unselected titles also split a single canonical row and distort line numbers; an omitted row can leave a title suffix behind. These consequences follow directly from the two loops; this review did not execute them.

Importing the existing `physical_lines` and changing only `enumerate(text.splitlines(keepends=True), 1)` to `enumerate(physical_lines(text, keepends=True), 1)` aligns the two consumers' source-line boundaries. `keepends=True` preserves original CR/LF/CRLF bytes after UTF-8 decoding/re-encoding. The existing matching/fence policy, canonical validation, selection validation, schema, source hash, budget check and read-only path stay unchanged. No new parser or fallback is needed. This does not certify broader CommonMark fence semantics; the plan correctly preserves the current TASK parser policy.

## Preservation oracle and acceptance

The new tests construct a list of explicit physical-line chunks and independently specify omitted indexes. Expected text is the exact concatenation of remaining original chunks; expected source_lines uses their original one-based positions. Neither oracle calls physical_lines or copies its regular expression. The candidate tests use genuine Python separator escapes (one backslash in source), not literal backslash strings. They exercise all eight nonphysical separators; the title/source-position family crosses each with LF, CRLF and CR and ends without a final newline. The misleading task suffix and pseudo-fence families cover distinct failure modes. The CLI family independently decodes actual stdout as UTF-8 under a conflicting parent encoding, checks exact text/positions/count, and confirms unchanged TASK bytes.

Existing tests retain selected/multiple IDs, duplicate/unknown/empty selection rejection, source hash/budget rejection, duplicate source IDs and fence closer suffix behavior. The new tests do not relax those contracts. Test methods use finite loops and CLI subprocess timeout=15; the outer planned adjacent-suite timeout=120 remains necessary. Static inspection found no test dependence on the helper being adopted. No requirement to add broad fuzzing or a second parser is warranted for this narrow change.

Before any completion claim, retain original-code failing output with the frozen original runtime SHA, then fixed-code output and actual changed source hashes; unexpected failures require inspection, not weakened fixtures. Independent result review must inspect those raw records and actual final diff and run the relevant local regression itself. Adding a CI command shows intended future coverage only; Ubuntu/Windows 3.10/3.12 success remains unverified until actual CI readback. Do not present local success as that matrix having run.

## Review dimensions and boundaries

| Dimension | Verdict | Basis |
| --- | --- | --- |
| intent | pass | Repairs literal context loss in an existing view under the authorized in-place SYSTEM-99 reliability scope. |
| guide | pass | Empty canonical guide and human-only directory preserved; ownership README read; no guide changes allowed. |
| assumptions | pass | Confirmed parser/view boundary mismatch; existing helper is already canonical parser authority; no new fence-policy assumption. |
| prior_results | pass | This is scoped correctness regression, not empirical-result reuse; no old pass label supplies acceptance. Previous wire work is separate and its exhausted gates remain closed. |
| acceptance | pass | Independent original-chunk oracle, bounded old/fixed regression and subsequent independent result review are appropriate. |
| risk | pass | Narrow import/iterator change; unchanged source binding, budget, error and read-only contracts. Source-preservation and line mapping are checked explicitly. |
| resources | pass | Bounded local regression only; no full suite, model call, timing/performance claim or old gate reset. |

Plan approval authorizes no new resource class, historical rerun or batch-completion claim. The full SYSTEM-99 remains open. The retained paper count is not independently revalidated by this review and supplies no model-quality/performance conclusion. Root retains sole ownership of TASK/stable Plan/source/tests/CI publication; ordinary nonforce publication still requires fresh fetch, owned paths only and actual remote SHA/tree readback. The foreign untracked evidence zip remains untouched.

Root subsequently reported an adjacent `advice_context._bound_topics` splitlines concern. That file and any advice-context expansion are **outside this approval**; require versioned plan and matching independent fixtures before production edits. No prompt_context change is approved. PID/ALIAS/role/Codex/wire exhausted gates must not be rerun or reset as part of this review.

No tests, model calls, old gates or production edits were executed by this reviewer. Remaining owner/action: root captures the original failure, applies only the approved production change after updating the stable SYSTEM-99 phase, runs bounded regressions, and hands immutable raw old/new evidence to independent result review.

## Version2 pre-execution addendum

Decision for the revised exact plan: **approve**. This supersedes the task-only production scope restriction above for the specific advice consumer change below. The original plan remains preserved at `plan-v1.md` with the original plan SHA in the table. No execution has occurred in this reviewer context.

Additional frozen inputs:

| Input | SHA-256 |
| --- | --- |
| Revised `plan.md` | `1a6ec32404547256f060fc56a035ffd9c8a51135a6a6fed310cb0fb7e58322c4` |
| `tests/test_advice_context.py` | `0e65b64847229be0e24a8e891af1986916a43bd60343c4d77f1e26965925baa2` |
| Original `agent_runtime/advice_context.py` | `1cdbf1eede0b18cc483ab38e9b4888b15dc20dad393012ccd416fa73d2d9c6b0` |
| `run_checks.py` | `681b63a5090d330f1e4460e8f4353bd16e1180881cdc0aa0f7c2f15f2b68b101` |

Task test source remains at the reviewed hash above. Revised plan explicitly supersedes its opening task-only sentence; interpret the complete document with the Version2 scope. Production ownership remains with root, with only the helper import and `_bound_topics` line-list construction additionally approved: replace `data.decode('utf-8').splitlines(keepends=True)` with `physical_lines(data.decode('utf-8'), keepends=True)`. Preserve the rest of advice discovery, section construction, error/ambiguity/comment/fence gates, source hash and budgets.

Static reasoning independently confirms the advice defect. An ordinary global line containing a nonphysical separator followed by `## FAKE` becomes a new heading in the old implementation. Its suffix and following global lines leave `leading_text`, even though they are the same physical source line/global preamble. Inside a selected section, the same suffix creates a spurious section boundary and excludes the remainder from selection. A pseudo-fence suffix can instead force the old code into an unterminated-fence error. Reusing the existing physical-line helper prevents invented headings/fences without changing H2 grammar or current fence policy. No prompt_context edit is covered.

Advice tests build expected leading text and selected-section text directly from original physical chunks, with explicit start/end ranges and omitted-section count. They cover eight separators by three physical endings, no final newline, headings discovery and view. Both actual CLI modes are exercised under conflicting cp936 parent output settings and require UTF-8 stdout, no stderr, exact source content/ranges and unchanged input bytes. The mutually exclusive discovery flag is correctly `--list-headings`, as read from the real CLI.

Nonblocking evidence caveat: the advice fixture combines misleading H2 suffixes with a pseudo-fence before the real headings. The old implementation is expected to fail through the unterminated-fence branch; this alone must not be reported as observed silent H2 truncation. The fixed exact oracle still checks all content and boundaries. Splitting H2-only and pseudo-fence variants would make the distinct old failure modes observable, but is not required for the narrow static fix. If fixtures are extended, preserve their expected original chunks and submit their changed hashes for result review.

`run_checks.py` statically confines baseline to task/advice test modules and fixed to those plus six adjacent modules. It binds runtime/test/CLI inputs before and after, retains full child stdout/stderr, uses `-B` and outer timeout=120, and makes no elapsed/performance measurement. It does not rerun wire gates or full suite. TimeoutExpired currently propagates before log writing; should a timeout occur, retain its partial outputs and classify the round incomplete rather than retrying or treating absent logs as success. Normal test failures are preserved by the runner. No extra run was requested by this review.

The seven review dimensions remain pass for Version2: the advice consumer has the same literal-source fidelity intent; guide/authorization and resource boundaries are unchanged; assumptions now have a concrete heading/fence mismatch; no empirical prior-result acceptance is reused; original-chunk oracles plus independent old/new result inspection remain adequate; reuse adds no new parser or runtime resource. Add both existing test modules to the existing CI matrix, and preserve the distinction between a CI command addition and actual matrix success. All other review limits above remain in force.

### Version2 fixture refinement before baseline

Root split the advice fixture as suggested before execution. Independently reread final source: `chunks(..., fake_fence=False)` now supplies a plain literal suffix by default; the API loops both false/true for every separator/ending, while actual CLI tests use the H2-only variant. This makes the fake-heading loss observable separately from pseudo-fence rejection without weakening any fixed expected text/ranges. Final approved advice-test SHA-256 is `870b66628325c2ce9a6d6a6dcfb62766033703f7edbdaa8194b41ceeba3ea411`, superseding the previous advice-test hash in this addendum. Plan and runner hashes remain unchanged. Decision remains **approve** for this frozen Version2 candidate and the two narrow reuse changes. Static review only; original/fixed execution and independent result acceptance are still pending.
