# Independent MATH-65 plan review — cycle 1

Decision: **revise**. One blocking finding (B1). This is a substantive plan review of the frozen files below, not a trusted ReviewSession receipt, host authentication, execution authorization, deployed supervisor, or result acceptance. No producer experiment or production data was run by this reviewer.

Reviewed plan SHA-256: `2dd42de19e6cc498f9f12dd67390f6005224cecf8f2eeb3468b59d2586047476`.

## Reviewed evidence

Read AGENTS.md, prompts/decision_review.md, workflows/project_document_workflow.md, workflows/dual_main_workflow.md, workflows/result_validation_workflow.md; TASK entry MATH-65, full MATH-65 detail; plan.json, fixtures.json, validation_plan.json, retrieval_protocol.json, prior_search.json, prior_knowledge.json, prior_decisions.json and preservation_baseline.json. Independently recalculated all nine frozen-input hashes: all match the exact plan. Read the two mathematical prerequisite cards in their Markdown form. GUIDE.md exists but is empty; guide/README.md is administrative guidance and explicitly says it does not establish GUIDE content or ongoing AI write authority. No guide files were changed. Prior search is partial and contains missing-record errors, which prevents treating it as exhaustive novelty evidence; the prior_decisions scope correctly limits it to a bounded search and mathematical prerequisites.

## Seven dimensions

| Dimension | Verdict | Reason |
| --- | --- | --- |
| intent | pass | Bounded mathematical knowledge extension addresses the approximate-marginal gap in the existing feasible-coupling card; no model, GPU, production or end-to-end claim. Current user authorization is inherited from the main task handoff, not independently authenticated by this file. |
| guide | pass | No substantive guide requirement found in the empty GUIDE; human-only directory remains excluded. Stable task inputs and preservation scope are explicit. |
| assumptions | pass | Finite nonnegative F, nonnegative probability marginals, full rectangular allowed edges, exact arithmetic and fixed linear actual-value cost make the proposed construction/proofs valid. Zero row, column and completion denominators require explicit branches. |
| prior_results | pass | Prior numerical-rounding data are not rebranded as this result. Exact transport prerequisite is applicable; approximate marginal repair is a new bounded delta. Search partiality is disclosed. |
| acceptance | fail | Stable Plan requires illegal-mass and negative-input rejection, but frozen T7 instantiates only negative F with perfectly normalized equal masses. B1 must be fixed before production. Remaining exact invariants, retrieval closure, preservation, six validation criteria, distinct result owner and consumer contract are sensible. |
| risk | pass | Sparse masks explicitly outside scope; exact examples cannot certify floating implementations; dual transport lower bound is distinguished from output-error lower bound. Source-specific date/title and asymptotic feasibility limitations are planned. |
| resources | pass | CPU Fraction fixtures and curated lexical retrieval are proportionate to 1800 seconds and at most two review cycles. No paid/model/GPU/Lean expansion. Actual ReviewSession/adapter/supervisor identity is not claimed; lack of authenticated runtime remains a separate dispatch limitation, not repaired by this review. |

## Independent mathematical assessment

Let a∈R^m_+, b∈R^n_+ have sums one, and F∈R^{m×n}_+ be finite. For p_i=Σ_jF_ij, take row factor x_i=1 when p_i=0, otherwise min(1,a_i/p_i), and X_ij=x_iF_ij. For q'_j=Σ_iX_ij, take column factor z_j=1 when q'_j=0, otherwise min(1,b_j/q'_j), and Y_ij=z_jX_ij. This convention avoids 0/0 even when target coordinates are zero.

Then 0≤Y≤X≤F elementwise, rows(X)≤a, rows(Y)≤a and cols(Y)≤b. Hence r=a−Y1 and s=b−Yᵀ1 are nonnegative, with common total τ=1−ΣY≥0. If τ>0, R=rsᵀ/τ has row sums r, column sums s and total mass τ. Therefore G=Y+R has exactly a,b as marginals. If τ=0, nonnegativity and zero total force r=s=0; G=Y has the required marginals without dividing by zero. The proof applies to rectangular matrices and zero marginal coordinates, without strict positivity assumptions.

For arbitrary mass M=ΣF, triangle inequality and elementwise domination give ||G−F||1≤||F−Y||1+||R||1=(M−ΣY)+τ. With 0≤C_ij≤D, <Y,C>≤<F,C> and <R,C>≤Dτ, so U=<G,C>≤<F,C>+Dτ. Negative costs would invalidate this domination argument and are excluded. If C is the actual fixed-linear value distance, the exact repaired marginals give output error≤U by the existing transport proof. The cheap raw cost alone is not an upper certificate.

**Normalized-F stronger bound, independently derived.** Assume additionally M=1. The row removal A=Σ(F−X)=Σ_i(p_i−a_i)_+=||p−a||1/2 because p and a have equal total. The column removal B=Σ(X−Y)=Σ_j(q'_j−b_j)_+≤Σ_j(q_j−b_j)_+=||q−b||1/2, where q=cols(F) and q'≤q. Thus τ=A+B and ||G−F||1≤2τ≤||rows(F)−a||1+||cols(F)−b||1. This is a valid derivation under normalized F; it must be distinguished from the precise constants and assumptions of the cited classic lemma. No general-mass F version of this final normalized bound is claimed.

For any finite potentials f,g, h=max(0,max_ij(f_i+g_j−C_ij)) makes f'=f−h feasible on all rectangular edges. Since Σa=1, L=a·f+b·g−h≤OPT≤U. L can be negative and is a transport-cost lower bound, not a lower bound on output error. Clamping L to zero would also remain valid for nonnegative C, but is unnecessary. The source comparison should preserve this scope.

**Sparse rejection.** The rank-one correction can create every edge where r_i s_j>0. A forbidden such edge invalidates the supported coupling. T5 requires the forbidden (1,2) edge with a=(1,0), b=(0,1), diagonal-only mask; its masked feasible set is empty. General sparse feasible sets need a support-aware feasibility/completion algorithm and are outside this method. The implementation must refuse unsupported masks rather than silently returning an unrestricted G as a masked certificate.

## Blocking finding B1

Location: fixtures.json, case T7; MATH-65 stable Plan statement “非法质量/负值”; validation_plan reference_boundary and implementation criteria.

Problem: T7 contains F=[[-1,0],[0,1]], a=b=(1/2,1/2). It exercises negative F only. Its textual label additionally says unequal/unnormalized marginals, but no such inputs exist. A producer that never validates probability masses could pass the frozen eight cases and still fail the promised invalid-mass boundary.

Required revision: retain T1–T8 case identities and add explicit public T7 subcases for (i) unequal marginal totals with a nonnegative finite F, and (ii) equal but nonunit marginal totals with a nonnegative finite F. Each must freeze a concrete expected rejection. For example, F=0, a=(1,0), b=(1/2,0) for (i), and F=0, a=b=(1/2,0) for (ii). Keep the existing negative-F subcase. Update fixture and complete-plan hashes, with a versioned second review of the new exact SHA; preserve this first-cycle evidence. This adds no new scientific claim, model resource or scope expansion.

Reverification: read the explicit three invalid-input subcases and their expected decisions; recompute every affected frozen hash; check the producer is still blocked behind review and the independent result verifier will inspect the actual mass guards and refusal behavior. Do not merely change the T7 label or reuse the negative-F failure as evidence for both mass guards.

## Nonblocking cautions and downstream obligations

Recent-paper and classic-PDF assertions were assessed as proposed reading obligations; this review does not certify that their source checks have already been completed. Their actual versions, sections and dates must be bound to producer evidence and read independently before publication. Curated Top3 hits establish lexical structure only, not unseen/model retrieval quality. Holdout preservation hashing is permitted; content must remain unread. General proofs and code-guard review remain necessary because eight public fixtures cannot establish all mathematical or malformed-input cases. All applicable result checks must be performed by the different result reviewer before any consumer uses raw outputs.

Compact verdict: intent=pass; guide=pass; assumptions=pass; prior_results=pass; acceptance=fail; risk=pass; resources=pass. FINAL=revise; blocking=[B1].
