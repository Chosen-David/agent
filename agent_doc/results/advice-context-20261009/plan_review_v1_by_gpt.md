# Independent plan review — CTX-20261009-01

Verdict: **revise**. The proposed implementation is reasonable; the immutable review object needs complete document and execution bindings before production work begins.

Reviewed object: `agent_doc/results/advice-context-20261009/plan.json`, SHA-256 `f41c988db0da70b2b1478735b86b1387e88f2f9a2b7baeaec1931531e5b5b782`.

This review is a separate local host invocation assigned to read the plan and its evidence. It is not an installed `ReviewSession`, authenticated runtime receipt, live supervisor, deployment, publication authorization, or result acceptance. Only the assigned review file was written; no tests or experiments were run.

## Seven checks

| Check | Status | Reason |
| --- | --- | --- |
| intent | pass | The task detail preserves the user’s context/advice/knowledge and multi-agent governance goal, agent-only scope, existing direct-main authority, no SGLang changes, retained historical/source bytes, and proposal-only lifecycle/database work. Implementation is a bounded improvement to an existing interface rather than authorization for a new service. |
| guide | fail | Both guide files are pinned and the entire human-only directory remains protected. GUIDE.md is empty; README explains protected-directory responsibilities. Human authorship is not independently established by the filenames. However, the reviewed plan does not bind the canonical TASK index/global project-document snapshot or complete advice decisions. Their absence prevents verification of completeness and conflicts. The revised object must distinguish protected version/read bindings from verified planning authority. |
| assumptions | pass | Source inspection confirms that `task_document_refs` currently deep-copies the global advice inventory, although `check_document_refs` binds freshness to adopted advice, guides, index and stable details. Restricting task inventory to task-relevant adopt/adapt sources is therefore technically plausible. It requires new explicitly reviewed plans; it must not silently migrate persistent plans or weaken exact-ref validation. |
| prior_results | pass | The pinned prior decision record states an actual partial search, 55 scanned items and 22 errors, with no stored data reused for the new claim. Legacy material is only design provenance. The lookup gaps are acknowledged and do not support an absence-of-history claim. |
| acceptance | pass | Stable inputs, all guides, full global assessment coverage, consumer stale rejection, nonbinding rejected/deferred/new advice, preservation, and same-workload serialized chars/bytes are explicit acceptance goals. The detail calls for task_manifest/ManagedEngine integration and regressions; token and model-effect claims are excluded. Independent result verification precedes publication. |
| risk | pass | The change is local, reversible and constrained to agent runtime/tests/documentation. It does not remove sources or deploy database/archive/background behavior. The highest implementation risk is accidental removal of global assessment coverage or stale-input checks; the listed negative tests directly address it. |
| resources | pass | The fixed 2 plan cycles, 2 test-fix cycles and 2700-second budget are finite, and a single implementation/document/TASK writer is specified. Host independent review is available through this actual invocation. Runtime receipt/service capabilities and model/token costs remain unestablished and must not be claimed. |

## Blocking finding B1 — Complete the frozen review object

Target: `plan.json` document bindings and `dag`.

The cited `workflows/dual_main_workflow.md` requires review of the actual complete DAG, task_refs, project index, stable Plan, verified guides/adopted advice, methods/inputs/outputs, completion conditions and resources. The current plan pins the new task detail and two guide files, but omits the canonical index and global project-document snapshot/assessment bindings. Its DAG also uses bare `raw.json`, does not explicitly represent the prerequisite independent review node, and has no per-node task_refs, allowed writes or evidence-based completion conditions. Names and a prose acceptance list do not freeze those execution boundaries.

Before production, create a new immutable plan version and retain this original. Bind the current canonical TASK index and complete global snapshot, together with advice assessments/adopted source hashes. Preserve the full global advice inventory; the proposed reduction applies only to node document_refs. Empty adopted_advice is valid when no advice is adopted; retain per-source defer/reject reasons rather than omitting the sources. For guides, explicitly record read/protected/version bindings and unknown human authorship where that is the actual evidence. Do not fabricate owner provenance or promote file content to new authority; the current user scope and AGENTS instructions support this work. Record the actual scoped task_refs so historical requirements are not marked complete or rerun by this task. Freeze the local-host DAG with exact central output paths, one writer and allowed writes for each node, and completion conditions for the producer, independent result verifier and publication. Represent or explicitly identify this prerequisite review step. Record the supplied current user scope and existing publication authority as host-provided references; this review supplies neither.

This is a local review-object correction. It does not require installing a supervisor, deploying `ReviewSession`, editing human guides, changing user scope or requesting permission already supplied by the user. If execution later uses managed Engine/ManagedEngine or PublicationLedger, their existing authenticated receipt and authorization gates remain separate requirements.

Reverification: independently review the complete revised object and verify every evidence hash; confirm TASK/global guide/advice coverage against the pinned sources, scoped task ownership, unchanged authority boundaries, exact producer/verifier artifact identity, and publication’s dependency on the independent usable-with-scope result verdict. Only then approve production under the remaining fixed budget.

## Implementation observations for the result reviewer

All 14 supplied evidence hashes matched their current files. Relevant source inspected: project-document snapshot/reference/check/binding functions; task_manifest prepare and contract checks; handoff_basis context selection/budget behavior; and cited project-document acceptance tests. No measured reduction or successful test outcome is asserted here.

Keep `validate_advice_assessments` operating on the full global inventory, and keep `validate_contract` exact node-ref equality. Test both `adopt` and `adapt`, a node with no relevant adopted source, multiple task_refs with overlap, and another node’s adopted source being absent from this node inventory. Retain adopted-source stale rejection through real consumers and all-guide add/edit/delete/rename protection. Measure the old and new serialized representation under identical content and serialization settings; report workload dimensions and chars/UTF-8 bytes, with tokens unknown unless a real pinned tokenizer is used.
