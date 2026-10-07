# Cooling as a fixed-point stopping problem

Task `KB-LIVE-2`; input version `synthetic-cooling-v1`; task references `[KB-CROSS-01]`. Decision: EXECUTE within the delegated synthetic task. Existing producer artifacts are unchanged. All new outputs are in this transfer directory.

**The returned value is certified within 0.03 °C of the model equilibrium, 20 °C.** The appropriate cross-disciplinary perspective is numerical analysis: treat the physical recurrence as an exact fixed-point iteration, and convert the measured step into an error certificate for the new point. This is a strict mathematical mapping of the supplied model, not a claim that an actual thermal system follows it.

Candidate comparison:

| Perspective | What it contributes | Decision |
|---|---|---|
| Numerical analysis: contractive fixed-point iteration | A proved step-to-error relation for the returned value | Adopt; directly answers the stopping question |
| Physics: units and dimensionless normalization | Check temperature offsets, scales, and the dimensionless update factor | Adopt as a consistency check; dimensional consistency alone cannot certify convergence or physical fidelity |
| Statistics: observed decrease as sampled evidence | Could address uncertainty given a specified stochastic model | Reject a universal deterministic certificate here; no sampling model, independence, or population assumptions are supplied |

The local structure query was `迭代 停止 步长 误差 不动点`. It returned the contraction certificate and statistical stopping/mean candidates. The full contraction entry and its related dimensional-analysis entry were read. Both have no required knowledge dependencies. Statistical candidates were rejected from their retrieved assumption summaries; no statistical theorem was invoked.

## Exact mapping, assumptions, and units

| Cooling object or relation | Numerical-analysis / unit-analysis object | Preserved structure and evidence | Limitation or minimal check |
|---|---|---|---|
| Temperature T_t | Scalar state x_t in X=[20,36] | Temperature coordinate in °C; T_0=36 lies in X | Lumped scalar model omits spatial gradients and additional states |
| One fixed time step | One application of G(x)=20+0.75(x-20) | Discrete iteration index t; fixed map | No duration in seconds is supplied; do not infer a continuous cooling rate or physical elapsed time |
| Distance between temperatures | Metric d(x,y)=abs(x-y) | Temperature difference, units °C (same numerical difference in kelvin) | Celsius absolute values have an affine offset; differences, not absolute Celsius ratios, carry the error interpretation |
| Temperature remains bounded | Complete invariant domain X | Closed interval is nonempty/complete; G([20,36])=[20,32], a subset of X | Invariance follows from the equation, not from finite observations |
| Multiplication of temperature excess by 0.75 | Uniform contraction factor q=0.75 | abs(G(x)-G(y))=0.75 abs(x-y) for every x,y in X | This global identity must not be replaced by a few observed ratios |
| Ambient equilibrium 20 °C | Unique fixed point x*=20 | Solve G(x*)=x*; q<1 | Equilibrium of this exact model, not a measured physical equilibrium |
| Step abs(T_(t+1)-T_t) | Old-point residual r_t=d(x_t,G(x_t)) | Temperature difference in °C | Requires the exact update, or an independently bounded oracle/residual error |
| Return T_(t+1), not T_t | New-point error certificate q r_t/(1-q) | Dimensionless multiplier 3 times a residual in °C | Using r_t/(1-q) would instead give the weaker 0.04 °C old-point threshold |
| u_t=(T_t-20)/(16 °C) | Dimensionless normalized excess | u_0=1, u_(t+1)=0.75 u_t | This simple coordinate scaling does not require or assert a Buckingham-Pi reconstruction of the physics |

The provided model is deterministic and exact; the numerical check uses rational arithmetic. No sensor error, uncertain coefficient, changing ambient temperature, additional input, rounding error, or model discrepancy is silently included. If these exist, their bounds and any changed invariant domain/contraction factor must be supplied before transferring the same certificate. For example, with a certified update error eta and an upper bound r_hat on the computed step, the same fixed-map assumptions give the returned-point bound (0.75 r_hat+eta)/0.25; this extension cannot assign an eta from observed noise alone.

## Derivation and reproducible check

For an exact contraction, the triangle inequality gives

\[
|x_t-x^*|\leq r_t+q|x_t-x^*|,
\qquad
|x_{t+1}-x^*|\leq\frac{q}{1-q}r_t.
\]

Thus the stopping test r_t<=0.01 °C guarantees

\[
|T_{t+1}-20|\leq\frac{0.75}{0.25}(0.01)=0.03\text{ °C}.
\]

For this particular affine recurrence there is an exact equality: r_t=0.25|T_t-20| and |T_(t+1)-20|=0.75|T_t-20|=3r_t. The generic certificate is therefore tight for the observed residual. Direct closed-form calculation, independent of the residual theorem, gives T_t=20+16(3/4)^t and r_t=4(3/4)^t.

Executed `verify.py` with Python's exact `fractions.Fraction` arithmetic; **84 checks passed**. It checks the closed form, invariant interval and exact posterior error at every update through the first stop, then checks the stopping boundary, temperature-unit shift, and countermodel below. The output is retained in `verification-output.json`.

| Quantity | Executed result |
|---|---|
| First qualifying t | 21 |
| Returned index / updates performed | T_22 / 22 |
| Observed stopping residual | 0.00951363581680198 °C |
| Returned temperature | approximately 20.028540907450406 °C |
| Actual model error / certificate from observed residual | approximately 0.02854090745040594 °C |
| Certificate from threshold alone | 0.03 °C |

The script confirms the preceding residual is greater than 0.01 °C, so this is the first qualifying step. Decimal displays are approximate; the output also retains exact fractions. Finite checks validate these examples and arithmetic; the algebra above supplies the general guarantee. No proof assistant, physical experiment, production-system experiment, or performance benchmark was run.

## Why three improving discussion rounds do not transfer the guarantee

**No: disagreement decreasing by about 25% over three rounds does not establish the same universal stopping guarantee.** Even interpreting the observation favorably as a separate 25% decrease in each round is insufficient. A discussion needs a specified state, metric, fixed update map, invariant complete domain, a proven uniform contraction factor, and a justified link between the measured disagreement, state residual, equilibrium, and desired correctness. None follows from the observed ratios. Adaptive participants, new evidence, randomness and shared error are additional possible mismatches. Agreement itself need not mean truth or task completion.

For an explicit falsification, a dimensionless disagreement sequence can begin

\[
0.02,\quad0.015,\quad0.01125,\quad0.0084375
\]

and next become 1. The first three transitions are exact 25% reductions, and the last observed value is below 0.01; both continued decrease and rebound are consistent with that prefix.

The executed countermodel makes the failure stronger: it constructs a fixed continuous piecewise-linear self-map of [0,1] through the ordered points

\[
(0,0),\ (0.0084375,1),\ (0.01125,0.0084375),\
(0.015,0.01125),\ (0.02,0.015),\ (1,1).
\]

It realizes all three observed decreases and then rebounds, while staying within [0,1]. Two fixed points (0 and 1) and a pairwise Lipschitz ratio 3173/9>1 rule out the required global contraction. Thus even granting a deterministic continuous self-map and an invariant complete domain does not rescue the claim from a finite trend. This is a synthetic logical counterexample, not a model fitted to real agents. Furthermore, disagreement between participants is generally not the consecutive-state residual used in the cooling proof.

Smallest useful follow-up for an actual discussion system: define the full state and distance, specify the update mechanism and evidence inputs, and prove or externally certify a uniform bound and an error-to-quality relationship. A few additional trend observations remain insufficient for a universal guarantee. Until those premises exist, keep the 25% observation descriptive and reject the theorem transfer.

Full local references, retrieval commands/results, assumption mappings and adoption/rejection decisions are in `knowledge-use.json`. Source URLs are provenance read from local entries; they were not freshly fetched. The local reference validator checks identity/dependency closure, not applicability. The root reviewer owns independent retrieval, scientific acceptance and TASK/handoff publication; all broader requirements remain under root ownership.

Reproduce after changing into this artifact directory (including if the directory has been moved). The numerical script has no repository dependency. For the reference check, point REPO_ROOT to the accessible source repository with the recorded corpus snapshot:

```bash
python verify.py
REPO_ROOT=/workspace/scratch/4f9639d1bad2/agent
PYTHONPATH="$REPO_ROOT" python -m agent_runtime.knowledge --root "$REPO_ROOT/knowledge" check-refs knowledge-use.json
```
