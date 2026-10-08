# Independent plan review — MATH-48, cycle 2

Verdict: **approve** the bounded version 2 plan. Both blocking findings are closed. This approval covers planning and permits the already authorized implementation to proceed; it does not accept experimental results or establish a deployed Engine/ReviewSession gate.

## Revisions checked

**F1 closed.** I reread the full revised DAG. Produce finishes with frozen code/input/raw/output/environment and a pending manifest; verify finishes with actual independent six-domain usable-with-scope acceptance; publish refreshes main, publishes without force and verifies the remote SHA. The three identical result contracts preserve producer → independent verification → publication, without a downstream publication condition on either predecessor.

**F2 closed.** The version 2 proof_constraint explicitly binds M0=L+CrR+ as the unique minimum-Frobenius-norm lift of each fixed supported truncated Cr. Invisible additions satisfy LNR=0 and must also satisfy rank(M0+N)≤r. Tied different optimal Cr can yield different minimizers, and no minimum norm across every tied Cr is asserted. The unchanged stable task Plan contained neither the erroneous completion predicates nor an unqualified global minimum-norm assertion.

## Mathematical assessment and result requirements

The exact independent-product MSE identity holds with finite noncentral PSD moments and fixed H. Write L=Sq^(1/2), R=Sk^(1/2), Pq=L+L, Pk=RR+ and C=LHR. A supported truncation satisfies PqCrPk=Cr. A reduced support SVD makes this explicit, including zero/tied singular-value boundaries. Then LM0R=Cr and rank(M0)=rank(Cr)≤r; every other fixed-Cr lift is M0+N with LNR=0. The Frobenius orthogonality of the supported and invisible matrix blocks proves the fixed-Cr minimum norm. The ordinary low-rank approximation lower bound applies to all LMR, and the supported truncation attains it, giving the tail singular value square sum.

The producer must show these arguments in the new card and retain rank, zero-support, full-effective-rank, ties and near-singular checks. Fixtures supplement the proof. Correlated pairs, centered covariance replacement, ridge and changed supports remain rejection boundaries or counterexamples; no true paired attention, top-k, model output or speed benefit follows from the score proxy.

## Seven checks

- intent: pass — the bounded singular case fills the existing SPD card's stated exclusion.
- guide: pass — empty GUIDE and explanatory README are read-only and correctly bound.
- assumptions: pass — independence, noncentral finite moments, fixed H, supported lift and qualified minimum norm are explicit.
- prior_results: pass — definition/source-only reuse and partial legacy search remain accurately disclosed.
- acceptance: pass — causal predicates and the identical frozen six-domain result contract are consistent.
- risk: pass — no production, SGLang, guide or historical evidence changes are approved.
- resources: pass — the fixed 2100-second wall budget, 150-second CPU test caps, installed libraries and bounded revisions suffice for this scope; no model/GPU experiments.

## Source, hash and host limits

The JSON binds the actual full v2 plan and DAG hashes, updated source metadata, protocol, prior query records and loaded card bodies. I recomputed every declared plan evidence hash and checked the unchanged validation-plan hash and equality of all three result contracts. The complete v1 revise receipt is preserved and hash-linked.

I independently queried the local file backend and read the weighted-bilinear, low-rank-SVD and pseudoinverse cards. I read the primary Higham/Bindel pages and versioned IO-SVD HTML §3.1 Eq2–8 and metadata. IO-SVD explicitly uses moment decoupling and damping; it is not the source of this exact PSD-support theorem. The inaccessible 2609.15838 source remains excluded.

This is an actual separate host collaboration context and same-context bounded revision review. No repo Engine/ReviewSession or remote supervisor deployment is asserted. No result code, raw numeric data or retrieval output is accepted here. Independent executed-code/data review must still bind frozen evidence and run before publication. Public regression fixtures do not imply unseen/model/token/performance acceptance.
