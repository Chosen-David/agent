# Independent result review — MATH-63

Verdict: **usable-with-scope** for the frozen finite-label mathematical derivation, eight public development fixtures, and bounded structural retrieval checks. This does not accept model quality, unseen evaluation, token savings, compression speedups, or production integration.

Reviewer: `/root/fano_result_review`, dispatched by `/root` as a distinct result reviewer, after the separate plan review by `/root/fano_plan_review`. The host observes the actual dispatch and returned result; this Markdown and the receipt do not authenticate independence themselves. I did not produce or modify the frozen producer artifacts, TASK, source cards, protocol, or plan.

## Frozen bindings and execution

I read AGENTS, decision-review, project-document, experiment execution, and result-validation requirements, MATH-63, the frozen plan/contract/validation criteria, actual scripts and knowledge implementations, new JSON/Markdown card, corpus prerequisites and mirror, manifest, prior-search decisions, producer raw observations and both regression logs. Prior matching data were not reused for this new acceptance. The six check domains remain those frozen before production.

`_snapshot` independently checked all 254 native path/hash bindings and returned manifest SHA `1b6c96c273e3b2526ff9af0ec4fe22f9f7c8c81694b007f625a76005577f3933`, validation-plan SHA `35cadaff65ece6de2214a01077869d58f9cbf22fcd1f196e09642e7cf722dc3a`. Plan cycle 2 has separate approval; I checked its referenced SHA and stable frozen inputs. Review evidence is confined to `independent_evidence/` and this review/receipt.

I separately executed:

- `python agent_doc/results/math-fano-message-20261009/verify.py agent_doc/results/math-fano-message-20261009/independent_evidence`
- `python agent_doc/results/math-fano-message-20261009/retrieve.py agent_doc/results/math-fano-message-20261009/independent_evidence`
- `python -m unittest tests.test_knowledge tests.test_knowledge_index` (34 tests, OK; own log)
- `PYTHONPATH=. python agent_doc/results/math-fano-message-20261009/independent_evidence/reconstruct.py`

All exited zero. Raw fixture replay is identical except elapsed seconds. Retrieval replay is identical except timing fields. Initial producer schema failure remains intact; the final `requires` uses the actual id/version object schema rather than a string.

## Mathematical and reference checks

The error-indicator entropy derivation is valid for a decoder in the finite label alphabet and logs consistently in bits. Given observation `(T,Z)`, the correct branch determines Y and the wrong branch leaves at most M−1 labels. Conditional independence of randomized decoding from Y is essential; an independent auxiliary random seed preserves conditional Y entropy, while correlated side information must enter Z. The weak bound follows from h₂≤1 and log₂(M−1)≤log₂M; it is a necessary bound and may be vacuous. The M=1 branch avoids zero denominators and M=2 removes the log₂(M−1) term.

For each fixed z, a deterministic C-message decoder outputs at most C labels. Its successful mass is at most the sum of the C largest posterior label probabilities. Randomized encoders/decoders cannot improve the linear success objective over deterministic extreme points; this also follows by expressing a conditionally independent decoder kernel as a mixture. Achievability requires direct label knowledge and sufficient encoding access; the converse remains valid without it. The C(z) extension, finite entropy bound and fixed-length bit/token cardinality bounds are sound. The variable-length example correctly exposes three distinguishable states rather than two.

My reference enumerates **decoder tables**, then maximizes encoder success by reachable labels; it does not call the producer's encoder solver. Entropy is independently calculated as H(Y)−H(T,Z), using deterministic observations, rather than the producer's posterior-entropy loop. This reproduces its deterministic first-optimum tie policy and diagnostic entropies within 1e−12.

| Fixture | Exact optimal success / count | Encoder count | H(Y\|T,Z), bits |
|---|---:|---:|---:|
| F1 | 1/2 | 16 | 1.188721875540867 |
| F2 | 1/4 | 256 | 2.4564355568004035 |
| F3 | 4/5 | 16 | 0.8877840558577584 |
| F4 | 1 | 16 | 0 |
| F5 | 1/2 | 1 | 1 |
| F6 | 3 distinct strings | — | — |
| F7 | 1/2 | 1 | 1 |
| F8 | 1 | 1 | 0 |

F4/F5 independently use labels 1…4 and Z=floor((Y−1)/2); all declared uniform priors and the F3 skew prior are explicit. Fixture IDs are exactly F1…F8 without duplication or omission. The floating entropy checks satisfy sharp Fano; they are sanity checks, not proof of the general theorem. The enumerator intentionally tests these frozen small cases and would require further validation before arbitrary configurations.

## Sources and selective research validity

I inspected the actual Duchi PDF/text title date and §2.3.2 Proposition 2.3.3, eq(2.3.1), printed pp31–32. Its estimator-conditioned Fano statement and error-indicator proof support the classic premise; consistent conversion from its log convention to bits is necessary. I also opened Tse's original Winter 2017 Lecture 10 PDF, Theorem 1 on p10-1, confirming the weaker form. Conditionalization and posterior top-C are the card's explicit derivations, not misattributed quotations.

I opened FOCUS original v1 abstract and HTML §4 and A.2/A.8–A.10. Title, five authors, 2026-09-29 submission timestamp and “Preprint. Under Review” match. The arXiv DOI is 10.48550/arXiv.2609.37590, currently labeled pending registration; no acceptance status was inferred. The card accurately treats citation frequency as an estimator, preserves assumptions about margins, draft–main mismatch and omission losses, and distinguishes metric proxies from total call cost. Default three rollouts and the omitted fifth contact example are supported. No paper experiments were reproduced. Its unqualified global KL claims were not imported.

## Integrity, retrieval, cost, and limitations

All 227 baseline paths, including holdout, match their frozen byte hashes. Holdout was hashed as opaque bytes only, never parsed, printed, or used to revise the entry. Both new mirror files exactly match the source card. The pending acceptance wording is accurate for producer artifacts; published corpus status permits the bounded retrieval test and is not independent result acceptance.

All six frozen query/backend combinations return the new ID in Top3, with complete Fano+DPI prerequisite closure, two entries and 9670 serialized payload characters ≤12000. I inspected search and context logic and actual indexed implementation. The protocol's wrapper name `sqlite-lexical-v1` actually invokes the existing **sqlite-fts5-rrf-v1** backend (document/section BM25 plus curated structural ranking); the nested actual backend is preserved. This metadata shorthand is disclosed and does not change the six reproducible structural observations. Exact public queries intentionally occur in aliases. Hits cannot establish semantic generalization, model premise refusal, or unseen task success. Manual premise decisions remain manual.

Measurement validity is N/A under the preauthorized criterion: no performance/model claim is accepted; seconds are diagnostics, characters are not tokens, and token cost is unmeasured. No GPU/model invocation or production compression changes occurred. General proofs are informal, not Lean-checked; finite tests cannot establish freedom from all bugs. The review validates exact frozen bytes, criterion-specific mathematical reasoning and public structural checks only. Host acceptance still needs the observed independent completion and pinned receipt provider; no callback identity is established by JSON.

Frozen task-detail/index full-byte inputs were checked against `approved_task_detail.md` and `approved_task_index.md`, preserved by the main owner before subsequent reporting edits; all other frozen plan inputs match current bytes. The immutable plan SHA is `2276c0db07451605acdc088aa1e20d63ed4d14896da6438ce7a28cb8ed8f551d`; that is the plan digest quoted by the cycle-2 reviewer, not the review document digest. Unrelated project-wide metadata validation has an existing COMM20-01 identity/date failure, reported by the parent; this review does not certify whole-project metadata or repair that separate task.
