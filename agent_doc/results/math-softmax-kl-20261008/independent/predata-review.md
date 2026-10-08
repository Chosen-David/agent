# Independent predata review

Reviewer: `/root/softmax_kl_verifier`, independently dispatched host collaboration context, distinct from producer `/root`. This is bounded direct-host review, not a protected ReviewSession or ManagedEngine deployment.

Decision: approve the proposed single-card, 64 public CPU fixture plan with tolerance 2e-11 and producer → actual independent verifier → publication dependency. No acceptance of data or publication is given before the frozen executed artifacts are inspected.

Read AGENTS, decision-review, project-document, result-validation, knowledge-access and result-reuse workflows; MATH-39/40 and unique TASK entries; proposed config/validation plan/prior search. No writes to TASK, card, guide or producer paths.

Independent mathematics: for finite logits on one nonempty fixed support, KL(p||q)=A(s+e)-A(s)-p·e and the integral remainder with weight (1-u) are correct. Popoviciu variance and the Hessian spectral bound yield R²/8 and ||e−mean(e)1||²/4. If every path probability is at least m, minimizing weighted squared deviations yields variance ≥m||e−mean(e)1||² and therefore KL ≥m||e−mean(e)1||²/2. Density ratios along the path lie in [exp(−R),exp(R)], giving the same ratios for directional variance through its minimum-over-centers definition; integrating gives 0.5 exp(−R)Var_p(e) ≤KL≤0.5 exp(R)Var_p(e), where R=osc(e).

Required boundaries: n=1 and constant errors have zero KL; saturation invalidates a global positive Euclidean lower constant; changing masks can give infinite KL; temperature τ>0 scales logits/errors by 1/τ; numerical exponent underflow is a floating boundary, not a failure of real full support. Numerical fixtures support bounded development checks, not formal certification or universal floating stability.

Knowledge access: actual files-lexical CLI query `python -m agent_runtime.knowledge --root knowledge search 'softmax KL Fisher' --limit 4` returned existing `math.softmax-barycenter-error` v1 sha256 `269f488663b18bde24bac5f9d15121d5b589d06c0b1e16b2ad82430d6de5f160`, snapshot `1ee332b3173fb2652610679ea29905f0ec22ad195fe098da7ac90fba27596e0b`. Read its matching Markdown, including sharp tanh TV, finite support and temperature exclusions. Reuse as a relation, do not duplicate it. Existing measurements do not establish the new KL identities.

Prior search reports seven missing record errors; this is bounded incomplete retrieval, not proof of comprehensive absence. Plan measurement_validity forbids N/A; actual structural retrieval and serialization-cost accounting must therefore be independently checked. Serialized local token counts must not become model tokens, billing, savings or performance claims. Full inaccessible PDFs must remain explicitly inaccessible; self-contained derivations can support mathematics independently without promoting a metadata page to full-paper reading.
