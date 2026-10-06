# Blind forward test E

Task ID: `knowledge-forward-e`. Task refs: `knowledge-forward-e/allocation`, `knowledge-forward-e/energy`, `knowledge-forward-e/ranking`.

## Retrieval and provenance

Read `/tmp/knowledge-forward-e/skill/SKILL.md`, then `references/execution.md` and `references/workflow.md`. Used only the supplied skill corpus and this task's outputs; no browsing, repository tests, rubric, other-agent outputs, external proof tools, or performance measurements. Source metadata inside local entries was read as metadata; external URLs were not opened or independently verified.

Actual file-backed searches, with limit 3, were `对称 群 平均 凸 约束`, `时间 能量 守恒 离散`, and `topk 排名 谱范数 误差`. These retrieved Reynolds averaging, Noether invariants, and the score-difference bound respectively. Candidate summaries were inspected before full reads. The three relevant full entries were read, then their required full prerequisites `math.symmetry-quotient` and `math.cauchy-schwarz`. To examine the basic ranking test and local related navigation, ran `related math.topk-margin` (including an incoming link to the sharper bound), and read `show math.topk-margin`. SVD and dimensional-analysis candidates were not needed and are not cited. Searches are relevance candidates, not applicability scores.

`evidence.txt` records commands, unabridged retrieval outputs and check results. `refs.json` contains authentic, deduplicated `show`-returned references, including every strong prerequisite. `check-refs` returned `valid: true` on snapshot `d416e98b46b25d0029c3af8914dfbea3cee23f31ccedb9dbe5846beabe82ff88`. Identity validation is not a mathematical applicability judgment.

## 1. Symmetric allocation

Let C = {x in R^3: x_i >= 0, sum x_i = 1}, f(x) = sum x_i^2, and G = S3 act by coordinate permutation. For minimization, averaging does remove all free variables without increasing the objective:

P x = (1/6) sum_{g in S3} g x = ((x1+x2+x3)/3)(1,1,1) = (1/3,1/3,1/3).

Every coordinate appears twice in each output position across the six permutations. Thus P = (1/3) 11^T, a projection onto the one-dimensional constant-coordinate subspace; the sum constraint fixes its remaining scalar. C is convex and permutation invariant, and f is convex and invariant, so Jensen gives f(Px) <= (1/6) sum_g f(gx) = f(x). Directly,

f(x) - 1/3 = sum_i (x_i - 1/3)^2 >= 0.

The unique minimizer is uniform, with value 1/3. For example, x=(1/2,1/3,1/6) has value 7/18 and averages to value 1/3.

The task does not explicitly state minimization versus maximization. The no-worsening conclusion above is for minimization. For maximization, averaging can worsen the objective: (1,0,0) has value 1, while its average has value 1/3. Indeed the maximum on C is 1 at the vertices.

With the one-hot constraint, the feasible set is {e1,e2,e3}, which is not convex. Its orbit average is still uniform, but infeasible. Averaging cannot justify variable elimination for that problem. Because every feasible point belongs to one permutation orbit and has value 1, keeping e1 as an orbit representative preserves the optimum for either direction. This removes equivalent choices without averaging them. If all labeled solutions must be returned, the other two labels must be reconstructed.

## 2. Energy diagnostic

Use the normalized oscillator L=(v^2-q^2)/2, H=(q^2+v^2)/2, qdot=v, vdot=-q. The exact continuous trajectory satisfies dH/dt=qv+v(-q)=0. This is an autonomous conservative Lagrangian system, so the relevant energy premise holds. Autonomy of an arbitrary ODE alone would not establish conservation of this H.

The stated simultaneous update is explicit Euler, not the exact flow. Algebraically,

2H_next = (q+hv)^2 + (v-hq)^2 = (1+h^2)(q^2+v^2),

hence H_next=(1+h^2)H. At h=0.2 and (q,v)=(1,0), the next state is (1,-0.2), H changes from 0.5 to 0.52, and relative energy growth is 4%. The exact-conservation claim is false even in exact arithmetic. At constant h, H_n=(1+h^2)^n H_0; 20 steps give approximately 1.0955615715. At zero initial energy (the equilibrium), or h=0, this recurrence has no drift; those trivial passing tests would not establish conservation generally.

This diagnostic separates continuous-model conservation from discretization error. For the exact method as stated, systematic growth is predicted by its update rule and need not indicate an implementation bug. If observed values fail this recurrence beyond numerical tolerance, investigate whether the implementation really uses simultaneous old-state updates, uses a different method, or has other numerical/model errors. Energy conservation alone cannot certify trajectory or phase accuracy: even an incorrect rotation rate can preserve q^2+v^2. Dissipation or forcing would require a different expected energy balance, e.g. vdot=-q-gamma*v gives dH/dt=-gamma*v^2. A conserved-energy check therefore has a specific model and discretization scope, not universal simulator correctness.

## 3. Joint score information yields a stronger guarantee

Interpret K and Khat as real d-by-n matrices with columns as keys, the same fixed q in both score computations, and the matrix 2-norm as the induced spectral norm. Let 1 <= k < n and let the supplied 0.13 be the boundary gap s_(k)-s_(k+1) in exact descending scores. Define e=s-shat=(K-Khat)^T q. Then

||e||2 <= ||(K-Khat)^T||2 ||q||2 = ||K-Khat||2 ||q||2 <= 0.04*2 = 0.08.

The coordinate consequence |e_i|<=0.08 would give the sufficient threshold 2*0.08=0.16, which 0.13 fails. Failing that test does not imply reversal.

The joint bound gives more. For distinct coordinates i,j and coordinate basis vectors u_i,u_j,

|e_i-e_j| = |(u_i-u_j)^T e| <= ||u_i-u_j||2 ||e||2 <= sqrt(2)*0.08 = 0.11313708499.

For any i originally inside the top-k set and j outside it,

shat_i-shat_j >= (s_i-s_j)-sqrt(2)*0.08 >= 0.13-0.11313708499 = 0.01686291501 > 0.

Thus the top-k set is guaranteed unchanged under the supplied joint information. This guarantees membership, not internal order, exact scores, softmax values, or downstream quality. If the stated gap is instead in approximate scores, the same argument with s and shat exchanged also guarantees their top sets agree. If the gap is merely sampled, estimated without a bound, or the query changes between computations, the guarantee requires additional premises or error terms.

A concrete worst-direction check uses d=1, n=2, q=2, K=[0.065,0], eta=0.08, a=eta/sqrt(2), and K-Khat=[a/2,-a/2]. This residual has spectral norm 0.04 and attains the maximum pairwise decrease sqrt(2)*eta. Scores (0.13,0) become approximately (0.07343146,0.05656854), still correctly ordered with the stated remaining gap. This demonstrates tightness of the bound for the unrestricted spectral residual model; no claim is made for a narrower structured approximation family.

For a failure contrast, entrywise-only errors (0.08,-0.08) would change (0.13,0) to (0.05,0.08), reversing the order. Their joint norm is 0.113137... > 0.08, so that example is excluded by this task's actual assumptions. At a boundary gap exactly sqrt(2)*eta, the permitted worst-direction error can create a tie; strict inequality is necessary for this guarantee. Below the threshold there may or may not be a reversal.

## Applicability audit

| Entry/premise | Task evidence | Status |
|---|---|---|
| Reynolds: finite linear group action and full uniform average | Six S3 permutation matrices | Met |
| Reynolds: orthogonal representation | Permutation matrices | Met |
| Reynolds optimization: convex invariant set and convex invariant objective | Simplex and squared norm; minimization interpretation | Met conditionally on minimizing |
| Reynolds optimization on one-hot set: convex feasible set | Three isolated vertices | Not met |
| Symmetry quotient: feasibility and objective invariant | All three one-hot vectors allowed, objective 1 | Met for static optimization; not full labeled enumeration |
| Noether energy: smooth autonomous Lagrangian, exact Euler–Lagrange trajectory | Normalized continuous harmonic oscillator | Met for continuous model |
| Applying continuous conservation to numerical iterates | Explicit Euler map is not exact flow | Not met; direct discrete calculation needed |
| Cauchy–Schwarz: real Euclidean vectors, same query | Real score model with q fixed between computations | Met under stated interpretation |
| Basic top-k sufficient margin > 2 epsilon | 0.13 < 0.16 | Not met; inconclusive alone |
| Sharper ranking: joint score 2-norm bound | Spectral residual and query bounds imply eta=0.08 | Met |
| Sharper ranking: finite top-k boundary, 1<=k<n | Interpretation of supplied top-set boundary | Conditional on valid boundary definition |
| Sharper ranking: strict margin > sqrt(2) eta | 0.13 > 0.11313708499 | Met |

## Verification and deliverables

`computations.py` runs exact rational checks for averaging and 20 Euler energy steps, then floating-point checks of ranking thresholds, a spectral-residual witness, an entrywise-only reversal, and the equality tie. All assertions passed; `computations.json` contains results. The symbolic derivations above establish the general statements; numerical examples alone do not. No formal proof or measured speedup is claimed.

All six used knowledge entries and complete strong dependencies are pinned by ID/version/SHA-256 in `refs.json`. Full retrieved entry records are saved alongside the report for audit. Nothing remains blocked; only the explicitly identified interpretation conditions need to be retained in downstream reporting.
