# Repository agent guidance

Read `prompts/decision_review.md` before substantive work. Follow the execution / proposal-and-wait / verify-or-ask gate; do not silently replace the user's goal or implement a material alternative before alignment. This is a project-scoped instruction, subject to higher-priority host instructions and user authorization.

Recheck the gate when new instructions or evidence change a decision. Carry the current decision, constraints, authorized actions, and paused scope into role handoffs and resumed tasks. Use `templates/decision_proposal.md` when a material alternative needs alignment; keep real proposals in the project's temporary area and link the specific version in chat.

For general orchestration use `prompts/orchestrator.md`; use domain workflows only when relevant. Shared decision-review text is embedded in the three main orchestration entry points for standalone use. When changing it, update all copies and run:

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
```

These checks include static prompt/config contracts and executable reader tests. They do not prove LLM compliance, live model access, plugin installation, or external runtime integration. Treat travel interface changes as pending the decision in `docs/decisions/travel_workflow_sync.md`; do not mechanically synchronize travel files.
