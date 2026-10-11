# EXP-CONTAM-01 candidate — publication blocked

Base: `f11cc4bc4e599fb6a4b7f3fc6e1141d454555686` (origin/main, fetched before edits and checked again after tests). Work was initially clean and fast-forwarded from `bcfb0ec`. No other changes were stashed, overwritten or staged. No matching parallel TASK existed. Checkout `.agents/skills` was absent; relevant source skills were read without editing them. Human guide was empty and untouched.

## Implementation and actual entry

Main-AI entry points (AGENTS, orchestrator, research_orchestrator, planner_main and derived references) require immediate exact-job stopping for confirmed applicable defects, even near completion. They route to the existing experiment execution contract and `Contamination` trusted-host API; the existing supervisor adapter's `maintain` may call it on an actual confirmed event. No monitor was installed or falsely announced.

The API freezes run/result/task/code/config/data and host job bindings, authenticates applicability through a host callback, revokes result eligibility before stop, requires exact exit/fencing readback, and recoverably renames only inventoried run-exclusive result/cache/leaderboard-entry/completion paths. Failure keeps consumers blocked; partial moves resume. Confirmation mismatch and unconfirmed/inapplicable risks do not stop. `inspect_result` checks revocation before/after its actual independent verifier; producer snapshots and ResultStore retrieval/reuse reject stale accepted results. Old evidence is preserved. Repair requires changed frozen code/config, an independent fix verifier, fresh run/result/job/output/cache identities and renewed host authority. Replacement reservation prevents duplicate reruns; the API never launches or adds resources.

`Store.cancel` was deliberately not reused as a single-job primitive: it cancels the whole chain. Existing result gates and project document write guards are reused. External jobs, shared leaderboard rows and undiscovered caches are not magically controlled by these instructions. Host authorization must refuse incomplete ownership/reference closure. No model, Claude, GPU, paid action or SGLang modification occurred.

## Actual checks

- `targeted.log`: 17 contamination tests passed, including real pidfd-owned child termination with another process surviving, actual repaired CPU execution, partial output preservation, cached acceptance rejection, stop/storage/move failures and replacement deduplication.
- `independent-review.md`: separate reviewer independently passed 17 contamination + 79 result-related tests and checked implementation/entry boundaries; source hashes recorded.
- `main-entry.log`: 5 main-AI contract tests passed after final entry edits.
- `experiment.log`: 10 existing experiment execution tests passed.
- `reader.log`: 3 reader tests passed.
- `full.log`: 1008 tests, 3 failures, 3 errors, 1 skipped opt-in tmux test.
- `baseline-full.log`: clean detached origin/main at the same SHA, 991 tests, identical 3 failures, 3 errors, 1 skip. No new failing test identity. The shared travel navigation test reports both failure and error; counts are unittest's exact summary.
- `sync.log`: three pre-existing stale model-with-knowledge mirrors. Only directly affected generated references were regenerated; unrelated baseline mirror files remain untouched.
- `decision.log`: an initial discovery pattern found zero tests; this is NOT counted as validation. The actual main-entry tests above were then located and run.
- `git diff --check`: passed.

Baseline blockers: (1) model-with-knowledge `scripts/project_docs.py`, `assets/knowledge/coverage.json`, `assets/knowledge/learning_state.json` differ from canonical sources; (2) bundled project_document_workflow links to absent `../docs/token_optimization/advice_meetings.md` in code-reading, travel and visual packages. These are not repaired in this narrowly scoped task.

CI: branch protection/required-check query via gh returned Forbidden. Connected GitHub combined-status read for base SHA returned `statuses: []`; that does not establish required CI success. No `.github/workflows` is present in this checkout. Required CI remains unknown.

## Resume

The user authorized direct non-force main publication only after validation, with a resumable candidate if validation cannot complete. Therefore save this candidate locally, keep EXP-CONTAM-01 unchecked and do not push main. Restore required baseline checks in their owning task, obtain required-CI visibility, fetch/integrate newest main without discarding concurrent work, rerun required checks and recheck frozen code review, then publish only this task's files using a non-force update. The working source and evidence remain in the candidate commit; there is no remote publication or installed external-job adapter to claim.
