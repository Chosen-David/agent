# Independent bounded communication optimization plan review

Date: 2026-10-09
Reviewer: `/root/communication_review`, separate host collaboration context.
Reviewed base: `bb5bf5b8edaebd8910f9a7af28830c668113d339`.
Decision: **revise**, limited to fixing the preregistration details below; the proposed implementation direction is reasonable.

This is a direct host review of the planner's supplied bounded plan. It is not a deployed runtime ReviewSession receipt, authenticated supervisor event, permission grant, or result validation. No performance measurements have been executed by this reviewer at this stage.

## Inspection and prior results

Read `AGENTS.md`, decision review, project document, dual main, result validation workflows, the communication workflow, `agent_runtime/communication.py`, and `tests/test_communication.py`. Read the canonical TASK index; `agent_doc/guide/GUIDE.md` is an empty file, so it adds no substantive constraints and its human provenance is not inferred from its name.

Actual prior-result query: `rg -n 'communication|latency|selective' agent_doc/results --glob '*.md' --glob '*.json'`. Hits included `combined-corpus-delta-v2-20261007`, `corpus-fd9012-delta-20261007`, and `combined-integration-v2-20261007` identity/test records. These record related consumer and regression evidence, not a current publish-history benchmark. Also read the preserved `docs/communication_efficiency/2026-10-07-selective/report.md` and `docs/communication_basis_validation/report.md`. They establish historical scope and useful integration targets, but measure context packing/encoding or structural behavior, not this ledger change. Their pass labels and timings cannot be reused as current performance or correctness acceptance.

## Seven review dimensions

| Dimension | Verdict | Assessment |
|---|---|---|
| Intent | pass | Reduce local publish/usage history-dependent work while preserving consumer control and delivery semantics. Direct main publication remains the parent's user-authorized action after evidence. |
| Guide | pass | Empty guide supplies no additional planning requirements. Human-only directory remains untouched. SGLang remains excluded. |
| Assumptions | pass with explicit scope | The hot path really performs COUNT per publish and optional joined SUM; usage scans both tables. Trigger-maintained integer counters are a plausible exact materialized aggregate. Runtime envelopes are immutable, and ordinary legacy APIs insert events/deliveries and update receipts. Arbitrary direct SQL corruption must not be implicitly covered. |
| Prior results | pass | Existing evidence informs regression scope but does not answer the new hypothesis. New targeted measurements and independent verification are necessary. |
| Acceptance | revise | The phrase “target accumulated-backlog median speedup >=1.25” needs a fixed set of workload cells, exact aggregation, repeat count/order, and measured operation before observing data. |
| Risk | revise | Freeze the supported legacy write contract and atomic migration test. Trigger install, backfill, and migration marker must be one write transaction, including concurrent first-open and an old connection publishing across upgrade. |
| Resources | pass for bounded host work | Standard-library local SQLite work and finite matrix are proportionate. Freeze a finite repeats/operations budget. No external service, paid model, or hidden background-runtime claim is needed. |

## Required refinements before measurement

1. Define the primary acceptance cells and computation in the validation plan. A suitable choice is publish latency with delivery budget enabled at backlog 1,000 and 10,000 for both fanouts, requiring every selected cell's baseline-median/candidate-median ratio >=1.25. If a different aggregate is preferred, fix its formula now. Record all cells including budgets off, backlog 0/100, usage, initialization and migration; preserve all repeats and vary/interleave arm order. State whether timing includes object initialization and distinguish steady API calls from CLI construction. Small-workload regressions are explicit tradeoffs, not suppressed failures.
2. Define legacy compatibility as the existing public API's inserts and receipt updates unless full arbitrary SQL mutation support is deliberately implemented and tested. Test a genuine pre-ledger schema populated by the old implementation; then keep an old Mailbox/connection alive during migration and publish afterward. Concurrent initializers and failure injected during migration must leave either pre-upgrade state or a complete exact ledger. Do not use Python `executescript` inside an already-open transaction without accounting for its implicit commit behavior.

## Implementation and validation notes

- Keep duplicate detection before caps: an exact duplicate must succeed even when the event/delivery cap is exhausted, including after ACK. Changed content must remain rejected.
- Independently recompute event count, UTF-8 bytes and joined delivery totals using SQL after every significant mutation; do not use the ledger as its own reference. Check multiple runs, byte-identical multibyte text, zero events/deliveries, and a rejected operation leaving all tables/counters unchanged.
- Check concurrent distinct events near event and delivery-byte caps, not just concurrent identical retries. Confirm no partial fanout and forced rollback after at least one delivery trigger fires.
- Receipt-only UPDATE must not change totals. Preserve order, pending delivery behavior, immutable receipt checks and `tokens: null`/usage scope.
- Initialization must be O(1) with respect to history after the one-time backfill; repeated opens must not double-count. Use a migration marker whose meaning and failure behavior are clear.
- If claiming exactness under direct event/delivery UPDATE/DELETE, add corresponding differential tests including run/seq/body changes, or narrow the claim. Public APIs do not expose those mutations, so implementing a broad SQL mutation surface is not required to accomplish this task.
- A covering index is a useful simpler comparison, but it still scans history for aggregate work. Do not weaken validation, change SQLite durability settings, exclude reference hashing from one arm, or compare different envelope sizes/fanouts to manufacture speedup.
- Freeze actual code/config/raw-data/environment identities before independent acceptance. Integration tests should include communication, revision delivery, handoff basis and selective context, followed by relevant repository regression. Hash integrity and a test runner exit code do not alone validate benchmark interpretation.

Engineering novelty is applying established transactional materialized counters to this mailbox's byte/event budget accounting with backwards-compatible migration. No new research algorithm, model quality improvement, token reduction, distributed delivery guarantee, or deployment is established by this plan.

## Next owner

Planner should freeze the two refinements and send the revised validation plan. Reviewer can approve that bounded revision, then independently inspect the frozen candidate and actual raw results. Publication remains blocked on that later result validation, not on new user permission for routine implementation details.
