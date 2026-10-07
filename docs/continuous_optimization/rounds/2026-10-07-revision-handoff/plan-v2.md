# Prospective protocol recovery preregistration v2

Applies only to future candidate/control experiments; no such experiment has run.
W1 plan, observations and inbox-visibility metric remain preserved unchanged.
Root accepts independent findings REV-W2-DESIGN-001/002. This clarification
corrects scope and measurement, not a retrospective pass or reduced release gate.

Baseline communication source is unchanged between 04becb4 and current main
ce0d1378983faae0837f8dfea0a10d82164d9935; bind exact source/input/implementation
hashes before execution. No implementation selected. Compare an explicit existing
publish-first adapter protocol first, against unchanged unsafe ACK-first controls;
add a journal or atomic helper only if a discriminating failure justifies its cost.

Supported protocol: single owned consumer, persisted exact event/receipt intent,
immutable references, publish request before incoming needs_revision ACK. Existing
legacy two-field ACK remains supported but alone cannot ensure a repair event;
unmigrated ACK-first callers remain an unsafe control, never counted as cured.
A conflicting prior receipt requires explicit reconciliation before publication;
a read precheck is not concurrent ownership or transaction protection.

Freeze before implementation the crash sites: before publication, after publication
before ACK, after ACK before host completion record; terminate a real child and
restart from saved intent. If an atomic helper is later proposed, preregister its
internal insertion/receipt/commit fault sites separately before editing that helper.
Freeze additional inputs not used in W1: conflicting consumed/rejected receipts,
missing/stale/mutated reference, changed event body, exact retry at event limit,
and two subscribers with one already acknowledged. Do not relabel W1 as heldout.

Record separately: (1) durable retry opportunity, (2) request persisted with exact
validated ID/body and subscriber state, (3) actual responsible consumer handling,
(4) original independent reviewer closure against actual revised artifact.
A normal inbox count or ACK cannot establish stages 3/4. W1 budget control retains
stage 1 only. At exhaustion, report blocked/pending, without deleting work or
inventing a budget increase. Any later authorized new-run migration is a separate
frozen recovery experiment, not success in the exhausted original run.

Minimum meaningful program improvement: all supported-path crash/restart cases
recover the same request and matching immutable incoming receipt with no duplicate
new event, lost subscriber state or conflicting orphan request; invalid/conflicting
cases fail explicitly without partial publication/ACK. Primary metric is exact
state consistency plus recovered request, not absence from the inbox. Retain all
unsafe legacy failures. No weaker route/version/hash/budget/receipt checks; no
new scheduler, semantic done state or automatic reviewer closure. If existing
publish-first protocol meets the standard, prefer it over extra runtime machinery.

Program reliability does not establish scientific quality or performance. Actual
handling and reviewer closure require the existing real host-model pipeline and
artifacts; all current roles and related handoff must pass on the final frozen
candidate. Complete 10/10 new full-text papers and synthesis before publication.
Same-condition A/B when observable; otherwise inconclusive. No commit/push until
all original batch release gates pass. Next bounded experiment budget: at most
six fault/state cases, one controlled restart per crash site, no paid runtime or
installation; stop and checkpoint at an unexplained conflict, not infinite retry.
