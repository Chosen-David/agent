# Independent plan review — MATH-48, cycle 3

Verdict: **approve** final version 3 for the bounded second producer attempt. Exact reviewed plan SHA is `d46fa083bebf9995a20e4be166908a24611d88029fa3d02380bc788879ca9450`; DAG SHA is `8ce3f2cb64bced995e44af621a6e92f50946f42ab316252d827885ba6d03082b`.

## Repair assessment

I read the actual independent boundary failure note and raw extreme-input observations. Finite scales/H returned Inf/NaN intermediate, SVD, lift or tail values; finite tiny-scale results also showed loss of relative accuracy. Adding explicit rejection guards for nonfinite reciprocal/intermediate/SVD/output/tail values and decomposition failure addresses the numerical-interface blocker while preserving the mathematical objective. Finite output must remain expressly separated from an accuracy guarantee. Rescaling or higher precision is a future option, not a performed remedy or newly accepted domain.

The current plan keeps the same exact PSD-support theorem, proof constraints, six-domain acceptance hash, total wall budget, test caps and zero model/GPU experiments. It uses the second existing producer attempt, not a reset budget. All producer/verifier/publication result contracts and DAG run ID now consistently use `math-singular-bilinear-20261008-v2`, with its own native result directory and v2 manifest/validation-plan paths. The original and v2 plan/DAG copies are byte-identical, and the v2 validation plan retains the original criteria hash. Stage predicates remain causal and independent acceptance still precedes publication.

The original failed code and manifest match the hashes cited by the independent boundary reviewer. Original raw/manifest/code/report/card/retrieval evidence is retained under `failed_numerical_v1`; it is historical rejected evidence, not accepted v2 data. Prior v1 and v2 plan reviews remain preserved. During this revision I found stale coverage/learning-state references in the first proposed v3 bytes. Planner fixed them and bound the actual boundary failure and preserved-code/raw/manifest evidence before this final verdict. Every final evidence reference was recomputed and matched.

## Seven checks

- intent: pass — bounded numerical-interface repair leaves the knowledge/theorem goal unchanged.
- guide: pass — protected empty GUIDE and README remain unchanged and correctly bound.
- assumptions: pass — exact independence/support/rank assumptions remain fixed; finite output is no uniform numerical-accuracy certificate.
- prior_results: pass — historical failure is preserved and its observations do not become accepted evidence.
- acceptance: pass — same frozen six-domain protocol; matching unique v2 contracts and fresh independent acceptance required.
- risk: pass — no theorem/production/SGLang/guide changes or overwritten historical failure are approved.
- resources: pass — second attempt and bounded revision continue the existing contexts and cumulative budgets without new dependency/model/GPU scope.

Rank selection in the 48-case noncoordinate float fixture must be decoupled from support dimension. Replacing r=case%5 with r=(case//6)%5 strengthens the originally required truncation/tail coverage; retain 48 cases and the original tolerance, and require actual positive-tail examples at the independent result gate. I do not accept earlier full-effective-rank cases as evidence of positive truncation tails.

## Required result gate and limits

The actual result reviewer must inspect repaired guards and explicit error semantics, check the independently observed finite extreme cases, run affected and unchanged accepted-range fixtures, and bind repaired executed code, raw outputs, card and manifest. No old result acceptance can stand in for this new gate. This plan reviewer did not independently rerun the numerical cases; I read their actual preserved observations and checked their bindings.

Earlier fixed-Cr minimum norm and stage-predicate findings remain closed. For each supported truncated Cr, M0=L+CrR+ is the unique minimum-Frobenius-norm lift; invisible additions must also preserve rank≤r. Tied optimal Cr are not globally minimum-norm equivalent. Probability/PSD-support arguments remain project derivations grounded in classical SVD and Moore–Penrose definitions; the IO-SVD damped moment-decoupled local-KL surrogate remains a reference distinction, and inaccessible 2609.15838 remains excluded.

This is same-context bounded review in the actual independent host collaboration task, with full previous receipts linked. It does not establish an Engine/ReviewSession or remote supervisor deployment, accept repaired v2 experiments, grant new budget, or support model/GPU/e2e/token/performance claims.
