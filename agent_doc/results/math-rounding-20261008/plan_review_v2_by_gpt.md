# MATH-47 independent plan review v2

Verdict: **approve** for the bounded knowledge-only plan. R1 is closed and no blocking findings remain. The approval concerns mathematical planning and public validation/retrieval acceptance; it is not a result acceptance, publication permission or authenticated Engine receipt.

The same actual separate reviewer context `/root/rounding_plan_review` read the revised complete plan, retrieval and validation protocols, and checked every DAG change against previously reviewed v1. The historical revise feedback in plan_review.json and plan_review_by_gpt.md remains unchanged. Root retained the original plan/DAG/validation byte snapshots before revision.

## Exact reviewed objects

- plan.json SHA-256: e706278f81594157d594b86ff371f73219ce1903483c6553d9c3b65705fec4fc
- dag.json SHA-256: 165adc5b895ed4da23239be3dc98b8899ff250dee44273f92ab5502b87f6d169
- validation_plan.json SHA-256: 4acb06900eb01f218b342a77cd6a1121c4d8685de1ac46f36912e25dafa615e1
- retrieval_protocol.json SHA-256: b39d453836e41fc9485c3106e18dfb6fcd39c94aad8b567814f809e7e00aa9ae

All ten plan and DAG evidence refs match actual bytes. The three produce/verify/publish result contracts are identical and point to the revised validation hash. The DAG changes are confined to that hash and the added frozen retrieval evidence; authorization, scope, dependencies and budgets remain as previously reviewed.

## Seven review domains

- **intent: pass** — MATH-47 stays within bounded reusable numerical knowledge and public CPU validation. It preserves the stored-input target and excludes production, SGLang, GPU, remote jobs and model improvement claims.
- **guide: pass** — GUIDE.md is empty; README explicitly describes its AI-origin directory explanation and does not supply human requirements. Both guide files were read without modification; all nine frozen evidence hashes match. Relevant advice is proposal material, not authorization.
- **assumptions: pass** — Correct RN binary64 primitives, gradual underflow, finite adjacent endpoints and no arithmetic reassociation/FTZ support the adjacent-float enclosure and interval induction. Unknown premises/range errors fail closed. gamma_2n is only a secondary no-range-error model crosscheck, not a replacement for the enclosure.
- **prior_results: pass** — Actual prior search candidates and missing-record errors are retained. The screening card explicitly assumes real arithmetic and marks former float checks as diagnostics, so rejecting those as enclosure evidence and running new exact-oracle checks is appropriate. No old measurement is accepted as current data.
- **acceptance: pass** — The six criteria and identical producer/verify/publish contracts are preserved. retrieval_protocol.json now freezes three exact theorem-name-free queries, numerical-analysis domains, required card ID in top3, both file/SQLite backends, public-development status and bounded context behavior. Independent result acceptance can rerun every required case.
- **risk: pass** — Reversible knowledge-only outputs, strict U_i<kth-largest L rejection, exact target and explicit tie policy keep the risk bounded. Independent result review precedes publication. Git publication still requires existing user/tool authorization and remote refresh; this review does not grant it.
- **resources: pass** — Local standard-library binary64/Fraction work and file/SQLite retrieval are feasible within the declared 2400-second total and CPU budgets. This reviewer ran only lightweight reads/hash checks and a knowledge CLI, well below its 120-second CPU-check ceiling. No model/GPU/API or deployed supervisor capability is assumed.

## R1 closure

retrieval_protocol.json freezes three exact public queries before any card/index/validation implementation changes: arithmetic absorption/ranking, electrical conductance-voltage linear quantities, and uncertified quantization/original-input error. Each uses the numerical-analysis domain and requires math.floating-dot-enclosure within top3 on both files-lexical-v1 and sqlite-fts5-rrf-v1. Its acceptance requires every case and preserves the separate premise-checking gate, with no model/scientific validity inferred from retrieval. It labels the cases public development and records a 12000-character context budget and partial/skipped inspection.

The protocol's actual hash is bound in both plan and DAG. The revised validation predicate requires all frozen cases on both backends. These changes make the required retrieval acceptance operational and close the sole v1 blocking finding. The independent result reviewer must still rerun the fixed cases, verify domain membership and ranks, preserve all failures and check the exact arithmetic/proof/data; current approval does not prejudge their results.

## Mathematical observations for implementation/result review

For a finite correctly RN-rounded primitive value, immediate predecessor/successor surround its exact value under the stated arithmetic premises. Interval addition is monotone and multiplication extrema occur at the four corners; applying an outward step to each computed extremum gives inductive containment. Exact Fraction comparisons should check endpoint inequalities directly, rather than round the oracle back to float or use tolerance.

Fail closed when a primitive or outward endpoint is nonfinite, including max-finite adjacency and overflow-before-cancellation. Gradual underflow allows zero/subnormal enclosures; tests do not constitute a universal runtime certificate. A secondary gamma_2n bound must explicitly require 2*n*u<1 and the no-range-error relative model, and should not be attributed as the exact bound printed in Higham's exposition, which uses gamma_n. These are details already covered by the plan's declared conservative crosscheck and mathematical result-review gate, rather than a demand to replace the primary interval method.

The strict deletion rule preserves all tie candidates at the threshold. A validated component box can widen a stored-input dot enclosure, but empirical error estimates, quantized-input resemblance and accurate residues do not certify that box. Sensor mapping must specify coefficient/measurement units and the target linear quantity. Terminal one-ulp inflation needs an explicit lost-intermediate-error counterexample, as planned.

## Actual independent source and knowledge use

Opened Higham's author page and checked conventional-product equation (1), gamma_n definition and componentwise versus normwise discussion. Did not read the whole textbook. Opened official Python math documentation and read nextafter/ulp direction and special/subnormal semantics. Documentation observed as 3.14.8; local recorded interpreter is 3.12.14, and docs alone do not prove local rounding conditions.

Opened arXiv metadata for Accurate Residues for Floating-Point Debugging and checked v2 submission history (September 1, 2026). Read Section 3.3 and neighboring error-propagation paragraphs in v2 HTML. This is a preprint; no final venue was verified. Its explicit exclusion of overflow/underflow supports the plan's refusal to treat debugger residue estimates as enclosure certification. No benchmark gains were transferred. The second recent candidate 2609.37844 was not independently read; its producer-recorded unavailable full text remains excluded.

Sources: https://nhigham.com/2022/09/13/what-is-fast-matrix-multiplication/ ; https://docs.python.org/3/library/math.html ; https://arxiv.org/abs/2604.06258 ; https://arxiv.org/html/2604.06258v2 .

Executed `python -m agent_runtime.knowledge --root knowledge search '浮点 点积 舍入 区间 筛除' --limit 3` in the actual repository. Snapshot bf56958a2aca7e0eb9743c01e0517a624fdd40afc393e69112acdbdcd594f356; files-lexical-v1. The relevant hit was math.residual-interval-screening@1, hash 8d775ddac76af9c7d192d55a3d240e26a863873c3a072223b6222dc27caa0129. Read its pinned full content; its explicit real-arithmetic assumption and tolerance-based float-diagnostic limitation support the decision to run new tests. Other broad interval hits were irrelevant data structures, illustrating why domain-filtered checks need a frozen protocol. No prior experimental dataset was reused.

## Limits and next owner

No validation implementation or raw outcome was reviewed or accepted. Lightweight source/hash/knowledge reads remain below the 120-second reviewer CPU ceiling. No GPU/model/remote job, formal proof, production edit, publication or deployment occurred. The full original user conversation was unavailable; intent/authorization assessment uses the explicit bounded handoff and canonical MATH-47 requirements. Token/cost and host authentication interfaces remain unavailable.

Root may progress within its existing authorized bounded local scope. Independent result verification is required before conclusions/publication. Any Engine/managed dispatch requires the real trusted host authentication gate; this document and JSON are documentary review evidence and cannot substitute for it. Material changes to these reviewed files/premises require versioned reconciliation.
