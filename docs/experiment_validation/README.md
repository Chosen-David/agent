# Post-data independent validation gate

Implemented 2026-10-07 in the shared document-architecture candidate. This directory records bounded executable controls, not a bug-free guarantee, model-quality result, GPU benchmark or host deployment.

## Actual integration

`agent_runtime/result_validation.py` validates declared producer → independent verification → consumer dependencies. `task_manifest.validate_contract`, `ReportingHandler`, `result_report` and `review` invoke the gate; the managed supervisor passes the trusted backend's `result_verifier` into dispatch and fresh report/recovery checks. Producer completion means raw production only and is stored as pending acceptance. Consumers cannot turn this into usable data without the independent provider.

The manifest binds source/inputs/configuration/raw records/outputs/environment, contextual acceptance protocol, actual run and bounded metric units. Before/after checks invalidate changed artifacts. Missing or crashed verifier, worker-authored pass JSON, inconsistent scope, stale bindings, failed and inconclusive checks cannot certify results. Failure routes explicitly to the existing main-AI versioned repair/retest flow and preserves raw evidence. No shell commands or module names from manifests are executed.

## Evidence and rerun

- `python -m unittest tests.test_result_validation -v`: positive independent arithmetic/reference/boundary recomputation and fault injection; actual SQLite/ReportingHandler producer–gate–consumer chain, direct invocation, live reporting and resumed-proof checks.
- `reference-run-v2/`: actual local CPU synthetic integer observations created by the bounded test fixture. No timing claim. `scoped-check.json` is an executable control result obtained by the test host callback; it does not authenticate a real third-party reviewer.
- `program-tests.log`: test command output for this candidate, subject to final integrated rerun after concurrent edits.
- Independent reviewer uses separately authored fixture/tests and frozen adversarial requirements outside these implementation tests. The frozen matrix, original callback-crash failure, final 14/14 retest log and reviewed source hashes are retained under `independent/`; its separately authored permanent test is `tests/test_result_gate_acceptance.py`.

The runtime adopts the existing trusted-controller semantic-acceptance boundary rather than accepting a worker's own success fields. An authenticated host adapter must actually perform/retrieve independent checks and protect review provenance. Hash completeness, scientific applicability and truthful actor identity are not automatically inferred; arbitrary unclassified shell work outside these hooks remains outside enforcement.

See [workflow contract](../../workflows/result_validation_workflow.md) for schema, all six check domains, versioned recovery and installation limits. See test source for a complete deterministic schema and host adapter fixture. The fixture's `runpy` executes only its generated test code; production code execution needs its own trusted host authorization and cannot be inferred from a result command string.

## Preserved metadata correction

`reference-run-v1-metadata-correction/` retains the initial numerical fixture without rewriting its raw records. Its recorded `python code.py` command only loaded a function, while fixture generation called that function in process. It therefore cannot establish the claimed reproduction-command provenance. The initial scoped-check JSON is retained as a superseded, insufficient test-controller report, not usable final acceptance.

The corrected `reference-run-v2/` actually invokes the recorded Python producer in a subprocess, verifies its successful exit, and derives raw/output files from that invocation. Current tests use this corrected path; independent formulas and explicit boundary checks remain separate. This correction illustrates why self-authored pass JSON is insufficient and why metadata/provenance needs actual independent review.

`report.json` binds the exact implementation, workflow, integration and evidence files for this scoped acceptance (18 implementation tests, 14 independent cases). Final whole-repository regression/publication is recorded by the parent release process; this report does not claim those stages completed.
