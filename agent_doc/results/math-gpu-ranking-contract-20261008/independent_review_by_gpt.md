# Independent document review: MATH-51

Verdict: **usable-with-scope**, for non-experimental SOURCE/PROOF/DESIGN documentation only. Reviewer context `/root/gpu_ranking_document_review` is separate from producer `/root`. GPU pruning remains a candidate. This is neither experimental result_validation nor Engine/tmux/server authentication.

I read AGENTS.md, decision-review and project-document guidance, MATH-51 detail, independent plan review, the actual report/advice, sources.json, and all three retrieved knowledge entries. The retrieved knowledge contents match all fields in their current corpus entries. Raw wrapper and corpus hashes are recorded separately from the knowledge store's declared semantic hashes; integrity does not establish scientific applicability.

The first manifest was superseded by the producer solely to correct the report's relative source link. The accepted CURRENT manifest SHA-256 is `5b13822ae264279e74e632322a04db7c74c0cfc29124fc24174422c8599c4bc2`. All eleven current manifest bindings match actual bytes. Report/advice contents are identical after normalising only that declared link difference. Current hashes are bound in the accompanying receipt.

## Mathematics and examples

The interval lift is valid: g>=s−δ>=L−δ and g<=s+δ<=U+δ for finite scores and a justified nonnegative itemwise δ. At least k lifted lower bounds reach τ, and corresponding actual g reach τ. Every deleted upper bound is strictly below τ, so its g is below at least k distinct scores and cannot belong to any Top-k solution. Equality must remain; C contains at least k, k=N keeps all, and C=N is a safe loss of benefit. The same stable ID tie rule within retained C recovers the fixed global tie-labelled set when reordering by g.

The document distinguishes prequantization ideal t, stored-real dot product s, dense output g and recomputation c. Equal stored inputs/full dimensions do not entail c=g when shapes or reduction trees differ. For a size-k selected A, c_i−η_i>c_j+η_j for every selected i and unselected j in C entails g_i>g_j; safe screening then gives the global g Top-k. Failed strict separation means unknown. The ζ input/rotation error for t is distinct from δ arithmetic error for g. The proxy ledger ρ+a+δ is a valid triangle inequality. All bounds, endpoint arithmetic, scaling/bias, masks and tie protocols retain the fixed score target and outward-rounding premises; none is certified for an actual kernel here.

I manually reviewed the public examples without numerical execution. The positive example compares 9.7 to 9.3 and 0.1. The permitted g=(9.9,10.05) reverses s=(10,9.95). At binary32 M=2^24, M+1 is an RN-even midpoint rounded to M, while 1−M is exactly representable, giving parenthesisations 0 and 1. For a=1+2^-23, a²=1+2^-22+2^-46: separate multiplication discards the last term and cancels with b; FMA returns the representable 2^-46. Flushing x=2^-149 in x·1 gives error x>u*x, rejecting the relative model. These are hand algebraic witnesses, not measured outputs.

Siemens times volts gives amperes; δ/L/U share amperes. The bilinear mapping is valid but does not certify sensor accuracy, input synchronisation or physical modelling. Sample maxima/quantiles and mean residuals do not supply deterministic itemwise certificates. Invalid bounds, NaN, overflow or unknown arithmetic correctly require retention/fallback.

## Actual source scope

I read native abstract/submission text and recent paper full-text extracted lines 440–570, including R1 per-operation IEEE FMA, R2 no runtime autotuning, R3 shape-fixed contiguous split-K with ascending second-stage reduction/no atomics, and R4 decode-bucket invariance for batch sizes 1–64. The abstract confirms authors, v1 and 2026-09-22 03:32:40 UTC. It carries no journal/acceptance information; the narrow preprint statement is supported. This is not full experimental review or replication, and its linear-layer construction supplies neither δ nor whole-attention certification. Paper performance is not represented as this project's measurement.

Actual native HTML SHA values match sources.json: abstract `37438cea42dfa0e6b8248eae8314f2f62fe54c57f86bd086da6e55a267999248`; full text `3484504d7dad53f27a72d35fd91681bfb6d98137120472e36d54d216097d7641`; PTX `0aa31c15735a30b5d7c0fa1fe02570dcd37fe80800afca74bcc96c9132b81fed`.

I read PTX 9.4 extracted lines 45229–45269: f16 and bf16/tf32 MMA have unspecified accumulation order, rounding and subnormal input handling. Nearby f64 has explicit FMA-like semantics, supporting the report's instruction-specific qualification. Scalar add.ftz.f32 at lines 12255–12288 flushes subnormal inputs/results and allows fusion of unqualified mul/add. I independently opened the official NVIDIA Floating Point and IEEE 754 page, displayed version 13.4, and read §2.2/§2.3/§4.4: fixed format/mode semantics, one-rounding FMA, nonassociative sums and FTZ flags. Historical hardware prose was not treated as current hardware evidence.

## Acceptance limits

No blocking findings. Adapt/defer/reject decisions remain scoped. Future GPU verification separates diagnostic finite comparisons from deterministic enclosure proof, distinguishes g/s from c/g, freezes input/shape/software versions and counts fallback/cache/synchronisation in fair comparisons. It reserves model quality and end-to-end gains for future same-budget measurements.

Acceptance cannot certify real kernel intervals, production behaviour, GPU/model accuracy, unseen retrieval, token savings, e2e benefits, formal proof or corpus publication. This review executed no numerical, model, GPU or regression experiment; it performed source reads, metadata/content/hash comparisons and wrote only these two assigned records. Changed document/source/manifest bytes require renewed independent review. Main agent retains TASK/state/publication ownership.
