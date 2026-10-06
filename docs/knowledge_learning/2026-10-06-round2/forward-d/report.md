# Blind forward test: residual accuracy and search optimality

Task ID: `knowledge-forward-d`. Task refs: `refs.json`; raw retrieval/check evidence: `evidence.txt`; independent checks: `check.py`. The authorized input was only `/tmp/knowledge-forward-d/skill`, and all outputs are under `/tmp/knowledge-forward-d`. No network, repository tests, evaluation rubric, or other agents were consulted. No performance measurement or claim is made.

## Retrieval and source use

Read the skill, its execution/workflow references, and knowledge README. Created a SQLite index at `/tmp/knowledge-forward-d/search.sqlite` with the supplied CLI. It indexed 10 published entries, snapshot `d416e98b46b25d0029c3af8914dfbea3cee23f31ccedb9dbe5846beabe82ff88`. The README says five seeds; the actual index reports 10, so the observed index result controls this report.

The first queries were structural descriptions, not theorem names:

| Initial query | Top result | Other returned candidates | Decision |
|---|---|---|---|
| `linear equations small residual solution error inverse sensitivity` | `math.linear-system-stability` | `math.cauchy-schwarz`, `math.score-difference-bound` | Read the first entry fully; the others concern inner products/rankings and are unnecessary here. |
| `feasible minimization lower bound suboptimality gap constraint` | `math.dual-certificates` | `math.cauchy-schwarz`, `math.low-rank-svd` | Read the first entry fully; the others do not address the objective/constraint certificate. |

Both used `--index /tmp/knowledge-forward-d/search.sqlite --limit 3`; both succeeded immediately. There were no failed or empty initial searches and no fallback query. The initial commands preceded creation of the evidence file: its header records their observed results honestly, and the complete search outputs are explicitly marked replays. Subsequent `show`, `tree`, and `section` outputs are logged directly. Read `math.linear-system-stability` section `s3` and `math.dual-certificates` section `s2` after examining their trees; full `show` was used for premise review.

The local entries cite Cornell CS6210, “Error analysis for linear systems: Beyond first order; Residual-based bounds,” and Stanford EE364A duality slides 5–2/5–3, 5–10/5–11, 5–18/5–19. These are provenance recorded in the provided corpus, not external pages fetched or independently revalidated in this offline test. Entry verification metadata mentioning repository tests was treated only as metadata; those tests were not accessed. The numerical and algebraic checks here are independent task checks.

## 1. Small residual does not certify solution accuracy

Model the data as exact real numbers and use the Euclidean vector norm and its induced matrix 2-norm. Let `x*` solve `Ax*=b`, let `xhat=(1,3)`, and define `r=A xhat−b`. No application accuracy tolerance or physical units were supplied. A residual threshold alone cannot define solution accuracy.

| Entry premise / required check | Task evidence | Status |
|---|---|---|
| Real square invertible A | Diagonal entries 1 and 10⁻⁴ are positive | Satisfied |
| Nonzero b for relative residual bound | b=(1,10⁻⁴) | Satisfied |
| Compatible induced norm | Explicitly use vector 2-norm and induced matrix 2-norm | Satisfied |
| Finite perturbation bound requires κ(A)‖E‖/‖A‖<1 | No matrix/data uncertainty E,e was supplied | Not needed for exact-data residual bound; unknown for a perturbed physical model |
| Accuracy target | No requested forward-error tolerance | Unknown; report actual error and conditional stopping criterion |

Direct solution and residual:

\[
x^*=(1,1),\quad r=(0,2\cdot10^{-4}),\quad \hat x-x^*=(0,2).
\]

Thus `‖r‖₂=0.0002<0.001`, but `‖xhat−x*‖₂=2` and the relative forward error is `2/√2=√2≈1.4142`, or about 141.4%. The second component has 200% relative error. This task instance is itself a counterexample to the claimed certificate.

The retrieved entry provides the relevant error structure. Since `A(xhat−x*)=r`,

\[
\hat x-x^*=A^{-1}r,\qquad
\|\hat x-x^*\|_2\le\|A^{-1}\|_2\|r\|_2.
\]

Here `‖A‖₂=1`, `‖A⁻¹‖₂=10000`, and `κ₂(A)=10000`. The absolute error bound is `10000×0.0002=2`, attained in this example because the entire residual lies in the sensitive second direction. Dividing and using `‖b‖₂≤‖A‖₂‖x*‖₂` gives

\[
\frac{\|\hat x-x^*\|_2}{\|x^*\|_2}
\le \kappa_2(A)\frac{\|r\|_2}{\|b\|_2}
=\frac{2}{\sqrt{1+10^{-8}}}\approx1.99999999.
\]

This conservative relative bound permits very large error; the smaller actual error is consistent with it. A bound too large to meet a target would not by itself prove failure, but here the explicitly computed error does prove it.

Appropriate checks and stopping criteria:

1. Report the residual norm, its scaling, and a trustworthy condition estimate or bound. The relative residual is about `1.99999999×10⁻⁴`. The approximate solution exactly solves the nearby right-hand-side problem `A xhat=b+r`; this small normwise RHS perturbation is a backward-error statement, not a forward-accuracy certificate.
2. Given a target relative solution error `ε`, a sufficient condition is `κ₂(A)‖r‖₂/‖b‖₂≤ε`. For example, `ε=0.001` would require `‖r‖₂≤1.000000005×10⁻⁷` by this bound. This is sufficient, not generally necessary.
3. If individual components matter, inspect scaling and component errors. Since this A is diagonal, `|r_i|/|b_i|` equals each component's relative solution error, giving `(0,2)` here. That equality does not automatically extend to coupled systems.
4. In floating-point implementations, recompute residuals with sufficient accuracy and account for uncertainty in A,b. If `A+E` and `b+e` represent the perturbed data, set `a=‖E‖/‖A‖`, `β=‖e‖/‖b‖`. Only when `κa<1` does the cited finite-perturbation bound `κ(a+β)/(1−κa)` apply. No numerical uncertainty bound can be asserted from the supplied task data alone.

## 2. Feasibility and unsuccessful search do not certify optimality

Model `p*=min{x² : x∈R, 2−x≤0}`. The candidate `xhat=2.1` is feasible and gives upper bound `U=4.41`. The statement “nothing better was found” supplies no global lower bound.

| Entry premise / required check | Task evidence | Status |
|---|---|---|
| Minimization with explicit full domain and constraint direction | Domain R; objective x²; inequality 2−x≤0 | Satisfied |
| Feasible candidate for upper bound | 2.1≥2 | Satisfied |
| Nonnegative inequality multiplier | Choose λ=4≥0 | Satisfied |
| Dual function is infimum over the whole Lagrangian domain | Compute inf over all real x analytically by completing the square | Satisfied |
| Strong duality conditions, if invoked | Objective convex; constraint affine; x=3 strictly feasible | Satisfied, but unnecessary for the weak-duality bound or matching certificate below |
| Search coverage proves no better point exists | No coverage evidence; x=2 is explicitly better | Not satisfied |

Write

\[
L(x,\lambda)=x^2+\lambda(2-x)
=(x-\lambda/2)^2+2\lambda-\lambda^2/4.
\]

The square is nonnegative and vanishes at `x=λ/2`, so the exact global infimum is

\[
g(\lambda)=2\lambda-\lambda^2/4.
\]

For every feasible x and λ≥0, `g(λ)≤L(x,λ)≤x²`; consequently `g(λ)≤p*≤U`. Choosing λ=4 gives `g(4)=4`. Hence the candidate has the justified bound

\[
0\le 4.41-p^*\le4.41-4=0.41.
\]

Furthermore, `x=2` is feasible with objective 4. Matching upper and lower bounds establish `p*=4`, so the gap is exactly `0.41`, not merely at most `0.41`. The candidate is 0.41-suboptimal (or ε-optimal only for an absolute objective tolerance ε≥0.41), and its relative objective gap with denominator p* is `0.41/4=0.1025`, or 10.25%. Its distance to the unique optimizer is `0.1`; objective gap and solution distance are distinct quantities. Uniqueness also follows directly because `x²−4=(x−2)(x+2)>0` whenever `x>2`.

The returned point cannot claim exact optimality. A certificate is available for `x=2, λ=4`: primal feasibility, dual feasibility, stationarity `2x−λ=0`, and complementarity `λ(2−x)=0`. At `x=2.1`, stationarity forces λ=4.2 while complementarity forces λ=0, so no such certificate exists. More simply, the feasible point x=2 already refutes optimality.

A critical failure mode: evaluating `L(0,4)=8` during a numerical inner search does not provide a lower bound on p*. It is a trial value above the true infimum 4, and using it would falsely assert `p*≥8`. Certified lower bounds require the exact infimum or a proven lower bound on it. The analytic square completion supplies that proof here; finite search samples alone do not.

## Checks, references, and limitations

`check.py` uses exact rational arithmetic for all input data, residual components, scalar objectives, the certificate, and the failure case; square roots are printed using floating point. All assertions passed. A finite rational grid independently checks implementation of the square-completion identity and feasible-objective inequality; the displayed algebra, rather than the grid, supplies the general proof. No formal proof assistant was run.

The two actually used entries have `requires: []` in their full `show` output. Thus the deduplicated union of their returned `knowledge_refs` is already the full strong-dependency closure. Distractor search results were not used and are not cited. `refs.json` contains exactly:

| ID | Version | SHA-256 |
|---|---|---|
| math.linear-system-stability | 1 | caacac2221436b3cd671b9a307f8598e8481af537400839a430f5558bd04b4a4 |
| math.dual-certificates | 1 | d165577ff3bfb7ebc14ff33ccc66d3641cf4f9afdae532636099bfefc07ab708 |

The final `check-refs` output is preserved in `evidence.txt`; it checks reference identities, not mathematical applicability. No unresolved mathematical issue remains for these exact inputs. Application-specific tolerances and data/roundoff uncertainty would be needed to turn these derivations into a deployed solver's acceptance policy.
