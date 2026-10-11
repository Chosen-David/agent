# TOK-FIVE required regression packaging repair

Parent correction: inherited test failures do not satisfy the required regression gate. Commit `bbdb7c02723068ad3d039356cfae0dd2045b0f4f` was a scoped code fix, not full acceptance. The original failed logs/review remain frozen in the parent evidence directory.

Fresh fetch found main still bbdb7c0 and the same two stale mirrors. Ran only the existing `python scripts/sync_plugin_references.py`; it changed exactly the bundled `coverage.json` and `learning_state.json`. Canonical `knowledge/` source bytes, meaning/state, generator and validators are unchanged. This copies already-published main content; it introduces no knowledge expansion and does not merge the old c535330 accounting candidate.

`mirror-check.json` records exact byte comparisons and canonical SHA-256 values. `generator-check.log`, `required.log` and `reader.log` contain the new checks. Independent review checks mirror equality, unchanged canonical/source code, scope and completed results before acceptance/publication.

No model or real-token experiment was repeated. This is the packaging prerequisite for the local reporting fix; it makes no provider billing, full-chain accounting, quality or cost-saving claim. Parent independently read back bbdb7c0 with Actions0 and no required checks; new-commit remote readback remains part of publication closure.

Final checks: generator `--check` exit0; required `python -m unittest discover -s tests -v` exit0,1022 run/1021 passed/1 opt-in tmux skip/0 failures; reader suite exit0,3 passed. Previous affected31-test review remains bound to unchanged implementation/tests. Required regression gate is now satisfied, unlike the preceding inherited-failure state.
