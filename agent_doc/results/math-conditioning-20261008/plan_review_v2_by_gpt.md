# Independent conditioning plan review, revision 2

Verdict: **approve scoped CPU production**.

Reviewed the revised assigned validation plan and DAG against the previously read repository instructions and result-validation workflow. No producer tests were run. This review authorizes neither result acceptance nor an authenticated Engine deployment; publication remains dependent on independent result validation.

Reviewed input SHA256:

- `validation_plan.json`: `a9a29eda11d1b80562e7f7ac31cf51fe21e5a81c262f44dfe7e0fefe83f2a87f`
- `task-dag.json`: `f9ee7fdf4fb116d4cf6c016c69cc1baa1bac0f28812d44eebadc15da46690d79`

The three prior blocking gaps are resolved sufficiently for bounded production:

1. The producer explicitly produces experiment data; the independent verifier has the required action and a distinct actor; publication depends on that verifier. Producer, verifier and consumer share the identical frozen result contract, whose validation-plan SHA256 matches the actual reviewed bytes.
2. The plan fixes a three-point sum-four simplex grid, all nonempty events, exact Fraction acceptance, invalid-input refusals, extended-value KL handling, numerical tolerance with its binary64 rationale, and targeted boundary/counterexample cases. It requires explicit equation proofs and independent arithmetic review. Zero-event handling is a refusal rather than a fabricated conditional distribution.
3. The plan requires complete case records and counts, code/input/configuration/raw-data/output/environment/plan manifest bindings, deterministic independent rerun, pinned primary source versions/locators, and recorded adoption/defer decisions. Elapsed seconds are metadata, and the retrieval-token quantity is explicitly a byte-based estimate.

## Production and acceptance boundaries

The card and independent result review must retain the dispatched claim assumptions: finite distributions; q supported on S and P(S)>0 for KL(q||P)=KL(q||P(.|S))-log P(S), with extended-value infinity handled explicitly; both event masses positive for conditional TV <= min(1,TV(P,Q)/max(P(S),Q(S))); and equal normalized candidate far fractions can coexist with different global far masses. These are scientific proof obligations, not consequences of a successful finite grid.

The producer must record exact values for targeted extras in the frozen input/configuration artifacts and preserve all failures. Source URLs/bytes or hashes and locators must be verified during source screening; listing them here is not evidence that their contents were checked. Missing source evidence blocks dependent literature conclusions. Independent acceptance must inspect actual code/imports, raw records, finite metric units, environment and all six checks, then bind reviewed artifact bytes. A producer pass summary alone is insufficient.

Approved scope: one finite conditioning topic, CPU arithmetic/development checks and bounded file-based primary-source screening, at most the two specified recent research papers plus the stated foundational references. No SGLang modification, model A/B, GPU/performance comparison, held-out model test, universal correctness certification, or authenticated Engine deployment is approved or demonstrated. Any eventual acceptance is `usable-with-scope` only and must preserve these limitations.
