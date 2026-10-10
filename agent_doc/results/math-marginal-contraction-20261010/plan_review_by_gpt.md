# MATH-79 ordinary Plan review — full feedback

Decision: approve, scoped strictly to the proposed bounded analytic candidate-document work. This is an ordinary independent read-only review, not a trusted ReviewSession receipt, managed-DAG approval, scientific result acceptance, or new publication authorization. The parent supplied the current user's authorization for candidate documentation and verified direct-main publication; this review neither independently authenticates nor expands that authorization.

Reviewed project: `/workspace/scratch/e902062ab206/agent`. Reviewed stable task: `agent_doc/task/task_details/MATH-79.md`, whole-file SHA-256 `01848e9f23a1a23300ab017afae070b6aec5d93e01b3e2851799a622e7bb573d`. Read the current AGENTS, decision-review, review-main, dual-main and project-document contracts; canonical TASK; MATH-78 stable plan and candidate @1; and all three current run evidence files. GUIDE.md is empty, so it introduces no substantive guide constraint; no human guide write is authorized. I did not run scientific tests or edit repository files. The final @2 candidate, source lock, public questions, navigation and acceptance report do not exist in the reviewed evidence yet and remain subject to the planned second review.

## Seven checks

- intent — pass. The proposed continuation addresses a precise gap in @1: replacing nonexpansive linear-in-time marginal accumulation by a geometric bound under an explicit contraction assumption. It preserves the current bounded learning/documentation objective without promising production compression or token savings.
- guide — pass within the supplied authorization. The actual GUIDE.md is empty; the plan explicitly protects the entire guide directory, old candidates, canonical corpus, runtime, Skill and SGLang. Its unique-author and append-only evidence/coverage treatment are consistent with project governance. No authenticated managed review or scientific backend is claimed.
- assumptions — pass as a plan. The inherited finite fixed P, fixed partition and full-microstate TV defect from @1, together with a legal fixed stochastic Q and Dobrushin coefficient rho < 1, suffice for the proposed marginal recurrence. Q contraction does not require actual Y to be Markov. Finite stochastic P has at least one stationary distribution, and contraction of Q implies a unique stationary distribution; irreducibility or convergence of P is unnecessary. Action/control/switching extensions are expressly excluded.
- prior_results — pass. The actual search records scanned=125, partial=true and 43 missing records; all three returned hits describe corpus integration metadata rather than matching contraction measurements. Rejecting their scientific reuse is justified. The knowledge retrieval's applicability=unchecked is not silently treated as proof: the full sequence-TV card was read, with its exact hash and finite-sequence assumptions. Historical CPU fixtures are not reused as current validation.
- acceptance — pass as a plan. Two bounded ordinary reviews, an explicit proof and boundary treatment, public developed analytic questions, immutable @1 preservation, dual navigation and remote-byte verification provide a reviewable document outcome. The plan correctly disclaims unseen tests, model measurements, formal verification and scientific host acceptance. Final publication must retain those distinctions.
- risk — pass. The central risk is confusing small marginal discrepancy with path-event safety. The proposed iid rare-failure counterexample directly addresses it. Stationary residual and stationary distribution distance are kept distinct; the recently screened paper's publication-version uncertainty is disclosed. No data deletion, production behavior change or unauthorized experiment is proposed.
- resources — pass for ordinary documentation only. The 1200-second limit and two ordinary review cap are explicit. Missing trusted ReviewSession and scientific result verifier are handled by excluding dependent experiments and production acceptance rather than fabricating capabilities or reopening MATH65. This approval supplies no additional review cycle or budget.

## Mathematical acceptance details for the final candidate

There are no blocking findings. The following are concrete nonblocking requirements already implicit in the plan and should be checked in the full-document review:

1. Define rho precisely as delta(Q)=max_(a,a') TV(Q(a,·),Q(a',·)), or explicitly as a certified upper bound on that coefficient, with 0<=rho<1. Retain every inherited object and the all-microstate defect assumption, including 0<=epsilon<=1 and the same fixed sampling interval. Write d_k <= min{1, rho^k d_0 + epsilon sum_(j=0)^(k-1) rho^j}; the geometric closed form follows. State k=0 separately or adopt a clear empty-sum/zero-power convention so rho=0 causes no ambiguity.
2. Show the actual mixture identity mu_(t+1)=p_t PR and mu_t Q=p_t RQ, or its equivalent conditional mixture; convexity yields TV(mu_(t+1),mu_t Q)<=epsilon. Then d_(t+1)<=epsilon+rho d_t. This argument remains valid when projected Y has history dependence.
3. For any stationary pi of P, set alpha=pi R. From TV(alpha,alpha Q)<=epsilon and beta Q=beta, derive TV(alpha,beta)<=epsilon+rho TV(alpha,beta), hence <=min{1,epsilon/(1-rho)}. This is a bound on each stationary pushforward; it does not assert P converges or has a unique stationary distribution. Prove Q's stationary existence/uniqueness using finite simplex contraction or finite-chain existence plus contraction, rather than assuming it.
4. Make the path counterexample share the same premises: on {0,1}, use P rows (1-epsilon,epsilon), Q rows (1,0), identity partition, initial point mass 0, and 0<epsilon<1. Then rho(Q)=0, d_k=epsilon for k>=1, but the event of any 1 in times 1..k has difference 1-(1-epsilon)^k. Therefore the marginal platform epsilon is invalid for that path event. A separate sequence-TV bound may still apply and is not contradicted.
5. Include a rho=1 example showing the geometric denominator is invalid, not merely undefined notation. A slowly mixing two-state Q can demonstrate that an arbitrarily small stationary residual need not imply a comparably small distribution distance when no contraction/mixing constant is supplied. Keep residual units/TV normalization consistent.
6. Preserve source attribution boundaries: the classical source supports the coefficient/contraction result; the aggregation recurrence and stationary pushforward application are project derivations unless a directly read source proves that exact statement. The current run contains retrieval evidence but no frozen source excerpts/lock yet, so the second review must inspect accurate version, locator and actual source support. A failed publisher access cannot certify equality with the 2025 formal article.
7. Before marking completion, preserve @1 and all old evidence byte-for-byte, record both full ordinary feedback texts and their dispositions, bind @2 and navigation paths/hashes, append the correct MATH-79 task/history/coverage outcome, and check only the authorized publication changes after synchronization. Missing current scientific measurements or trusted host receipts must remain explicit deferred scope, not a completed experiment.

## Compact verdict

```json
{
  "decision": "approve",
  "scope": "ordinary bounded analytic candidate-document Plan review only",
  "summary": "The fixed-Q contraction continuation is mathematically coherent and appropriately refuses trajectory and production claims; final proof/source/publication checks remain for the second ordinary review.",
  "checks": {
    "intent": {"status": "pass", "reason": "Precise marginal-error extension of candidate @1 within supplied current authorization."},
    "guide": {"status": "pass", "reason": "Empty GUIDE and protected human-only directory; no conflicting project requirement identified."},
    "assumptions": {"status": "pass", "reason": "Finite fixed kernels, partition, full-microstate defect and Q contraction suffice; Y Markov/P convergence are unnecessary."},
    "prior_results": {"status": "pass", "reason": "Actual partial search and missing records disclosed; metadata and historical CPU data not accepted as current scientific evidence."},
    "acceptance": {"status": "pass", "reason": "Explicit proof/boundaries, public analytic questions and second full ordinary review, with precise evidence limitations."},
    "risk": {"status": "pass", "reason": "Trajectory/stationary/control misuse is explicitly bounded; old artifacts and excluded code remain protected."},
    "resources": {"status": "pass", "reason": "1200 seconds and two ordinary reviews; no unprovided trusted/scientific backend or reopened budget."}
  },
  "findings": []
}
```
