# INSTALL-RECOVERY-01 independent result review

Verdict: ACCEPT — usable-with-scope. No blocking finding for valid existing installation model recovery and isolated explicit discovery. Native separate-context source/result review; not an authenticated runtime receipt or publication authorization.

## Objects and source review

Reviewed Plan v1, independent approval, setup.py imports/install/check/uninstall/discover/update_model_inventory/doctor/main, scripts/run_role.py inventory consumer, both changed test files, original reproduction/baseline, initial integration failure and final logs. Stable Plan prefix SHA256: `a04033f5bc9beba20addb32cebc280c7f66e6f1530b8958bbd0e3809a3545de8`. Base: `61a7ee343d36f9e211fd697282c78743a2160ab2`. No repository guide or production source was edited by the reviewer.

Explicit discover uses exclusive TemporaryDirectory output, validates inventory before install, retains target cwd and records timeout=30. Nonzero and TimeoutExpired become ValueError handled by main's existing setup-blocked exit; output load/validation failures remain controlled ValueError/OSError. The temporary context includes installer errors, so success, parse failure, timeout and installer conflicts clean only owned output. The pre-existing project model_inventory.json is untouched and is not a new authority.

Doctor's new helper validates manifest identity/schema/file mapping and every generated model path/fingerprint before the first write. Destination selection comes from expected_files, restricted to registered agents and model policy/routing, not arbitrary manifest keys. Missing files are restored only when prior ownership exists; missing ownership fails closed. Changed or symlinked selected files are preserved/rejected. Re-rendering full registered agent text is accepted only after its previous complete fingerprint matches. Unselected files/unknown manifest fields and copied-skill snapshots survive. Manifest inventory and selected hashes are written after model files; doctor checks fresh state before reporting success. This retains the explicit limit that per-file atomicity is not a multi-file transaction.

## Independent executed checks

- `python -m unittest discover -s tests -p test_install_recovery.py -v`: 14/14 pass, reviewer-normal.log.
- Same with `python -O`: 14/14 pass, reviewer-optimized.log.
- Combined discovery of test_setup.py, test_setup_portable.py, test_model_discovery_setup.py, test_setup_doctor.py, test_model_routing.py, test_install_profiles.py and test_role_process.py: 57/57 pass, reviewer-integration.log.
- Independently git-show loaded baseline setup.py in a private root with unchanged repository resources, bound the final candidate 14 tests to that old module, and reran. Reproduced failures=18/errors=3, reviewer-baseline.log. Subtest assertions mean these counts are not 21 separate defects. Original producer baseline had only the initial 11 cases (14 failures/3 errors); three final ownership/invalid-inventory/missing-file cases explain the changed count, not code or acceptance drift.
- Additional executable reviewer_probe.py: concurrent explicit discoveries use distinct outputs and return their own inventory values, retain timeout=30 and remove both temporary parents. This tests helper isolation, not concurrent whole-installer transactions.
- Direct helper rejects invalid manifest schema, files mapping/hash type and missing ownership without changing any fixture bytes.
- Real temporary install → mocked discovery → doctor → actual `scripts/run_role.py --project ROOT --role research-write --dry-run` subprocess succeeds, selecting claude-opus-5-5 without explicit inventory or an adapter. The consumer actually loads installation.json model_inventory after check. No model is executed by this preview.
- Actual `setup.py --target ROOT --discover` subprocess without gateway returns exit 2 with `setup blocked: model discovery failed:` and no traceback/project .claude writes. No gateway call is made without configuration.
- `git diff --check` passes for the reviewed source/task worktree at review time.

Tests exercise the real install/doctor/check/repeat-install/uninstall chain, refreshed routes and manifest hashes, untouched standalone inventory, non-model user prose/orchestrator, early and later model-file conflicts, repository/project identity, missing manifest, symlink/human-guide fixture protection and copied-skill/unknown metadata preservation. These are local CPU correctness fixtures, not production backend measurements.

## Initial integration correction

The preserved integration-initial.log has one failure among 57: old `test_all_fallback_discovery_unavailable` mocked check as an installed fallback report while its target had no installation manifest. New declared behavior intentionally does not discover/install for such uninstalled targets. The sole test edit adds real empty installation first; it removes no assertion and still verifies discovered None preserves errors/fixes. New dedicated uninstalled-target coverage requires no discovery and no project writes. This is a justified fixture correction, not suppression of a failure in the declared installed path.

## Hashes and remaining limits

| File | SHA256 |
| --- | --- |
| setup.py | 66d694843fd6c21f0f3979d049b29255c586763fac4425ccb63d5ba234e394d0 |
| tests/test_install_recovery.py | 9d93199fde0ddbad7daaebd4edd61221f9e75b6646408168029bed16c141490e |
| tests/test_setup_doctor.py | d51c5b31e47b30858ccf5bca6bc78be525e9b04b09f239b0a3a454ac088a05b4 |

A pre-existing malformed top-level installation.json (e.g. `[]`) still raises AttributeError in original check() before doctor reaches this helper. Independently observed and left unchanged; the helper's object validation does not establish controlled recovery of every corrupt manifest through doctor. Keep that caller issue pending. The accepted scope is valid installed-manifest recovery, plus the stated selected-file malformed ownership checks and explicit discovery cases.

No live gateway/model/tmux server, native Windows, model capability heuristic, performance/quality/cost or full SYSTEM-99 completion is accepted. I/O failure, process interruption, same-user races and multi-file/concurrent installation transactions remain unproven. Empty/no-eligible discovery can legitimately remain fallback and be rediscovered later. Publication requires the main agent's fresh fetch, exact-file integration, ordinary nonforce update and remote SHA/tree/content readback.
