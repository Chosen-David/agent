# Independent conditioning plan review, revision 3

Verdict: **approve scoped CPU production for result v2**.

Reviewed only the current assigned validation plan and DAG against the applicable repository/result-validation instructions and the prior review. No producer tests were run and no producer outputs, task state, or cards were changed. This is plan approval; independent result acceptance remains required before publication.

Reviewed input SHA256:

- `validation_plan.json`: `c6acb5c22856bdc92cd63ab4df25a51244ba7a9dfa0cb0d69c75085182a41c1a`
- `task-dag.json`: `54c1ebb2fc6b1d40db0aa30c77ec6a85773992e58f063b1beed0cc1d5939fe75`

The producer, independent verifier and publication consumer retain identical contracts, now for `math-conditioning-cpu-20261008-v2`; their validation-plan hash matches the actual current bytes. Explicit experiment classification, verifier action and dependency order remain intact. Case coverage, exact arithmetic acceptance, float tolerance, source-screening obligations and scientific scope are unchanged from the approved revision 2.

The nonempty `seeds: [0]` field is acceptable because the plan explicitly defines 0 as an unused deterministic enumeration marker. It does not create a random experiment or support a statistical claim. The v2 summary filename and lossless gzip raw-record filename make the new production round distinguishable. Independent result review must decompress and inspect the complete records, reconcile counts and ensure all actual artifacts/configuration/commands and their hashes belong to this v2 contract; the compressed file's hash alone is insufficient. No prior acceptance is inherited, and earlier raw/failed evidence must remain preserved.

Approval retains all revision 2 scientific obligations: explicit finite-conditioning proofs and their event/support assumptions, invalid-event refusal, extended-value KL handling, and the conditional-versus-global far-mass counterexample. Listed primary sources still require actual retrieval/readback and relevance decisions. All six checks and artifact bindings must be independently accepted for `usable-with-scope` before publication.

Approved scope remains bounded CPU arithmetic and public development checks, plus the specified primary-source screening. No SGLang change, model A/B, held-out model evaluation, GPU/performance comparison, formal-proof certification or authenticated Engine deployment is approved or demonstrated. The reported Engine seed requirement was not independently inspected in this plan-only review; the explicit marker is a transparent compatibility adjustment within the scientific scope.
