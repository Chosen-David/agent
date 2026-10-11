# One hourly optimizer

After the five immediate accepted/main-verified 2026-10-11 rounds, one WSL tmux timer invokes a fresh native Windows Python `scripts/token_optimizer.py` once per 3600-second due slot. This is an actual authenticated Codex app-server optimization worker, not a heartbeat presented as optimization. State/raw transport and admission receipts stay in PROJECT_ROOT/.agent-runs/token-optimizer-hourly; one OS worker lock and one WSL timer lock reject duplicates. Restart keeps next_due; missed slots do not cause catch-up bursts. The timer requires the user's Windows/WSL host to remain running; tmux protects terminal detachment.

Before model work: preserve dirty/conflicting work; fetch and fast-forward main; verify HEAD against fetched main; sync/check installed skills; read fresh authenticated quota. Unknown/disallowed quota, spend control or any window >=90% skips inference. Probe mode neither starts a turn nor consumes/advances the next scheduled slot. Failed/skipped slots remain recorded, not successes.

Worker scope is this repository's token optimization. Only relevant skills are enabled, app tools remain available for ordinary non-force main publication, unrelated advice/projects and duplicate agents/schedules are excluded. One optional short no-tool A/B pair has <=2200 supplied chars per prompt, at most two calls and <=50000 measured paired tokens, with independent validity/quality checks. CPU-only/estimates/negative observations and worker exit never increment real-success accounting.

The parent turn has a 1200-second deadline and interruption at observed cumulative usage >=75000. An in-flight request may overshoot; this is not a hard bill limit. Child benchmark usage is separately recorded and is not included in the parent's provider counter. Raw pending work survives interruption. The actual backend is Windows-only; WSL runs the timer/CPU verification. Cleanup targets only the still-live owned Windows backend PID tree. Never force-push or auto-stash/delete concurrent files.

Consumer opt-in examples:

```text
python scripts/task_context.py --root PROJECT_ROOT --task-id ID --sha256 SOURCE_SHA
python scripts/log_context.py --root PROJECT_ROOT --path job.log --sha256 SOURCE_SHA --needle ERROR
python -m agent_runtime.communication --root PROJECT_ROOT --db MAILBOX --plan PLAN inbox-index RECIPIENT
python -m agent_runtime.communication --root PROJECT_ROOT --db MAILBOX --plan PLAN read-pending RECIPIENT SEQ --body-sha256 SHA
python scripts/advice_context.py --root PROJECT_ROOT --path agent_doc/advice/meeting.md --heading ISSUE --sha256 SOURCE_SHA
```

All paths resolve under explicit PROJECT_ROOT. TASK retains all non-task text; details/dependencies still require retrieval. Logs use within-line literal matches, never an absence-of-errors proof. Mailbox index is one pending page; retrieve full version-bound bodies and validate referenced evidence before acting. Advice selects explicit literal H2 topics outside fences, retains leading shared text, and rejects missing/duplicate topics, HTML-comment layouts and unclosed fences. Full source remains the recovery route. Views do not replace human GUIDE priority, evidence verification, ACKs or global completion checks.
