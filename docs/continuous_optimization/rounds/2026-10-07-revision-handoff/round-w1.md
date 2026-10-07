# Revision handoff recovery — unpublished batch

Baseline main: `04becb4ad8bc3e114d66c13dfe95af9cc2b53573`, freshly pulled
fast-forward and independently read through GitHub. No other live worker was
reported by the current host. Previous batch is published and remains intact.
The platform did not expose a scheduler run ID; root host identity is observable,
not proof of continuous background execution.

## W1 new progress

Read current root TASK, AGENTS, decision protocol, role/backend registries,
optimization state, communication research/runtime/workflow/tests/demo,
project memory workflow and existing evaluation pipeline entry. Fifteen roles
remain registered. No role, Skill, runtime or external integration modified.

Preregistered [plan.md](plan.md) before executing [baseline replay](evidence/baseline_replay.py).
Actual [baseline.json](evidence/baseline.json):

| Order / interruption | Reviewer pending | Implementer pending | Result |
|---|---:|---:|---|
| ACK first, process exit 73 | 0 | 0 | Repair stranded in normal inbox view |
| Publish first, process exit 73 | 1 | 1 | Retry deduplicates, ACK then succeeds |
| ACK first, event budget exhausted | 0 | 0 | Repair not delivered; original ACK persists |
| Publish first, event budget exhausted | 1 | 0 | Original message remains available |

Both stranded cases retain the `needs_revision` status record: database loss is
not claimed. The existing demo already publishes first, a passing control.
Current runtime intentionally leaves semantic closure to trusted adapters;
this is a reproducible orchestration contract risk, not a failed promise of
automatic finding closure. Existing communication unit suite: 14 passed,
0 failed, 0 skipped. Program execution used synthetic files and SQLite;
no new model task was performed.

Research: 1/10 new full-text papers, [AgentDropout notes](research/agentdropout.md).
Nine remain; synthesis and pinned upstream Skill/dependency inspection pending.
Learning suggests preserving required repair/recheck edges while evaluating
cost; it does not justify learned pruning or confer recovery semantics.

## Decision / next checkpoint

No implementation selected. Compare publish-first host contract/journal against
a compatible optional combined operation, especially failure between commits,
event budget exhaustion, immutable receipt conflicts and retry. First complete
relevant research; retain CO-016 organization and corrected-intent leakage
queue items without unrelated edits. Reuse existing model eval pipeline for
targeted communication and all-role candidate gates.

| Evidence category | This wake |
|---|---|
| Program | Four diagnostic paths; existing communication 14/14 |
| Actual role tasks | Not run on a new candidate |
| Cross-role model handoff | Not run; synthetic process control only |
| Old/new A/B | No candidate; model comparison not executed |
| External backend integration | Not executed |

Unpublished checkpoint, not a completed round. Research, candidate selection
and release gates remain incomplete; no commit or push. Convergence counter
stays zero. Existing recurring task is unchanged.
