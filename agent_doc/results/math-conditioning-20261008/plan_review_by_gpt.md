# Independent conditioning plan review

Verdict: **revise before data production**.

Reviewed only the assigned validation plan and DAG, repository `AGENTS.md`, and the applicable result-validation and document/decision instructions. No producer code was executed and no result, card, task index, or runtime state was changed. This is a plan review, not result acceptance or authenticated Engine approval.

Reviewed input SHA256:

- `validation_plan.json`: `f366a8beaec27bbc6186ec96f0ffdb8e64ebb0e99e246aa622d2f97fcc49e406`
- `task-dag.json`: `98119d542f1e40c2497180d58246319d98b3cdbf595a1cadf483eedfd24617a7`

The bounded CPU topic, distinct producer/reviewer owners, producer-to-verifier-to-publication dependency order, and explicit exclusion of model/GPU capability claims are appropriate. The intended conditioning identities are suitable for scoped knowledge validation. Public development checks cannot support unseen-case or model-capability conclusions.

## Blocking gaps

1. **Freeze the actual result contract.** The DAG lacks producer `task_type: experiment` or `produces_data: true`, producer `experiment_result`, verifier `action: verify_experiment_result` and `result_validation`, and publication `required_result_refs`. Add the same result ID, producer task/actor, manifest path, scope, and actual validation-plan path/SHA256 to all three contracts. Do not invent future output hashes. A node whose ID happens to be `verify_experiment_result` is not the explicit action/contract required by the workflow. The direct host graph may remain explicitly bounded; this request does not require pretending an authenticated Engine deployment exists.

2. **Replace the repeated generic acceptance sentence with falsifiable criteria fixed before execution.** Specify finite-case grids and required case categories, exact Fraction equality/inequality acceptance, a justified numerical tolerance for float KL and normalizers, required invalid-input outcomes, and required raw records/counts. Freeze the claims and assumptions: for finite distributions, q supported on S with P(S)>0, KL(q||P)=KL(q||P(.|S))-log P(S), distinguishing finite KL from extended-value infinity when q has mass where P is zero; both event masses positive for TV(P(.|S),Q(.|S)) <= min(1,TV(P,Q)/max(P(S),Q(S))); zero event mass refusal; and two distributions with equal normalized candidate far fraction but different global far mass. Include equal/asymmetric/tiny event masses, S equal to the whole support, zero-probability atoms, and a sharpness or independent bound check. Record independent references/derivations, rather than merely repeating producer arithmetic.

3. **Specify complete reproducibility and source-screening evidence.** The data-integrity procedure currently mentions only validator/output hashes. Require manifest bindings for actual code dependencies, inputs, configuration, raw case-level data/logs, outputs, and environment; a frozen execution command and deterministic inputs/seeds/repeats; finite metrics with explicit units; and independent reread/rerun evidence for all six checks. Pin the intended primary source identities and versions (MOIRA v1, October 3; MassAlloc v1, September 26), retrieval/source locations and bytes or hashes when available, and record relevance/assumptions plus adopt/defer/reject reasons. Source unavailability must block dependent literature claims or explicitly narrow them. Define elapsed-time methodology and byte/token-estimate rules; elapsed seconds are run metadata, and estimated retrieval tokens are not measured model tokens or a performance comparison.

## Recovery and scope

Version the revised plan/DAG, obtain another independent plan review, then produce data and independently validate the executed code and frozen artifacts before publishing the knowledge card or any data-supported report. Preserve failed/pending records. Final acceptance may be `usable-with-scope` only, retaining limits: finite declared cases, CPU arithmetic checks, primary-source screening, no Lean proof, no held-out model evaluation, no SGLang changes, and no model A/B or performance claim.
