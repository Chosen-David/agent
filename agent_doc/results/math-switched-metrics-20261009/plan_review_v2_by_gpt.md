# MATH-62 independent plan review — cycle 2

Decision: **approve** for the exact plan-v2.json bytes listed below and its matching frozen validation contract. No experiment result or publication is accepted by this decision.

## Actual reviewer context

This is the same independently delegated reviewer agent as cycle 1, receiving a new review turn with the revised files. It is separate from the planner/producer context, but **a new turn is not a newly created fresh context**. No authenticated ReviewSession, host signature, runtime receipt, deployed monitor or enforced dual-main adapter is claimed. The parent remains responsible for honest reporting of that distinction and for a distinct independent result-verification context. This is the second of two bounded review cycles; the original started_unix and budget remain unchanged.

Cycle 1 feedback is preserved byte-for-byte at plan_review_by_gpt.md, SHA-256 d83e9995f44519e5d956916f050111c2e0fc9cab6601fcac1c0df0acc8f95870. Its original plan/contract hashes remain unavailable following the reported concurrent rewrite; none are invented here. Cycle 2 pins the actual immutable plan-v2.json and current matching inputs.

## Full review

The revised mathematical contract resolves the first blocker. With V[t]=x[t]^T P_sigma[t] x[t], each update contracts in its current metric by a, and the post-update conversion to P_sigma[t+1] costs at most mu only when the mode changes. Iterating therefore gives V[t]<=a^(t-s)mu^N(s,t)V[s], with N counting u from s through t-1, including the last post-transition conversion and no invented initial switch. The all-window count bound gives V[t]<=mu^N0*(a*mu^(1/tau))^(t-s)*V[s]. For finite SPD metrics this implies a Euclidean squared-norm bound with max_i lambda_max(P_i)/min_i lambda_min(P_i). No eigenvalue estimate is needed to prove the stated energy bound.

The strict condition certifies decay; equality does not universally certify strict decay. Read the plan's phrase “decay iff” as decay of this conservative exponential bound, consistently with its explicit “sufficient only”; it is not an iff characterization of actual switched-system stability. The final card must retain that distinction. The common metric also supplies a sufficient certificate, not a necessary characterization. Distinct affine equilibria do not fit the homogeneous common-origin recurrence.

The second blocker is resolved to a workable bounded acceptance contract. Eight distinct case categories cover the positive certificate, per-mode metric checks and conversions, instability under alternation, finite dwell block, a=1 boundary, zero input and affine refusal. Six records must meet Top3 new-card retrieval on both backends; a four-entry full prerequisite closure must remain within 18000 characters. The two specified regression modules and exact candidate/holdout preservation are acceptance gates, not optional checks. Source/proof inspection and independent rerun retain separate obligations, and producer/verifier/publisher references equal the same frozen contract. No numerical or retrieval measurement has been reviewed or produced by this reviewer.

The source extraction supports screening 2609.37840v1 as continuous affine practical stabilization around a desired operating point that need not be a common subsystem equilibrium. The retrieved excerpt visibly uses continuous dynamics, average-system Hurwitz assumption and hybrid target sets. It cannot be cited as a proof of arbitrary homogeneous discrete switching. The own elementary discrete derivation is the scientific basis for this card; selective extraction, font warning and preprint status remain explicit. Bibliographic attribution of the classic source and all eventual card claims still require independent result verification. This reviewer read local excerpt/provenance; it did not retrieve or visually audit the full original PDFs.

The dependency order remains plan review, production, distinct independent verify_experiment_result, then root publication. The result contract is identical in all three roles and its validation hash matches actual bytes. Current declared evidence_refs also match actual bytes. The report additionally pins source and prior-decision inputs that supplement that manifest. Outputs may be produced only within the original bounded local card/evidence scope; the root keeps serialized TASK/publication ownership. No guide writes, holdout content reads, scope expansion, cost claims or token benefits are authorized. The parent must freeze baseline candidate hashes before edits and expose actual manifest/code/raw/card/retrieval outputs to the result verifier. Missing output, stale dependency or failed predicate blocks result acceptance; this plan approval cannot override those conditions.

No blocking finding remains in the revised scientific/acceptance plan. This approval does not install the repository runtime or satisfy a hypothetical authenticated ReviewSession requirement; it supplies actual independent reviewer feedback for the manual authorized workflow only. Publication and remote integration still require the parent's current authorization and independent accepted evidence.

## Compact verdict

```json
{
  "decision": "approve",
  "summary": "Cycle 1 mathematical and measurable-acceptance blockers are resolved for this bounded local plan; approval is plan review only, pending independent source/code/data acceptance.",
  "checks": {
    "intent": {
      "status": "pass",
      "reason": "Single homogeneous switched-map card remains within MATH-62 and the fixed-linear-iteration transfer boundary; recent affine p-norm direction is screened/deferred."
    },
    "guide": {
      "status": "pass",
      "reason": "Empty GUIDE.md supplies no substantive requirement; human-only directory exclusion and SGLang exclusion preserved. Current stable task/evidence hashes match plan-v2."
    },
    "assumptions": {
      "status": "pass",
      "reason": "Finite same-dimensional real maps, common origin, no reset/disturbance, uniform SPD inequalities, allowed edge metric comparison, squared-energy convention and terminal switch count are explicit. Strict discrete dwell sufficient condition and equality limitation are frozen."
    },
    "prior_results": {
      "status": "pass",
      "reason": "Actual partial ResultStore search and pinned KB results retained; prior_decisions explicitly rejects three corpus hits as new science and limits MATH-61 to prerequisite/design without raw-data reuse."
    },
    "acceptance": {
      "status": "pass",
      "reason": "Eight distinct public case categories, exact PSD checks, six Top3 retrieval records on two backends, four-entry prerequisite closure <=18000 characters, preservation and two regression modules are now deterministic acceptance predicates; independent rerun and proof/source review remain mandatory."
    },
    "risk": {
      "status": "pass",
      "reason": "Common metric is sufficient; affine/different-equilibrium and arbitrary layer switching transfer refused. No finite examples as general proof, no performance/model/GPU/token claim or holdout content use. Raw evidence remains pending until distinct result verification."
    },
    "resources": {
      "status": "pass",
      "reason": "Original 1800-second start and maximum two review cycles retained; about 255 seconds elapsed at report generation. Public Fraction and local retrieval checks are bounded CPU work. Model cost/token unknown and no deployed ReviewSession claim."
    }
  },
  "findings": []
}
```

## Actual reviewed file hashes

All SHA-256 digests below were captured from actual current bytes at review. The plan evidence hashes and producer/validator/consumer validation-contract equality were checked read-only.

```json
{
  "AGENTS.md": "ff97d09aeb35cff3a973d1423f325ef6274f33b4c68830e8c899821e989bd63a",
  "prompts/decision_review.md": "55b793450ff0e3d29696dae7626afab7f15d1ab843baa396dcc1d564e532c849",
  "prompts/review_main.md": "599497c0e8cdb5b7cd151342a34f3bb905267c8674b96ea967761a705f0ba38d",
  "workflows/dual_main_workflow.md": "639f19cf9de42d65935b3a42b8e9f6e8aa6e4a2145254ad59202642974eb9644",
  "workflows/project_document_workflow.md": "1907fa8868ec00c04018601cb49a1e273e70c46d5c8a53eeef33359d79d023da",
  "agent_doc/guide/GUIDE.md": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "agent_doc/task/TASK.md": "a52907eaf3a9af394767fb68a00b1330e7c35b83744566afca98affcafe962f5",
  "agent_doc/task/task_details/MATH-62.md": "003f3641a7367800c3acf5fe5345fc4808300489ed6e27ddf49faa91eef1ac0f",
  "knowledge/coverage.json": "d8aff97b17dd00f644f3ef1564b2b3183cce2d24f51c76c67aa44e16d93548e7",
  "knowledge/learning_state.json": "6c08fc99f1440fac49f6d154f631a0c20132aa66cfd7ee81b88cd1e7cd208dad",
  "agent_doc/results/math-switched-metrics-20261009/plan-v2.json": "1db2ff7dda940bf9601f620e21a4e9240085e446300679c2f1a4f39d412eab8d",
  "agent_doc/results/math-switched-metrics-20261009/contract.json": "6d4c9fb91eaa925e80149a10a9583045a8eed43b58baa8e0391f1a3555d7d7d1",
  "agent_doc/results/math-switched-metrics-20261009/validation_plan.json": "a25c47d55cee053945e8382e1ee70ff02b1c6dcd3eb6dac9fae6986f29aa9515",
  "agent_doc/results/math-switched-metrics-20261009/prior_search.json": "501c14e78d0428904f1624bc366255ad4cc1274a9ea188cb45382c1c890dce6a",
  "agent_doc/results/math-switched-metrics-20261009/prior_knowledge.json": "d6a432fa072f7873bf34e1b22e69289eb90e02b04561a0012c7d1b4aa1ff3369",
  "agent_doc/results/math-switched-metrics-20261009/prior_decisions.json": "7bc560c81ab0a640ee1383274718399a0f96357adbdab444b71a870f2b561e0f",
  "agent_doc/results/math-switched-metrics-20261009/sources.json": "4500e2cede516fb1041c8302f524df054601d4854c6d08da3535d77cba321f6e",
  "agent_doc/results/math-switched-metrics-20261009/research_extraction.json": "8079aae29c9d71affa617d0274795bf1a3267ac880d5b13d67b6df412a91e3a1",
  "agent_doc/results/math-switched-metrics-20261009/research_excerpt.txt": "96a4749cebe5ff8d69fd8105427c0983cef4d34148b258c124492a8974f2529b",
  "agent_doc/results/math-switched-metrics-20261009/preservation_baseline.json": "73f0860fa96790d52cff4d01003055b8238461285a2570718d2840bd6776b391",
  "agent_doc/results/math-switched-metrics-20261009/plan_review_by_gpt.md": "d83e9995f44519e5d956916f050111c2e0fc9cab6601fcac1c0df0acc8f95870"
}
```
