# Independent plan re-review — MEM-CLAIM-12 v2

Decision: **revise** (one acceptance-definition blocker remains). Manual independent review only; no ReviewSession receipt, performance run or integration acceptance is claimed.

Reviewed exact plan-v2.json SHA256: a5fd5f667f80cacfdf97020e0822a7fa87466375400be624f007dae72877234a. The prior plan and full review remain intact. Also read actual core.py guarded cycle implementation and source-screen.md navigation context; historical report inspection is recorded in the prior review. No implementation changed and no experiment ran.

| Dimension | Outcome | Reason |
| --- | --- | --- |
| intent | pass | Unchanged authorized local Agent handoff scope; no model KV/QA/TTFT inference. |
| guide | pass | Empty read-only human guide and repository boundary unchanged. |
| assumptions | pass | Two legacy waves remove shallow workloads before adjacency allocation; residual>=64 and raw-dependency density<=4*residual bound admission. These are experiment hypotheses rather than promised improvements. |
| prior_results | pass | Relevant historical star regression is acknowledged, used to shape admission, and not reused as this candidate's performance evidence. |
| acceptance | fail | All six workloads are listed, but performance.controls still gates only small/empty, leaving shared/star/dense without binding non-regression criteria. Tiny-sample batching remains unspecified. |
| risk | pass | Whole-graph exact-type admission, no normalization, immutable input preservation and failure returning to the unchanged legacy loop address the semantic risk at the plan level. Actual code must substantiate this. |
| resources | pass | Two candidate iterations, local CPU, sequential independent evidence gate and bounded publication remain suitable. |

## Resolved algorithm and compatibility findings

The proposed two-wave guard is proportionate for this bounded experiment. Exact builtin-type screening must happen before additional dependency hashing, membership, customized iteration or field access; verify each claim has exact dict type before reading its fields, each dependency container exact list/tuple before iteration, and IDs/status exact str before new hash/equality operations. Guard checks themselves may inspect builtin graph/claim containers and use type/identity. Any exotic object anywhere in the graph must prevent fast traversal rather than partially inspect a prefix with new semantic operations. The exact screen is over the entire graph, including already removed nodes, because pending parents may refer to them.

Check all remaining parents against the complete original graph and all supported-child parent statuses, including already removed parents. Unresolved counts must count only parents still pending. A zero unresolved degree may not ignore a missing parent. If any missing parent/status error/cycle occurs, return failure from the optimization attempt and let the unchanged existing pending loop decide exception precedence; never raise a new fast-path error or replace its pending state. Do not repeat an expensive failed attempt on later waves. These are concrete implementation checks, not evidence that the yet-unwritten candidate already satisfies them.

Residual63/64/65, density thresholds, custom strings/containers, tuple dependencies, same-process multi-error type/message parity, identity and no-mutation checks are now mandatory through the added v2 statements. Interpret older 'where feasible' wording as superseded by the explicit mandatory exotic-control clause; remove the stale wording for clarity when revising.

## Remaining blocker and exact repair

Change performance.controls to require **each non-primary workload** (256 shared layered DAG, 8 chain, empty, 512 star, 256 dense DAG) to have median regression <=15%, preserving all negatives and inconclusive=no publication. Currently 'each small/empty' does not express the stated intent and can permit acceptance despite a large shared/star/dense regression. Freeze identical batched calls per sample for tiny inputs before measurement so the per-call median is reliable; report batches/raw observations and calculate from complete-call measurements. Add the planned invalid-fallback overhead observation as diagnostic, retaining its outcome without claiming a universal invalid-input gain.

Version the corrected immutable plan and re-review before producer execution. No need to ask the user: this is a precise acceptance correction within their existing authorization. Once corrected, the plan's narrowed experiment merits approval; actual integration still requires independent source/raw-data review and every frozen gate.
