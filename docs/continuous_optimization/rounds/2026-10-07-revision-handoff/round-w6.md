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

## W3: six prospective existing-API controls and third reading

Git fetch and connected GitHub ref readback both match main ce0d137; no remote
change, no need to restore or fast-forward dirty checkpoints. W2 hashes verified
before continuation; root only live executor. Decision EXECUTE bounded diagnostic.

Frozen plan-v2 and w3-preflight identify six cases. Reused CommunicationTests
fixture and current Mailbox: three real child exits73 before publish, after
publish and after ACK restart from saved intent; one request and matching receipt
remain. Conflicting prior receipt is rejected before new publication; mutated
finding blocks replay, preserves pending incoming and already persisted outgoing.
Exact duplicate at event limit preserves two subscribers' independent receipts.
Six assertions pass in the completed run, not six model tasks. References are
synthetic, SQLite and process interruptions real. No semantic finding closed.

First probe attempt failed preparing a modified plan in an existing database;
runtime correctly rejected it. Original probe and failure retained; repaired
fixture uses fresh database and saved DB name, then one bounded rerun completed.
See evidence/protocol_probe.py, w3-first-failure.json, w3-protocol-results.json.
No timeout/performance/token benefit claimed; unchanged unsafe W1 controls remain.

AgentSpec full main text/experimental tables/limitations and Figure4 read; batch
3/10. Existing preconditions are a candidate mechanism, no DSL/import adoption.
The six controls justify further existing-protocol evaluation, not necessity of
a journal/atomic API. Remaining invalid-input cases and real model repair→original
reviewer recheck need new bounded preregistered work; all-role final gate absent.
No production API/Skill/workflow changed or release candidate selected. No commit
or push; same batch remains incomplete, convergence counter unchanged.

## W4: concurrent main preserved and six input-boundary controls

Main advanced from ce0d137 to 1d041699067555d782e201fe56d0bddf853532fb.
Git and connected GitHub agreed. Preserved32 working/checkpoint files outside
checkout, verified hashes, restored clean HEAD, fast-forwarded, then merged only
local TASK append and restored unchanged optimization records. MATH05/06 and
knowledge changes retained. Nine direct dependencies unchanged; no invalidation
of existing communication controls. One root executor observed, no second model
worker. W3 checkpoint preserved before edits.

Preflight froze six remaining cases before script execution. boundary_probe.py
imports existing saved-intent probe and CommunicationTests fixture, no alternate
model evaluation runtime. Missing ref/stale version/unapproved route/exhausted
budget/changed duplicate body/conflicting needs_revision reason all rejected,
with status exactly equal before and after; 6/6 assertions, first run, no retries.
See w4-boundary-results.json for raw errors and state. Synthetic records and real
SQLite, zero model tasks; budget stays blocked, not authorized migration or done.
Together W3/W4 cover12 scoped program controls, not broad production safety or
scientific repair. Legacy ACK-first hazards retained. No generic suites rerun.

SagaLLM published full main paper read, batch4/10; limitation/qualitative evidence
notes distinguish compensations from local transactions. No new runtime justified
by the scoped evidence; owned publish-first recovery remains the smallest pending
protocol candidate, not adopted/released. Six original readings and final frozen
real-model repair/reviewer closure/all-role gates remain; no code/Skill/workflow
change, commit or push. Next bounded work should freeze actual finding/repair
inputs and rubric in existing eval pipeline while continuing complementary papers.


## W5 incremental checkpoint

Preserved41 files, verified36 checkpoint hashes, clean fast-forward to main
5ec5c681cb98b1692b57945bf5e6f4ce49a9d752; GitHub ref agrees. Nine communication/
guidance/eval dependencies byte-identical; concurrent information knowledge and
TASK content retained. No active prior executor observed.

Research6/10: ACRFence and AgentRR original methods/cases/limitations read;
key figures actually viewed, exact scopes and rejected unevaluated imports in
notes. Shared six-paper mechanism table normalized; four remain. No adoption.

Existing scripts/agent_eval_pipeline.py prepared pinned baseline tasks/fixtures/
rubrics before each dispatch; actual collaboration host ran independent reviewer,
writer, then same original reviewer. Executor task/inputs exclude rubric and root
scoring notes; shared filesystem is instruction isolation, not security sandbox.
Root independently read actual full manuscripts/reviews/closures, recomputed CSV
means and compared all six table tuples and unchanged sections. Initial3/3,
writer4/4,recheck3/3 required checks pass; three original finding IDs correctly
closed in new snapshot, original findings remain immutable/open historical records.
Mailbox2events/2deliveries/2receipts/0pending readback. Writer actually publishes
hashed revised artifact before consuming original review. Private completed DB
checkpoint retained outside public evidence; JSON statuses/logs and artifacts kept.

This is actual model execution on explicitly invented timing fixtures, not a real
benchmark. No new general program suite (unchanged dependencies), final-candidate
all-role task, model crash recovery/needs_revision ordering, fair A/B or external
backend integration. Exact model/seed/token/cost/latency unknown; A/B inconclusive.
No runtime/Skill/workflow production edit or candidate, commit or push. Legacy
ACK-first failures retained. Next: remaining four papers/synthesis, justify minimal
protocol scope, then final-bound candidate targeted recovery and complete gates.

## W6: ten original readings and mechanism synthesis completed

Git/GitHub initial fresh main readback matched5ec5c68; final Git fetch remains
identical. Retained owned dirty checkpoints. W5 118 historical artifact hashes
resolve unchanged, including frozen round/synthesis snapshots; no competing host
executor observed before two bounded independent paper reads.

AgentGit/HANDRAISER independent original readings completed; root reopened key
original method/setup/limitations. Root completed Gated Coordination/AgentDebug
core original text, required experimental/ablation/limitation sections and selected
figures. Original PDF rendering bypassed web screenshot textual placeholders;
no public PDF/figure copies stored. Exact read scopes, exclusions, source IDs and
PDF hashes recorded. Same Winners recovery paper and microservice recovery HTML
access failures not counted; accessible AgentDebug substituted. Ledger10/10;
one ten-row mechanism table combines prerequisites, evidence, costs, failures and
adoption decisions. Paper inconsistencies and domain-specific metrics retained.

The smallest selected experiment proposal remains owned publish-first with saved
exact immutable intent/current refs/conflict rejection and independent recheck.
Reject new scheduler/trained pruning/streaming/runtime imports. Existing12 program
controls and W5 actual synthetic closure support feasibility, not this exact model
crash path. w6-recovery-preregistration.md freezes needs_revision, after-publication
child interruption, one replay, owner handling and original reviewer closure.
Not executed; no invented result.

Five evidence classes this wake: program tests no new execution (unchanged prior
controls retained); role tasks no new final-candidate runs; cross-role exact recovery
prepared only (W5 real diagnostic preserved); fair A/B inconclusive/no candidate;
external backend integration not executed. No production code/Skill/workflow edit,
release candidate, commit or push. Batch remains open and convergence count0.
Next: execute exact host recovery diagnostic, decide minimal implementation, bind
final candidate and run all current-role/targeted/handoff/nonregression gates.
