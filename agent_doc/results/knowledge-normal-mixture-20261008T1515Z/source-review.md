# Independent source and plan review

Reviewer: mixture_plan. Accessed: 2026-10-08. Start: `b93e66c6f65cbc3a82c14472b9f657d8a38279d2`.

## Decision

**approve** for one normal-mixture candidate and finite CPU verification within the existing deadline and zero-GPU/paid budget. This is not publication acceptance. The inspected prior Freedman, betting, alpha-spending and vector-concentration cards do not supply this scalar closed-form result with its proposed complete local proof. Public holdout metadata was read; no reserved paper or answers were accessed. GUIDE.md was empty. Repository decision/project/knowledge instructions and prior Freedman outcome were read.

## Primary evidence

Actually read [fixed PDF v9](https://arxiv.org/pdf/1810.08240v9), §3.2 Lemma 2/equation (14), PDF pp.8–9, and Appendix A.3 Lemma 2 proof/Proposition 5 equation (51), pp.26–27. The [abstract page](https://arxiv.org/abs/1810.08240v9) confirms 2022-08-06 revision date. The stated boundary agrees with the l0=1 specialization. The proposed all-real-lambda conditional MGF assumption is sufficient and stronger than the paper's general process-level formulation. The PDF explicitly discusses measurability for the mixture construction. Proposition 5 does not itself give a separate full Gaussian-square-completion proof; that expansion must be labeled the card's derivation.

License: parent reports the HTML page explicitly declares arXiv perpetual non-exclusive distribution license. My license-link call failed; license terms were not independently retrieved. Direct urllib retrieval returned HTTP tunnel 403. No PDF byte hash, journal-byte identity, software license or source-code reuse was certified. No upstream text/code vendoring is planned.

## Required proof and scope

Use `requires=[]` with a self-contained finite-truncation Ville proof; betting may be related navigation. For fixed lambda, prove the exponential process is a nonnegative supermartingale; use joint measurability and nonnegative Tonelli to mix, establish expectation at most one, complete the Gaussian square, and invert the threshold. All-real-lambda control supplies both tails without an extra delta/2. Each finite-time V is finite and nonnegative; rho is fixed positive, delta in (0,1). State that conditional variance and sample variance are not automatically valid proxies, and data-selected rho is not covered. V=0 is permitted. Prefer log M computation and high-precision checks near crossing thresholds.

The proof is mathematical review, not formal verification. Finite CPU cases do not certify infinite-horizon coverage, model improvement, sample efficiency or eventual stopping. Keep retrieval baselines and failures and apply the independent code/data gates before publication.

## Suggested locally derived negative checks

- D=99 with probability .01 and -1 otherwise has mean zero and variance99; at lambda=.1 its MGF is about200, greater than exp(.495). True variance need not be a valid sub-Gaussian proxy.
- One fair ±1 observation with empirical variance set to0, rho=.01 and delta=.05 gives boundary about .2448 and false crossing probability1.
- Reusing one fair sign for every D_t gives marginal sub-Gaussianity but violates conditional MGF after the first observation. With wrongly assumed V_t=t, rho=1, delta=.05, t=100 has |S_t|=100 versus boundary about32.73 on every path.

These are proposed analytic checks, not claims of executed experiments. Candidate scientific review remains pending.

## Candidate science and development evidence review

Read candidate JSON/body and the full verify.py plus checks.json. Main proof, all-real-lambda assumptions, predictable proxy, Gaussian integration, finite-stop Ville argument, inversion, units and negative examples are sound. One minor wording correction is required: finite random q does not imply unconditional L1 integrability of D, so the unqualified claim “蕴含条件零均值” should be deleted or explicitly localized. This does not invalidate the main theorem or require narrowing its hypotheses.

Independently executed verify.py through runpy, intercepting Path.write_text in memory so the original output was not overwritten. All 14 result records and source SHA matched checks.json exactly. Independently recomputed all 256 iid-walk boundaries at 80 decimal digits; every float boundary differs by less than 1e-12 and the minimum integer-lattice gap is 0.001728495163294502266246229742728581295515636872900583274192166163274564744213. Thus the recorded exact integer path classification is supported; the finite-horizon crossing probability is 0.018629229197864933. The predictable-amplitude tree uses past S to choose amplitude and exact rational masses. Quadrature is a numerical consistency check with a tail bound, not a formal integration-error certificate. Invalid-domain checks cover their six listed inputs, not every possible numeric overflow.

Verdict at this snapshot: revise-minor-wording. Source review and plan approval remain valid. Independent frozen cases were not opened. No unseen-test, production, formal-proof or publication claim is made.

## Final scientific acceptance after wording repair

Actually reread the corrected candidate: the unqualified conditional-zero-mean claim is removed and classical L1 integrability is explicitly separated from the nonnegative exponential proof. Verified verify.py hash is unchanged. Final verdict: **usable-with-scope**; `proof=derivation-reviewed` is warranted for this stated scalar theorem and complete local argument. Prior wording issue and its review are retained above. This does not approve retrieval, independent frozen-case, synchronization, publication or CI gates; those retain their own reviewers and evidence. Final body SHA256: `094932212ab677067d2343c9f5b4c9757bbbb913dc8b82133fa28ca167d6ed30`.
