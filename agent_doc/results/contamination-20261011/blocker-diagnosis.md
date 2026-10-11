# Exact baseline failures and continuation disposition

Task: EXP-CONTAM-01. Follow-up instruction: finish required validation or persist a complete resumable candidate in Library; no new models, GPU or paid operations. Remote fetch still resolves main to `f11cc4bc4e599fb6a4b7f3fc6e1141d454555686`. Original implementation candidate is `33be6930d9dd783abef9d893067a4f4d75773c45`.

These are six unittest failure/error records, not six separate root causes. The travel test emits both a subtest failure and an outer error. Clean main and candidate logs have identical failure identities.

| Record | Exact test | Failure site | Source/affected file and root cause |
| --- | --- | --- | --- |
| error | test_code_reading.DistributionTests.test_standalone_links_and_routes | tests/test_code_reading.py:112; tests/markdown_links.py:100 | plugins/research-assistant/skills/code-reading/references/project_document_workflow.md links to missing ../docs/token_optimization/advice_meetings.md |
| error | test_travel_contract.TravelDocumentationContractChecks.test_plugin_navigation_closes_inside_distributable_subtree | tests/test_travel_contract.py:223 | Attempted read of plugins/travel-assistant/skills/travel-planner/docs/token_optimization/advice_meetings.md raises FileNotFoundError |
| error | test_visual_explanation.VisualTeachingPackageTests.test_entry_and_shared_workflow_links_stay_inside_each_skill | tests/test_visual_explanation.py:57; tests/markdown_links.py:100 | plugins/research-assistant/skills/explain-research-concepts/references/project_document_workflow.md has the same missing relative target |
| failure | test_knowledge.KnowledgeTests.test_bundle_exact_and_cli_without_repository | tests/test_knowledge.py:228 | plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/coverage.json and learning_state.json are stale copies of knowledge/coverage.json and knowledge/learning_state.json |
| failure | test_plugin_reference_sync.PluginReferenceSyncTests.test_generated_plugin_references_are_current | tests/test_plugin_reference_sync.py:17 | Existing sync tool reports the two JSONs above and plugins/research-assistant/skills/model-with-knowledge/scripts/project_docs.py stale |
| failure | test_travel_contract.TravelDocumentationContractChecks.test_plugin_navigation_closes_inside_distributable_subtree, source=plugins/travel-assistant/skills/travel-planner/references/project_document_workflow.md, href=../docs/token_optimization/advice_meetings.md | tests/test_travel_contract.py:230 | is_file() assertion fails for the same absent travel package target; the later error is its attempted read |

## Attribution, not a waiver

- `b41d1313b64103f686b0690d466f61f8aa7bcd18` (`feat(advice): bound change navigation and document supervision cost boundaries`) is the latest change to workflows/project_document_workflow.md. Its first navigation paragraph contains the advice_meetings link. scripts/sync_plugin_references.py explicitly puts this workflow in RAW_COPY_SOURCES to preserve project-relative examples. Thus an ordinary sync preserves the bad relative navigation link; correcting this needs a source/packaging decision for the existing advice document distribution, not a contamination reference change.
- `a73c4a77b8edc1dbb9f967c7d682f0bc43b02f9c` (`perf: provide version-bound task scope without replaying historical rows`) last changed agent_runtime/project_docs.py. The stale bundled copy differs in parse_requirements: canonical closing-fence detection additionally requires no non-whitespace after the fence token. Contamination uses the root write guards; it neither changes this parser nor uses the knowledge skill's bundled parser.
- `bcfb0ec2eb48af6cbcb53cc77de4ed417c8e88c6` (`docs(math): derive residual witnesses for transient amplification`) last changed the canonical coverage/learning files. Their knowledge bookkeeping drift is unrelated to contamination validity/stop/cache behavior.
- `git diff f11cc4b..candidate --name-only` contains none of those canonical sources or stale mirrors. The five generated references actually changed for contamination match the current existing render() output. No additional contamination-generated reference is stale or missing.

The three mirrors could be regenerated mechanically, but that would adopt unrelated knowledge/task-parser work and still not fix the separate advice-link packaging policy. Under the follow-up's direct-scope limit, leave them intact and do not weaken tests. Attribution shows earlier unrelated work; it does not claim those authors were concurrently active in this session.

## Exact stop capability boundary

There is NO shipped general OS/scheduler stop adapter in this candidate. Contamination.contain calls a trusted host-provided stop(binding), checks exact job identity plus stopped/fenced/source readback, and performs local revocation/quarantine. Fcntl locking requires POSIX. The executable test adapter alone holds a pidfd for one test-owned local Linux child, sends SIGTERM, observes pidfd readiness and wait exit; its fixture has no child ranks or retry dispatcher. Another test process demonstrably remains alive. Mock callbacks test failure paths, not real remote stopping.

Not implemented/deployed: remote SSH/scheduler cancellation, process-tree/cgroup/multi-rank fencing, arbitrary PID ownership authentication, shared external leaderboard transactions, discovery of unregistered external caches, or any SGLang control. This candidate cannot be described as able to stop SGLang. The host must implement/authorize those exact operations and prove the full reference closure before enabling this API. It never launches jobs or expands budgets.

## Portable handoff

No code changed during this follow-up. Preserve the original independent review hashes and logs. A new local documentation-only commit records this diagnosis; a Library candidate archive will contain a complete tracked source snapshot at that commit, the base-to-candidate binary-safe patch and commit patches, all test/review logs (inside the source snapshot), SHA256 inventory, source/base/tree identities and restore instructions. No private .agent-runs, credentials, environment files, or local Git configuration enter that archive. It remains NOT PUBLISHED and must pass the required checks before a non-force main update.
