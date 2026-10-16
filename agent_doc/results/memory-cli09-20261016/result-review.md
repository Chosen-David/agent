# MEM-CLI-09 independent result review

Verdict: usable-with-scope for the candidate code and targeted reliability observations; final publication remains conditional on completed required regression logs and unchanged hashes.

Frozen baseline: 9e2064bf534a4438aa6132d55920c8d1574f5aa2. Reviewed production diff, full added tests, frozen plan, baseline failure and focused/-O logs. Candidate source SHA256: 82ddddac68994fd53191d51a5177a91501752709023c7440161f8b7e70a950e9. Test SHA256: 5417c7e6f481d75fde00339052b65fce2947fd7395d5842b141c7e558e3d55f4.

Implementation: _load_document_refs checks the same original falsy path condition and retains Path.read_text default encoding. Its catch contains only file reading/json decoding and catches JSONDecodeError/UnicodeDecodeError exactly. MemoryError chains the source error and follows existing main error JSON/return2. The main outer handler is unchanged. Calls remain after construction; no database hydration is inside the helper catch. No production SQL/ledger methods changed.

Baseline log shows 4 methods run, errors=8, each malformed-input subcase fails with uncaught decoding. After log shows 5 methods pass; 8 malformed subcases now return structured failure with empty stdout and identical business table snapshots. The added fifth method verifies first-add initialization order. These are 8 inputs, not 8 independent real-world workloads or performance samples.

Independently executed reviewer-check.py (raw reviewer-raw.json) verifies 13 groups: four real process-entry malformed JSON/UTF8 cases across add/correct; exact business table/sqlite_sequence preservation; legacy missing-index upgrade still occurs before malformed decoding with unchanged business state; valid current document snapshot add/correct; genuine stored scope corruption raises JSONDecodeError in history/check/correct; genuine stored document snapshot corruption propagates; falsy helper path compatibility; first-add creates an empty initialized ledger on malformed UTF8. This demonstrates the new handler does not broadly relabel database corruption as user input errors. New clocks/identity in successful operations are not compared across separate executions; no exact differential speed or successful-output byte claim.

Integrity: raw observations identify the actual source/test hashes. The independent script exercises public subprocess and actual SQLite corruption rather than reproducing helper logic. Targeted before failure and after/-O logs were read, not produced by this reviewer. At review time full-tests.log and reader-tests.log were still in progress, so no full-suite completion claim is accepted yet. Producer must supply completed final-hash regression outputs before publication; existing behavior or syntax inspection is not a substitute.

Numerical/measurement scope: binary reliability outcomes only; timing N/A because no speed claim. Invalid document file behavior is controlled error2 rather than uncaught exception. Schema/filesystem initialization can occur before failure; do not claim zero side effects or a whole CLI transaction. Existing input JSON schema and OSError rules are unchanged. Recursion/depth errors, hostile filesystem races, model KV, quality, TTFT, live models and deployment are outside scope.

Manual independent review only: no managed ReviewSession/host receipt/service installation asserted. Parent MEM-STORAGE-01 remains open. No production/test files modified by reviewer.

## Regression harness checkpoint

Producer reports an attempted inline final-regression harness failed: multiprocessing spawn tried to reopen `<stdin>`, then serialization of TestCase failure tuples raised TypeError. This is not usable final regression evidence and is not classified as a production-code failure. Failed harness evidence remains preserved in failed-final-regression.json and failed-runner-note.txt. A guarded on-disk runner is required; final publication condition remains pending its actual output. Initial normal CLI full run is separately reported successful, not substituted for the final harness.

## Final frozen regression acceptance

Read the actual guarded on-disk regression_runner.py and final-regression.json after completion. Runner discovers the two intended directories serially, retains errors/failures as string test IDs with tracebacks, writes explicit TestResults, and returns failure if source changes or any result fails. Actual final source before/after hashes both equal the reviewed 82ddddac68994fd53191d51a5177a91501752709023c7440161f8b7e70a950e9; current source and tests still match the hashes above. Full suite ran 1,229 tests, 8 skipped, errors/failures empty, successful true (75.272 s). Reader ran 3, no skips/errors/failures, successful true (1.582 s). These are producer executions independently inspected, not a second independent full-suite rerun. Earlier invalid stdin-runner remains preserved and excluded.

Final verdict: usable-with-scope; the final-regression condition is now satisfied for these exact code/test bytes. Safe to publish this bounded CLI reliability correction after ordinary fresh-main/concurrency and exact staged artifact checks. It remains no claim of performance, KV/model task quality, whole CLI atomicity, managed acceptance, or universal correctness.
