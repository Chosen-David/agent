# MATH-47 independent plan review

Verdict: **revise**. The bounded outward-enclosure method and independent result-review ordering are reasonable. One blocking acceptance issue remains: freeze the required retrieval cases and success predicate before editing the knowledge card/index.

This is the actual separate reviewer task context `/root/rounding_plan_review`, reviewing the complete files named below. It is documentary feedback, not an authenticated ReviewSession/Engine receipt, a permission grant, an installed supervisor, or scientific result acceptance. Root remains the producer and sole TASK author. The reviewer wrote only these two feedback files.

## Exact reviewed objects

- plan.json SHA-256: b5060645e8697bf3731b386bc47ac4306f2acc64f57087c2279242153fa22ddf
- dag.json SHA-256: b1ed549532b42f0de184b68e5fa8b5d2d9e693e09a70b12608677c84d11b03e8
- validation_plan.json SHA-256: c0bb23acfd6bd0d405c05a081fc23cd0800800c30d446ee3c57ffb6f00babedc

All nine evidence_refs in the plan matched their actual bytes at review. The validation protocol hash matches the three identical produce/verify/publish contracts. Read AGENTS.md, decision-review/project-document/dual-main/knowledge-access/result-reuse/result-validation guidance, review-main prompt, canonical MATH-47 detail and index entry, both guide files, both relevant advice records, source/prior/environment records and pinned screening card. Advice remains advice; the empty GUIDE.md imposes no invented project requirement.

## Seven review domains

- **intent: pass** — MATH-47 stays within bounded reusable numerical knowledge and public CPU validation. It preserves the stored-input target and excludes production, SGLang, GPU, remote jobs and model improvement claims.
- **guide: pass** — GUIDE.md is empty; README explicitly describes its AI-origin directory explanation and does not supply human requirements. Both guide files were read without modification; all nine frozen evidence hashes match. Relevant advice is proposal material, not authorization.
- **assumptions: pass** — Correct RN binary64 primitives, gradual underflow, finite adjacent endpoints and no arithmetic reassociation/FTZ support the adjacent-float enclosure and interval induction. Unknown premises/range errors fail closed. gamma_2n is only a secondary no-range-error model crosscheck, not a replacement for the enclosure.
- **prior_results: pass** — Actual prior search candidates and missing-record errors are retained. The screening card explicitly assumes real arithmetic and marks former float checks as diagnostics, so rejecting those as enclosure evidence and running new exact-oracle checks is appropriate. No old measurement is accepted as current data.
- **acceptance: fail** — The six mathematical/code/data criteria are appropriate and the identical result contract appears on produce/verify/publish, but required domain-filtered file/SQLite retrieval has no frozen queries, domains, expected IDs, rank cutoff or pass predicate. Success can currently be chosen after seeing results.
- **risk: pass** — Reversible knowledge-only outputs, strict U_i<kth-largest L rejection, exact target and explicit tie policy keep the risk bounded. Independent result review precedes publication. Git publication still requires existing user/tool authorization and remote refresh; this review does not grant it.
- **resources: pass** — Local standard-library binary64/Fraction work and file/SQLite retrieval are feasible within the declared 2400-second total and CPU budgets. This reviewer ran only lightweight reads/hash checks and a knowledge CLI, well below its 120-second CPU-check ceiling. No model/GPU/API or deployed supervisor capability is assumed.

## Blocking finding R1

Target: plan.json acceptance and validation_plan.json reproducibility, with no separate frozen retrieval protocol.

The plan requires theorem-name-free domain-filtered file/SQLite retrieval, but provides no fixed query strings, domain filters, required IDs/rank cutoff or exact success predicate. A query selected after observing successful retrieval could satisfy the current prose. This prevents independently operational acceptance of that required part of MATH-47.

Minimal fix: before changing the card/index, freeze a public retrieval protocol with query text, domains, expected IDs and maximum ranks, both backends and an all-required-cases predicate. Bind its actual hash to the revised plan/evidence and validation protocol. Keep existing holdouts unchanged and call the new queries public development cases. Re-review the revised complete objects; later independent result acceptance must rerun every frozen case and retain failed evidence. This does not require a different topic, production implementation, model call or larger budget.

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

No arithmetic implementation or raw result exists yet, so no result is accepted. Reviewer checks were only source reads, lightweight hashes and the knowledge CLI, below the 120-second CPU ceiling. No GPU/model/remote job, formal proof, production change, publication or deployment was performed. Full original user conversation was absent; intent was assessed against the explicit bounded handoff and canonical MATH-47 requirements. Token/cost and host authentication are unavailable; this document does not assert either.

Root owns the minimal protocol fix and versioned reconciliation. Once R1 is closed, this reviewer can assess the revised complete plan within the same separate reviewer context. Engine or managed dispatch remains subject to a real authenticated host receipt; this written review cannot manufacture one. Independent result verification remains mandatory before knowledge conclusions/publication.
