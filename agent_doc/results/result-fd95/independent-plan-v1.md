# RESULT-FD-95 independent plan review v1

Date: 2026-10-20. Reviewer: separately invoked `result_fd95_review` agent, read-only source inspection plus this reviewer-owned record. This is a real tool-backed independent review, not an authenticated ManagedEngine/ReviewSession receipt or a deployed supervisor.

Decision: **revise** for one project-document prerequisite; the bounded technical approach is approved. Before executing baseline tests or implementing the fix, the main writer must register RESULT-FD-95 in the canonical TASK and create its matching detail Plan. At review time `rg` found no RESULT-FD-95 in `agent_doc/task/TASK.md`, and `agent_doc/task/task_details/RESULT-FD-95.md` did not exist. The review may be resolved by independently reading those additions; no technical redesign is requested.

## Frozen reviewed inputs

- Claimed baseline: `e30dfce8424f7912a3716dd6ef035f648808e2f7` (parent owns Git verification; reviewer did not run Git).
- `plan.md`: SHA-256 `0bfe1645759c3cb845b313e54c9703ef596a20b93d5790df96d8a93fd826ce07`.
- `agent_runtime/result_store.py`: SHA-256 `3da82814e44acdc8ff8aa26e4b5d103825713d515c688e0ca06e63518cb02c1b`.
- Prior `artifact-fd77/report.md`: SHA-256 `40d88572dea936aa275dbfe0c988ef81189324f4f697cddfbd4eee5c8db4dd8d`.
- Read AGENTS.md, prompts/decision_review.md, project_document_workflow.md, result_validation_workflow.md, dual_main_workflow.md; inspected canonical TASK, empty guide, complete result_store implementation, result_validation._bytes ownership pattern and existing result-store test structure.

## Required review dimensions

| Dimension | Outcome | Evidence/reason |
| --- | --- | --- |
| intent | pass | Local ownership repair directly supports the scoped reliability goal; no algorithm, API, permission or service change. |
| guide | pass | Existing GUIDE.md is zero bytes; no guide write proposed or performed. Canonical task binding remains the separate blocking prerequisite above. |
| assumptions | pass | _read and _check_ref acquire real fds before fdopen enters a context; _save mkstemp acquires an fd whose temporary pathname cleanup does not itself close it. Source independently confirms the ownership gap, without importing historical leak counts. |
| prior_results | pass | artifact-fd77 covers result_validation._bytes, not these sites. Reusing the established ownership pattern is appropriate; fresh local reproduction is still mandatory. |
| acceptance | pass | Plan requires real acquisition, per-fd closure checks, injected failures, successful controls, byte/error policy preservation, ordinary and optimized tests, broad regressions and independent result review. |
| risk | pass | Small local ownership change; preserve no-follow flags, bounds, hashes, immutable publication and temporary cleanup. No performance/general correctness claim authorized. |
| resources | pass | Bounded local standard-library CPU work with disposable synthetic inputs; missing tmux/managed host honestly disclosed. |

## Implementation and verification guidance within approved scope

1. Start each ownership `try` immediately after successful acquisition (in _check_ref ensure digest setup cannot escape ownership protection). Use fdopen(closefd=False), with exactly one raw-owner close in finally. Do not close when open/mkstemp itself failed.
2. _save needs an outer temporary-name cleanup finally and an inner descriptor-owner finally. Finish stream context/flush/fsync and raw close before assert/link publication. fdopen, write, flush, fsync or link failure must remove the temporary name, leave no leaked owned fd, and not publish partial bytes. Preserve FileExistsError translation and existing immutable target.
3. Count leaked acquired descriptors using captured real fds and fstat before cleanup; global /proc counts and an expected exception alone are insufficient. Baseline leaks must be explicitly closed after recording so later cases are uncontaminated.
4. Independently review the actual candidate and raw observations after implementation. This plan opinion grants no result acceptance or publication authority. No test data were produced in this initial review.

Next owner: main writer adds canonical task/detail and reports exact paths; reviewer reads them and issues an addendum. Source/tests, TASK, guide, Git and remote jobs were not changed by reviewer.
