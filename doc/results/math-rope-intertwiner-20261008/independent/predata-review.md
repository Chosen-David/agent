# Independent predata review: MATH-41 / MATH-42

Reviewer: separately dispatched host-context agent `/root/rotation_verifier`; producer is `/root`. This is a bounded direct-host review, not a ManagedEngine/protected review receipt. No experiment data were produced or consumed for this decision.

Decision: approve the stated bounded 32-case CPU structural experiment for subsequent independent result validation. This does not accept future data or certify model quality, performance, deployment, formal proof, or universal correctness.

Read AGENTS.md, decision_review.md, project_document_workflow.md, result_validation_workflow.md, knowledge_access_workflow.md, result_reuse_workflow.md, MATH-41/MATH-42 detail plans, config.json, validation-plan.json and prior-results.json. The reviewer writes only this run's independent/ directory. Main AI retains the only task index and card author role.

## Mathematical review before data

For real-linear S:C→C, S(z)=az+b conjugate(z) is unique. Evaluating both compositions gives coefficients a(e^(i theta)−e^(i phi)) and b(e^(−i theta)−e^(i phi)); their simultaneous vanishing is necessary and sufficient. This supplies an elementary independent derivation, requiring no complex-field Schur lemma to infer a real scalar commutant.

On 0<theta,phi<pi, equal frequencies permit precisely complex-linear maps, and unequal frequencies permit only zero. Signed-opposite frequencies permit antilinear maps. All frequency comparisons for integer positions are modulo 2pi. At theta=phi=0 or theta=phi=pi both coefficients are free, so the real 2×2 intertwiner is arbitrary; different scalar groups do not mix. These degenerate cases override a simplistic signed-frequency classification.

The real Frobenius norm of z↦cz+d conjugate(z) has square 2(|c|²+|d|²). Thus the proposed defect identity is correct with delta-plus=|e^(i theta)−e^(i phi)| and delta-minus=|e^(−i theta)−e^(i phi)|. Dividing by min(delta-plus,delta-minus) is valid only when both gaps are strictly positive. Zero or small gaps require explicit handling; near resonance the bound can be large.

Orthogonality permits a telescoping sum for positive integer m with norm bounded by |m| times the generator defect. For negative m, the inverse defect is −R_phi^(−1) E R_theta^(−1), which has the same Frobenius norm, then the same telescoping argument applies. m=0 has zero defect. A condition for all integer positions implies the generator condition because m=1 is included; a selected position set lacking m=1 does not imply it.

For multiple blocks each block pair satisfies this same equation. Equal-frequency multiplicities admit a complex matrix and can be reduced equivariantly, but an inner-product-preserving map on an entire d-dimensional real domain must be injective and therefore cannot land in real dimension r<d. A restricted exact claim must name an invariant subspace and its dimension; sampled finite inputs do not establish a global guarantee. NoPE belongs to the theta=0 trivial group; it cannot mix equivariantly with nontrivial frequency groups.

## Knowledge and prior-result access

Actual reviewer CLI query: `python -m agent_runtime.knowledge --root knowledge search 'rotation intertwiner commutant frequency RoPE real Schur' --limit 5`. Files-lexical-v1 snapshot fc95818f63ca92ebf996b00fad329fc025ceeb23510d33952de98e7bec83719f returned math.hermitian-spectral-schur plus unrelated Schur-complement/Jordan/attention candidates. Actual show: `python -m agent_runtime.knowledge --root knowledge show math.hermitian-spectral-schur`. Read version 1, sha256 d9b71b5d13923136c8fec1a36a6eaff3fc0be781c6f1ba5cd46aa7166fe363c1. This card concerns unitary triangularization, not representation-theoretic Schur's lemma, and is rejected as a classification authority. Its real-rotation boundary is consistent with the elementary derivation above. No requisite knowledge refs were supplied by the producer; result handoff must bind the actual new card/corpus and references once frozen.

Read actual prior-results.json: two bounded searches found only historical-vex-softmax-rope-20261007 with unknown stored validation; eight incomplete result-record errors were preserved. This is no evidence of exhaustive search or reusable classification data. Reviewer additionally queried `python scripts/result_store.py --root . search 'RoPE rotation intertwiner' --limit 5 --max-scan 200`; its actual returned candidates/errors were inspected before any new experiment. No prior measurements are accepted for reuse.

## Result-validation conditions

The six declared criteria are retained without postdata relaxation. The repeated procedure text is broad but binds fixed 2e-12 float tolerance, exact Fraction branches, code/input/raw agreement and complete structural retrieval/token accounting. measurement_validity disallows N/A: review the actual retrieval and token-accounting protocol as structural measurements, exclude latency/model savings claims, and report any missing mandatory criterion as inconclusive.

Future review requires the frozen card, executable code, inputs, raw cases, outputs, environment and manifest; exact rational rotations must test full real-linear solutions rather than floating-point proximity alone. Boundary fixtures must cover distinct, signed-opposite, zero/pi, integer aliases, mixed blocks, rank obstruction and approximate finite horizons. Float tolerances must be justified for the bounded input scale, and equality/zero-gap cases must not divide by zero. Independent reruns will write only independent outputs and must preserve producer raw bytes.

The externally referenced MIT/Etingof source and recent-paper source have not yet been provided to this reviewer as frozen source artifacts. Their precise attribution and applicability remain result-review checks. No paper result is needed to justify the elementary algebra above. Awaiting the producer's frozen artifact handoff.
