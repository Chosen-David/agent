# Independent result review v2

Status: **usable-with-scope**. Actor `/root/conditioning_result_verifier`; stable review run `math-conditioning-independent-20261008_v2`. This is direct host independent review, not an authenticated Engine deployment.

Manifest SHA256: `e634acbe9b29cc364d47234cef09412e7155c393056d19ee118b75c3092d8a43`. Reviewed plan SHA256: `c6acb5c22856bdc92cd63ab4df25a51244ba7a9dfa0cb0d69c75085182a41c1a`. Full actual artifact/check evidence bindings are in the paired JSON.

1731 complete raw records match the lossless gzip, producer JSON and separate independent rerun. Counts: 1113 exact TV, 462 zero-event refusals, 21 projection minima, 99 KL decompositions, 18 forward-KL infinities, and 18 targeted extras. Independent overlap-TV checks all valid grid cases and 4294 extra sum-six cases; Decimal80 KL/normalizer reference has maximum binary64 absolute difference 5.551115123125783e-17. Producer maximum recorded error is 2.220446049250313e-16, below 1e-12.

Proof review: for a>=b the triangle inequality gives conditional L1 <= (A+a-b)/a, while complement L1 >=a-b, yielding TV<=delta/a; symmetry gives the max(a,b) denominator. Both masses must be positive. KL(q||P) decomposes with -log(a) on q supported in S and q absolutely continuous to P; Gibbs equality yields the unique minimum. If a<1, forward KL(P||P^S) is infinite. Positive q on zero P gives extended infinity, never an infinity subtraction. The family (a*c,(1-a)*d) has identical conditional c and different mass a, proving nonidentifiability. Partitioned LSE yields sigmoid(u-v); certified omitted-score upper bounds give the optional mass lower bound only with complete legal coverage. These are independently reviewed finite derivations, not Lean proofs.

Primary URLs and stated locators were actually retrieved/read; source decisions are saved in independent_results_sources.json. MOIRA estimates are not certified bounds; MassAlloc discovers all legal QK scores and post-score matching is not full cost matching. No paper performance or model-quality claim is locally reproduced.

All active v2 manifest artifact and plan SHA256 bindings checked before/after; gzip is complete lossless JSON, identical to uncompressed producer and independent rerun. Exactly1731 records with summary counts, maximum and finite metric units reconciled.

Knowledge validate and candidate pinned show pass using canonical JSON-entry hash, distinct from Markdown artifact hash. Published-only check-refs correctly refuses candidate consumption; later publication/retrieval validation belongs to the integration stage. Retrieval bytes/token estimates and hit rates are not yet measured here. Timing covers one CPU arithmetic loop only.

Limitations: no formal proof, model/GPU A/B, unseen model tests, or claimed model-quality improvement. Helpers assume the frozen matching finite shapes and logits; zip length validation, nonfinite-logit API behavior and production integration are outside the accepted harness scope. Earlier revision1 plan rejection and v1 raw evidence are preserved.
