# Shared mechanism comparison — 10/10, research synthesis

| Paper | Preconditions / mechanism | Evidence and cost | Failure / combination | Decision and repository target |
|---|---|---|---|---|
| AgentDropout v1 | Train participation/edges | Tables1–7; training cost | Pruning can remove required repair edges | Reject learning runtime; mandatory-edge controls pending |
| Optima v1 | Weight training with quality/token objectives | Tables1–3,C,E; training overhead | Compact messages can omit correction evidence | Reject training; sufficient evidence refs pending in eval pipeline |
| AgentSpec v3 | Observable action predicates | Tables4/6 tradeoffs; predicate maintenance | Overblocking and missing context; no crash proof | Pending adapter preconditions; reject DSL import |
| SagaLLM published | Domain compensation and durable dependency state | Four selected cases; qualitative Table10 | Compensation may fail; conflicts with duplicate Engine ownership | Pending dependent-only repair/recheck; reject new coordinator |
| ACRFence v1 | Exact prior effects plus proposed semantic replay/fork | Small attack experiment; mitigation unimplemented | Classifier errors/unknown overhead; authorization still separate | Pending exact restart intent in communication workflow; reject proxy |
| AgentRR v1 | Repetitive tasks, audited experience checks | Form illustration; no matched aggregate or ablation | Stale trace/summary gaps; human audit cost | Pending bounded parameterized recipe; reject new store/private reasoning capture |
| AgentGit v1 | Saved state and reusable trajectory prefixes | One prompt sweep; Figures6–8; no crash study | Restore cannot undo external effects | Pending exact-intent comparison; reject new Engine/runtime |
| HANDRAISER v2 | Trained chunkwise listener | Tables1–8; rollout/SFT cost; token proxy | Late corrections can be lost; repair edges protected | Pending optional boundary fixture; reject durability/streaming adoption |
| Gated Coordination v1 | Verified private state and calibrated escalation | Tables2–10; domain-specific costs | Under-escalation; block-quality metric; mandatory review cannot skip | Pending actionable owner routing; reject copied thresholds |
| AgentDebug v1 | Failed traces and bounded targeted reruns | Table1/Figures5–7; claimed token matching | Inferred causal labels differ from executed intervention | Pending affected-only evidence/recheck fixture; reject forced guesses |

## Current decision and evidence state — 2026-10-07 W9 checkpoint

The ten rows above retain the paper-level mechanism proposals and their evidence
limits. They are not ten implemented optimizers. Research reading remains 10/10
within the explicit scopes and exclusions in the notes and ledger; this update
adds no reading, reproduction, publication verification or new paper count.

Selected for the local candidate: the minimal owned publish-first recovery
contract in the existing communication workflow and its generated reference.
It preserves exact immutable outgoing intent, validates current delivery/receipt
and evidence, publishes successfully before needs_revision ACK, and requires the
responsible role's repair plus original-finding independent recheck. The candidate
is `50dd681a6a1c2cd8064c6b5bdbd60e5ff10271d7e8c5041a2c690ae19781f8ee`;
runtime and standalone Skill bytes are unchanged. This adopts a bounded process
contract for evaluation, not a new Mailbox API, coordinator, scheduler, scientific
done state, learned gate or claim of atomic/exactly-once external effects.

Local evidence now goes beyond the W6 proposal: W7's
`../evidence/needs-revision/recovery-result.json` records the exact
needs_revision publish-before-ACK owned subprocess interruption/replay path;
W8's `../evidence/w8-candidate/consumer/results.json` records targeted recovery,
budget and conflicting-receipt cases. Their original versions, failures and
candidate bindings remain historical evidence, not automatically final-V3 passes.
The independent impact report in
`../evidence/w9-release/independent-impact/report.md` supports only scoped reuse
of unchanged prior scientific writing/figure evidence.

At this dated W9 checkpoint, all 15 final-V3 roles have produced outputs, as
reported by the coordinating main AI; production is not independent acceptance.
The real affected handoff has completed its initial request/recovery stage:
`../evidence/w9-release/handoff/review-initial/stage1-result.json` records child
exit73 after publication, duplicate replay returning seq2, the original
needs_revision receipt, the still-unacknowledged writer request, and no findings
closed. Writer repair and original-reviewer recheck are ongoing at this checkpoint.
This is a real owned host subprocess recovery, not a model-session/Engine restart
or autonomous backend wakeup. Complete handoff, independent final-role acceptance,
remaining nonregression gates, publication and remote verification remain pending.

General reusable recipes must not regenerate irreversible actions or revive stale
scientific conclusions. Paper mechanisms informed the minimal design; local
experiments supply its bounded operational evidence. No model quality, latency,
token/cost benefit or repository-wide safety gain is inferred; fair A/B remains
inconclusive. Historical W1–W7 synthesis files and pre-correction copies remain
unchanged; this dated section supersedes their proposal-era status only.

Combination: AgentSpec-style observable preconditions and exact restart identity
support publish-first; SagaLLM/AgentDebug inform dependent-only repair and independent
recheck. AgentGit/AgentRR caution against replaying stale effects. Optima,
AgentDropout, HANDRAISER and Gated Coordination motivate optional-cost experiments,
but pruning/interrupting mandatory findings conflicts with correctness. Keep these
cost mechanisms pending rather than combine four unevaluated optimizers.


## Final W9 acceptance addendum

Latestmain3851bbb integrated; candidatef2455801 has unchanged V3 workflow bytes. Fresh protected15-role/47-criterion run passed after independently reviewed materials. Original ungated15 retained as a real setup failure. Actual writer/recheck now completed:2findings resolved,1rejected preserved,3events3receipts0pending. Targeted controls and scoped historical scientific reuse accepted; commit/push/readback still pending. See ../round.md and ../evidence/w9-release/release-acceptance.json. This addendum supersedes the earlier W9 in-progress status without rewriting its original observation.
