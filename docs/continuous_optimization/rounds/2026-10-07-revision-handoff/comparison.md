# Mechanism comparison before implementation

These are design hypotheses, not candidate test results. W1 baseline is fixed.

| Approach | Recovery invariant | Compatibility / maintenance | Unresolved failure |
|---|---|---|---|
| Publish first, then ACK | Failed publication keeps original pending; crash after publication retries same immutable ID | Current API, existing demo already works | Adapter may reverse order; a later conflicting ACK can leave a published request inconsistent with the prior receipt |
| Host journal and reconciliation | Save intended event and receipt before either; replay/check both on resume | Existing adapter can own journal; additional protocol and state reconciliation | Journal + mailbox are separate transactions; corrupt/stale journal or missing replay still requires diagnosis |
| Optional combined transaction | Publish event/deliveries and incoming ACK together, or neither | Additive API/CLI, shared validators required; preserve legacy ACK behavior | Does not protect unmigrated ACK-first callers or external side effects; immutable evidence still requires host control |

Default recommendation remains unselected pending targeted controls and full
research synthesis. A combined operation could remove a local crash window
and reduce adapter sequencing burden, but must prove useful beyond the already
passing publish-first control. Do not add another finding/task-done database.

Before testing a candidate, explicitly bind evaluation to the recommended/migrated
path: preserving legacy `acknowledge` means ACK-first misuse remains possible.
Report that limitation, not a claim that every caller is now safe. Original W1
failure stays in the record. Never compare old ACK-first misuse only against new
valid usage and call it an overall performance improvement.

Required comparison additions: missing reference and stale version before ACK;
pre-existing consumed/rejected receipt; exact retry after success; same ID changed
content; budget limit; approved recipients with independent receipts. For an
atomic candidate inject real failure before commit and restart. Original review
owns semantic finding closure and rechecks actual repaired artifacts.

No runtime change approved by evidence yet. This is same-goal local reliability
work within existing authorization; it does not grant paid resources, external
services, new scheduling or modifications to another repository.
