# Independent plan review — MATH-48, cycle 1

Verdict: **revise**. Two bounded edits are required before implementation. This is an actual independent host collaboration review; it is not a deployed Engine or ReviewSession receipt.

## Findings

1. **F1 — causal completion predicates (blocking).** `dag.json` gives produce, verify and publish the same condition: accepted evidence and remote code SHA. Produce must finish by freezing the executed code, inputs/configuration, raw outputs and pending manifest; verify must finish by returning an independently accepted bound receipt; only publish needs the verified remote SHA. Otherwise the predecessor stages depend on their downstream publication.
2. **F2 — fixed-truncation minimum norm (blocking).** For a fixed supported truncated matrix Cr, define Pq=L+L and Pk=RR+. Require Pq Cr Pk=Cr, then M0=L+CrR+ has L M0 R=Cr and rank(M0)=rank(Cr)≤r. Every lift of this fixed Cr is M0+N with LNR=0. Such an addition stays rank feasible only if rank(M0+N)≤r. The supported M0 block is Frobenius orthogonal to the invisible blocks, so M0 is the unique minimum-Frobenius-norm lift of this fixed Cr. Tied singular values can change the optimal Cr and its lifted norm; do not claim a minimum norm over every optimal truncation.

## Mathematical assessment

The intended exact identity is sound under independent q/k, finite noncentral second moments, fixed H and an integer rank budget. C=LHR is supported. A supported truncated SVD attains the global unconstrained rank approximation lower bound and admits the rank-preserving pseudoinverse lift. A reduced support basis avoids ambiguities in zero singular vector choices. Zero support, zero budget and full effective rank remain valid boundary cases. The minimum score risk is the tail singular value square sum. Arbitrary correlated pairs require fourth-order joint information, so the independent-product formula must be rejected there. Ridge defines a different objective, and tiny positive eigenvalues remain positive in the mathematical claim.

Higham's author exposition directly supplies SVD/MP definitions and minimum-norm least squares. Bindel's lecture directly states truncated-SVD Frobenius optimality; its later dimensional typos should not be copied. I also read the versioned IO-SVD original HTML §3.1 Eq2–8 and metadata: its reduction explicitly uses moment decoupling and damped positive definite moments. It supports the reference distinction, not an attribution of this project's singular-support theorem. The versioned metadata observed only v1 dated May 15, 2026; no final venue is asserted. The inaccessible 2609.15838 source stays excluded.

## Seven checks

- intent: pass — singular support is the missing case of the existing bounded SPD interface.
- guide: pass — empty GUIDE and the explanatory README were read and left untouched; plan evidence hashes match.
- assumptions: fail — clarify fixed-Cr minimum norm and rank-feasible additions (F2).
- prior_results: pass — only definitions/source pointers are reused; partial legacy search is disclosed.
- acceptance: fail — remove circular stage completion predicates (F1); the six-domain CPU/retrieval protocol is otherwise scoped appropriately.
- risk: pass — prohibited production, SGLang, guide and historical evidence edits remain excluded.
- resources: pass — declared 2100-second wall budget, 150-second test caps, installed CPU libraries and bounded revisions support this small task; no model/GPU experiment is proposed.

## Evidence and limits

The companion JSON contains exact SHA-256 bindings for the current full plan, DAG, protocol, source/search records and cards. Every declared plan evidence reference was recomputed and matched. I independently ran the file-backend structural knowledge query and loaded the relevant original card bodies. No experimental result is accepted by this review; the independent executed-code/raw-data gate must still run before publication. Character and CPU-time diagnostics do not imply token or performance gains. Parent must retain this full feedback before patching and present a newly hash-bound version for same-context reread.
