# Integrated candidate: still blocked, not published

Requirement: EXP-CONTAM-01. Latest remote main fetched and integrated: `897c03284106a47d24e1c0adf7ae76902e36cc9f`. It adds only MATH-84 research material, TASK and knowledge coverage/learning records; it does not fix the pre-existing gates. Isolated candidate integration build: `044201214ee371c4ad3505d851aa1c2d346328fc` (merge parents f767653 and 897c032). Incoming remote files are preserved byte-for-byte; the one append conflict in TASK was resolved by preserving all remote bytes and the single EXP-CONTAM-01 entry. No unrelated source was repaired and no test was relaxed.

## Test provenance

All logs in this directory were newly produced after that merge, against build 0442012. `test-source.json` pins the build and independently reviewed runtime/test hashes; `comparison.json` confirms the exact same six failure records on a clean 897c032 worktree. The later evidence-only commit adds logs/report and task progress; it does not change tested runtime, tests or workflows. Independent code review is the earlier actual /root/review review bound to those unchanged hashes, not a new model call or an invented review.

- Integrated full suite: 1008 tests in 80.795 s, FAILED (failures=3, errors=3, skipped=1).
- Clean latest main: 991 tests in 82.233 s, identical failure/error identities and one opt-in tmux skip.
- Affected contamination: 17/17; result-related: 79/79; reader: 3/3. These latest runs were performed by the main execution context.
- sync_plugin_references --check still reports exactly three stale mirrors; the five references actually generated for contamination match existing render output.
- Required branch checks cannot be read (Forbidden); combined commit statuses for 897c032 are empty, not proof of required CI success.

## Current six failure/error records and files

1. ERROR `test_code_reading.DistributionTests.test_standalone_links_and_routes` (tests/test_code_reading.py:112, tests/markdown_links.py:100): `plugins/research-assistant/skills/code-reading/references/project_document_workflow.md` links to absent `../docs/token_optimization/advice_meetings.md`.
2. ERROR `test_travel_contract.TravelDocumentationContractChecks.test_plugin_navigation_closes_inside_distributable_subtree` (tests/test_travel_contract.py:223): FileNotFoundError reading `plugins/travel-assistant/skills/travel-planner/docs/token_optimization/advice_meetings.md`.
3. ERROR `test_visual_explanation.VisualTeachingPackageTests.test_entry_and_shared_workflow_links_stay_inside_each_skill` (tests/test_visual_explanation.py:57): `plugins/research-assistant/skills/explain-research-concepts/references/project_document_workflow.md` has the same absent relative target.
4. FAILURE `test_knowledge.KnowledgeTests.test_bundle_exact_and_cli_without_repository` (tests/test_knowledge.py:228): `plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/learning_state.json` differs from canonical `knowledge/learning_state.json`; the accompanying coverage.json is also stale by the explicit sync check.
5. FAILURE `test_plugin_reference_sync.PluginReferenceSyncTests.test_generated_plugin_references_are_current` (tests/test_plugin_reference_sync.py:17): stale `plugins/research-assistant/skills/model-with-knowledge/scripts/project_docs.py`, `plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/coverage.json`, and `plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/learning_state.json`.
6. FAILURE `test_travel_contract.TravelDocumentationContractChecks.test_plugin_navigation_closes_inside_distributable_subtree` (tests/test_travel_contract.py:230, subtest source=plugins/travel-assistant/skills/travel-planner/references/project_document_workflow.md): is_file() fails for the same missing advice_meetings target. This is the same travel test as record 2, which additionally errors when attempting to read that file.

Source attribution remains in ../contamination-20261011/blocker-diagnosis.md: prior advice navigation/raw-copy distribution policy, task parser mirror and mathematical knowledge bookkeeping, not this contamination feature. New MATH-84 main does not resolve them.

## Delivery and remaining boundary

Keep candidate pending. Update existing Library identity `libfile_8f0f6bd737ac8191a8380422c3d7c9b7` with expected_current_version=0; do not create another Library file or drop the guard. The source archive identity is the final evidence commit, while test attribution remains build 0442012. Package includes the full tracked integrated source, binary-safe diff against 897c032, history, logs, hashes and restoration instructions. Old Library version is retained by replacement.

No model, Claude, GPU, paid operation or SGLang change was introduced. Runtime has no general stop adapter: it invokes a trusted host callback. Actual stop testing covers one test-owned local Linux pidfd child and preservation of another process. Remote/multirank/process-tree fencing, shared external leaderboard transactions and SGLang stopping are not deployed capabilities. Publication remains gated on real required checks, new main integration if it advances, and non-force remote readback; no main push was attempted.
