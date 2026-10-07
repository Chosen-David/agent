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

## W2: preserved fast-forward, research and mechanism comparison

Remote main advanced to `ce0d1378983faae0837f8dfea0a10d82164d9935` with
knowledge and knowledge-test changes. Preserved all ten existing checkpoint
files/working copies before a clean fast-forward; merged TASK appends, retaining
MATH-03/04 and REV-01/02/03. GitHub and Git head matched. Ten direct communication
/role/guidance dependencies remain byte-identical: original baseline stays valid,
without rerunning unchanged tests. See `evidence/w2-integration.json`.

New full-text reading: Optima, bringing this batch to **2/10**, eight remaining.
AgentPrune original v1 HTML and PDF retrieval returned DisabledError; not read,
not counted; substituted accessible Optima. Readability and evidence sufficiency
remain separate from token minimization. See `research/optima.md`.

New pinned upstream reading covers review reception, scoped re-review and the
review-package → sdd-workspace script interface. See `research/upstream-review.md`;
no install, script execution or effect claim. Their ledger/filename mechanisms
do not supply atomic receipt/request consistency or scientific acceptance.

`comparison.md` contrasts current publish-first, host journal and optional atomic
operation. No winner or implementation selected. Compatibility review explicitly
retains legacy ACK behavior: an opt-in helper would protect migrated callers,
not cure ACK-first misuse everywhere. Next comparison must include immutable
receipt conflicts, failure before commit and a passing current-protocol control.

Before independent review, new executions: none; previous 14/14 program
evidence remains applicable to unchanged communication code. No new candidate.
Research synthesis and final-candidate all-role/targeted real handoff gates remain
incomplete. No commit/push; this is the same unpublished batch, not a round
completion or convergence increment. Next wake resumes eight original readings
and discriminating recovery comparison, not another baseline reset.

## W2 independent diagnosis and prospective clarification

Actual independent host-model design review completed; report preserved. Two
focused fixture outcomes were reported by the reviewer (receipt conflict and
mutated-reference retry); exact script/stdout not retained, so these are bounded
reported diagnostic observations, not release tests. No frozen candidate role
tasks, scientific closure, quality A/B or external integration ran. Root accepted
REV-W2-DESIGN-001/002: supported adapter protection differs from universal legacy
ACK safety; retained retry differs from actual handling/reviewer closure.
`plan-v2.md` freezes prospective distinctions and fault controls before execution.
Original W1 plan hash verified against checkpoint; a misplaced W2 scope append
was removed and retained in plan-w2.md. All W1 hashes resolve unchanged. No
mechanism adopted and no source/Skill changes, commit or push. Eight readings,
recovery experiments and final candidate real-role gates remain.
