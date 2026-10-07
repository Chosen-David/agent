# Scoped review — KB-LIVE-1

Review date: 2026-10-07. Decision: **needs_revision for provenance/assumption reporting; mathematical claims pass under the stated Euclidean interpretation.** Provisional correctness and reproducibility rubric; no venue or full manuscript assessment.

## Materials and actual actions

Read trusted task.json, request.json and plan.json; AGENTS.md/TASK.md and the assigned research-review guidance. Consumed seq 1 with the actual Mailbox CLI using consumer-owned request and corpus. Read every artifact returned in consumed-handoff.json, including answer, knowledge usage, local retrieval output, verification script and output. Independently searched the current knowledge corpus, read all three relevant entries and prerequisite closure through the CLI, and executed independent_verify.py. No repository tests or previous evaluation documents were read or run. TASK.md contains historical summaries; linked historical artifacts were not opened.

## Scientific assessment

For any selected i and unselected j, write e_i = q^T(khat_i-k_i). Under a common-dimensional Euclidean norm and unchanged q, Cauchy–Schwarz follows by minimizing the nonnegative squared norm ||q-t d||² in t (zero d is trivial). Hence |e_i| <= 3*0.02 = 0.06. The perturbed cross-boundary difference is at least 0.15-|e_i|-|e_j| >= 0.03 > 0. This proves unchanged membership for every such pair and does not prove internal ordering. The strict inequality handles boundary ties correctly.

For the arithmetic mean of individual error norms, total error is at most n*0.02, so pairwise score loss is at most 3*n*0.02. The given values certify n=2, while the producer's n=3 example has exact mean 0.02, original scores (0.15,0,-3), and replacement scores (-0.03,0,-3), strictly changing top-1. A second independently constructed example splits error 0.03 across both boundary keys and also reverses the pair with mean 0.02. Failure of the sufficient bound is not itself a reversal proof. No unjustified sqrt(2)*0.06 global-norm certificate was applied.

The nine reviewer-owned rational checks pass (REV-C01–REV-C09, independent-output.json). Finite checks verify arithmetic and counterexamples; the argument above supplies the general inequality reasoning. Producer checks were not treated as truth merely because they passed or had matching hashes.

## Required reporting repair — REV-F001

The producer knowledge-use.json says input_version `synthetic-dot-product-task-v1`; the trusted request/handoff says `synthetic-dot-products-v1`. Also, answer.md and knowledge-use.json call a 2-norm and n/k constraints explicit task givens, whereas the trusted task.json only says norm and a top-k boundary gap. The Euclidean interpretation is reasonable, but it must be distinguished from the exact supplied evidence. The producer already makes the arithmetic-mean interpretation clear.

This is a minor, confirmed traceability and assumption-reporting gap, not a counterexample to the conditional mathematics. Close it by preserving the old records and adding a precise source-version mapping or new corrected record, explicitly identifying adopted interpretations, then issuing a new immutable handoff for independent recheck. Root owns repair; reviewer does not edit producer files. findings.json records stable ID, evidence, and acceptance conditions.

## Boundaries and next action

All three required/used entry IDs, versions and content hashes agree in the current independent retrieval. Whole-corpus snapshot changed; this alone does not establish staleness of these entries and was not counted as a defect. Local source metadata is not fresh external source verification. No network, formal prover, model quality comparison, performance claim, full manuscript/PDF review, daemon or server deployment is involved.

Root should resolve REV-F001 and publish a new event. Receipt for seq 1 is needs_revision, exported after ACK through actual Mailbox status. The original event and producer artifacts remain unchanged. Repository requirements implicated: KB-ACCESS-01 (actual retrieval and applicability evidence) and KB-ACCESS-03 (actual scoped role use). This review does not complete the broader root requirements.
