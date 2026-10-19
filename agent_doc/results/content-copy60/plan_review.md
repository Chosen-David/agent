# CONTENT-COPY-60 independent plan review

Reviewer: `/root/copy60_review`; producer/planner: `/root`. Scope: bounded candidate probe only, no production or publication acceptance. This is an actual independent context review, not a managed ReviewSession receipt or supervisor deployment.

## Initial review

Decision: **revise** pending the narrowly specified clarifications below. Reviewed plan SHA-256: `73847a91162e5d5f6d4e5e81c0d0ba8db349ef61a22cd832891ae52780b5a32a`.

The immutable-string hypothesis is sound for ordinary scalar Unicode strings. Lone surrogate and surrogate-pair strings must take the original JSON path because JSON roundtripping may combine escaped pairs. Exact string type excludes custom subclass behavior. Preserving JSON cloning for metadata retains nested mutation isolation and JSON normalization. Actual source inspection confirms that subclass-overridden get activates `_metadata`'s hook fallback; the revised isolated-module design correctly avoids this benchmark confound while preserving custom-hook dispatch.

Required clarifications before measurement:

1. Make fast-path eligibility conservative: exact dict and exact string keys, or equivalent justified semantics, with original full clone for custom mappings/non-string top-level keys. Rebuilding by original keys otherwise breaks JSON key normalization/collisions. Keep original exceptions for invalid metadata and cycles.
2. Freeze direct insertion-order comparisons (content first/middle/last), scalar Unicode/lone and paired surrogates, string subclass, nested tuples/non-string metadata keys, invalid objects/cycles, output mutation and custom get behavior. Sorted canonical hashes alone cannot validate dictionary insertion order.
3. Freeze aggregation before timing: e.g. ratio of medians of the 11 paired samples, with raw pairs retained. State whether peak threshold applies to every case. Replace remaining “baseline and subclass” wording with the module candidate design.

Seven checks: intent pass (authorized local hypothesis); guide pass (empty GUIDE and explanatory README read, directory read-only); assumptions revise (JSON normalization and class identity need explicit boundaries); prior_results pass for feasibility-only (no old latency reused, read-boundary56 historical review inspected); acceptance revise (aggregation/order comparison missing); risk pass (candidate only, fail closed on mismatch); resources pass (bounded CPU, one benchmark pass, no external service).

No speed, correctness or result usability claim is made. Production integration still requires independent executed-code/raw-result inspection and full regressions. Current TASK does not yet include CONTENT-COPY-60; main owns reconciliation before any publication/completion claim. No managed workflow execution is authenticated by this review.

## Revised plan review before measurements

Decision: **approve** for the bounded candidate probe. Revised plan SHA-256: `a194027598d5ce02fb247e1f0e1e6c3c8b8daf404d444d6a927254cb361e541c`.

The added eligibility paragraph resolves every blocking finding above: exact dict and exact ASCII string outer keys avoid normalization collisions and key surrogates, content uses original JSON fallback outside exact surrogate-free strings, direct key-list comparisons supplement canonical hashes, and targeted cases cover mutation isolation and invalid metadata. The explicit isolated native-module statement supersedes the remaining historical subclass wording. Ratio of sample medians and independent per-case traced peak thresholds are frozen before timing.

Seven checks now pass for this scope: intent (same bounded optimization goal), guide (read-only empty GUIDE), assumptions (conservative eligibility plus original fallback), prior_results (prior evidence only; no borrowed latency), acceptance (explicit semantic and performance gates), risk (production unchanged and mismatch rejects before timing), resources (single CPU benchmark pass within 180 seconds).

This approval authorizes no result claim or production integration. Reviewer must inspect actual probe code, raw samples, output comparisons, environment and artifact hashes after execution. A failed performance gate remains valid negative evidence when independently verified; no tuning retry is approved. TASK reconciliation and separate regression/integration phase remain main-owned.
