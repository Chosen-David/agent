# Independent handoff consumer-boundary review

Reviewer: `/root/runtime_coordination`; reviewed main's new consumer API/CLI changes and migrated callers. Reviewer originally authored the crossfeature runtime fixtures, so rerunning those is regression verification, not independent self-grading of model performance. No implementation or worker output was edited.

The consumer boundary behaves as requested in executed positive and adverse tests: intact producer bytes plus explicitly matching caller version pass completion; mismatching version fails; missing caller version fails completion even if the producer inserts an inline `expected_input_version`; legacy integrity-only inspection remains available and CLI `completion_verified` remains false. Unicode identifiers compare exactly, including whitespace differences. Malformed caller intent fails rather than being inferred from producer fields.

Executed `python -m unittest discover -s tests -p 'test_handoff*.py' -v`: 20 tests pass, including real CLI subprocesses. Reran four migrated crossfeature runtime tests successfully. Independently probed 108 JSON-compatible malformed values across the new caller argument and all top-level handoff fields: zero crashes; zero malformed expected-version values accepted. The probes included null, booleans, numbers, lists, objects, blank/whitespace strings. Positive intact byte hashes were computed from real temporary files. No claim of exhaustive schema fuzzing.

A real adverse boundary remains explicitly outside this change: with unchanged real artifact bytes, rewriting the producer's `input_version` from v1 to v2 and supplying trusted expected v2 passes. Version equality cannot authenticate the producer's provenance or establish that file contents actually represent the current input. The docs correctly disclaim scientific/semantic truth and authentication; no generalized semantic acceptance should be claimed from this API.

Migrated tests use fixed explicit caller version literals; they do not derive trusted consumer intent from the record under test. Runtime integration reads the independent consumer fixture, preserves successful original-byte inspection and observes the specific mismatch error. Its new success is a program comparison, not a host-model result. The original failure report remains preserved.

## Reporting finding

`runtime_execute.py` initially continued hashing the original `runtime_rubric.json`, whose frozen consumer criterion says the existing validator lacks a consumer argument and must record a known false negative. The followthrough now expects rejection and records a pass. Preserve the original rubric and historical report, but bind this changed implementation run to an explicit followthrough rubric/revision/addendum. This is a provenance inconsistency, not a reason to erase the original result or weaken the new completion gate. Parent has been notified; correction awaits recheck.

Remaining scope: caller trust is supplied by the host, not authenticated by this CLI; byte-integrity checks do not certify arbitrary scientific content; concurrency/path-race limitations of the existing validator remain. Paper semantic acceptance is separately reviewed by another worker.

## Reporting finding resolved

Rechecked `runtime_followthrough_rubric.json` revision `consumer-context-v2`: it explicitly requires independent consumer-v2 rejection while intact producer bytes pass integrity-only inspection, preserves missing-context rejection, and identifies the retained historical rubric. Actual rerun saved to `runtime-results.json`: 38 pass, zero fail/skip/gap. Independently recomputed new rubric SHA-256 and matched the saved report. Both original runtime_results.json and runtime_rubric.json remain byte-identical to committed HEAD. The reporting provenance issue is resolved. Missing/malformed consumer-context behavior remains additionally covered by the separately executed 20 handoff tests documented above; this 38-case runtime count does not include those tests or any new model evaluation.
