# Independent normal-mixture review

Reviewer: `/root/mixture_unseen`, separately dispatched by parent `/root`.

## Pre-candidate freeze

- Cases SHA256: `6120eb62238f9f66f42d25dd2e6ec8e5e8fbdbeee470c641fd80a681724f3613`.
- Verifier SHA256: `c9a9956f35f5029a80738d4d042a195d327d279c476da5ade71ec0d8f1b38205`.
- Start commit: `b93e66c6f65cbc3a82c14472b9f657d8a38279d2`.
- Parent confirmed fetch + fast-forward before edits. Guide was empty; AGENTS, decision review, schema FORMAT, knowledge access, project document and result validation instructions read.
- Only public holdout metadata read. Reserved benchmark answers, unpublished scientific drafts and historical independent verifier code were not read or executed.
- Prior Freedman result metadata and published Freedman/betting/alpha-spending cards were inspected for applicability only. Their historical pass labels are not reused as acceptance for this theorem.
- Nine independently specified scientific cases and six fresh bilingual lexical queries are frozen in `independent_cases.json` before seeing the candidate. Their details were withheld from the author.
- Execution pending candidate-ready notice. Machine checks cannot substitute for semantic scientific review. These checks do not measure an LLM's application success, empirical power, infinite-horizon simulation coverage, or formal proof.

## Isolated-corpus run 1

Parent requested testing `/tmp/knowledge-normal-mixture-1515/published-corpus` before canonical promotion. The sole verifier revision adds `--root`; original complete source and its frozen digest are preserved in `independent_results.json.verifier_revisions`. Frozen cases, six queries, and thresholds are unchanged. The isolated root marks the candidate published for ordinary retrieval/ref validation, with proof still `not-checked`; that is a staging state, not canonical publication.

Command: `python agent_doc/results/knowledge-normal-mixture-20261008T1515Z/independent_verify.py --root /tmp/knowledge-normal-mixture-1515/published-corpus`.

All nine machine checks passed. All six fresh queries return the target in top five (ranks 1, 2, 1, 1, 1, 2). Independent Simpson integration differs from closed form by at most 2.23e-16 relative error. An exact 14-step adaptive Rademacher tree has crossing probability 0.02630615234375 against delta=0.2; this finite sanity check is not an infinite-time proof. The independent rare-spike example refutes use of variance as the subGaussian proxy. Full raw values and returned rankings remain in the result file.

All nine scientific cases passed manual review against the complete candidate. Gaussian predictable-scale observations, adaptive bounded noise, zero proxy, unit changes, and stopping events are handled consistently; marginal-only guarantees, variance-only proxies, post hoc rho tuning and restricted-lambda assumptions must be rejected. Case-by-case findings are in `manual_scientific_review`.

The fixed-lambda exponential process, nonnegative conditional Tonelli step, square completion, finite stopped-process expectation, and increasing-event limit establish the stated two-sided bound. `requires=[]` is scientifically defensible because the proof is self-contained. The old Freedman, betting and alpha-spending cards are correctly navigation-only. A nonexistent strong dependency cannot be omitted for a meaningful negative test; this specific case is N/A, while the real stale-digest rejection passed.

Independently checked [Howard et al., fixed arXiv v9](https://arxiv.org/html/1810.08240v9), Section 3.2 equation (14) and Appendix A.3 Proposition 5 equation (51), on 2026-10-08. Setting the initial constant to one gives the card's formula and two-sided probability statement.

Verdict: **usable-with-scope for candidate scientific content and frozen independent checks**. No scientific blocker found. Canonical promotion, final verification metadata, corpus synchronization and final refs remain parent-owned and require final readback. This is neither formal verification nor empirical model/sensor validation.

## Isolated-corpus run 2: integrability clarification

A separate scientific reviewer identified that a finite random proxy need not imply unconditional L1 integrability. Parent removed the original unqualified conditional-zero-mean statement and explicitly requires checking integrability when a classical L1 conditional mean is needed. Run 1 is preserved as the actual earlier review; its lack of an integrability finding must not be represented as having found that issue.

I read the exact body diff and reran the unchanged frozen checks. The nonnegative exponential-process argument does not require unconditional E|D| to be finite, so the clarification is correct and the theorem remains valid. All nine checks and all six retrieval queries pass again. Scientific cases were rechecked against the change. Run 2 isolated candidate ref: `math.normal-mixture-boundary` v1, SHA256 `9de2108490547d0c90e3eede3076f2647f127395aa6b526a6cf8e5589356c6e1`.

Verdict remains **usable-with-scope**, subject to canonical final readback. Original verifier source is preserved in results; current root-selectable verifier SHA256 is `00c91ef1fe8d875b863ba449630cd067fc94c64a25863c3b5ade76aebbb6d53a`.

## Canonical run 3: final refs and applicability

Command: `python agent_doc/results/knowledge-normal-mixture-20261008T1515Z/independent_verify.py --root knowledge`.

The scientific body is byte-for-byte identical to isolated run 2. Canonical status is `published`, proof metadata is `derivation-reviewed`, and the frozen case-file digest is unchanged. All nine machine checks pass again; all six bilingual queries still retrieve the target in top five. The unchanged scientific body retains the run-2 applicability acceptance. Earlier runs and original verifier source remain preserved.

Final knowledge ref: `math.normal-mixture-boundary` v1 SHA256 `918e3c4c11706109d08a36c4bedec42ed25774285aa0a7db19f76078d25d730e`.

Canonical snapshot: `d43e482d0207eb792941eb07c8b39203d6de93fcc049f8c36e74a26a2f97073f`.

Final scoped verdict: **usable-with-scope** for the frozen nine scientific scenarios, six fresh lexical queries, reference closure, negative stale-digest check and independent numerical sanity tests. No remaining blocker in this delegated scope. This does not certify all corpus regressions, remote publication, an LLM application benchmark, production sensor assumptions, or a formal proof; those claims are not made here.
