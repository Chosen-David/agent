# ROLE-MODELS-01 verification

Scope: role-model preferences, installation lifecycle, native/default selection and trusted executable adapter protocol. Offline only; no live vendor access or model quality claim.

- `targeted.log`: 12 routing/subprocess cases.
- `setup.log`: 11 existing installer cases.
- `independent-review.json`, `independent-*.log`: separate-context code review, additional process/lifecycle checks and frozen code hashes.
- `regression-first.log`: initial 1522-test run, 3 task metadata errors retained.
- `task-integration.log`: four tests passed after adding required Task-ID/Date.
- `regression-final.log`: 1522 tests, OK, 8 skipped.
- `reader.log`: 3 reader tests passed.
- `integrated.log`: 39 tests after fast-forward to 33636a6f, including concurrent intake/next_step additions and this change's integration.

Commands: `python -m unittest discover -s tests -v`; `python -m unittest discover -s apps/paper-reader/tests -v`. The integrated suite discovers test_model_routing.py, test_setup.py, test_repository_task_integration.py, test_intake.py and test_next_step.py.

Source/model rationale and official references: `docs/role_models.md`; configuration is `config/role_model_policy.json`. Availability is host-declared, default capabilities unverified. No provider credentials or backends were installed. No tmux supervisor was started. Machine-authenticated dual-main runtime receipts are outside this local review's scope.
