# Independent revised plan review — COMM-PERF-01

Decision: **approve** for the bounded manual-host implementation/measurement scope below. No blocking findings remain. This is approval of a plan, not acceptance of unproduced data or proof of improvement.

Binding plan SHA-256: `8d8ae18d169d51a9d4f1553d7c743d1c6c65d050c79a01258bda7f9ef9eb3c37`.
Validation protocol SHA-256: `b457fef0ecd00dba31c0564ce73ae3b783932b3b1fbb2771a89c0d20b67d3b0a`.
Project: `/workspace/scratch/54fe46ee5dc7/agent`.
Reviewer: independently dispatched Work collaboration context `/root/comm_review`; manual review only, not a runtime-authenticated ReviewSession receipt or tmux/supervisor deployment. Original v1 feedback remains in `plan_review.md`, original plan in `plan-v1.json`.

| Required check | Verdict | Reason |
| --- | --- | --- |
| intent | pass | Targets durable inbox polling work while preserving communication semantics; claim scope remains local synthetic SQLite workloads. |
| guide | pass | GUIDE is actually empty, unchanged and human-owned; no project-guide conflict. |
| assumptions | pass | Six deterministic workloads, recipient reader0, target run0, prefix receipts, cross-run placement, limit20, nearest-rank p95 and two exact candidate variants are fixed. Construction treats events as the total interleaved count, consistent with `i%runs` and `events/runs`. |
| prior_results | pass | Historical selective-context experiment measures a different cost. Read raw prior_search.json:56 directories,23 errors, partial coverage. No matching result reused and no exhaustive-search claim. |
| acceptance | pass | The same hashed result contract links producer, independent verifier and publication. Six validation criteria are frozen. Trustworthy negative results are usable, separately from the unchanged positive adoption thresholds for default_backlog/large_backlog/drained. |
| risk | pass | Exact semantic checks, migration, multiple runs, independent recipient receipts and reference/receipt/retry regression coverage are planned. Polling gains may entail write/storage/setup cost and cross-run-selectivity limitations; these are measured and must remain visible. |
| resources | pass | Stdlib, one local CPU experiment, at most two predeclared variants,31 pairs and5 warmups; no paid model/GPU/external deployment. Stop after the bounded candidates and preserve negative evidence. |

## Resolution of original blockers

R1 is resolved by deterministic fixture construction, exact recipient/limit, named gated cases, p95 rule, bounded index-only and index-plus-`ORDER BY d.seq` alternatives, and equivalent backup-derived arms with alternating order from the validation procedure. `e.seq=d.seq` in the join establishes the proposed order substitution's semantic equivalence; performance remains unproven until measured. Every candidate result must retain an identifiable arm and all raw samples; a final choice cannot erase index-only observations.

R2 is resolved by `validation-plan.json` and identical protocol hash/scope/identity bindings in producer, verifier and consumer. The eventual independent verification still must read actual executed code, semantic references, fixtures, raw data and environment, recompute summaries and rerun representative cases. It is not satisfied by JSON pass labels or this review. If those checks fail or are incomplete, dependent conclusions remain blocked.

## Exact approved scope

Add `communication_pending_recipient_seq` on `communication_deliveries(recipient,seq) WHERE receipt IS NULL`; optionally use the predeclared semantically equal `ORDER BY d.seq` after the index-only comparison. Add corresponding regression tests and deterministic stdlib performance harness/evidence/documentation. Preserve routing, input/run identity, immutable per-recipient receipts, publish/retry, reference validation and budgets. Measure all six cases and all specified overhead; do not add candidate algorithms or move the improvement thresholds after observing data.

Direct main publication remains dependent on the user's existing authorization, independent code/data acceptance, preservation of unrelated changes, remote synchronization and the task's actual acceptance outcome. This review does not authorize broader deployment or claim that the continuous optimization program is finished.

## Evidence and limitations

Independent source/test read bindings remain those in v1 review (implementation unchanged before review). Revised task detail SHA-256 `e4085f92b2d516f03a00abfdae16ecc93c11e5442cd00493f7024e87ce4054a9`; task index SHA-256 `958f25ee9931ef8e9c22c1ed5d94dc1c2f9504a7bc4d356f25ee301a3156ad4c`; empty GUIDE SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

Knowledge lookup executed read-only: `PYTHONDONTWRITEBYTECODE=1 python -m agent_runtime.knowledge --root knowledge search 'SQLite communication pending index inbox' --limit 3`, corpus snapshot `451ca92210e1d1b4d6dc95ac097bd37f30ee1c832669d9688596787f52a2a239`. Returned `ds.faiss-exact-vector`, `ds.hnsw-recall-budget`, `math.convex-projection-certificate`; rejected as unrelated to SQLite delivery polling. No knowledge_refs or theoretical transfer claims are used. Actual source semantics and forthcoming measured evidence govern this task.
