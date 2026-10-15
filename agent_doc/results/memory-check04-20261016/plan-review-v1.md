# MEM-CHECK-04 independent plan review v1

Decision: **revise**, limited to freezing the missing measurement details before
measurement. The implementation direction is adopted for the bounded manual
chain. This is a separate real agent context's review, not a managed
ReviewSession receipt, resource expansion, performance result or result acceptance.
No tests or new measurements were run in this review phase.

Reviewed baseline HEAD: `2d7ddc46b13b24ecc0c3611b1d8dcb63df7e6b10`;
project_memory.py SHA256:
`b9f939410eee1e7c7477982ff9b0a1c95bd7d952ec706b5b179707d0d598ccf6`.
Read AGENTS, decision_review, project_memory, project_document, dual_main,
result_reuse and result_validation workflows, the actual _check/_get/_insert
implementation and existing memory-check tests, current TASK and MEM-STORAGE-01 /
MEM-CHECK-03 details, previous check03 plan/config. GUIDE.md is actually empty;
the guide README is directory governance, not populated human requirements.
No guide, source, task or historical evidence files were edited.

## Findings and required revision

1. Freeze exact fixtures, seed, warmup, aggregation and resource/stop budget.
   The existing plan specifies the primary chain, but the small/shallow,
   multi-root and branch controls lack exact nodes, edges, roots and payloads.
   Apply the <=15% ratio-of-medians latency guard to each fixture individually.
   Include a wide fanout control to expose eager stack expansion costs.
2. Keep traced peak and untraced time separate. Freeze a small repeated traced
   protocol (for example 7 randomized pairs), identical warmup and GC handling,
   entire check() allocation window including connect/commit/close, retained
   output treatment and aggregation. Build fixtures and compare equality outside
   measurement. Keep every raw value, failed sample and order.
3. Prefer explicit iterator frames which follow one parent at a time. Avoid
   eager push of all parents: it increases width-dependent auxiliary storage and
   may alter exposed malformed dependency behavior. Drop each non-requested
   packet before following its parent; retaining the loop's entry variable can
   silently preserve the claimed problem. Retain only requested packets, checked
   IDs, and active path dependency iterators.
4. Differentially compare complete results, exception class/message, actual _get
   order and document-check order against pinned source. Cover diamond, roots
   encountered as ancestors, sibling duplicates, cycles and dangling edges in
   deliberately isolated malformed stores, invalid refs including string
   subclasses, legacy/missing schemas, JSON/state errors and errors at multiple
   reachable positions. Do not invent a new dirty-store contract.
5. Shared _check callers require add/accept/correct regression coverage, in
   addition to public check, mutation isolation and real next-call document,
   correction and file-path freshness. Deep 1024/1200-node success is a separately
   stated reliability extension; baseline RecursionError is not numerical parity.

## Intent, assumptions, prior results and scope

The observed recursive visit frame retains each full entry while traversing its
parents, so packet lifetime reduction is a concrete local hypothesis. No new SQL,
schema, memoization lifetime or model service is needed. The checked-before-parent
rule already tolerates cycles and must remain in place; changing it would change
legacy behavior. Ordinary requested order remains independent of traversal order.

Reviewer executed the read-only ResultStore query
`MemoryLedger check DFS peak memory recursion`, limit5/max-scan200. It scanned200,
partial=true and reported60 errors. The relevant hit was
`memory-check03-20261016`, record SHA256
`8ec9d62cdce189f902181651caf02c850aa9878db3e50e6dd0c3b5d34c6945fa`.
It measures request-root hydration CPU time, not iterative traversal peak memory.
Adopt its compatibility/measurement-design context only; rerun for this new claim.
Other lexical hits are unrelated corpus/communication studies. Search is bounded
and is not an exhaustive absence claim or acceptance of stored validation.

The target remains Python tracemalloc allocation peak on synthetic local SQLite
plus bounded untraced warm-store CPU wall controls. It establishes no RSS,
SQLite-native cache, GPU, model KV, QA, token or TTFT benefit. The broader
MEM-STORAGE-01 remains incomplete without a real model backend. The parent is
the sole TASK writer, and final independent code/data validation is still needed.

Recovery: freeze the above details in a versioned config/plan before editing or
timing, then obtain follow-up review. Failed gates retain the baseline and all
negative evidence; thresholds must not be relaxed after observing outcomes.
