# Independent result review — CTX-20261009-01

Verdict: **usable-with-scope**. All six required domains pass for the exact frozen contract. No blockers found in this scope.

Verifier: `/root/advice_context_result_review`, fresh independent child of the parent host invocation, separate from producer `root-advice-context-producer`. Actual local read/execute review completed 2026-10-09T10:18:52.722423+00:00. The parent must authenticate this actual child completion event; this document and JSON do not authenticate their own author. This is a local review, not a deployed runtime verifier, ReviewSession, supervisor, service or publication receipt.

Manifest SHA-256: `bb188636b0bc3f4ddf4811d77bc5b4793df8e3f2e85df42285a9676672502f48`. Actual `_snapshot(root, plan.json.dag[1].experiment_result)` resolved all **63** distinct bound paths (including validation plan), without stale or missing bindings. The current plan SHA-256 is `acbeadf42cc3b931958de010922aef4b425b9070afcfe5447ff514efefc6e6ba`; its separate plan reviewer approved that exact local scope. All immutable inputs/outputs were left untouched.

Accepted scope: Task-scoped advice inventory, preserved global document/advice gates, metadata-only canonical task repair, public CPU regression/serialized size checks; no model/token/latency/deployment or SGLang claim.

## Implementation and reference boundaries

Read actual Git patch, frozen baseline, project_docs discovery/binding/check paths, task_manifest prepare/validate/dispatch/report routes, handoff integration, tests, generator mapping, report and design. The implementation filters before JSON deep copying: only node `advice` discovery inventory changes from full global discovery to that node's adopt/adapt paths. Node `adopted_advice`, task details, all guides, full guide reviews and unknown snapshot fields remain equivalent to baseline. Each resulting object is detached. Global `project_documents.advice` and full assessment coverage are unchanged. Global validation still checks every adopted source, even sources belonging only to siblings; task checks bind the task's adopted/adapted sources. Deferred/rejected/new proposals keep the existing checkpoint semantics. Complete contract validation rejects old broad node shapes; standalone per-task byte checking is not claimed to enforce all global shape conditions.

The frozen baseline bytes equal Git blob `bb5bf5b8edaebd8910f9a7af28830c668113d339:agent_runtime/project_docs.py`, not a recreated approximation. Independently enumerated **448** cases: all 4^3 disposition combinations for three sources and all seven nonempty task subsets. Source scopes were [A,B], [B,C], [A]. The reference expectation was constructed directly from these explicit source scopes and adopt/adapt membership, independently of candidate filtering. Each case checked exact selected source/hash map, advice=adopted_advice, equality of every other baseline field, preservation of global snapshot, and detached nested guide/unknown fields. Cases include none/some/all applicable advice, overlaps, rejection/defer and no saving when every source applies. This matrix is an object-level diagnostic; executable full-plan fixture checks are the separate tests below.

Fresh targeted tests additionally exercised complete prepared contracts and consumer checks for missing global assessments, stale adopt/adapt, siblings, new/deferred/rejected sources, guide add/edit/delete/rename, stable task inputs and invalid legacy shapes. Existing task_manifest/handoff/result-validation tests independently passed. Limited supported-entry checks do not prove OS isolation, hidden model behavior or absolute correctness.

## Actual independent executions

All Python invocations used `PYTHONDONTWRITEBYTECODE=1`; requested measurement output went to `/tmp`, not the frozen run.

```text
python -m unittest tests.test_advice_context_scope tests.test_project_docs_acceptance tests.test_project_docs_workflow tests.test_project_docs_init tests.test_task_manifest tests.test_handoff_basis tests.test_result_validation -v
Ran 148 tests in 13.810s

OK

python agent_doc/results/advice-context-20261009/measure.py --out /tmp/advice-context-independent-raw.json
exit 0; output identical bytes to frozen raw.json

python -m unittest discover -s apps/paper-reader/tests -v
Ran 3 tests in 1.091s

OK

python scripts/sync_plugin_references.py --check
exit 0; empty output

git diff --check
exit 0; empty output
```

My first targeted command mistakenly named nonexistent `tests.test_project_docs`; the remaining 59 tests ran but the loader added one error (60 reported, FAILED errors=1). The actual error was `ModuleNotFoundError: No module named 'tests.test_project_docs'`; it was not an implementation failure. The failed reviewer log remains `/tmp/advice-context-independent-tests.log`, hash `82aad2e49eca77a3445d1ef27c8cbc963da09510ba7eb4ddbd26728e379ec301`. I corrected the module selection and got 148/148, with no source changes. Final independent test log hash: `36721f6cc96c03cc369ba7deeefbab097d897128f71d3fb7fa085f83914e655e`. The retained observations in this review are durable independent evidence; temporary files are not result-contract artifacts.

Inspected the frozen producer full-tests log rather than repeating its entire suite. Independently counted every individual verdict: **859 tests = 851 ok + 8 skipped**, consistent with the final summary. Seven skips require optional plotting/PDF/font dependencies; one requires opt-in real tmux/socket access. Final frozen reader log is 3/3. These pass observations do not claim optional features were exercised. Preserved first production measurement error says native snapshot rejected missing identity/date in MATH-55/56/57 and emitted no raw.json. The first full regression has precisely one stale generated-reference failure plus 8 skips; final sync repair does not erase it.

## Data integrity and exact repairs

All four original/current pairs were freshly read as bytes. WRITE-EVIDENCE equals one replacement of `## Stable plan` by `Task-ID: WRITE-EVIDENCE-20261009-01\nDate: 2026-10-09\n\n## Plan`. MATH-55/56/57 each equals one replacement of `## Plan` by its matching Task-ID, Date 2026-10-09, blank line and original `## Plan`. Every marker occurs exactly once. Every other byte, scientific statement, existing status/progress and historical evidence remains unchanged. This independently verifies all four repairs, beyond the measurement script's WRITE-only assertion and producer metadata_checks' three MATH entries.

```json
{
  "WRITE-EVIDENCE-20261009-01": {
    "exact_metadata_only": true,
    "before_sha256": "c58cd15269b0a9f0032a80e22cfb322e4ea98b4e5d7b2a9e79127066a79c3a3b",
    "after_sha256": "c16b2f03f52d67dc6e1d11dc1068422c28bc6e1f6c37dbc62748bc17a64d8d32"
  },
  "MATH-55": {
    "exact_metadata_only": true,
    "before_sha256": "1995631c1333a4edaa982c2de8f40de9d61a68c29993fb69580ae64e642b0b28",
    "after_sha256": "63e45868825fbfbce67659c5e2b50c11b4e6a73b513481d1595bae7656551d64"
  },
  "MATH-56": {
    "exact_metadata_only": true,
    "before_sha256": "300e0ad5e7ec88b97b8f813c4f255098813379efabbcf8ef0f493b4934785879",
    "after_sha256": "80a873fe5f9ef557684eff5e424c6885aa0ab71dc94e397097c3279256da4385"
  },
  "MATH-57": {
    "exact_metadata_only": true,
    "before_sha256": "12b4367731bc3419ff875def0be1851d752f07c9597c3780f9d24bae96eea533",
    "after_sha256": "dd39605fbde32b692c38516a5e2489e0a147a004c1ce379f1e5e3031999fb8aa"
  }
}
```

Native current snapshot recovers 194 details, 2 guides, 7 advice. Both guide inventories and actual hashes equal startup inventory; `git diff --name-only -- agent_doc/guide` is empty:

```json
{
  "agent_doc/guide/GUIDE.md": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "agent_doc/guide/README.md": "f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261"
}
```

Generated workflow/runtime mirrors match their canonical generator; canonical code-reading source is byte-identical to initial Git with SHA-256 `113149a9f316c06228210890c322081f20c52a70cf72138416e6ec5f7b52e872`. The extra two-line stale mirror repair changes the existing generated copy only. Full artifacts remain bound by receipt, including original failures, prior-search partial/missing-record evidence and source metadata.

## Numerical sanity and measurement validity

Fresh measured JSON is byte-for-byte identical to frozen raw.json, SHA-256 `c7c69d72297add3d5fe46c16d539e0770d8dab8cbeba698991a7b3ec4f43ab2d`. Same input objects feed frozen baseline and candidate; identical Unicode/minimal sorted JSON settings count Unicode characters and UTF-8 bytes. All counts are nonnegative finite integers, bytes >= characters, tokens remain null, and each candidate count <= corresponding baseline. No-advice row is identical. Every field except node advice was independently compared, and source snapshots did not mutate. No random sampling, timing statistic or float-to-token estimate is involved.

| Workload | Tasks/advice | Node characters before/after | Node UTF-8 bytes before/after | Global + nodes characters before/after |
| --- | --- | --- | --- | --- |
| public-synthetic | 1/0 | 706 / 706 | 722 / 722 | 1232 / 1232 |
| public-synthetic | 4/50 | 22585 / 4377 | 23481 / 4505 | 28979 / 10771 |
| public-synthetic | 40/500 | 1960371 / 52361 | 2041331 / 53641 | 2021349 / 113339 |
| current-repository-shape/no-adoptions | 194/7 | 263621 / 114629 | 282245 / 114629 | 291406 / 142414 |

These are serialized representation diagnostics: the synthetic snapshots and current-repository empty-adoption/empty-review shape are **not runnable complete plans**, billing requests or model prompts. The separately prepared test fixtures are runnable program contract fixtures. No real tokenizer ran; no model, semantic quality, total token cost, latency, fee, KV-cache saving, universal savings ratio or deployment gain is established.

## Design/source claim audit

The result report and design distinguish implemented reference reduction from proposed lifecycle records, logical archive, rebuildable index, revision/fencing coordination and real-model experiments. They keep global coverage and single-author authority; they do not claim automatic deletion, shared KV caches, consensus correctness or deployed databases. The historical-input sum nL0+h*n(n-1)/2 is an explicitly assumed repeated-input model, not a measured complexity/billing result. No measured literature benefit is transferred to this repository.

Independently reopened primary pages on 2026-10-09: ACM https://arxiv.org/html/2607.23809v1 table 1 defines lossless as raw-content retention, while its tool description and Appendix B.4 use an LLM to extract requested information from archived messages. Thus original retention does not guarantee complete summary/recall; the design explicitly states this distinction. Grounding Agent Memory https://arxiv.org/html/2609.11060v1 §3/4/5 separates read-only curator probes and excludes separately tracked curation from task-agent costs, matching the design's call for total accounting. SQLite https://sqlite.org/wal.html §1 explicitly requires same-host WAL processes, matching the stated cross-machine limit. This spot check supports bounded design attribution, not all literature, formal consistency, publication status or adoption readiness.

## Six-domain decision and limitations

All six verdicts are pass: actual implementation/consumer review, independent reference matrix and executable adverse controls, complete bindings/source preservation, exact counters and denominator, truthful representation scope, exact replay and relevant regression/reader/mirror checks. `_review` schema validation and final `_snapshot` equality must pass after this file is fixed; the JSON receipt carries their exact bindings.

Acceptance is restricted to the frozen patch and inputs. I replayed the targeted 148 tests, reader and mirrors; the broader 859-test result is independently inspected producer log, not a claimed second full-suite execution. Optional visualization and real tmux cases remain skipped. Raw data lacks model/tokenizer/latency/GPU/cross-machine observations; no model-quality benefit, deployment or final publication is accepted. Synthetic/shape diagnostics cannot replace human guide/advice provenance or full-plan approval. Existing standalone direct helper calls rely on validated callers; complete contract shape checking is separate. Hash completeness and finite tests do not guarantee bug-free code, scientific applicability of advice, hidden dependencies or a functioning future host backend. Any bound-byte change invalidates this acceptance and needs new verification. No frozen artifact or current task index was edited by this verifier.
