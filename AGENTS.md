# Repository agent guidance

Read `prompts/decision_review.md` before substantive work. Follow the execution / proposal-and-wait / verify-or-ask gate; do not silently replace the user's goal or implement a material alternative before alignment except the explicitly bounded supervisor-continuation case in that protocol. This is a project-scoped instruction, subject to higher-priority host instructions and user authorization.

Recheck the gate when new instructions or evidence change a decision. Carry the current decision, constraints, authorized actions, and paused scope into role handoffs and resumed tasks. Use `templates/decision_proposal.md` when a material alternative needs alignment; keep real proposals in the project's temporary area and link the specific version in chat.

For an existing authorized task chain with an actual supervisor event and an unanswered decision, follow the bounded continuation protocol in `workflows/supervised_continuation_workflow.md`. Reversible defaults must be logged; complete the user baseline before isolated exploration. Silence does not override explicit wait/stop or required authorization, and the protocol does not install a supervisor.

For general orchestration use `prompts/orchestrator.md`; use domain workflows only when relevant. Shared decision-review text is embedded in the three main orchestration entry points for standalone use. When changing it, update all copies and run:

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
```

These checks include static prompt/config contracts and executable reader tests. They do not prove LLM compliance, live model access, plugin installation, or external runtime integration. Travel entry points share `plugins/travel-assistant/skills/travel-planner/references/planning_contract.md`; preserve their navigation and package-local link closure. The approved scope in `docs/decisions/travel_workflow_sync.md` covers portable instructions, not JourneyPilot runtime integration.

## Persistent user preferences and task supervision

User preference recorded 2026-10-03: always pull the latest remote before starting repository edits, and fetch/pull again before every push; integrate concurrent changes without force-push and verify the remote SHA afterwards. Preserve unrelated changes. SGLang is explicitly out of scope and must not be modified.

For authorized multi-step tasks, proactively use `workflows/task_supervision_workflow.md`: compose a validated DAG, evidence predicates and bounded adaptive supervision. The executable `agent_runtime` core does not grant host permissions or install a service. Announce a started monitor only after real ID plus matching live readback. No supported backend means a precise blocker; continue independent authorized work. Complete all required evidence checks, stop only owned monitors and read back cleanup. Never confuse blocked/failed/cancelled with done. Read the existing continuation protocol for low-risk defaults and baseline-first exploration; do not duplicate or relax its permission gates.

## TASK.md and tmux ownership (user preference, 2026-10-06)

For authorized multi-step server work, the main AI owns configuration and maintenance of the task DAG, supervisor, timers and every agent. Automatically ingest project `TASK.md`, or accept a user-triggered plan and reconcile it into the same file. Preserve stable requirement IDs and existing evidence. Use the tmux-managed entry point in `workflows/task_supervision_workflow.md` even when the main AI is already in tmux; do not tie supervision to the SSH client or silently fall back to a foreground process.

After every task outcome, compare against `TASK.md`: identify the requirement, actual results/data and evidence, acceptance outcome, remaining work and next owner/action. Completion requires all requirements mapped, independently verified and reportable; checkboxes, missing ready nodes or failed budgets are not success. Changed requirements require a versioned replan. Main AI maintains a real host adapter and recovery path, continues authorized independent work and keeps supervision alive for unresolved work. Respect explicit cancellation and all authorization/budget boundaries. SSH disconnect does not cancel; host shutdown/reboot is not covered by tmux. Verify live IDs/readback before claiming startup, and clean up only owned resources after final reporting. Do not claim a remote server deployment when only repository configuration was changed.

Keep the single active `TASK.md` at the current project root. Read it on startup/resume, before delegation, after every outcome and before final reporting. The main AI serializes task-file changes; agents return evidence and proposed updates. Keep high-frequency runtime state in `.agent-runs/<run_id>/`, not in competing task files. Use `code-organization` for proactive output planning, cross-agent artifact handoffs and incremental CODEMAP upkeep; designate one writer per output path and preserve active job paths.

## Project memory and artifact lifecycle

Use `workflows/project_memory_workflow.md` for cross-session evidence and corrected user intent. Keep stable instructions here and current requirements/results in root TASK.md. Bind memory references to source and immutable dependency IDs; corrections invalidate affected interpretations/reports, not raw historical measurements. Independent verification still owns acceptance. Keep `.agent-memory/` private; never claim a local correction deleted inaccessible cloud memory.

Reuse parameterized scripts and existing evaluation catalogs. Keep immutable run evidence with a stable report index as described in `workflows/code_organization_workflow.md`. Complete the entire authorized TASK baseline before bounded `agent/<task-id>/<run-id>` exploration; apply the existing real-supervisor, permission and budget gates.
