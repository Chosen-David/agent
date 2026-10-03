# Cross-feature evaluation: research and bounded adoption

Research checked 2026-10-03. This is an engineering adoption note, not a benchmark
result. The local implementation remains `scripts/agent_eval_pipeline.py` and the
existing role catalog; no third-party evaluator or paid model dependency is added.
Papers were read through their versioned original arXiv HTML; implementation files
were read through the connected GitHub API at the commits below. Direct terminal
GitHub HTTP access failed with proxy 403; the connector read succeeded. Upstream
frameworks were inspected, not installed or executed. Repository changes and real
host results require their own evidence; this note establishes neither.

## Primary sources and inspected implementation

| Source | Verified method / code | Transfer and limitation |
| --- | --- | --- |
| [τ-bench, 2406.12045v1, §3](https://arxiv.org/html/2406.12045v1) | Evaluates final database plus required communicated outputs; defines pass^k as all k trials succeeding, unlike pass@k's at-least-one. Explicitly notes a correct end state can still violate required confirmation. | Prefer executable end-state checks, plus separate authorization/process checks. Synthetic customer-service outcomes are not evidence of scientific-writing quality. |
| [τ²-bench, 2506.07982v1, §3.3 and Appendix B.2](https://arxiv.org/html/2506.07982v1) | Uses task-specific subsets of database, environment assertion, communication, natural-language and action checks. User and agent can both change a shared world; solver/communication ablations diagnose failures. | Use heterogeneous criteria and producer/consumer state checks. Our artifact pipeline has no dual-control user simulator, so we borrow the separation rather than claim τ² coverage. |
| [AgentDojo, 2406.13352v1, §3–4](https://arxiv.org/html/2406.13352v1) | Separates benign utility, utility under attack and targeted attacker success, using environment checks; warns injected content can also target an LLM judge. | Include good cases to expose blanket rejection; retain independent trusted oracles. This smoke suite does not establish prompt-injection robustness or reproduce AgentDojo. |
| [Inspect official scorer documentation](https://inspect.aisi.org.uk/scorers.html) | Separates per-sample scorers from aggregate metrics; supports format, exact, model-based and custom checks. | Preserve check-level explanations and measurement failures. Generic text matching cannot establish rendered figure or research-paper quality. |

The inspected source pins are separate from paper versions; current implementation
behavior must not be retroactively attributed to a paper's published experiments:

- **τ²** [`evaluator.py` at 5bfa7e37b36656b37dc6d022156be6563c1007f3](https://github.com/sierra-research/tau2-bench/blob/5bfa7e37b36656b37dc6d022156be6563c1007f3/src/tau2/evaluator/evaluator.py):
  `evaluate_simulation` retains component breakdown and combines only configured
  `reward_basis` components; unevaluated declared bases raise. `strict_replay`
  controls recorded tool-output consistency. **Do not copy** its no-criteria
  success branch: this repository correctly requires nonempty frozen criteria.
- **AgentDojo** [`task_suite.py` at 089ed468cf3ed0322acc66b0211f26d9d90dbf60](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/task_suite/task_suite.py):
  `_check_user_task_utility` and `_check_injection_task_security` accept traces and
  before/after environments. `check()` uses `GroundTruthPipeline` to validate task
  definitions. That is fixture validation, **not** a model run. The task runner
  retries missing outputs; locally every attempted run must remain separately
  visible, including failures, instead of collapsing retries into one success.
- **Inspect** [`_metric.py` at 93f7182cf2ce9be22724b05e499cd1358d7ed41d](https://github.com/UKGovernmentBEIS/inspect_ai/blob/93f7182cf2ce9be22724b05e499cd1358d7ed41d/src/inspect_ai/scorer/_metric.py),
  commit whose changelog names **0.3.276**: `ScoreReason` distinguishes
  `no_response`/`refusal` from `grader_failed`/`scoring_failed`; `Score` preserves
  explanation, metadata and edit history. `Score.unscored` is excluded from its
  metrics; here also report the entire frozen denominator so exclusions cannot
  inflate coverage. `MetricScores` distinguishes epoch-reduced and unreduced data.

## Adopt a small contract, not another framework

Retain `prepare → record-start → collect → grade → report`. Existing source/input/
output hashes, immutable attempts, worker/grader identity checks, exact criteria
coverage and first/latest attempt distinction already supply most needed mechanics.
Extend only the developer entry boundary and case-specific contracts/evidence.

1. Freeze the task catalog, fixture/generator seed, split, rubric and budgets before
   role dispatch. Require a real host start event, turn output, skill commit and
   collected input/output hashes. A test that fabricates receipts tests the
   recorder; it contributes zero real-host attempts. Missing host access is
   `not_run`/blocked, never a model pass.
2. Keep three distinct evidence layers: **program checks** (actual generated files,
   state transitions and validator execution), **role observations** (what the
   worker actually read/rendered/executed and delivered), **independent review**
   (semantic adequacy against frozen criteria). A controller replay can check a
   PDF but cannot retroactively prove the worker viewed it. Output prose claiming
   execution is insufficient. Hash equality proves content identity, not truth.
3. Use trusted deterministic oracles where possible: numerical values/units,
   file bytes and actual rasterization, repository branch and tensor execution,
   state/lease transitions, exact consumed handoff version. Use independent
   semantic judgment for genre, evidence sufficiency, and visual meaning. A
   section heading, filename, or self-reported status is never sufficient.
4. For each feature include a valid control, one targeted defect, and a boundary;
   add a separately generated holdout whose content/structure was not used to fix
   the detector. Freeze holdout before reveal, and do not tune on it. Renaming a
   training fixture is not a holdout. Record exposure when workers share a host
   filesystem: separate directories/context instructions are not OS isolation.
5. Preserve expected truth in controller/reviewer material. Workers receive only
   task inputs and applicable skills; they do not receive answers, rubric,
   expected failure labels, or controller paths. Review artifacts as untrusted
   data. A reviewer saying “pass” is not an oracle; retain the exact evidence and
   adjudicate disagreement against the actual file/state/trace.
6. Record `expected`, `observed`, verdict, evidence and reason per case. For a
   defect detector define positive = defect present: false positive rejects a
   good case, false negative accepts a defective one. Separately record whether
   its explanation is sufficient. Ungradable/missing evidence is not silently a
   true negative. Report feature-specific confusion counts and coverage rather
   than pooling unrelated rubric scores into a single quality percentage.

Suggested record additions can remain controller report metadata rather than a
new framework: `feature`, `split`, `execution_layer`, `oracle_kind`,
`expected_defect`, `observed_decision`, `reason_sufficient`, `artifact_refs`,
`host_event_refs`, `elapsed_seconds`, `tool_calls`, `tokens`, `cost`,
`measurement_status`. Unknown host usage/cost is `null` with explanation, not 0.

## Reliability, budget and inference limits

For n independent, predeclared trials of one frozen case with c successes,
τ-bench estimates pass^k using `choose(c,k) / choose(n,k)` for `n >= k`; pass@k
uses `1 - choose(n-c,k) / choose(n,k)`. Averages are across a stated case set.
The independence/configuration assumptions matter. Repairs that see prior
feedback are adaptive attempts, not independent samples. Distinct features are
not repeats. With one host trial, only observed first-attempt results are valid;
pass^k for k > 1 and a model stability claim are unavailable.

If budget permits, predeclare three independent fresh-context runs for two
high-risk cases (render mismatch and runtime recovery); cap attempts, elapsed
time and tool calls. Report each outcome and any variation without selecting
the best run. Keep recovery outcomes separate. Do not spend unbounded trials to
reach a pass threshold; failures remain actionable evidence. These counts are a
local smoke budget, not a statistically powered estimate of deployment success.
For future A/B comparisons match task hashes, tool/permission configuration,
model settings and budgets; report paired per-case differences and uncertainty
clustered by case rather than treating correlated attempts as independent cases.

## Production boundary and acceptance experiments

**Normal user tasks must never start the synthetic suite or benchmark.** Explicit
development optimization, feature-validation or CI invocation is the only eval
entry. Add `--dev-eval` to preparation commands; direct API calls are explicit
developer interfaces. This guard is an accidental-trigger control, not a security
boundary or proof that a model always obeys a prompt. Do not add eval imports or
gold/rubric paths to normal runtime orchestration context.

Production task checks remain active: reading actual deliverables, rendering
requested figures, validating a task's handoff and checking permission are
necessary task acceptance. An explicit user request to read ten exemplar papers
before writing is a task requirement and must not be removed as “benchmarking”.
Only synthetic benchmark fixtures, gold answers and eval orchestration stay out.

Execute these boundary tests alongside feature cases:

- A normal runtime task completes necessary artifact checks with evaluator
  imports/launches guarded; no evaluation run directory or synthetic fixture is
  created. Check the real executable path, not just the presence of prose.
- `prepare` without explicit developer opt-in rejects before creating output;
  the same command with opt-in prepares a valid run.
- Explicit research writing still honors requested exemplar reading and actual
  artifact checks. A keyword such as “test” inside ordinary task content must not
  be treated as permission to run the benchmark.
- Missing role start, missing actual artifact, stale source/handoff version,
  blocked permission and cancelled execution cannot satisfy completion.

These are the recommended adoption/acceptance conditions. The accompanying
case reports must identify which were actually executed, which failed or remain
unrun, and which only have structural coverage. No external framework result or
limited synthetic sample establishes generalization to real private research.
