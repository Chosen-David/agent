# Retrieval rank-truncation check

Task ID: `knowledge-forward-a`. Task refs: `report.md`, `refs.json`, `evidence.txt`, `check.py`.

**Result:** A gap of 0.18 guarantees the selected Top-k set is unchanged under exact truncated SVD, the stated Euclidean query bound, and unchanged queries. A gap of 0.10 does not guarantee this: both changed and unchanged sets are possible. Average error 0.01 alone is insufficient for a deterministic guarantee. No acceleration was measured or established.

## Model and prerequisites

Let K be a finite real d-by-n matrix with keys as columns; q is a d-vector with ||q||₂ ≤ 3. Let K_r retain the r largest singular values, and let s=Kᵀq and ŝ=K_rᵀq. For 1 ≤ k < n, the gap is Δ=s_(k)−s_(k+1), using decreasing score order.

| Knowledge assumption | Task evidence | Assessment |
|---|---|---|
| Exact truncated SVD, singular values descending | Rank truncation and first discarded singular value supplied | Interpret as exact truncated SVD; an arbitrary rank-r approximation needs its own residual bound |
| Fixed queries, Euclidean inner products and norms | Kᵀq, fixed queries, norm ≤3 | Satisfied under Euclidean norm interpretation |
| Spectral residual δ=0.025 | First discarded singular value | Satisfied by exact truncated SVD |
| Every score has bounded absolute error | Derived below, not inferred from an average | Satisfied for the SVD setting |
| Strict Top-k boundary gap >2ε | 0.18 or 0.10 | Satisfied for 0.18 only |
| All queries covered by a single set guarantee | Norm bound alone | Each query must also have the specified boundary gap |

Internal order within the selected set need not remain unchanged. The analysis does not assume a numerical floating-point or approximate-SVD error is zero in an implementation: those errors need a certified bound if a machine-level guarantee is wanted.

## Actual local retrieval and source handling

Ran the skill's offline lexical search with `向量 压缩 点积 排名 误差`, limit 3, against `/tmp/knowledge-forward-a/skill/assets/knowledge`. It returned `math.cauchy-schwarz`, `math.low-rank-svd`, and `math.topk-margin`. Read all three full `show` results. Top-k has a strong prerequisite on Cauchy–Schwarz, which was read in full; the other two have no strong prerequisites. All three are directly applicable; no retrieved candidate was treated as correct merely because of its retrieval score.

Read `SKILL.md`, `references/execution.md`, `references/workflow.md`, and the knowledge format contract. The local entries identify Cornell low-rank lecture notes and Wisconsin inner-product notes; Top-k is explicitly a local derivation, not an attributed verbatim external theorem. External sources and Lean were not accessed or executed. Metadata's source-check claims are inherited provenance, not a new verification by this run. No repository tests, rubrics, or other agent outputs were read.

## Derivation

By the truncated-SVD spectral residual result,

||K−K_r||₂ = σ_(r+1) = 0.025.

For every column index i, Cauchy–Schwarz and the operator norm give

|s_i−ŝ_i| = |qᵀ(K−K_r)e_i| ≤ ||q||₂ ||K−K_r||₂ ||e_i||₂ ≤ 3×0.025 = 0.075 = ε.

For every original selected item i and unselected item j,

ŝ_i−ŝ_j ≥ s_i−s_j−2ε ≥ Δ−0.15.

Thus Δ=0.18 leaves a strictly positive lower bound 0.03 and preserves the set. At Δ=0.10, this sufficient condition fails; failure of a sufficient condition alone does not imply a changed set.

The matrix structure permits a sharper pairwise bound: |qᵀ(K−K_r)(e_i−e_j)| ≤ 3×0.025×√2 ≈ 0.106066. This is an independent direct consequence of the same operator norm, not a new retrieved theorem. The 0.10 gap also fails this sharper sufficient condition.

## Executed concrete checks

`check.py` uses Python's standard library and assertions. Full command/output evidence is in `evidence.txt`.

An actual SVD-compatible counterexample for gap 0.10 uses r=1, k=1, two keys, U=I, and orthonormal right singular rows:

v₁=(sin θ, cos θ), v₂=(cos θ, −sin θ), θ=π/4−0.1.

Take singular values (0.15003385983535586, 0.025), q=(0.2447447650104062, 2.99), and

K = [[0.09496862864437114, 0.11615127494135712],
     [0.019354176961923663, −0.015824532666923956]].

The query norm is 3. Original scores are (0.0811120638170789, −0.018887936182921103), with gap 0.10. Rank-one truncation gives (0.023243074700927145, 0.02842741649118153), reversing the winner. Orthogonality, singular-value ordering, norm, original gap, and reversal were checked. This demonstrates an actual possible failure, not just failure of the generic criterion.

An unchanged example at gap 0.10 is K=diag(0.1/3,0.025), q=(3,0), r=1. Before and after scores are (0.10,0). Thus a claim of inevitable change would be false.

For average absolute score error 0.01 alone, take n=20, k=1, scores (0.18,0,−1,…,−1), and errors (−0.10,+0.10,0,…,0). The average absolute error is exactly 0.01, but the new leading scores are (0.08,0.10), changing the selection. Replacing 0.18 by 0.10 also flips the selection. This average-only example intentionally does not retain the 0.025 spectral residual guarantee; it addresses the scenario where the only evidence is the average measurement. If the original residual certificate remains available, it still guarantees the 0.18-gap case regardless of an additional average observation.

A mean signed error is even less useful because of cancellation; sample means need not apply to unseen scores. If a full-population mean absolute error and n are known, then max error ≤n×mean, but n and a sufficiently small resulting bound are needed. A certified per-score maximum, per-boundary-pair perturbation bound, or direct full-score ordering check could provide the missing evidence.

## Evidence needed for acceleration

Factored scoring evaluates V_r Σ_r U_rᵀq in roughly O(dr+nr) arithmetic, versus O(dn) dense scoring. This is a cost hypothesis, not timing evidence. Storing a reconstructed dense K_r and multiplying it densely may save no work. Top-k selection still processes n scores unless the algorithm also changes that step.

A defensible acceleration claim needs a concrete implementation and baseline on the same hardware, d, n, r, dtype, batch size, query distribution, and quality criterion. Measure end-to-end latency and throughput with appropriate warmup and device synchronization, repetitions and variability; include projection, memory movement, score materialization, and Top-k. Record preprocessing/SVD time and storage, and the number of queries or updates across which preprocessing is amortized. Compare total baseline cost N*T_dense with T_decomp+N*T_factored, including maintenance costs and any differences in caching. For literally reused fixed queries, a cached-score baseline may also matter. Report accuracy/selection checks beside timing. No such measurements were supplied or executed, so “accelerates retrieval” remains unsupported, not disproved.

## Validation and limitations

The local `check-refs` command returned `valid: true` for all three references and their full strong-dependency closure. This validates published content identities and prerequisites only, not mathematical applicability. Numerical checks passed. The general guarantee follows from the derivation; finite examples are not a formal proof. No performance experiment, external source re-verification, full retrieval-system benchmark, or formal proof was performed.

No skill files were modified. There are no blocked mathematical steps for this task. The parent agent must decide how to integrate this forward-test output; any real implementation-level guarantee or speed claim still requires its numerical-error and benchmark evidence.

## Actual knowledge_refs

```json
[
  {
    "id": "math.low-rank-svd",
    "version": 1,
    "sha256": "a62b7eb5702662d678165acad4d439826ac79260bc083dda8b8f7763681621b8"
  },
  {
    "id": "math.cauchy-schwarz",
    "version": 1,
    "sha256": "348bb06707e13b217534f030e094e381c236c0fe3ee12e11d15a817733e9716c"
  },
  {
    "id": "math.topk-margin",
    "version": 1,
    "sha256": "8ec1eb1965bfe909c5d0033901ee0237b3cbbb6e2cf34c799ee05d8ac8035792"
  }
]
```
