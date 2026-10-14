# Independent plan review

Verdict: **approve** for the bounded local repair and data production in this plan; result acceptance and publication remain pending. Review object: `plan.md` SHA-256 `0391ae9da02904418ff5eb1486598f1991f9819d273631d4027c8a3d2206d834`; actual read hashes are in `plan-review-evidence.json`.

| Check | Verdict | Reason |
| --- | --- | --- |
| intent | pass | Restores existing fenced-code heading suppression contract using a small correction; no algorithm, model or novel research claim. |
| guide | pass | GUIDE.md is actually empty (0 bytes), no substantive human guide constraints inferred. AGENTS read; guide directory excluded from writes. Parent is sole source/task writer. |
| assumptions | pass | Current source opens any matching fence prefix and closes equal/longer same-character prefix regardless of tail. CommonMark 0.31.2 §4.5 independently retrieved: closing tails permit only spaces/tabs; backtick opening info forbids backtick. Implementation/expected semantics restricted to this extractor's top-level ATX heading scope. |
| prior_results | pass | prior-search contains 230 scanned, partial=true and missing-record errors; three lexical candidates do not cover this code/semantic boundary. No evidence reuse accepted. Search incompleteness disclosed, not treated as exhaustive no prior work. |
| acceptance | pass | Frozen bounded cases and baseline mismatches precede edits; complete section dictionaries and exact source ranges, unchanged real corpus cases, root/mirror parity, old-engine rejection/rebuild, ordinary and -O runs, required repository/Reader checks. Independent verifier consumes actual code and raw data. |
| risk | pass | Local fence-state change and engine version invalidation are narrow and reversible. Full CommonMark/container/HTML semantics excluded; false-close/missed-open and stale cache are explicit regression targets. No guide/history overwrite. |
| resources | pass | Standard-library CPU only, bounded calls, no model/GPU/fee/deployment; full suite uses existing duration allowance. |

## Required execution interpretation

1. Closing-fence tail checks must strip only line terminators before ASCII space/tab validation; broad `strip()` would incorrectly accept non-ASCII whitespace. Include NBSP/form-feed rejection and CRLF/no-final-newline coverage where existing splitlines behavior permits it. Opening tilde info may include backticks; opening backtick info may include tildes. Greedy contiguous fence length must be preserved.
2. Freeze hand-authored expected heading positions before executing the fixed candidate; reconstruct expected complete output from those positions and source slices without reusing the candidate fence branch. Preserve baseline failure logs and input/code hashes.
3. ENGINE_VERSION must change. Show actual old-version indexed_search rejection, then rebuilding unchanged source records and corrected chunks; a version-string test alone is insufficient.
4. Real corpus equality concerns complete section output, with input IDs, hashes, denominator and all differences retained. Any changed corpus output must receive semantic review rather than blanket rejection if it is an independently confirmed bug correction.
5. Quality improvement here means bounded parser correctness. Agent/model quality, cost, latency and scientific novelty remain unmeasured. Historical 52 papers do not constitute new ten-paper reading progress.

## Boundary and next step

This is an actual separate reviewer invocation's local textual review, not a fabricated ReviewSession signed receipt or proof of a deployed supervisor. No full execution DAG was supplied; this document does not certify an unseen DAG, host authorization, or publication. KNOWLEDGE-FENCE canonical detail did not yet exist at inspection; parent should reconcile task tracking before dependent reporting. Wait for parent-provided baseline/fixed snapshots, raw evidence and executed commands; perform independent new-case, full-output/source-range, ordinary/-O, cache and corpus checks then write review.md. No source/task/guide writes were performed by this reviewer.
