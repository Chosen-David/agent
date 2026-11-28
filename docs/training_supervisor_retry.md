# Follow a managed training retry

A task identifies a scientific measurement and its downstream review. Each launch has its own registry claim, owner and managed output. Bind the known initial attempt, then explicitly bind its registered successor if a technical failure requires a replacement. These operations can also adopt a successor that is already running or finished.

Set the review template's `task` to the logical task name and its `evidence` to the literal `{attempt_evidence}`. Supply the usual independent reviewer, contract, authorization and downstream fields expected by `ResearchHandoff`. The evidence path is resolved beneath the selected attempt's managed physical output at bind time. The launch and consumer must share the registry and filesystem.

```sh
python -m agent_runtime.training_supervisor "$registry" bind "$task" "$old_claim" "$old_owner" \
  --expected-request "$intended_request" --review "$review_template" \
  --max-attempts 2 --evidence-relative timing
python -m agent_runtime.training_supervisor "$registry" rebind "$task" "$new_claim" "$new_owner" \
  --after-owner "$old_owner" --reason 'corrected failed launch configuration'
python -m agent_runtime.training_supervisor "$registry" watch "$task" \
  --interval 20 --retry-wait 300 --timeout 7200
```

Use `tick` for a single reconciliation in an existing supervisor. Start `watch` before or after the rebind. It follows the latest attempt and allows a bounded grace period for an explicit rebind. Restarting the watcher resumes from durable attempt history. Elapsed watch deadlines return 75 and leave the task inspectable. A live attempt is never replaced merely because it is slow. Reuse the same registry when launching retries through the ordinary claim and resource lifecycle.

The intended request may describe a correction to a documented failed first launch in the same scope, family and goal. Every successor must match the intended scientific identity, including any configured input/recovery or benchmark protocol. A successful launch cannot be replaced. A different objective requires a new task. Compare-and-swap predecessor ownership prevents competing successors from overwriting one another.

A successful process receipt and available evidence enqueue exactly one review in the existing `research_reviews` outbox. The installed review consumer must service that task via `ResearchHandoff.advance` or `tick` and verify the evidence before using it. Review status `completed` requires the review receipt and downstream confirmation. Running processes with stale registry state require host reconciliation. This watcher does not infer death, issue training launches or recover orphaned leases.
