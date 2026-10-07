# Revision handoff recovery: preregistration

Baseline: `04becb4ad8bc3e114d66c13dfe95af9cc2b53573`. Owner: main AI.
TASK mapping: REV-01 diagnosis/research; REV-02 candidate; REV-03 acceptance/publication.

Problem hypothesis: `needs_revision` removes an incoming delivery from the normal
inbox without proving that its follow-up request exists. An adapter that ACKs
before publication can strand repair work after interruption or publication
failure. The durable status record remains available: this is not database loss,
and the documented publish-first demo is a control, not a failing example.

Counterfactual: ACK-first interruption/exhausted budget leaves reviewer inbox
empty and implementer inbox empty; publish-first interruption keeps the incoming
message pending and repair request durable. Publish-first budget failure should
leave the incoming message pending. Execute these four paths using actual
SQLite, files and separate Python processes before proposing an implementation.

Primary criterion for any candidate: zero stranded repair requests across these
four paths plus heldout crash points, restart and idempotent retry. Minimum useful
improvement: eliminate the reproduced ACK-first failure without weakening any
version, route, reference, budget, subscriber or immutable-receipt checks.
Preserve the existing two-field ACK API unless an explicitly opt-in extension
is justified; no new scheduler, semantic done state or automatic finding closure.

Competing hypotheses: publish-before-ACK guidance and a host journal may suffice;
a combined operation may reduce adapter errors but add unneeded API complexity.
Compare both before adoption. A transaction cannot make external scientific
actions exactly once or freeze mutable files. Reviewer owns original-finding
revalidation. No quality/token improvement follows from a program test.

Budget: this wake prepares baseline and begins research; maximum four diagnostic
cases and one original paper, no model/runtime installation or paid calls. Stop
implementation until baseline and compatibility review are recorded. This batch
requires ten newly fully read Agent papers, one synthesis table, upstream Skill
and dependency source reading, targeted independent actual communication chain,
all dynamically registered role tasks and related handoff on the frozen final
candidate, program/non-regression checks and ordinary main publication/readback.
Those gates are not complete during baseline preparation. Reuse existing
`scripts/agent_eval_pipeline.py` and catalogs; do not build another model harness.

Model A/B must bind actual same model/tools/input/budget and isolated rubric;
unobservable model identity or token telemetry is unknown/inconclusive. Keep
previous batch evidence unchanged. Broader writing/diagram generalization and
CO-016 rollback tests remain queued, rather than adding unrelated edits here.
