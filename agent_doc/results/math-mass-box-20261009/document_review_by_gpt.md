# MATH-57 independent completed-document review

Verdict: **approved-with-scope**. No blocking finding for the frozen document-only derivation and conditional migration candidate.

Document: `agent_doc/advice/全局注意力质量区间与near_far参数证书_by_gpt.md`  
Document SHA-256: `7062518f210ea8e8a6309022fe7e08e73dc1f14671d48c21cfca8196f2899f58`  
Plan SHA-256: `abf02e72a7de15889698bb3b021ccca2c32c5d94371b132b29d5021d5015b360`.

Independent role: host-invoked `/root/mass_box_document_review`. This is actual local completed-document review, not a signed ReviewSession, formal proof, executed numerical-result acceptance, GPU/model certification or deployed integration. The reviewer read AGENTS, decision/project-document governance, MATH-57 detail/index, frozen plan and plan review, actual advice, sources, usage records and canonical KnowledgeStore premises. Only the two review outputs were written. No experiment, regression suite or production change was performed.

## Actual checks

- **proof_and_boundaries**: pass: A>0, B>=0; monotonicity gives S-lower/C-upper minimum and reversed maximum; both endpoint vectors belong to the independent box. S=J gives 1, empty S gives 0 with pruning rejected. Singleton J and point boxes specialize correctly.

- **box_vs_reachable**: pass: sharpness explicitly belongs to independent boxes; correlated reachable logits only inherit an outer bound. z1=z2 example correctly exhibits strict looseness.

- **full_denominator**: pass: complete finite nonempty legal deduplicated J, finite ordered logits, shared target/scaling and positive temperature; illegal mask entries removed. Candidate-only mass is explicitly rejected.

- **rounding**: pass conditional: shared finite shift and outward subtraction, certified exp and nonnegative summation, finite endpoints and division premises required. Lower aL/up(aL+bU) and upper aU/down(aU+bL) follow ratio monotonicity, provided denominators used are positive and final division is directed. aL=0, unavailable positive upper denominator and empty event/complement receive conservative separate treatment. FTZ/overflow/unknown primitives cannot certify.

- **local_output**: pass conditional: fixed values/W and valid finite diameter D yield D(1-m_lower). Triangle addition D*tanh(w/4) is conservative since the same-S diameter is at most D. No nonlinear/deep/autoregressive or e2e claim follows.

- **near_far**: pass for document candidate: positional far differs from score-importance retention; all legal J and actual retained S are required per configuration; original alpha/beta/gamma semantics must be frozen. Concrete positional partition remains a consumer prerequisite.

- **source_claims**: pass: independently opened Vertex-Softmax v1 Sections 2/3/6 and Appendix D and CUDA13.2.0 Sections 5.5.9.1/2. Local mathematics is not attributed as novel and numerical caution is correctly preserved.

- **knowledge_pins**: pass: KnowledgeStore(knowledge) semantic metadata+Markdown refs and bodies matched all three saved usage records; raw JSON file SHA is not this semantic ref format. Each requires list is empty.

- **manifest**: pass: all six frozen artifact byte hashes match document_manifest; frozen plan hash matches plan-review approval.

## Primary-source readback

[Vertex-Softmax v1](https://arxiv.org/html/2605.10974v1), Sections 2/3, defines a fixed-coefficient independent finite score-box objective; indicator coefficients recover the event-mass special case. Section 6 restricts local exactness and identifies discarded correlations/coupling. Appendix D explicitly separates real-arithmetic soundness from ordinary PyTorch evaluation. The [v1 abstract record](https://arxiv.org/abs/2605.10974v1) was also opened. Formal publication was not established by this review.

[CUDA13.2.0](https://docs.nvidia.com/cuda/archive/13.2.0/cuda-programming-guide/05-appendices/mathematical-functions.html), §5.5.9.1, lists directed basic intrinsics. §5.5.9.2 describes single-precision intrinsic errors as observed, nonexhaustive and unguaranteed. This supports rejecting a guessed fixed-ULP exponential certificate from that table.

## Concrete nonblocking findings and implementation boundary

- **I1 (nonblocking-consumer-prerequisite; 局部输出与逐层求解接口)**: No implemented final local_error_upper arithmetic is certified in this round. An implementation must evaluate 1-m_lower, D multiplication, optional tanh term, extra errors and their sum outward; ordinary nearest-rounded evaluation may underestimate the bound. Validate D/w bounds and threshold comparison against the same target. Carry into any implementation/acceptance contract; no frozen-document edit required for document-only approval.

- **I2 (nonblocking-consumer-prerequisite; 一般推导 / near-far migration interface)**: The attachment preserves positional near/far semantics but deliberately does not instantiate a distance rule. A consumer must bind the exact position rule, threshold/boundary convention and mask to F subset J and N=J\F (or document another actual partition), with provenance; mass formulas never choose that rule. Freeze concrete partition and configuration provenance before implementation or numerical acceptance.

- **I3 (minor-source-metadata; sources.json CUDA read_extent)**: The observed-error-not-guaranteed caveat independently verified at §5.5.9.2; read_extent also labels an error caveat as §5.5.7. The advice itself correctly places the intrinsic ULP caution in §5.5.9. Use §5.5.9.2 as the exact caveat locator in subsequent consumer evidence; no mathematical revision required.

The document may be published as the task-level conditional attachment after the parent records this review. This verdict authorizes no certified local-error computation, near/far deployment, published knowledge card, autonomous retrieval evaluation, regression/GPU/model run, token savings, speedup or end-to-end quality claim. Those remain separate work with their own actual inputs, implementation and independent acceptance. A changed document hash requires review reconciliation.
