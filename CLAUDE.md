# Claude Code repository entry

@AGENTS.md

Before substantive work, read `prompts/orchestrator.md` and use it as the general main-AI workflow. Keep user/project constraints and host permissions authoritative.

For first-time integration, read `SETUP.md` and run `python3 setup.py --target .` for this repository, or pass the user's actual project directory. This installs the main-AI import, the full Skill catalog and corresponding Claude subagents without replacing unrelated project instructions. Do not claim installation or background supervision until checked.

For authorized multi-step tasks, automatically read project `TASK.md` or reconcile a user-triggered plan into it. The main AI owns task chains, agents, timers and the tmux supervisor. After each outcome, reconcile requirement IDs, actual data/evidence and remaining work. Follow `workflows/task_supervision_workflow.md`, including host adapter requirements, restart and completion checks.

Keep `TASK.md` at the current project's root as its single active task list. Before delegation and after outcomes, use `code-organization` to coordinate output directories, artifact manifests and consumer references. Agents report task/file/data changes to the main AI; they do not create separate root task lists or overwrite one another's outputs.
