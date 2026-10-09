# Independent result review: MATH-56

Actor: /root/inverse_result_review. Parent dispatched a fresh result-review context distinct from root-inverse-producer and inverse_plan_review. This is an actual local child review, not a deployed authenticated ReviewSession or a live monitor. Only independent_* paths written. Verdict: usable-with-scope, contingent on parent observing this actor's completion and accepting its host identity.

## Actual implementation and independent references

Read contract, six frozen criteria, cases, actual validate.py/retrieve.py, raw/retrieval outputs, relevant card JSON/Markdown, sources and environment. Exact fixture update computes Ai, Z=Ai U, T=V^T Ai, S=I+V^T Z and candidate Ai-Z S^-1 T; singular-base and singular-S exceptions correctly reject. Fraction Gauss-Jordan has pivot search and all-row elimination. Fixed dimensions are valid; this is fixture code, not a general production solver accepting arbitrary ragged or malformed inputs. Independent_verify uses 2x2 determinant/adjugate direct inverses and coordinate solves rather than the producer's elimination/update. All ten unique frozen IDs independently reconstruct and match raw values. In particular B=[[4,0],[4,1]] gives x=(3/4,1), the rank-deficient factor case gives inverse diag(1/3,1), and the ridge update gives [[3,2],[2,7]], h=(3,5), x=(11/17,9/17). Singular base diag(0,1) can become identity but still cannot use A inverse. Zero capacitance gives singular diag(0,1).

## General proof independent of finite samples

For A invertible and arbitrary rectangular n by k factors, define M=[[A,U],[-V^T,I]]. Multiplication on the left by [[I,0],[V^T A^-1,I]] yields [[A,U],[0,S]]. Multiplication on the left instead by [[I,-U],[0,I]] yields [[B,0],[-V^T,I]]. Both multipliers are invertible block unit triangular matrices. Thus M invertible iff S invertible (A invertible), and M invertible iff B invertible (I invertible). No full column rank of U or V enters any implication, including k>n or zero factors.

With Z=A^-1 U and T=V^T A^-1, B A^-1=I+UT and BZ=US. Therefore for X=A^-1-ZS^-1T, BX=I+UT-USS^-1T=I. A square right inverse is the inverse. For rank one this yields the stated two-solve solution with beta nonzero. The card proof signs and block dimensions agree.

For real symmetric A>0, addition obeys t^T(A+uu^T)t=t^TAt+(u^Tt)^2>0 for nonzero t. For deletion use the unique SPD square root: A^-1/2 B A^-1/2=I-ww^T, w=A^-1/2 u. Congruence preserves positive definiteness and inertia. If w=0 this is identity. Otherwise the eigenvalue on span(w) is 1-||w||^2 and on its orthogonal complement is 1. Hence B>0 iff a=u^T A^-1u<1; a=1 singular; a>1 invertible and, for n>=2, indefinite (for n=1, negative definite). The card states the n=1 exception correctly. A covariance name cannot replace symmetry/SPD premises.

For true invertible B, r=b-B xhat implies xhat-x=-B^-1 r and the norm bound. It is an exact identity, not an accurate floating residual calculation guarantee. The card separates authenticated residual/norm envelopes from heuristic diagnostics. Ridge C/h updates preserve their unnormalized Gram/rhs definitions; centered/normalized covariance requires additional mean/count handling. Dense operation/storage counts include n^2 k, n k^2, k^3 and original-factorization exclusion; this supports algorithmic scaling only.

## Actual binary64 numerical witness

Independently executed Python radix2/mantissa53 operations at u=2^54. fl(1+u)=u, theta=2^-54, u*theta=1 exactly, xhat=0. True B=u+1 and x=1/(u+1)>0; exact true residual=1, eta=1, forward relative error=1. Both scalar nonzero A and true B have condition number1. Beta is huge, not near zero. This is a valid counterexample to stability inference from nonzero beta or well-conditioned scalar systems, specific to the recorded arithmetic order. Direct division by rounded B returns 2^-54 and is a diagnostic, not a general direct-inverse recommendation. No MSM, FMA, GPU or alternative-order test executed.

## Source extents and provenance

Read supplied classic HTML's Sherman-Morrison, Sherman-Morrison-Woodbury and General Formula sections with image alt equations; source hash matches sources.json. Formula and Schur relation agree; the author's simplified k-dependent flop discussion is not adopted as the complete general-k cost.

Read supplied recent PDF text header (arXiv:2609.12266v1, 10 Sep2026), abstract, Section1 including Algorithm1.1, Section3 introduction/3.1 and Algorithm3.2 with adjacent correction derivation. SM solves Ay=b and Az=u then outputs y-z theta. MSM also forms d=b-u theta, solves Aw=d, theta1=(v^T w-theta)/beta and outputs w-z theta1: three A solves. The abstract explicitly calls universal MSM stability/instability an open problem. The card appropriately treats it as a candidate and author experiments as reported observations. No unread theorem constants, universal stability theorem, latest-version confirmation, formal-publication status or reproduced MSM experiment is accepted. The PDF hash matches sources.json; independent network provenance authentication was not performed.

## Integrity, reproduction and scope

508 artifact bindings verified before and after. Recursive canonical corpus and plugin mirror covered completely excluding only live learning_state.json; original immutable learning_state, TASK and plan-detail snapshots remain bound. Replay preserves original __file__ and frozen reads, redirects only the three write destinations to independent_*; all ten raw cases and six retrieval records equal the originals excluding only diagnostic seconds. Frozen code is inspected, and replay is separately compared rather than overwriting original evidence. Six public fixed file/SQLite queries hit the card, context includes required Schur premise, refs validate; these are structural tests with manual premise decisions, not LLM unseen/refusal accuracy. Holdout files were only hashed; contents not inspected. 53 relevant knowledge regressions passed and mirror --check passed. Timing/characters/bytes have no performance, token or model meaning here; measurement_validity is preallowed N/A. No model/GPU/end-to-end evaluation or general numerical solver certification.

Natural-language mathematics review is not formal proof checking; ten public fixtures do not exhaust all inputs. Hash/schema validity authenticates byte bindings, not reviewer identity or scientific universality. Live state may be changed later for completion without retroactively changing the frozen original snapshots, within the declared exclusion.
