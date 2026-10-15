# MEM-SCOPE-02 independent plan review

Decision: approve the bounded manual-host experiment. This is a real separate
tool context review, not an authenticated runtime ReviewSession receipt or a
grant of publishing authority. No implementation, test, timing, or task-file
changes were made by this reviewer.

Reviewed baseline: `f872166a7ce4c61e21353dad83a83729d44440ca`.
Stable plan file SHA256:
`261211b66c13e21d7584c2479f4b7bb75a8aecb7469a97344fea1c275a713dbc`.
Baseline source SHA256:
`5ae35f1dcad87ab759fe4aab5f7deb522c9a3ea1d01ef8118c4ca65547ef7b19`.
Baseline retrieval tests SHA256:
`2b9be8611ce2070c667bfada19e4620ac8d9160524eaaa64edb2526c31e0ea43`.

## Seven review dimensions

- Intent: pass. Reducing unnecessary scope-unmatched hydration serves the
  existing memory-storage task without implying model KV or LLM quality gains.
- Guide: pass within stated authorization. GUIDE.md is empty; the entire human
  guide directory remains read-only. Only this Agent repository is in scope.
- Assumptions: pass for experiment admission, not proven benefit. The existing
  mixed-status branch already decodes all JSON before hydrating selected rows;
  avoiding a subset of hydration is plausible but must be measured.
- Prior results: pass for bounded reuse. Read the prior report, independent
  review, benchmark source, and task detail. Their status-sparse measurements
  do not measure the new scope-sparse claim. Reuse design/failure knowledge,
  not prior timing values. Parent recorded a partial ResultStore query with
  61 read errors; this review does not claim full historical coverage.
- Acceptance: pass. Complete return parity plus two history fixtures >=25%
  median reduction and controls <=15% regression,21 paired full-entry timings,
  fixed before results. The reference must be current f872 list(), not the
  older eager reference used to measure MEM-STORAGE-01.
- Risk: pass with required boundary checks below. No schema/index/cache change;
  restriction to exact built-in ledger/status/scope types contains API risks.
- Resources: pass. One local CPU context,30-minute total wall limit, maximum
  two candidates, serial main/independent timings. No service/model/GPU use.

## Required implementation and validation cases

1. Collect metadata with fetchall and completely Python-decode every scope
   and existing document snapshot before any scope membership evaluation.
   Keep the same connection/transaction through hydration and returned list.
2. Evaluate membership only for requested-status rows. A non-container scope
   on excluded status must remain status-short-circuited. A selected-status
   null/numeric scope must raise after all JSON decoding; pair an early such
   record with later malformed scope and document JSON to verify precedence.
3. Exact string membership semantics: T1/T10/T, empty string, absent match,
   empty list, JSON list/dict/string values, selected and excluded invalid
   types. No SQL LIKE/json_valid replacement.
4. Exact built-in str scope only. None, str subclass, non-str scope, ledger
   subclass, str status subclass, all status, empty/all-requested-status
   databases retain the current path. Preserve status validation before I/O.
5. Full packets, dependency order, document refs, stable created_at/ID ties,
   correction/acceptance behavior, old schema without document table, missing
   dependency table including zero selected or scope-matched IDs.
6. Python JSON BLOB/UTF-8/depth errors; retained exception traceback followed
   by immediate writer succeeds (no surviving cursor read lock).
7. Timings use the same bytes for before/after, warmed paths, complete list
   return, post-timing full-value comparison and unchanged database hashes.
   Record all pair/order samples. Include mixed-history no-scope and full
   scope-match controls as well as small/all-active fallbacks. Do not measure
   in parallel with tests or other benchmarks.

## Limitations and next step

No performance or correctness test was run during this plan review. Existing
arbitrary-corrupt-database limitations do not become universal equivalence
guarantees. No claim about cold disk, peak RSS, concurrency strengthening,
LLM answers, token use, or actual tensor KV performance is admitted.

Await the parent's frozen implementation and evidence handoff, then independently
review and reproduce serially within the remaining budget. Only assigned
independent evidence paths may be written by this reviewer.
