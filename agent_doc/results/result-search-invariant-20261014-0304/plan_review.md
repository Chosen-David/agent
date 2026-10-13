# Independent plan review

Reviewer role: independent hosted agent; review of supplied plan, actual ResultStore.search, _context, _unknown, and result-store tests. This is a manual review record, not a deployed ReviewSession receipt.

Verdict: REVISE before production adoption; APPROVE isolated baseline/candidate measurement for ordinary plain JSON context only.

The optimization targets a genuine repeated input-only traversal. The full search timing and exact entire-return comparison, fixed max_scan/limit, large plus control contexts, and >=10% declared threshold are suitable bounded evidence for local CPU retrieval only. Keeping show(), assert_not_revoked(), record validation, and equality inside each record loop preserves those checks.

Required refinement: current _context accepts dict/list/scalar subclasses and other JSON-serializable values (e.g. tuples), and _unknown runs within each record exception handler. Unconditionally moving it before the loop changes exception timing and handling, and can evaluate user code on an empty registry that previously never evaluated it. Do not silently strengthen the public API to pure ordinary JSON. Retain original evaluation path for unsupported/exotic contexts, or explicitly prove the candidate has no observable change for the supported public inputs. A plain-container fast path must check nested scalar/container subclasses too; custom string/int equality may also have effects. Avoid repeated validation wrappers that erase the measured gain.

Required boundary evidence: empty and missing registry, no successfully shown records, incomplete context, known complete, nested unknown, accepted exotic/context subclasses with equality effects or errors, invalid JSON/NaN, revoked and corrupt records, all-return exact equality. Concurrent caller mutation cannot be made correct by the current synchronous API alone; state its unsupported assumption and do not claim general semantic equivalence under mutation.

Independent results review pending. No production files modified by reviewer.

## v5 reconciliation

APPROVE guarded v5 candidate after review and executable checks. Iterative exact-builtin classifier, lazy evaluation inside first usable record, one-time classification and subclass/instance-hook fallback resolve requested semantic boundaries. Final performance and 18-case boundary evidence are recorded in review.md. Production source equivalence and required regressions remain pending.
