# Host-driven Agent evaluation pipeline

This small standard-library runner freezes the actual repository skills and records
model-task execution and independent review. It **does not call a model**, install
an external runtime, guarantee model behavior, authenticate receipts, or publish
commits. The host invokes its real worker/subagent facility and supplies observable
execution receipts. Python tests of this runner are not model-task results.

## Boundary and provenance

`prepare` resolves a Git revision once and reads tracked files from that commit,
not from a potentially dirty worktree. Its snapshot contains `plugins`, `prompts`,
`workflows`, `templates`, `config`, and `agent_runtime`, plus `AGENTS.md` and the main entry point’s explicit handoff/backend, paper-validation and experiment/supervision dependencies, excluding `tests`, `evals`, and rubric files.
The worker receives only its prompt, inputs, output directory, and applicable
snapshot entry points. The explicit dependency allowlist closes the main
orchestrator’s known local handoff/backend links; this is not a transitive
dependency resolver. Optional apps, external runtimes, and links outside the
snapshot require separately declared capabilities. A missing dependency must
be reported as blocked or ungradable, never silently replaced. The manifest freezes expected cases, source commit,
snapshot/input/prompt/task-catalog/rubric and pipeline-implementation SHA-256 hashes, and adapter metadata.
The full catalog is the fixed denominator; missing cases cannot disappear from
reports. Baseline and candidate comparisons must use identical task/rubric/input
hashes and model/tool/budget configuration. One successful run does not establish
improved success rate.

The controller must retain the manifest outside worker write access or verify it
against an external trusted copy. Start records bind its bytes to each attempt.
The runner checks integrity at transitions and report time; it cannot detect a
change that was made and restored between checks. Receipts and reviews supplied
by a trusted controller are records, **not cryptographic execution attestation**.
Changing an actor string does not prove a different model context. The controller
must actually isolate worker/reviewer contexts and inspect real artifacts/tools.
All paths share a filesystem by default: directory separation is not a security
sandbox and does not prevent a malicious worker from finding the rubric.

## Catalog and adapter contract

Tasks use the existing `evals/tasks.json` format:

```json
{"cases":[{"id":"example","role":"research-write",
 "skill":"plugins/research-assistant/skills/research-write/SKILL.md",
 "prompt":"Write a bounded result paragraph from the supplied data.",
 "fixtures":["measurements.csv"]}]}
```

`role` defaults to `id`; a general main-AI case can select
`prompts/orchestrator.md` as its skill entry point. Fixtures default to
`evals/fixtures` at the pinned commit. External fixtures require explicit
`--fixture-root`; paths must remain inside it. Rubric JSON uses
`{"criteria":{"example":["check one","check two"]}}`. Empty criteria, duplicate
cases/checks/fixtures, missing skills, and mismatched case sets are rejected.

Adapter JSON defaults to `{"name":"host","model":"unspecified","max_attempts":3}`.
Record the actual model configuration, tools, and budget here when available;
`unspecified` is honest missing provenance and cannot support model-matched A/B
claims. `max_attempts` is an enforced integer from 1 to 10. Host invocation must
also enforce wall-clock, tool-call, and monetary limits: this recorder does not
own the running process. A mock adapter never passes the real-task gate.

## Commands and directory interface

```bash
python scripts/agent_eval_pipeline.py prepare --dev-eval --revision FULL_SHA --out /tmp/agent-eval
# Optional: --repo /path/to/repo --tasks /path/tasks.json --rubric /path/rubric.json
#           --fixture-root /path/fixtures --adapter /path/adapter.json
python scripts/agent_eval_pipeline.py record-start --run /tmp/agent-eval \
  --case example --actor actual-worker-id --receipt /tmp/start.json
# Host sends the task to that real worker and observes its execution.
python scripts/agent_eval_pipeline.py collect --run /tmp/agent-eval \
  --case example --attempt 1 --receipt /tmp/complete.json
# Host invokes a genuinely separate reviewer with the frozen criteria and outputs.
python scripts/agent_eval_pipeline.py grade --run /tmp/agent-eval \
  --case example --attempt 1 --grade /tmp/review.json
python scripts/agent_eval_pipeline.py report --run /tmp/agent-eval
```

The example commands require a custom catalog containing `example`. The default
catalog instead uses the current registry's role case IDs. Paths:

- `RUN/snapshot/`: fixed role definitions and their dependencies.
- `RUN/cases/CASE/task.txt` and `inputs/`: immutable task inputs.
- `RUN/cases/CASE/attempts/0001/outputs/`: worker delivery directory returned by start.
- Each attempt: `start.json`, `collection.json`, then independent `grade.json`.
- `RUN/{manifest,tasks,rubric}.json`: controller/reviewer material.

Do not give the worker the rubric or grading instructions. A reviewer may read
observed tool results supplied by the host in addition to artifacts. Actual
render/open evidence is needed for image/PDF tasks; a worker's sentence claiming
that it viewed a file is insufficient.

If the host cannot export worker tool events, use the
[observable tool proxy](../evals/pipeline_smoke/host_tool_proxy.md) for required
process checks. The worker requests the operation during its task; the controller
executes it and returns the actual result. A later reviewer replay checks the
artifact but does not retroactively prove the worker performed that operation.

Start receipt (generated from the host's real dispatch response):

```json
{"event_id":"unique-host-dispatch-event","kind":"start","actor":"actual-worker-id",
 "adapter":"host","case_id":"example","attempt":1}
```

Completion receipt uses a distinct observed event ID, `kind:"complete"`, the same
actor/case/attempt/adapter, and `status:"produced"`, `"infra_error"`, or `"blocked"`.
Additional host evidence fields are retained. `produced` only means delivery,
never correctness. The collector recursively hashes all output files. Every transition and
report rejects symlinks anywhere inside the run tree, including case/attempt
ancestor directories and records. A duplicate active dispatch or reused start-event ID is rejected.
Existing records are written exclusively and cannot be overwritten by these APIs.

Review contract:

```json
{"grader":"actual-independent-reviewer-id","case_id":"example","attempt":1,
 "output_hashes":{"result.md":"ACTUAL_COLLECTED_SHA256"},
 "checks":[
   {"criterion":"check one","verdict":"pass","artifact_refs":["result.md"],"evidence":["result.md:4; input.csv row 2"]},
   {"criterion":"check two","verdict":"fail","evidence":["Missing required uncertainty statement"]}
 ]}
```

Every exact frozen criterion must appear once, with `pass`, `fail`, or
`ungradable` and nonempty evidence locations (or a specific missing-evidence
explanation). A passing check must reference at least one collected output:
prefer `artifact_refs:["relative/output/path"]`; legacy evidence beginning with
an exact collected path followed by `:` also supplies a reference. Explicit
references must stay inside outputs and name known collected files. Missing
references cannot be made passing by a free-form success assertion. The runner
revalidates receipt metadata, event uniqueness, attempt directory identity, and
the exact nonempty task/manifest/rubric case sets on report replay. It validates
this record structure and hashes, not the
semantic truth of its prose. An independent reviewer or executable domain oracle
must establish that truth. Empty grading, same worker/grader ID, absent outputs,
changed inputs/source/rubric, and outputs modified after collection cannot pass.

## Recovery, reporting, and release

An unfinished attempt blocks duplicate scheduling. After collection, the host may
start a new numbered attempt within the frozen budget, with a new receipt and
fresh outputs directory. It must not rewrite the first attempt or reuse its
outputs. Reports retain all attempts and expose both first-pass counts and latest
attempt counts; success after recovery cannot inflate first-pass success.
Infrastructure errors, blocked tasks, ungradable checks and absent executions
remain visible. An integrity failure requires a new prepared run, not editing
hashes to resume. The controller should explicitly record the recovery reason.

`report` returns JSON: `expected`, `passed`, `first_pass`, `complete`,
`integrity_errors`, and case/attempt details. Its CLI can successfully emit a
report containing failures: **exit code zero means report generation, not task
success**. Use `report --require-complete` for a nonzero exit when incomplete; consumers
must also inspect every relevant evidence gate.
Nothing in this script commits or pushes. Publication additionally requires the
repository tests, intended improvement evidence, non-regression coverage, fresh
remote-main reconciliation, and post-push verification.

The minimum real smoke catalog covers every current role plus general routing
and actual cross-role handoff; held-out/failure/adversarial variants and repeated
paired trials remain separate evaluation layers. Do not interpret a small,
synthetic smoke suite as real scientific/travel task success or backend runtime
integration.

The additional `evals/pipeline_smoke/tasks.json` catalog is a host plan, not a
standalone DAG scheduler. Merge its independent cases with the registry catalog
before freezing. Prepare `chain-writer` separately only after collecting the real
`chain-coordinator`: copy its `analysis.json` and `aggregate.csv` unchanged to a
new fixture root, set the writer case's `fixtures` to its declared `handoff_inputs`,
then prepare the writer run. Record source collection and source/destination
hashes. The generic recorder does not interpret `depends_on` or move files for
the host. Check both actual writer inputs exist before dispatch. This avoids
mistaking an empty fixture list for a completed handoff.

## Research adaptation

The design combines τ-bench's task-end-state emphasis
([2406.12045v1](https://arxiv.org/html/2406.12045v1)) with explicit artifact checks,
and borrows the task/solver/scorer distinction from
[Inspect AI](https://inspect.aisi.org.uk/eval-sets.html). Unlike retry cleanup defaults, it retains every attempt. It deliberately keeps
host invocation as an explicit adapter boundary instead of claiming a portable
Python script can spawn this host's agents. Research motivates candidate
mechanisms; the tests and separately recorded real runs establish only the local
effects actually observed.

API equivalents are `prepare_run`, `record_start`, `collect`, `grade_attempt`,
and `report`. See `tests/test_agent_eval_pipeline.py` for controlled behavioral
checks; their generated receipts are test fixtures, never execution evidence.

## Development-only boundary

`prepare --dev-eval` is an explicit development/CI operation. Without the flag the CLI exits before creating outputs; the legacy preparer has the same gate. Python `prepare_run` is an explicit developer API, never called by ordinary runtime routing. Ordinary task execution must not load synthetic fixtures, hidden rubrics or benchmark gold. Task-required correctness, artifact/permission validation and the ten-exemplar prewriting contract remain mandatory where applicable. The flag is intent separation, not an authorization or security sandbox.

The snapshot dependency allowlist includes the data-visualization validator imported by paper delivery. This closes an executable dependency, rather than treating two independently existing scripts as an integrated pipeline.
