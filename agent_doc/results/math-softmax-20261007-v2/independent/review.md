# Independent review — math-softmax-20261007-v2

Verifier: `/root/independent_math_verifier`, a separately delegated collaboration agent. Producer: `/root`. The main host must authenticate the actual delegation/completion events; this file does not self-authorize a runtime provider.

## Scope and findings

Read the frozen card, metadata, validation plan, script, configuration, manifest, raw data, summary and failure-v1 record. The finite mathematical derivation is sound under its stated premises:

- The signed probability difference has equal positive/negative mass; the two convex barycenters are at most the transformed value diameter apart. Thus the norm error is at most D TV, for any norm and fixed linear W.
- For exp(logit error) in [m,M], the secant bound for absolute deviation gives TV ≤ (M−μ)(μ−m)/((M−m)μ). Minimizing μ+mM/μ at sqrt(mM) yields tanh(osc(error)/4). The m=M case and common shifts are handled separately. Two-point probability tilting attains the bound.
- Conditional normalization gives TV=1−p_S and the exact pruning identity; decomposing original → exact restricted → approximate-logit restricted → approximate-value restricted yields the three-term bound. Adaptive choice of S does not invalidate this pointwise statement. Exact final logits/values remove the latter two terms.
- Rank/overlap or attention mass alone does not determine a value-weighted output. The scalar cancellation fixture is correct; it is not evidence for downstream task accuracy. Nonfinite masks, negative weights and changing values require separate premises or decomposition.

Script inspection: float64 stable softmax subtracts max; random sizes and projection orientation are consistent, subset pairwise distances broadcast correctly, scalar norms/TV values are finite, and singleton/full-set cases are included by the generator. No production code, model or accelerator is measured. The helper is a finite fixture implementation, not a robust universal API: arbitrary finite logits may underflow some probabilities to zero, hence arbitrary extremely unlikely subsets could produce p_S=0 in floating arithmetic; such cases are not covered by these random fixtures. The mathematical statement uses exact positive finite-softmax probabilities and remains valid. The card warns about underflow/overflow and does not claim a production implementation.

## Independent observations

Executed `python doc/results/math-softmax-20261007-v2/verify.py doc/results/math-softmax-20261007-v2/independent`: 416 / 416 pass. All 416 numerical records and frozen config exactly equal the producer records, including IDs, bounds, equality flags and pass flags. Timing differs as expected and is only a verification duration.

Added `independent/reference.py`, using 90-digit Decimal direct probability normalization, independently of the shared NumPy softmax path: 7 sharp two-token cases (w=0,1e−8,.1,2,10,40,800), 4 exact Decimal subset normalization/pruning identities, and one all-record comparison. 12 / 12 checks pass. This supplements, rather than merely copies, the rerun reference.

Manifest/config/source/card/raw/output/environment and plan hashes are read and checked through `_snapshot`; review JSON binds the exact complete snapshot. 416 raw IDs are unique; counts and summary/metrics agree. Failure-v1 documents an incorrectly requested equality in an otherwise valid upper-bound fixture; v2 changes the force logits to the actual sharp construction. The failure record is retained, not reclassified as successful or silently removed. It records the earlier failure rather than a complete historical raw v1 execution; this review does not certify that prior failed run's full data.

## Source spot checks

On 2026-10-07 independently opened primary sources. Author textbook PDF `https://darkwing.uoregon.edu/~dlevin/MARKOV/mcmt2e.pdf`, Proposition 4.2 and Remark 4.3, PDF pages 63–64 / printed 48–49, confirms the TV identity; it does not establish the attention-specific tanh derivation. OVAL `https://arxiv.org/html/2610.06686v1`, Appendix A.2 Proposition A.4, states a value-diameter times infinity-norm logit perturbation bound, matching the card's separate attribution. MC-Sparse `https://arxiv.org/html/2610.06801v1`, §4.2 Eq.(1), defines an oracle maximizing cumulative dense-attention mass; §4.3 addresses discarded tail error with diffusion-step residual reuse. The card limits these to research screening and does not assert local reproduction or a transfer to autoregressive inference.

## Verdict and limits

All six required check domains pass for the frozen **finite CPU float64 development-data scope**. This is independent code/data and natural-language proof review, not Lean/formal verification, model A/B, GPU performance validation, unseen-model acceptance or a guarantee beyond the checked fixture range. No theorem novelty, FASA improvement, token saving, speedup or end-to-end accuracy result is established. The wider host retrieves/dispatches knowledge separately; retrieval structure tests, if any, are outside this numerical manifest and need their own reporting.
