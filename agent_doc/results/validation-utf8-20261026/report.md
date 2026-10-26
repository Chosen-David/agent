# Validation CLI Unicode preservation

SYSTEM-99 Version42 scoped correctness checkpoint; the system batch remains open.

Both validation CLIs printed non-ASCII JSON using inherited terminal encoding. Under forced cp936, restore crashed on non-BMP text; inspection lost the pending response to an encoding error, and a handled duplicate-key error emitted non-UTF8 stderr. Reuse configure_utf8_output at both main entries, preserving schema, adapter selection, validation policy, arguments, formatting and exit rules. No production duplicate or truncation added.

Frozen tests run as real subprocesses without -X utf8. Restore covers all three saved observation statuses in both formatting modes with complete-object equality, errors, limitations, artifact/review hashes and read-only files. These saved observations are display-only, including synthetic usable-with-scope values; restoring one never authenticates acceptance. Actual inspection remains pending without a verifier, including context-write/restore. The real duplicate Unicode key requires exact stderr JSON and exit2. Independent pre-execution review corrected an invalid proposed missing-path assumption: that reader intentionally returns a generic ASCII error. No results existed before the correction.

Command for each local regression: python -B -m unittest tests.test_validation_context tests.test_result_validation -v. Original scripts at fcba9e56 plus the frozen new tests: 29 methods, 9 failed assertions/subcases and 1 decode error, not ten independent defects. Fixed and independent runs: each29 passed, no skips. Raw logs and command/exit JSON retained separately; inputs.json pins exact source/test hashes. Independent scope acceptance is in result-review.md. Existing four-platform-matrix workflow adds test_validation_context; remote CI is separately checked after publication.

Correctness only: no fullsuite replay, old gate reset, model task success, token/provider usage, speed or batch-completion claim. Samebatch fresh body records remain13; prior PID/ALIAS/role/Codex/fullchain gaps remain open. Human guide and unrelated untracked files unchanged.
