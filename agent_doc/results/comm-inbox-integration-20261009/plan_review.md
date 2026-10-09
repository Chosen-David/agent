# Independent integration delta proposal review

Decision: **approve** the fresh bounded compatibility/performance revalidation after integration with upstream `0498816bbe0a9d5eeee78284d2cba94817c4eb7c`. This is a bounded collaboration-context proposal review, not a trusted runtime ReviewSession receipt or experiment-result acceptance.

## Reviewed identities

- Current integration commit observed: `de6531f`.
- Upstream ledger baseline and saved `baseline_communication.py` SHA-256: `eecfe2b16a40d6118db8d7c99f9a89311eaaf491a55a51b6ac65c924d2ae115e`; the saved file matches `git show 0498816:agent_runtime/communication.py`.
- Candidate `agent_runtime/communication.py` SHA-256: `c322cdb7d61dbc98bb8e6139bb817b1825742aa3aca9285b35609556384dd975`.
- `validation_plan.json` SHA-256: `139ec3420e6995a0ac6de7753109526d192a11d2ce48cea7366cda3523a254ae` (unchanged validation criteria).
- `scripts/benchmark_communication_inbox.py` SHA-256: `4208cc9d64b23f835ec71ab39aed1ea1d8aff853cbe9d0663f88bac7e1c19931`.
- Current `agent_doc/task/task_details/COMM-INBOX-01.md` whole-file SHA-256: `558fe906aa037111b32d38e0876ea6cf501902a6b045a214d50b9663e28b8e6f`. The frozen integration plan snapshot retains the reviewed scope, matrix, criteria and budget; later Progress reflects historical outcomes, not new acceptance by this reviewer.

## Full delta review

I inspected the upstream ledger implementation, current source, three-line diff against upstream, fixture seeding and the unchanged validation plan. Upstream now maintains exact event/delivery byte counters through an initial transactional backfill and INSERT triggers. The candidate remains solely a partial index on `communication_deliveries(recipient,seq) WHERE receipt IS NULL`; it does not change ledger backfill, triggers, public methods, budget checks or ACK updates.

Index membership changes on ACK but ACK does not remove deliveries or change billed delivery bytes. INSERT triggers and the additional index maintain separate state inside SQLite's existing writes. No apparent semantic incompatibility follows from their composition. Both baseline and candidate fixtures create Mailbox first and then INSERT deterministic rows, so the upstream triggers account for seeded rows rather than leaving an empty usage ledger. The updated baseline must be used for write overhead and migration comparison; old accepted performance samples remain historical and cannot certify the new composition.

The fresh matrix and independently reviewed result gate are appropriate because upstream changes initialization, publish costs and triggers. Required one-run 20k empty/pending VM thresholds, all-case exactness, finite raw latency samples, balanced pairs, write overhead criterion and migration bound remain unchanged. Multi-run data remain mandatory even without a speed threshold. The benchmark's index migration now measures an already-ledger-enabled populated database; do not describe that timing as combined upgrade from a pre-ledger schema. Combined compatibility is additionally covered by upstream populated-legacy/concurrent-upgrade/rollback tests, which must be included in fresh regressions. This proposal approval does not assert those tests or fresh measurements have passed.

The new experiment repeats the same index variant against changed dependencies; it does not consume a new optimization variant or authorize expanded experimentation. Retain <=2 total candidate variants, the declared sample/warmup matrix and <=10 CPU minutes per experiment. As in the original review, history=20000 with five pending messages means up to 20005 total event rows; this is the exact previously frozen matrix, not a larger history sweep. No GPU, model or new service is introduced. Inconclusive/failed gates keep the baseline and block publication of improvement claims.

Existing result acceptance from the earlier source version remains scoped to that version. Fresh independent verification must read actual baseline/candidate/fixture code, recompute all aggregates, rerun the declared cases and check manifest hashes before publication. Root owns full regression completion, new dependency failures, fresh remote integration and ordinary non-force push/readback. Any later upstream implementation change again invalidates dependent acceptance until evaluated.

## Compact verdict

| Check | Status | Reason |
|---|---|---|
| intent | pass | Same authorized inbox improvement, fresh validation after integrating concurrent main changes. |
| guide | pass | No additional guide constraint or human-guide write introduced. |
| assumptions | pass | Index and transactional counters operate on compatible unchanged event/delivery semantics; measurements remain conditional. |
| prior_results | pass | Old evidence preserved as historical; fresh baseline hash matches upstream and old acceptance is not carried forward. |
| acceptance | pass | Exact same frozen matrix and thresholds, new independent result gate and full dependency regressions. |
| risk | pass | Counter triggers, ACK membership and populated migration considered; no query/API/ledger change by this candidate. |
| resources | pass | Same variant and bounded matrix/budget, no added hardware/model/service requirements. |

Blocking findings: none for this delta proposal. Reporting constraint: distinguish index migration on a ledger-enabled database from a full pre-ledger upgrade; do not combine their timing claims. No performance result has been accepted by this review.
