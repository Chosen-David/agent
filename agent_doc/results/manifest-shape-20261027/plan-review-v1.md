# MANIFEST-SHAPE-01 independent plan review v1

Decision: **revise**. Cycle 1/2. This is a separate-context source review, not an authenticated ReviewSession receipt, execution authorization, result acceptance, or publication clearance.

Reviewed original plan-v1.json SHA256 `29141340dbf3cc990e9489effaadb5868122fd071009eadcbf5ab6abce6a6394`, budget.json, complete draft test, setup.py install/check/uninstall/update_model_inventory/doctor/main, model_routing.validate_inventory, relevant repository governance and old install-recovery-1756 plan-review-v2/result-review. No tests or probes executed.

| Domain | Verdict | Source-grounded assessment |
| --- | --- | --- |
| intent | pass | Distinct malformed-container CLI handling closes an explicitly excluded old recovery scope. Existing needs_setup and ValueError CLI semantics remain the target, without schema migration or repair. |
| guide | fail | At initial review, actual SYSTEM-99 stable Plan was52, while v1 proposed53 but supplied no binding to an actual reconciled stable Plan53. AGENTS/project_document/dual_main require stable inputs reconciled and version-bound before dispatch. Human GUIDE is empty and README is explanatory; neither grants new authorization. |
| assumptions | pass | install dereferences previous.get; check only guards top-level objects; uninstall retains stronger required mappings/value checks; updater retains schema/identity/fingerprint checks. Shared early container validation is a coherent bounded fix. |
| prior_results | pass | Actual old reviews expressly exclude nested metadata and malformed install/uninstall. Current formal retrieval preserves missing-record errors rather than claiming registered acceptance. Old results constrain design only; no old counts or consumed executions are reused. |
| acceptance | pass | Four frozen methods invoke actual subprocess CLI and compare target directory/file/link snapshots after controlled refusal. Explicit inventory gives deterministic initial installation; gateway/TMUX are absent. The exact eight-module command exercises impacted caller regressions. Fixed and independent all-pass remain future requirements. |
| risk | pass | Existing diagnostic fallback must remain read-only and convey no ownership; uninstall/updater stronger preflight must remain. Offline fixtures do not prove live discovery, authenticity, deep semantics, hostile filesystem or whole-installer transaction safety. |
| resources | pass | Shared1200sec deadline,120sec suite limit,20sec children, one baseline/fixed/independent each and at most two reviews are explicit; old exhausted branches remain consumed. |

Blocking revision: reconcile actual SYSTEM-99 stable Plan to Version53 with this bounded stage before Progress, then freeze a new proposal version binding its actual stable-prefix SHA256. Preserve v1 and this feedback. Revalidation is read-only comparison of actual prefix/hash and unchanged method/test/budget identities; no baseline before approval. Native authenticated backend remains unknown and must not be represented by this prose review.

During this pending review the parent reported a stable-plan update, then preserved original v1 and created plan-v2.json. That is a new review object, not retroactive acceptance of v1. No production/test/task/guide source was edited by this reviewer; only assigned review evidence was written.

Additional pre-baseline oracle finding from parent static inspection: refused() originally restores malformed bytes once for a sequence, while cli() raises on unexpected success before the later command cases execute. Therefore baseline can lose later-command coverage for that malformed input; mutation is retained as failed evidence but later intended independent cases are not reached. Restore the same exact malformed JSON bytes and snapshot independently within each command subtest; allow unittest subTest to isolate each failure. Freeze corrected draft/hash in v2. This strengthens input isolation and removes no assertion.

Correction to the immediately preceding oracle explanation: command subTest suppresses the AssertionError and continues the loop, so the original defect is actual later-command input contamination after unexpected success, not lost later-command coverage. The required fix remains exact per-command restoration plus a fresh snapshot. Parent correctly identified this control flow; this correction preserves the initial mistaken explanation as historical feedback.
