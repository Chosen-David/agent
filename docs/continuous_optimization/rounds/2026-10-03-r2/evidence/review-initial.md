# Independent program review — initial findings

Scope: synthetic program-level records only. No role rubric inspected, no paid model invoked, and no user repository tracked files edited by this reviewer. Test driver and fixtures are outside tracked delivery. These tests exercise acceptance integrity, not semantic grading quality or proof that a host actually ran a model.

Source SHA-256: `f8b4217bf3618681e1ffdd411c8d5b1bb61f9565cc1b3e284b8b82bc218d04c0`.

23 cases: 14 correct accept/reject decisions, including one valid positive control; 9 false accepts. Three reject cases raised exceptions, so the count does not imply graceful error handling.

## Blocking findings

1. **Receipt invariants are checked on ingestion but not on report replay.** Seven cases mutate a persisted start/completion receipt's actor, case, attempt, kind, status, or required event ID. `report()` still returns `complete=true`, because it checks adapter names and manifest hash but not these fields. Revalidate persisted records exactly as on ingestion, and bind numeric attempt to directory name.
2. **Empty task set passes vacuously.** Before dispatch, changing `manifest.expected_cases` to an empty list and `manifest.cases` to an empty object makes `report()` return `complete=true` with expected=0. Compare exact nonempty case IDs among frozen tasks, rubric, manifest; do not use `all([])`/0==0 as completion.
3. **Pass evidence may name an escaped/nonexistent file.** `evidence=['../../../../nonexistent.txt:1']` is accepted. Decide whether evidence is structured location or free-form commentary. If location, require every passing check to refer to at least one collected artifact and reject escape/unknown paths; if commentary is allowed, separate it from artifact references and explicitly bound the scoring claim. Missing-evidence explanations should not count as a passing artifact assertion.

## Robustness findings

`grade=[]` and `checks=['pass']` cause uncaught `AttributeError` via `.get`. Missing case directory raises at report preflight. All are rejected in effect, but should produce a consistent nonzero CLI error/invalid report instead of a traceback. Shape validation should precede business checks.

## Controls that behaved correctly

Legal control accepted; absent grade, not-collected attempt, empty assertion list, self-grading, mock adapter, changed input/output, manifest mutation after start, malformed JSON, and symlinked output did not pass.

These are consistency tests, not tamper-proof authentication. An actor with arbitrary write access to every record can rewrite hashes and receipts; this pipeline correctly documents that host receipts are not cryptographic execution attestation. No stronger security claim is requested here.
