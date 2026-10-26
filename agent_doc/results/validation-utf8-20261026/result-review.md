# Independent result review: VALIDATION-UTF8-01

Decision: usable-with-scope for the bounded local correctness repair. No blocking issue found.

Production diff changes only the two CLI imports and invokes existing configure_utf8_output at each main entry. Arguments, object construction, compact/pretty serialization, adapter trust, context-write opt-in and return/exception paths are unchanged. CI adds only validation-context coverage to the existing four OS/Python combinations; native remote CI remains separately unverified.

The inserted helper/test methods exactly match approved proposed-tests.txt, SHA256 08be5576045f92186cf1c387b5351a4dc155123a49310ae6a8ab81769e5b8b23. Current test_validation_context.py SHA256: a73db410edaf76caf660cd29a59bad596a7f05c5889826df06ab0974d1955ce0. Actual byte-capturing subprocesses force cp936 and disable UTF-8 mode without -X. Strict UTF-8 decoding plus full JSON equality checks complete Unicode restore data for three display-only statuses and both modes. Genuine pending inspection updates plan/manifest/contract scopes and plan hashes coherently, preserves exit 2 and empty stderr, and retains context roundtrip coverage. Duplicate Unicode JSON keys exercise the real handled error path and exact complete stderr error object with exit 2/empty stdout. Full fixture-file hash dictionaries verify read-only restore, normal inspection and failed-input paths.

Reviewed preserved baseline/fixed logs and metadata: baseline ran 29 methods and recorded 9 failures plus 1 error across Unicode subcases, including stdout UnicodeEncodeError and invalid UTF-8 stderr; these are not ten independent defects. Fixed run passed 29 methods. No timing/performance inference follows from run durations.

Independently executed exactly once: `python .agent-runs/validation-cli-2357/run_checks.py independent`. Its exact two-module unittest command passed all 29 methods, exit 0. Independent log SHA256: 509230d86ce51519ec1dd5a46e0cb5f3c3c310f48ac22c1f4933ee3fb4975d09; independent metadata SHA256: bf429d39d6fb5b587aa0665f9cac737aefa81de22311315898dc39d701e50072.

Baseline log/metadata SHA256: dc47c8cbb345e1656cc619b62aba243072f7e1b7df3d6a3983ac4d0c4e1465c2 / 501522968c83e512b12a52e86f6761170106d6f26882ed59ee5ae31db24cc733. Fixed log/metadata SHA256: d145bce99ac219ee1cdb6beeaacfd570804d66217412fee3ae910d94eca447a2 / bf429d39d6fb5b587aa0665f9cac737aefa81de22311315898dc39d701e50072.

Tracked diff is limited to the two CLIs, one test module, one CI step and SYSTEM-99 Version42 phaseY. No guide or historical-evidence tracked change; the unrelated pre-existing untracked evidence archive remains present. git diff --check passed. No prior blocked gate was rerun/reset, no fixture/production edits were made by the reviewer, and no model/performance/fullsuite/global or batch-completion acceptance is implied. Publication and exact remote readback remain main-owned.
