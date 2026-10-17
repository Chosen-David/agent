# Independent plan review — MEM-CLAIM-12

Decision: **revise**. A bounded experiment is justified; the current plan is not yet ready for producer execution. This is a manual independent review of the supplied handoff, not an authenticated ReviewSession receipt, managed dispatch authorization, or result acceptance.

## Review object and checks

Project: `/workspace/scratch/88c3234ecfbc/agent-memory`. Plan SHA256: 8ba31a7ea5b2ea271271797f64b085e54a71bf305d1667389069ae3716282809. Baseline: `4e4199d789812c6964329c02231733472d65a700` as declared in plan. I read AGENTS.md, prompts/decision_review.md, workflows/project_document_workflow.md and dual_main_workflow.md, canonical MEM-STORAGE-01 stable plan and progress, TASK index, the empty read-only human guide, supplied plan/reference-hashes/prior-search, actual handoff_basis.py, _ids implementation, relevant BasisTests, communication consumption/context/impact callers, and the historical reports cited below. All 12 supplied reference hashes match current bytes. No performance experiment or code change was made.

| Dimension | Outcome | Assessment |
| --- | --- | --- |
| intent | pass | Local evidence-claim validation is a real Agent handoff gate and fits the continuous Agent improvement authorization. Keep the parent memory/KV task open and distinguish this from model storage or end-to-end Agent latency. |
| guide | pass | GUIDE.md is zero bytes with the supplied empty hash. No substantive guide restriction is invented; the human-only directory remains untouched. Explicit current authorization and repository boundaries govern. |
| assumptions | fail | Deep-chain repeated scanning is visible in actual code, but treating all large valid graphs as attractive fast-path candidates ignores known shallow/dense overhead and accepted Python subclass behavior. See B1/B2. |
| prior_results | fail | Search truthfully reports 223 scanned, six lexical hits, partial=true and 65 missing-record errors; it does not justify treating the directly relevant historical DAG experiment as unavailable. See B1. No old measurement is accepted as this candidate's result. |
| acceptance | fail | Complete claim_graph latency and 21 paired samples are appropriate. However the listed layered DAG has no explicit acceptance gate, and broad/shallow/dense invalid-fallback behavior lacks a frozen performance/compatibility decision. See B1/B2. |
| risk | pass | Bounded local CPU changes, independent result review before integration, no schema/output changes, negative retention and publication readback are appropriate. Extra O(V+E) adjacency memory and two-algorithm maintenance are real costs to document. |
| resources | pass | Existing Python, no GPU/paid resources and at most two candidate iterations are adequate. Use sequential timing outside regressions. Small controls require batched calls to make timer overhead negligible. No monitor/service deployment is claimed. |

## Actual contract and fallback assessment

claim_graph first performs schema/evidence/premise checks in input order and builds a dict whose values are the original claim objects. Its existing graph pass repeatedly creates a ready set from all pending claims, rejects a round with no ready nodes as cyclic, then checks each ready node's unknown-parent and supported-parent rules. For a deep chain this repeats a shrinking scan for each depth: the quadratic hypothesis is a code-based inference, not a measured benefit. Returned graph insertion order, claim identity, errors and nonmutation are observable.

check_handoff_basis consumes that graph before required-claim selection; basis_context uses it to include ancestors and retain candidate/rejected claims. Mailbox.consume_handoff reaches the gate before writing communication_basis, and prepare_context goes through consumption and another basis check. basis_impact also calls claim_graph. Therefore weakening validation could let unsupported evidence be consumed; successful direct claim_graph timing cannot be reported as complete Mailbox or complete basis_context acceleration.

Falling back to the unchanged original graph loop on ANY unknown parent, unsupported supported-edge, or cycle is a sensible way to retain multi-error precedence on ordinary immutable inputs. Do not raise from the preliminary fast pass: an unsupported edge elsewhere may coexist with a cycle or an unknown parent on a currently ready node, and the legacy round/set traversal determines which error appears. Do not mutate graph, claims, dependency lists or a pending set later reused by the fallback. Hash-seed-dependent ordering among simultaneously ready failures should remain baseline-relative within the same process, not be replaced by a newly promised global deterministic order. Duplicate dependencies already fail _ids before graph validation; test this rejection rather than silently deduplicating accepted input.

## Blocking revisions

### B1 — Reuse the relevant negative result and freeze all control decisions

Read and bind `agent_doc/results/dag-cycle-20261013-1601/report.md` (and inspect its relevant actual source before copying a guard). That report records an eager adjacency approach regressing a 512-star control by 21.29%, then an accepted guarded approach: two legacy rounds, sufficiently large sparse residual graph, exact builtin strings and original fallback. These are transferable design/negative-result lessons; its core.validate timings are NOT evidence for claim_graph and must not be reused as candidate measurements. The partial search's missing record error is not missing raw evidence. Also bind memory-context10 report only as adjacent handoff context evidence, not current claim-graph validation.

Revise the candidate admission policy before measurement and add frozen non-regression gates for shallow broad/star graphs and dense graphs, including the already listed 256-node shared layered DAG. A <=16 legacy route is reasonable for tiny controls but cannot alone address the documented 512-star failure. A shallow-round/residual-size or similarly justified guard may avoid eager allocation. Do not require all graph shapes to gain >=25%; require each non-primary control to stay within the chosen <=15% allowance, or predeclare an explicit bounded tradeoff rather than decide after results. Preserve the 512-chain primary >=25% gate and both producer/independent acceptance.

Freeze batched calls per tiny sample, input construction outside timing, identical batching, timing environment, all 21 raw pairs, and median calculation. Include a targeted malformed/fallback latency observation to quantify extra work; no new universal invalid-input speed claim is required. State extra adjacency memory and maintenance cost even if peak memory is unmeasured.

Revalidation: review a versioned revised plan and its relevant prior-evidence hashes before the first producer benchmark; later independent reviewer validates all listed workload gates on the exact final source.

### B2 — Replace optional subclass compatibility with an explicit boundary

The current code accepts list/dict subclasses and str subclasses through isinstance, and _ids also accepts tuple dependency containers. A preliminary pass can add reads/hash/equality calls before invoking the old loop; falling back only after detecting an error does not erase their observable effects. `plain and subclass container controls where feasible` is too optional for an unconditional unchanged-contract claim.

Specify a conservative fast-path admission rule preserving original behavior for customized containers/IDs (for example, exact builtins used by the optimized traversal with immediate legacy fallback before additional traversal), or provide an equally concrete compatibility argument and mandatory tests. Keep tuple dependencies valid. Test representative custom string hash/equality and dependency/container access, exact error type/message, no mutation and original claim identity. Avoid broad catches that hide unrelated programming errors.

Revalidation: independent differential review across ordinary generated DAGs, invalid mixtures, builtin tuple dependencies, and representative subclass controls; differential errors compared in the same process/hash seed. No need to claim support for arbitrary concurrent self-mutating objects.

## Alternatives and experiment value

Python graphlib.TopologicalSorter is a mature candidate for structural cycle checking and an independent oracle. It is not a semantic drop-in: predecessor entries auto-create missing nodes and CycleError timing/text differ, and it still needs supported-edge guards plus legacy fallback. A small direct Kahn pass is understandable here because compatibility checks and fast-path admission dominate the integration. Either choice can be justified without benchmarking both libraries; avoid turning two allowed candidate iterations into an unbounded algorithm contest. Consider graphlib for an independent reference that does not merely repeat candidate logic.

Retaining the small original loop solely as the compatibility/error path is proportionate if the final optimized helper stays compact, shares schema validation, and earns the frozen gain with all controls. A large duplicated validator, opaque tuning or unsafe generalized fast path would outweigh one synthetic deep-chain improvement. The available structure and existing historical negative result justify this limited experiment after revision; they do not justify integration now.

## Next owner and unchanged gates

Planner owns plan revisions and canonical Progress; I wrote only this review. After B1/B2 are resolved, request an independent review of the exact revised plan. Producer → independent code/raw-data validation → full repository/Reader/relevant -O checks → final-source/hash confirmation → fresh remote integration/nonforce publication/readback remains mandatory. This review supplies no blanket approval from older passes and no permission expansion.
