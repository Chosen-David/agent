# Independent plan review: MEM-CONTEXT-10

Verdict: ACCEPT for bounded local implementation and measurement, subject to the explicit compatibility and scope conditions below. This is manual scoped independent review, not a managed ReviewSession receipt or installed supervisor.

Plan SHA256: `26cac1c7cf497fb97e502e0c1534b686213a1196ade8845bdb977a8c4d3f3110`. Baseline: `4a19ee121eb283a5364bf8fff4aa146c8f5deec8`.

Read AGENTS.md, decision review, project document workflow, actual basis_context/check/_walk/_connect; human GUIDE is empty and stays untouched. Parent MEM-STORAGE-01 remains open. Prior result search exists and matching assumptions do not support reusing older timing as new closure data.

The real context pending loop repeatedly calls check on ancestors; check already traverses their ancestors. A chain therefore repeats graph hydration quadratically across generations. The proposed whole validated closure can remove that repetition without trimming payload, changing acceptance status, skipping document checks, or altering refs/known-ID semantics. Keep default check retaining only requested roots to avoid regressing the prior memory-peak improvement.

Required implementation/validation constraints:
- Fast closure is only for the exact ordinary built-in MemoryLedger path. Preserve customized _get/_check/_connect/document checker/sqlite connector and subclass/fake-ledger behavior via baseline fallback; do not assume hasattr implies compatibility. Tests must exercise altered getters and fake ledger patched at handoff_basis.
- Preserve baseline initial check_handoff_basis error precedence, selected-claim roots, root packet content, sorted final entries, full serialization, reused IDs and errors on immutable state. Test duplicate/shared roots, known ancestors (still validate even if omitted), candidate/stale/document corruption and malformed JSON/schema.
- Existing baseline spans read transactions. A single SQLite snapshot is a coherence improvement but is not identical to all concurrent-writer interleavings; document the immutable-state equivalence boundary and test stale transition between calls if observable. No cross-call cache.
- Validate every requested root and ancestor exactly with the existing iterative traversal. Do not replace document checks or status gates with existence-only SQL. Avoid recursion/depth limits.
- Benchmark actual full basis_context with identical complete outputs and input database hashes. Keep setup/fixture construction outside both timers, include validation, connection, hydration and serialization, use 21 randomized AB/BA pairs and 3 warmups, no concurrent producer/reviewer measurements. Deep chain96 plus a real shared graph primary; small and empty controls independently bounded at15%. Fixed max_chars200000 must hold without bypass. Report only local warm CPU context assembly, no model KV/QA/TTFT claim.
- After candidate freezes, independent actual code/raw/output/contract review and independent primary/control measurements are required before publishing; full repo and Reader checks remain mandatory. Negative results remain evidence and must not be tuned away.

No production or test files edited by reviewer. No paid/GPU/model resources used.
