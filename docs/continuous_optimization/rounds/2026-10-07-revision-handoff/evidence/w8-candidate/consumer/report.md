# Actual owned local revision consumer

CODE-READ-REV-W8-CONSUMER-001; task refs REV-02 / REV-03. Actual repository commit `c66b5ced2bbb15ef6d42a4c8530256b4152c94ed`; frozen workflow candidate identity is preserved in `identity.json`. The runtime matched the frozen API hash exactly. Repository runtime and Skill were not edited.

| Scenario | Actual observation | Remaining status |
|---|---|---|
| Publication → child SIGKILL → one replay | Child exited -9 after outgoing seq 2 was committed; original seq 1 receipt was null. Replay returned duplicate=true, same seq 2, then wrote exact saved needs_revision receipt. | Request recipient still pending; synthetic finding open. |
| Event-budget rejection | max_events=1 allowed seed, rejected outgoing publish with ValueError. Original receipt stayed null. | Original remains pending; no request, no ACK, no budget extension. |
| Existing receipt conflict | Saved needs_revision disagreed with existing rejected receipt; preflight stopped before publishing. Existing receipt preserved. | Main AI reconciliation required; no request. |

One actual child restart, zero local corrections. Ordinary review evidence was read and hash checked. Each scenario has one owned reviewer consumer and a distinct immutable run/plan; routes are only author→reviewer and reviewer→author. All SQLite state lives in the assigned owned private directory. The consumer used the actual local Engine Store and Context.current checks for token/lease/cancellation plus the task hash authorization reference before publication and ACK. Engine completion denotes only bounded scenario evidence capture.

`consumer.py` is the editable driver; `results.json` and `report.json` provide machine-readable outcomes and source/edge/config/check scope. Each scenario retains immutable `intent.json`, `plan.json`, `ownership.json`, synthetic source, full API JSONL, actual child command/exit/stdout/stderr, Engine readback, Mailbox status/inboxes and SQL row export. `source-publish.json` and `source-evidence.json` fix commit/hash/function/lines. Injected interruption, budget rejection and conflict records remain intact. `driver.stdout.log` contains actual successful assertions/outcomes; stderr is empty. No unexpected failure occurred.

Mailbox.publish validates references before exact dedup and budget handling (communication.py:89–130); acknowledge is an independent immutable receipt transaction (144–163); status preserves receipts (165–171). Publish→ACK is not atomic and the single-owner preflight is not a concurrency lock. No external exactly-once, production adapter migration, model-session restart, model quality, scientific closure or performance improvement is claimed. These are synthetic local protocol observations, not invented experiments.

Next action: main AI inspect state independently and reconcile the budget/conflict cases. For the successful transport run, the responsibility author must actually handle the pending request, publish a revision, then the original reviewer must reread old/new evidence against the original finding condition before scientific closure.

Owned local lease capability tokens in command/API/Engine readback records are redacted for delivery. Complete raw observations were preserved privately before redaction; `redaction-provenance.json` binds each changed file to its raw and redacted SHA-256. All outcomes, receipts, seqs and reference hashes remain unchanged.
