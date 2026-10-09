# Independent plan review — MATH-63

Decision: **revise** (cycle 1). Plan file SHA-256: `0007569278ec5c16f8c574bebf3fbef26493e5639cd9db76018c72f4c1bf9637`.

This review is an actual separate agent invocation examining repository files. It is a content review, not a deployed ReviewSession receipt, managed-dispatch authorization, tmux monitor, or independent result acceptance. No measurements were run; only this review file was written. The original 1800-second and maximum-two-cycle limits remain in force.

## Full review

Read AGENTS.md, prompts/decision_review.md, prompts/review_main.md, project-document/result-reuse/result-validation/dual-main workflows; canonical TASK entry and stable MATH-63 detail; plan, validation plan, contract, prior search/knowledge/decisions and preservation baseline; existing DPI card; guide files. GUIDE.md is present but zero bytes, so its lack of substantive requirements is accurately stated. Its README governs ownership and was respected. No holdout content was read.

The proposed mathematics is sound within its stated finite scope: define finite label Y, observed message T and declared side information Z; use the error-indicator argument for conditional Fano; combine H(Y|Z)-I(Y;T|Z)=H(Y|T,Z) with I(Y;T|Z)<=log2 C; independently prove success<=E_Z(sum of the largest min(C,M) posterior label masses). The latter is a sharper counting converse and must not be confused with achievable success for a restricted encoder observing X rather than Y. M=1 is a separate trivial case. Fixed-length bit/token alphabet counts are valid as cardinality bounds. Length, timing, tools and correlated decoder randomness are part of observations/side information; independent decoder randomization cannot improve optimal classification. No entropy calculation or public finite fixture proves a general theorem or an LLM performance claim.

The producer -> distinct verify_experiment_result -> publish chain has a consistent result contract and actual matching validation-plan hash. Six validation criteria are present; measurement-validity N/A is appropriately permitted for no performance claim. Exact Fraction probabilities, diagnostic entropy tolerance, fresh independent enumeration, 6 backend/query checks, 2-card character closure and preservation hashes are suitable bounded acceptance evidence. The latest FOCUS v1 paper selection must be verified from original dated/versioned text during production; plan approval would not certify that unread source or its empirical claims.

Prior-result search records 90 scanned entries, lexical candidates and missing records. Its errors prevent exhaustive absence claims. Prior decisions appropriately reuse only DPI design/provenance and no old measured data for the new claim. The 227-entry preservation manifest includes the holdout path; hash-only verification must preserve every baseline entry and leave holdout content unread. Unrelated cards, cursors, production runtime, SGLang and human guide files remain protected.

## Seven checks

| Check | Verdict | Reason |
|---|---|---|
| intent | pass | Bounded foundational information-theory enrichment, structural retrieval and a conditional routing transfer fit the stated task; no deployment or compression gain is promised. |
| guide | pass | Empty GUIDE verified; guide ownership and current task constraints preserved. |
| assumptions | pass | Finite labels, declared side information, base-2 units, finite observed message count and separate M=1/variable-length boundaries are explicit. General proofs and cardinality versus achievement must remain separate. |
| prior_results | pass | Actual bounded lexical search and limitations recorded; no stale measurement reused for a new claim. |
| acceptance | fail | Eight cases are required but stable detail enumerates only seven named families; exact query strings and immutable dispatch-input bindings are absent. |
| risk | pass | Public small fixtures, no model/GPU/production changes, single-writer task index, independent downstream acceptance and baseline preservation contain the relevant risk. |
| resources | pass | CPU-only bounded enumeration/retrieval/regression fits 1800 seconds and <=2 cycles; tokens/cost remain unknown, and no deployed supervision is falsely asserted. |

## Blocking findings and minimal changes

1. **Target:** stable MATH-63 acceptance and plan.json. **Problem:** uniform4, uniform8, skew, two-class side information, variable length, binary and M1 give only seven named families despite the eight-case requirement. **Change:** freeze eight unique case IDs with probability/message constraints and expected property. An explicit C>=M saturated-success case would cover a useful missing boundary. **Recheck:** distinct reviewer can map exactly eight rows to independent reference procedures and raw case IDs without selecting an eighth case after observing outcomes.
2. **Target:** plan.json retrieval acceptance and document/evidence bindings. **Problem:** three unnamed structural queries and mutable paths permit accidental protocol drift. **Change:** freeze the exact three theorem-name-free queries, expected new card ID and both file/SQLite Top3 requirement; record current hashes for stable task detail, prior search/decisions/knowledge, validation protocol and preservation baseline. Bind the canonical index snapshot or document its current immutable version. These are content bindings, not invented runtime authentication. **Recheck:** recompute actual plan/evidence hashes and confirm exact-query, six-hit, <=12000-character two-card closure and 34-test requirements remain unchanged.

Approval must await the revised frozen plan. Preserve this first-cycle feedback and the original plan identity when recording a second-cycle review. Failed or incomplete result verification must block publication rather than consume old pass labels. If no trusted runtime host exists, report that limitation explicitly; this review never supplies that host.

## Compact verdict

```json
{"decision":"revise","plan_sha256":"0007569278ec5c16f8c574bebf3fbef26493e5639cd9db76018c72f4c1bf9637","checks":{"intent":"pass","guide":"pass","assumptions":"pass","prior_results":"pass","acceptance":"fail","risk":"pass","resources":"pass"},"blocking_findings":2,"scope":"independent content review only; no deployed ReviewSession authorization"}
```
