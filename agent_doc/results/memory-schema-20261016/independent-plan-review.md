Manual independent plan review for `Chosen-David/agent` at `06ed701b30fc6f83c554f1f240b1f05122d387e3`.

**Verdict: adopt with the safeguards below.** This is a same-goal, bounded implementation optimization for ordinary ledger transactions. It is not a managed `ReviewSession` approval, result validation, implementation acceptance, or publication authorization. I made no edits and ran no tests or experiments.

I read `AGENTS.md`, the decision/document governance, the current task constraints and human-only guide directory, relevant implementation/callers, `tests/test_memory_check.py`, and MEM-CHECK-03/04 reports and independent reviews. Their measured results support retaining the current traversal architecture; they do not establish this candidate’s performance.

| Review area | Finding |
|---|---|
| Intent | Pass: reduces repeated schema discovery while preserving full memory validation. Scope remains this repository; TwoLevel is excluded. |
| Guide | Pass: `GUIDE.md` has no substantive requirements; guide files remain read-only. |
| Assumptions | Conditional: ordinary SQLite connection, transaction, factories and no schema-changing reentrancy must be explicit. |
| Prior results | Pass: reuse existing methods/fixtures, not historical speedups as new evidence. |
| Acceptance | Needs a frozen correctness/performance protocol before measurement. |
| Risk | Low within the ordinary path, provided fallback and error-order safeguards hold. |
| Resources | No execution performed. Candidate count, timing budget and stopping conditions still need binding by the parent. |

The implementation should satisfy these requirements:

- Keep `_get(db, entry_id)` unchanged and uncached by default. Share its hydration body with a helper accepting optional request-local schema state.
- Initialize one fresh state per `_check` traversal, including repeated checks within one transaction. Use a distinct “unknown” state so an absent table is cached correctly.
- Preserve `SELECT entries → missing-ID error → dict(row) → scope JSON decode → schema query → document snapshot query/decode → dependencies query` ordering. Cache only a successfully completed schema lookup; do not set the state before the query succeeds.
- Preserve every unique DFS visit, hydration, status check, document check, checked-set placement and requested-root retention. In particular, malformed hydration data must still precede a stale-status error.
- Leave `handoff_basis.py` calls separate: required refs before subset validation, supplied refs afterward, known-memory checks and successive pending expansions unchanged.
- Use an immutable reference to the original `_get` for the override gate. A patched/wrapped `_get` must receive every original call on fallback.

**Connection compatibility needs a precise bound.** Prefer `type(db) is sqlite3.Connection`, rather than `isinstance`, because subclasses can override `execute`. Require `db.in_transaction`, `db.row_factory is sqlite3.Row`, and `db.text_factory is str`; wrappers and other factories should follow the original path without normalization.

Those conditions alone do not prove a connection is ordinary: callbacks or reentrant code can execute DDL through the same connection during traversal. This is a code-derived compatibility caveat, not an observed failure. The plan should explicitly exclude schema-changing connection hooks/reentrant customization from the optimized-path equivalence claim, or restrict optimization to connections whose ordinary lifecycle the implementation actually controls. Do not claim arbitrary genuine SQLite connections are guaranteed equivalent merely because `in_transaction` is true. A schema query disappearing is also intentionally observable to tracing/authorization hooks.

Meaningful validation should cover:

1. **Optimized-path parity against pinned HEAD:** complete packets or exception class/text across existing graph, malformed-data, legacy-schema, missing-table and first-error fixtures. Include deep chains, cycles and requested roots first reached as dependencies.
2. **Actual optimized-path traversal order:** existing tests patching `_get` deliberately exercise fallback. They cannot by themselves establish that the optimized helper preserves DFS/error/document-check order. Instrument the shared helper or SQL/document events without replacing `_get`.
3. **Schema lookup cardinality:** one lookup per successful optimized traversal for both table-present and table-absent cases; direct `_get` remains uncached. Unknown IDs and invalid scope must fail before any schema lookup.
4. **Fresh state between calls:** check, change schema, check again—even within the same transaction. Include failed traversal followed by repair and retry, and absent→present plus present→absent document table.
5. **Fallback behavior:** wrapped/replaced `_get`, connection wrapper/subclass, no transaction and nonstandard factories retain baseline behavior and error ordering.
6. **Freshness and integration:** real document changes, ancestor correction, caller-result mutation and handoff ordering still fail or return as before.
7. **Performance:** measure the full public `check` entry with frozen paired randomized samples. Include one-node/small controls, long chains, wide/shared graphs, many roots and legacy absent-table cases. Keep timing separate from query-count instrumentation; retain all samples and predeclare regression limits.

The structural benefit is bounded: schema discovery changes from once per hydrated node to once per traversal. Full entries, dependency reads, document bindings and filesystem validation remain. Any wall-time benefit is unmeasured, and this candidate establishes no model KV, QA, token or TTFT improvement.

---

## Revised ownership plan and implementation static review

This section follows the parent's tighter ownership plan and subsequent read-only inspection of the actual candidate diff, `tests/test_memory_schema_check.py`, and `.agent-runs/memory-schema-20261016/plan.json`. The original review above is preserved verbatim. No tests or experiments were run by this reviewer; the only write is this assigned private review artifact. This remains manual review, not a managed approval receipt.

**Revised plan: adopt.** Restricting caching to the built-in public `check()` ownership path resolves the generic-transaction concern. `_get(db,id)` and `_check(db,refs,root=None)` preserve their signatures and default uncached behavior. Direct `_check`, `_insert` and customized entry paths retain per-node schema lookups. The shared hydration helper plus shared traversal engine avoids algorithm duplication. Every optimized public call owns a new state list; separate handoff check calls remain separate transactions and validations. The tightened scope is a same-goal low-risk implementation, with no need to change architecture, delivery or project scope.

The frozen plan now supplies meaningful performance gates: both 512-node table-present and legacy table-absent chains must improve complete-check median wall time by at least 10%; each control must regress no more than 15%; 21 seeded randomized pairs, three warmups per arm and five complete calls per sample. Setup, equality checks and GC are excluded symmetrically. One local CPU, at most two candidates and 30 minutes are bounded; no model/GPU/API work is included. These are prospective gates, not measurements or acceptance.

**Implementation static verdict: revise one compatibility blocker before freezing/measurement.** The candidate guards class `_get`, `_check`, `_connect`, `check_document_refs`, `sqlite3.connect`, exact connection type, factories and transaction. However public `check()` resolves `self._connect()` and fallback `self._check(...)`, while its guards inspect only class attributes. An exact `MemoryLedger` instance can have its own `_check` attribute: the original public method honored it, but the fast route now silently bypasses it. An instance-owned `_connect` can similarly supply a custom connection with hooks despite passing the class guard. This finding is from Python attribute resolution and the inspected source; it has not been experimentally reproduced here.

Required fix: test the actual instance resolutions, or exclude instance-owned `_check`/`_connect` attributes before enabling the fast route; add regression cases for both. Prefer calling `MemoryLedger._walk` on the fast route rather than `self._walk`, because the helper is a new internal engine and instance shadowing should not unexpectedly redirect the ordinary route. Retain class-level override gates as well.

Other static observations are favorable: `_read_entry` keeps the first row and scope decode before schema access; `[]` versus `[False]` correctly distinguishes unknown from known-absent; successful lookup is cached only after execution; binding/JSON/dependency hydration remains ordered; `_walk` keeps DFS/checked/root-retention logic; no handoff edits appear. Existing direct-call same-connection-DDL regression appropriately exercises uncached `_check`.

The new tests cover optimized table-present/absent query count and actual native DFS order, `_get` and class `_check` overrides, cross-call schema changes, direct `_get` freshness, and direct `_check` DDL compatibility. The unknown/bad-scope test currently checks exception outcomes but not zero schema-query count despite its name; strengthen its observation if that ordering is claimed as directly tested. Broader pinned-baseline differential, freshness, document/error ordering, fallback variants and performance/data checks remain necessary as already frozen in the plan. No measured gain or implementation acceptance is established by this static review.

## Static follow-up: instance override repair

Re-read the actual repaired source and added regression code. Reviewed source SHA256 is `7623375d43446933955ef83d6aad1f2737a2768c0056bad594b55464c4814ce4`; test file SHA256 is `13c3164a89127b71b043e3d0f9e590ddcdeecd6dd9cbac496197f77f8563620e`.

**The identified blocker is resolved in the inspected source.** The fast route now requires `_check` and `_connect` to be absent from the exact instance's `__dict__`, and calls `MemoryLedger._walk` directly. An instance `_check` sentinel regression verifies dispatch compatibility; an instance `_connect` context manager with a trace callback requires four uncached schema lookups on the diamond. Both target the actual earlier defect. This reviewer read these tests but did not execute them; the parent's report of 31 passing memory tests is producer evidence, not independent execution.

The parent reports initial candidate measurements passed the prospective gates but were retained as `measurement-primary-v1.json` and explicitly not accepted because they bound the defective source. That treatment is appropriate: repaired-source timing and independent code/data validation must bind the repaired source identity. I did not inspect or validate those raw timing data in this plan/static review. No remaining blocking finding was identified in this bounded static follow-up. Performance, comprehensive differential correctness, final regressions and publication remain downstream obligations; this is not managed runtime approval or final result acceptance.
