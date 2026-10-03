# Noise / experiment development holdout

Development acceptance only. Normal reviewer or implementation use does not launch this suite.

`python evals/noise_holdout/build.py --output /absolute/new/run` freezes the two skill packages and creates 12 synthetic cases with seed73019, hidden controller oracle and file hashes. The destination must not exist. These cases are independent of the public measurement example used during implementation; they are not claims about real papers/models.

For a real role evaluation, dispatch fresh host-native workers with `fork_turns=none`, reuse `protocol/host_worker.md`, and provide only task/input/snapshot paths. The controller records actual dispatch and creates start.json; a worker must never fabricate its own host receipt. One worker handles reviewer cases c01–c10, another handles CPU/mock implementation cases c11–c12. This is instruction isolation on a shared filesystem, not hard sandbox secrecy.

Freeze completed outputs with hashes. Dispatch a fresh independent judge following `host_reviewer.md`, giving the oracle, rubric, frozen inputs, full outputs and observed dispatch/completion records. Grade substantive evidence and rerun CPU checks; do not implement keyword grading or write expected values into actual output fields. Retain fail/ungradable results and original attempts. If repaired, use a new version/attempt and rerun affected cases plus regression.

The current run reused the repository's host-worker/reviewer protocol with these explicit snapshot paths; it did not claim the `agent_eval_pipeline.py` CLI imported the results. CPU unit tests, real host role outputs and independent judge assessments are separate evidence layers. Full model/tool trace attestation is unavailable; loaded.json/execution.md are worker accounts corroborated by direct artifact checks and controller-observed dispatch/completion.

Coverage: null and large effects, paired versus unpaired, nested correlation, pseudorepeated timers, mismatched warmup/compile/interference, summary-only uncertainty, candidate selection on test, equivalence failure, time/order drift, mock OOM recovery and missing sample rejection. Limited synthetic coverage cannot establish general robustness.
