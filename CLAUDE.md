# Claude Code repository entry

@AGENTS.md

Before substantive work, read `prompts/orchestrator.md` and use it as the general main-AI workflow. Keep user/project constraints and host permissions authoritative.

For first-time integration, read `SETUP.md` and run `python3 setup.py --target .` for this repository, or pass the user's actual project directory. This installs the main-AI import, the full Skill catalog and corresponding Claude subagents without replacing unrelated project instructions. Do not claim installation or background supervision until checked.

For authorized multi-step tasks, automatically read project `doc/task/TASK.md` or reconcile a user-triggered plan into it. The main AI owns task chains, agents, timers and the tmux supervisor. After each outcome, reconcile requirement IDs, actual data/evidence and remaining work. Follow `workflows/task_supervision_workflow.md`, including host adapter requirements, restart and completion checks.

Keep `doc/task/TASK.md` as the current project's single active, date-grouped task index; maintain methods/progress/evidence in `doc/task/task_details/*.md`. Before delegation and after outcomes, use `code-organization` to coordinate output directories, artifact manifests and consumer references. Agents report task/file/data changes to the main AI; they do not create separate root task lists or overwrite one another's outputs.

Read `workflows/project_document_workflow.md`: verified human `doc/guide/guide.md` leads project planning within current user decisions and host permissions. AI never writes any file in `doc/guide/`. Human/AI proposals in `doc/advice/` require evidence-based adopt/adapt/reject/defer decisions with reasons before affecting execution.

After each test/experiment produces data, require `workflows/result_validation_workflow.md`: independent `verify_experiment_result` between producer and every consumer; pending/invalid data cannot support conclusions. Fix and retest failures/stale versions, preserve raw evidence, and claim usability only within the verified scope.

For every new project instruction, first search prior results under `doc/results/` using `workflows/result_reuse_workflow.md`, compare code/input/config/environment/metric/scope and current independent validation, and record reuse decisions before scheduling new experiments. Keep new data in `doc/results/<run_id>/`; old indexed references do not imply files were moved. Never skip explicit reproduction or the mandatory result-validation gate.
