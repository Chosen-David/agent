# Reproduce the independent program cases

The saved `adversarial_checks.py` is the exact independent test source. Its relative source location expects a private two-level run directory, not this archive directory. Copy it before executing; do not run in-place here.

```bash
mkdir -p .agent-runs/pipeline-independent-replay
cp docs/continuous_optimization/rounds/2026-10-03-r2/evidence/adversarial_checks.py .agent-runs/pipeline-independent-replay/
python .agent-runs/pipeline-independent-replay/adversarial_checks.py replay-1
```

Use a new label on another replay: previous artifacts must not be overwritten. The 25-case script includes both the original 23 cases and two subsequently discovered ancestor-symlink cases. Initial result JSON retained the original 23-case scope. All receipts and grades in these tests are explicitly synthetic program fixtures, not evidence of a model run. Model smoke records are separate.

Baseline root suite:120 passed before new pipeline; reader first attempt failed all3 because the ordinary sandbox forbade sockets. Approved loopback rerun passed3/3, and final reader log is retained. That environmental failure was not skipped or recorded as a pass.

## Replay current model records without model calls

From the repository root, after fetching the recorded revisions:

```bash
python docs/continuous_optimization/rounds/2026-10-03-r2/evidence/replay_model_records.py \
  docs/continuous_optimization/rounds/2026-10-03-r2/evidence/model-current.tar.gz \
  --repo . --out .agent-runs/r2-replay-new \
  --runner scripts/agent_eval_pipeline.py
```

Use a new output directory. The script rejects unsafe archive members, reconstructs each source snapshot from its pinned Git revision, verifies source hashes, and runs the original implementation's report gates over retained inputs, outputs and exact independent grades. The committed `replayed-reports.json` came from a real successful replay: 18/18 at a223ffc, writer 1/1 at a223ffc, and replacement implementation 1/1 at a3906ea. The effective selection has 19 unique cases, not 20 different tasks. This verifies recorded evidence integrity; it does not rerun the model or authenticate host records cryptographically.

`model-current.json` and `model-history.json` provide archive SHA-256 and sizes. Historical records deliberately include failed/ungradable/incomplete runs and old implementation hashes. Do not pass them through the current implementation and label a mismatch as a new model failure. Their corresponding frozen runner copies are included under `runners/`; they are audit history, not the current release gate.

To execute new tasks, follow `docs/agent_eval_pipeline.md` and the worker/reviewer/tool-proxy protocols in `evals/pipeline_smoke/`. The recorder itself does not invoke models. Populate the writer's dynamic fixture list with the actual producer output files before preparing its manifest; `depends_on` is descriptive and does not perform transfer.
