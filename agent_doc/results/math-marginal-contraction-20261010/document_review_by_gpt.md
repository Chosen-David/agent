# MATH-79 ordinary independent document review — full feedback

Verdict: **approve**, within the ordinary document-review scope only. No blocking mathematical finding. This is the second/final ordinary review requested by the parent; it is not a trusted ReviewSession receipt, independent scientific result gate, experimental validation, or deployment authorization.

## Exact reviewed objects and scope

- `agent/agent_doc/advice/MATH-79-marginal-contraction_by_gpt.md`, SHA-256 `ceddf20eae453bc649717fec08c4d7cd39dec2a1db0c45d073e65bf4eea15074`.
- `agent/agent_doc/task/task_details/MATH-79.md`, SHA-256 `01848e9f23a1a23300ab017afae070b6aec5d93e01b3e2851799a622e7bb573d`.
- Governance read: `agent/AGENTS.md`, `agent/workflows/dual_main_workflow.md`, `agent/prompts/decision_review.md`, and `agent/workflows/project_document_workflow.md`.

The request's shorthand `task/task_details/MATH-79.md` was resolved to the existing canonical task detail above. No repository files were edited and no tests, CPU science, Lean, model evaluations, or GPU work were run. Review checks finite algebra and the scope/classification of the stated claims. It does not independently authenticate the source-reading logs, external publication metadata, human-guide provenance, historical search results, or prior @1/knowledge-card bytes.

## Mathematical review

1. **Finite Dobrushin contraction: pass.** For a signed difference of probabilities, positive and negative masses both equal `d=TV(p,q)`. For `d>0`, normalizing them gives probability vectors `u,v`. The identity `uQ-vQ = sum_ab u_a v_b (Q(a,.)-Q(b,.))` follows from both normalized sums being one. Triangle inequality gives the claimed row-diameter bound. Multiplying by `d` recovers the contraction. The `d=0` case is separately covered. Finite row-stochasticity makes all measures and TV norms well defined.

2. **Marginal recursion and geometric bound: pass, conditional on the explicit @1 defect premise.** Uniform microstate block-transition defects imply the one-step marginal defect by convexity under the actual microstate law. This does not require the observed process to be Markov. Triangle inequality plus contraction yields `d_(t+1) <= epsilon + rho*d_t`; induction yields the displayed geometric sum. Capping at one is valid for probability TV. The treatment of `k=0`, `rho=0`, `epsilon=0`, and `rho=1` avoids the undefined expressions and correctly separates strict contraction from the linear fallback.

3. **Unique stationary reduced distribution: pass.** A finite probability simplex is complete under TV, the row-stochastic map preserves it, and `rho<1` makes it a contraction. Banach gives existence, uniqueness, and convergence of the reduced iterations. This is a statement about Q, as the document says.

4. **Stationary pushforward bound: pass.** For any stationary original distribution pi, `mu_*=pi R` stays fixed as a marginal under the original stationary chain, so the defect bound gives `TV(mu_*,mu_*Q)<=epsilon`. Comparing with the Q fixed point and contracting gives `(1-rho)TV(mu_*,nu_*)<=epsilon`. The text correctly avoids claiming Q-stationarity of `mu_*`, uniqueness of pi, or convergence of the original chain. No reversibility or detailed balance is needed for this argument.

5. **Path counterexample: pass.** Interpret “单点分区” as singleton blocks, so g is the identity on the two states. Both rows of Q are `(1,0)`, hence rho=0. Both rows of P are `(1-delta,delta)`, so the uniform defect is delta and every postinitial marginal has TV delta from Q. Postinitial states under P are iid. TV from the deterministic all-zero path equals one minus its P probability, namely `1-(1-delta)^T`. The fixed common initial state does not change that result. This directly prevents replacing a trajectory bound by the bounded marginal error. The example also remains correct without a decimal approximation.

6. **Policy counterexample: pass.** Each constant-destination action kernel has row diameter zero. Choosing action a in state a gives the identity kernel with row diameter one. Thus per-action contraction alone cannot certify the state-dependent policy kernel. The text properly limits its certificate to a fixed, certified Q and does not assert a broader adaptive-control theorem.

## Six public analytic examples

1. For rows `(.8,.2)` and `(.3,.7)`, TV row distance is .5. With epsilon=.02 and d0=0, the bound `.04*(1-.5^20)<.04` is correct. The marginal/path distinction is correct. **Nonblocking wording improvement:** the quoted question itself does not specify equal initial macrodistributions; the answer explicitly imposes d0=0. Add “初始宏观分布相同” to the question if refining it, or keep d0 as a stated condition in the answer. If d0 is unknown, the unconditional geometric expression must retain `.5^20*d0`. This is a question-completeness issue, not a false conditional formula.
2. With epsilon=0 and d0=1, d1<=.5 and d0=1 are correct. Exact kernels do not remove the initial discrepancy instantly.
3. The two-state swap has rho=1, unique stationary distribution `(.5,.5)`, and persistent point-mass oscillation. It correctly distinguishes uniqueness from strict one-step contraction.
4. For the symmetric two-state matrix, rho=`1-2a`, stationary distribution `(.5,.5)`, residual a, and actual stationary distance .5 are all correct. The residual bound is exactly .5 in this example; omitting the contraction denominator would be invalid.
5. The iid path probability `1-.99^1000` is correct. Shared seed language does not change the two path laws or their TV distance.
6. The stated two-state Q has stationary distribution `(.6,.4)` because .2 times the first stationary mass equals .3 times the second. With certified epsilon=.02 and rho=.5, the stationary pushforward bound is .04. The text appropriately makes this a model-conditional statement, preserves dimensionless probabilities and fixed step interval, and does not infer real molecular measurements, rates, energies, conservation, or detailed balance.

## Claim and source classifications

The classical finite contraction is attributed to Del Moral and also proved self-contained. The geometric recursion and stationary pushforward calculation are presented as project combinations, not a new named theorem or an attributed Michel/Siegle result. The Michel/Siegle reference is used for the limited distinction between invariance residual and distribution distance. The document explicitly distinguishes arXiv v3 from an unverified formal-publication lead, says publisher access failed, and avoids claiming publication-fulltext inspection or version equivalence. It states the author lecture-notes version without inventing an exact internal revision date. The physical example and task-state migration are conditional examples/proposals, not empirical observations. These classifications are sound as written.

External bibliographic particulars and the cited page/section were not independently reopened in this review. Preserve the producer's actual source retrieval evidence; this approval does not upgrade those particulars to independently authenticated facts. Likewise, no historical data reuse or measured token/performance gain was accepted here.

## Compact seven-area verdict

- **intent: pass** — the supplement addresses bounded long-run marginal error and explicitly refuses unsupported path-level or physical claims.
- **guide: unknown outside review scope** — no human-guide provenance/content authentication was requested or performed here. The inspected document does not authorize guide editing or production changes. This ordinary verdict must not be consumed as a full trusted plan-review approval.
- **assumptions: pass** — finite fixed kernels, all-microstate defects, certified epsilon/rho, stationary original distribution for the stationary comparison, and marginal scope are explicit.
- **prior_results: pass for classification only** — the document avoids treating old CPU samples or corpus metadata as current empirical evidence; the actual search/read receipts were not authenticated here.
- **acceptance: pass for ordinary document scope** — self-contained proof and all six examples are algebraically correct under their stated conditions. No unseen test or scientific acceptance is claimed.
- **risk: pass** — trajectory and policy counterexamples address the key invalid migrations; measurement, floating-point, omitted-state, and real-kernel certification gaps remain explicit.
- **resources: pass for this call** — this review performed only reads, algebraic assessment, and the requested scratch feedback save. No extra reviewer, experimental budget, or production work was initiated.

Recommendation: adopt the ordinary document feedback as approve; optionally clarify the initial condition in example 1. Preserve this feedback in full. Keep all trusted-host, scientific-verification, measurement, and future-budget limitations in force.
