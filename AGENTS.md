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
