# Independent engineering review

Reviewer: `eval_research` host agent, independently reviewing code it did not
author. Date: 2026-10-03. Scope: evaluator CLI gates, orchestrator boundaries,
runtime synthetic tests/reporting, and executable development-boundary tests.
This is program review, not a real-role semantic grade.

## Findings

1. **Report accounting defect — resolved and independently retested.**
   In `evals/crossfeature/runtime_execute.py`, the version-mismatch fixture branch
   originally emitted `unexpected_rejection` if the integrity validator found an
   error. The summary enumerated only `pass`, `fail`, `not_run`, `known_gap`, and
   process exit checked only fail/not_run. Therefore this case disappeared from
   summary counts and exited successfully. A corrupted fixture must be an
   explicit failed/invalid measurement, not silently omitted. Sent to controller
   for correction. Revised `summarize()` counts every unknown outcome as failure.
   The same independent instrumentation now emits fail=1 for one case and returns
   `True` (nonzero exit). `test_crossfeature_reporting.py` also passed independently.

   Independent reproduction instrumented only the reporter's `validate` call to
   return `['artifact 0: sha256 mismatch']` and suppressed unrelated unittest
   suites. Actual `main()` produced one `unexpected_rejection` case, all-zero
   summary, and `False` (exit zero). This is a controlled reporting test, not
   evidence of an actual corrupted production artifact or a model run. Local
   reproduction: `/tmp/crossfeature-research/invalid-report-reproduction.json`.

2. **CLI documentation regression — resolved by source read.** `README.md`'s legacy preparation example
   lacked the new `--dev-eval` flag at review time, so the documented command
   fails. Update invocation examples alongside the explicit CLI change. This is
   a usability defect; the gate itself behaves correctly. The example now includes
   `--dev-eval`.

## Independently executed checks

- `python -m unittest discover -s tests -p test_crossfeature_runtime.py -v`:
  **4/4 passed**. Tests execute real SQLite state and reopen, exact lease expiry,
  stale-result journaling, stable idempotency key/new claim token, actual missing/
  good/tampered bytes, zero-byte integrity semantics and handoff hash validation.
- `python evals/crossfeature/runtime_execute.py --out /tmp/crossfeature-research/independent-runtime-report.json`:
  **37 program checks passed, 1 known gap**. Legacy fault cases include real
  multiprocess claim exclusion, worker termination/recovery, authorization,
  cancellation and proof invalidation. The reported consumer-version gap is
  honest: byte-integrity validation alone has no expected consumer version.
- `python -m unittest discover -s tests -p test_development_eval_boundary.py -v`:
  **3/3 passed**. Both preparers reject without the flag before creating output;
  flagged pipeline preparation succeeds and its pinned delivery-validator import
  executes; actual `agent_runtime` init/tick completes an ordinary artifact task
  under a Python audit hook rejecting known eval/rubric file access.

The new flag is checked before preparation and short-circuits correctly for
non-prepare subcommands. The public Python preparation API remains explicitly
developer-invoked; no new runtime import/call into evaluation was observed.
Orchestrator text preserves genuine task artifact checks and ten-exemplar
prewriting requirements. Adding the visualization checker to snapshot dependencies
closes a real imported dependency and the new executable import probe covers it.

## Coverage limits, not disguised passes

- The audit hook test covers one real artifact-task execution path. It is not a
  universal proof about every host model's routing, child-process access or
  arbitrary ordinary user prompt. A keyword-bearing ordinary task and successful
  flagged legacy preparation would strengthen coverage; these are not covered
  by the three current tests.
- The exact-expiry test recreates Engine/Store against the same SQLite database
  in one process; separate legacy tests supply actual process termination and
  multiprocessing coverage. Do not call the new test alone a process-crash test.
- A declared zero-byte artifact passing is correct for the documented byte-hash
  contract. It establishes no semantic adequacy; no change should silently turn
  this into a paper/figure acceptance gate.
- The runtime rubric is hashed into the report, but unittest source assertions
  determine its program pass verdicts. This is not a per-criterion semantic
  grader, nor a model output. The controller must retain criterion-to-test
  coverage and the known consumer-version false negative in the final matrix.
- The reviewer did not change production code or lower any acceptance criteria.

## Follow-up: paper fixtures and corrected-code verification

Independent corrected-code test runs: reporting **1/1**, development boundary
**3/3**, runtime boundary **4/4**, crossfeature delivery **2/2** passed. The latter
executes both architecture input splits and paper declaration controls. This is
10 Python test methods, not 10 model tasks. Corrected reporting reproduction is
`/tmp/crossfeature-research/corrected-invalid-report.json`.

`paper_cases.evaluate()` actually calls `validator.validate(record, root)` and
derives observed accept/reject from its returned errors; expected decisions only
classify the result afterward. It does not assign expected answers to actual
outputs. The 10 generated cases yielded **7 matching decisions, 3 false negatives,
0 false positives** at the declaration-control layer. The three misses remain
`audit_disguised`, `copied_body`, `dispatch_as_start`; the unit test explicitly
preserves those gaps instead of calling them semantic passes. Model execution is
recorded as `not_run`. Generated role/publication receipts are clearly marked
synthetic and are not genuine start/read events.

**Material scope limitation:** the good-control PDF writer emits text only. The
manuscript references a separate real `figure-1.svg`, but the generated PDF does
not embed that figure. The synthetic exemplar PDFs describe bars and tables in
text, rather than drawing them. Consequently the good control is a bounded
research narrative and declaration-integrity control, not a fully illustrated
research-paper PDF acceptance or proof of ten published exemplars' actual visual
reading. A host worker may legitimately reject the complete-delivery claim while
accepting the narrative; that must not be mislabeled a model false positive.
The abstract-only and missing-figure cases mutate declaration metadata, so their
program rejections demonstrate metadata checks. Independent actual-reading
evidence is still needed for the separate host-role assessment.

Copy detection is also deliberately bounded: the copied fixture duplicates the
supplied reference; the holdout uses an explicitly attributed short quotation.
These test a narrow distinction, not general plagiarism detection. Keep every
conclusion aligned with these actual materials and the frozen task scope.
