# INSTALL-RECOVERY-01 final independent result review — Plan v2

Verdict: ACCEPT — usable-with-scope. No blocking finding in the declared offline recovery scope. This is an actual native separate-context source/result review, not an authenticated runtime receipt or publication permission.

## Reviewed candidate and history

Reviewed Plan v2 and plan-review-v2.md, setup.py's real install/check/discover/doctor/update_model_inventory/uninstall/main paths, scripts/run_role.py's consumer, both test files and original/initial/final producer logs. Stable Plan prefix SHA256: `3319ee8b8908530eddd08dd9220e2dad031e31062a7f072d1720e3e46192c632`. Base: `61a7ee343d36f9e211fd697282c78743a2160ab2`.

Preserved result-review-v1.md and reviewer-* logs describe v1 only. That review found a real caller gap: top-level nonobject installation metadata caused AttributeError in check before the updater's validation. The main agent elected to repair it, version the Plan and obtain a new approval. V1 acceptance was paused, not reused to accept the changed candidate. Final review includes new v2 source, tests and execution below. No repository guide or production code was edited by this reviewer.

## Implementation assessment

Explicit discovery writes only within a unique TemporaryDirectory, validates inventory before installer preflight, retains target cwd, uses timeout=30 and converts nonzero/timeout into the existing controlled ValueError CLI path. The context includes install errors, so first-use success, parser/schema error, timeout and installer conflicts clean only owned output. Existing project model_inventory.json bytes remain untouched.

Doctor selects model-policy/routing and registered generated agents from expected_files, never arbitrary manifest paths. The helper validates manifest schema/identity/file-fingerprint mapping and every selected path/ownership/hash before its first write. A locally edited or redirected model file blocks all model changes; a missing owned file may be restored, while missing ownership is rejected. Full agent re-rendering occurs only after its prior complete fingerprint matches. Unselected files, CLAUDE.md, unknown manifest fields and copied-skill snapshots remain unchanged. Updated model inventory and file hashes reach the authoritative installation manifest, then doctor recomputes check before reporting success. Standalone inventory is not a second authority.

V2 check validates dict immediately after JSON load and resets manifest={} on read/validation failure. The existing needs_setup error is retained; it does not persist the empty fallback or grant update ownership. With discovered data, the helper rereads actual malformed bytes and rejects before writing. This repairs the observed top-level array/null/scalar caller gap without claiming comprehensive nested-field validation.

## Independent executed evidence

- `python -m unittest discover -s tests -p test_install_recovery.py -v`: 16/16 pass, reviewer-v2-normal.log.
- Same with `python -O`: 16/16 pass, reviewer-v2-optimized.log. Assertions use unittest methods and remain active under optimization.
- Combined discovery of test_setup.py, test_setup_portable.py, test_model_discovery_setup.py, test_setup_doctor.py, test_model_routing.py, test_install_profiles.py and test_role_process.py: 57/57 pass, reviewer-v2-integration.log.
- Independently loaded git-show baseline setup.py in a private root with unchanged resources, bound final 16 tests to that old module, and reran. Final baseline reproduces failures=18/errors=9, reviewer-v2-baseline.log. V1 final 14 cases had 18 failures/3 errors; the additional six errors are the three top-level inputs in each new caller test. Producer's earliest 11-case baseline had 14 failures/3 errors. These subtest counts are not distinct defect counts.
- Executable reviewer_v2_probe.py reruns the additional ownership/concurrency/consumer checks on final code. Two overlapping explicit discoveries return their own inventories through distinct output paths, retain timeout=30 and clean both parents. This is helper isolation, not whole-installer concurrency safety.
- Invalid helper manifest schema, mapping, hash type and missing ownership reject without changing fixture bytes. Candidate tests also cover later agent conflicts, foreign repository/project, missing-but-owned restoration, non-model edits, copied skills and unknown metadata.
- Real install → mocked discovery → doctor → actual `scripts/run_role.py --project ROOT --role research-write --dry-run` subprocess succeeds and selects claude-opus-5-5 with no explicit inventory or adapter. The consumer reads installation.json after its normal check. No model is executed.
- Actual `setup.py --discover` without gateway returns controlled exit 2, no traceback and no .claude creation. For array/null/integer/string manifests, actual subprocess `--check` and no-gateway `--doctor` return needs_setup JSON and exit 2 with no stderr traceback. Valid discovered inventory against each corrupt manifest is rejected by doctor and actual main control flow with zero fixture writes.
- `git diff --check` passes for reviewed source/task changes at review time. Source hashes are recorded below and in reviewer-v2-probes.log.

Tests exercise actual installation → discovery fixture → doctor → check → repeat install → uninstall consistency, refreshed routes/hashes, second resolved doctor skipping discovery, untouched user inventory, non-model prose/configuration, complete conflict preflight and symlink/human-guide fixture protection. They are ordinary CPU correctness regressions, not live backend measurements.

## Test correction and limitations

The preserved integration-initial.log has one failure among 57: old test_all_fallback_discovery_unavailable mocked an installed fallback check report while its root had no manifest. The frozen plan intentionally makes uninstalled doctor skip discovery/implicit installation. The sole edit adds real empty installation first; no assertion was removed. Dedicated uninstalled-target tests require no discovery and no writes. This fixture correction is justified and the failure remains recorded.

| File | SHA256 |
| --- | --- |
| setup.py | ca0a973fce898818ab3f5e471353075445e522f460635dba1462e987dbcf0507 |
| tests/test_install_recovery.py | bb3f138b56b013f73ccf4dd837c034ee688d30597a8df711ec4e5b70d224c029 |
| tests/test_setup_doctor.py | d51c5b31e47b30858ccf5bca6bc78be525e9b04b09f239b0a3a454ac088a05b4 |

No live gateway/model/tmux service, native Windows, heuristic capability accuracy, model quality, speed, total cost or SYSTEM-99 completion is accepted. Per-file atomic writes and manifest-last do not guarantee rollback on I/O failure, process interruption, same-user races or concurrent multi-file installation transactions. Empty/no-eligible discovered inventory can legitimately remain fallback and be retried later. This repair does not comprehensively validate all nested corrupt metadata or repair malformed install/uninstall entry paths. Publication still needs the main agent's fresh fetch, exact-file/nonforce update and remote SHA/tree/content readback.

## Publication evidence readback appendix

At the main agent's publication checkpoint, independently reread the three reviewer v2 raw logs from disk. They remain complete: normal and optimized each contain all 16 test lines plus `Ran 16 tests`/`OK`; integration contains all 57 test lines plus `Ran 57 tests`/`OK`. The setup.py and both test hashes still exactly match the final candidate table above. No tests or production code were rerun or modified for this document-only check.

| Raw log | Bytes | SHA256 |
| --- | ---: | --- |
| reviewer-v2-normal.log | 2757 | 0af3e78ca408dcfc62bddab2a879cee19a9128fc7ffbc929e8b5223d183ec835 |
| reviewer-v2-optimized.log | 2757 | fbbcc15f3509880b1c2d25d3d0cb63cb23e2c1f9022a95b1db54e271fe686505 |
| reviewer-v2-integration.log | 8507 | 6e57d847e8fb9248bc46395508238e26bccaefe01d590ef955ba6c8f9bc7695b |

Producer optimized-v3.log currently has only 1443 bytes/9 lines, no suite summary, SHA256 `758c165cd9ed0041a24192a4263172f58b60d54d2ef629860a6ab5c75c8f7df4`. That partial persisted file cannot independently substantiate a 16/OK count, despite the main agent's earlier session-output observation. Its bytes were not rewritten or padded. The discrepancy's mechanism is unknown; no cause is inferred from prior workspace observations. Final acceptance and the reported 16/16/57 verification rely on the complete independent raw records above, together with the actual source/probe review, not this incomplete producer file. The final bounded verdict remains ACCEPT usable-with-scope.
