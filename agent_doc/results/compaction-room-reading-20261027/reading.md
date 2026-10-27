# SYSTEM-99: compaction headroom reading

Primary: [2610.25516v1](https://arxiv.org/html/2610.25516v1), Jithin VG / Ditto PS, submitted 2026-10-18T20:15:30Z; checked 2026-10-27. Actual HTML text §§1–7, Tables1–4 and captions1–6 read; references opening incidental, no appendix present in HTML, no PDF/author code/raw runs inspected.

## Method, experiments and limitations

Reply/framing reserves precede delayed briefings; history/checkpoints persist. Literal checks cannot certify semantic fidelity. Version1.x recall (239 small-model probes, single runs) differs from Version2.0 execution. The 1.2B writer often used deterministic fallback. Customer-service strategy comparisons lack an uncompacted arm.

SWE: fixed scaffold, 100 selected tasks, two repeats/arm; unconstrained analysis reuses unaffected budgeted sessions. Long-pair membership uses both trajectories, still outcome-dependent. Bootstrap clusters tasks; McNemar pools dependent repeats. Added-task replication alone is nonsignificant. Threshold sweep changes window and selects previously long tasks; 8B rarely compacts. Time limits remove reported gains. Cache reuse is modelled with serving cache disabled; tokens/solve differ from total tokens/model time. CPU accuracy transfer is argued, not measured. Literal fidelity excludes semantic omissions; late unused checkpoints also consume resources.

Arithmetic discrepancies remain unresolved:

| Source | Literal counts | Displayed pp | Count-derived pp |
| --- | --- | --- | --- |
| Table2 long/all | 54−42 /102 | 12.3 | 11.76 |
| Table2 added | 19−15 /42 | 10.4 | 9.52 |
| Table2 short | 45−44 /98 | 1.7 | 1.02 |
| Table3 48K discordance | 6 versus6 | 2.4 | 0 |

Raw adjudication unavailable.

## Current repository relation and decision

Static source audit at abb0ea5a: `compose_entries` deduplicates exact shared blocks only within one returned payload; its character cap is not the provider's token window or an output reservation. `task_view` retains non-task text and requires details/dependencies to be reread. These interfaces do not own live conversations, delayed summarizer application or reasoning settings. Their bounded display behavior is intentional, not a demonstrated missing reservation defect.

`short_appserver_usage`, `short_probe_usage` and `current_turn_usage` explicitly restrict accounting to one no-tool turn. Their counters cannot establish all actors, summarizers, retries, discarded checkpoints, tool execution, provider cache pricing or end-to-end task quality. No fresh backend calls, tests or old pilot replay occurred.

**Defer** lossy compaction and threshold changes. Reconsider only with verified host ownership, restorable inputs, per-task correction/dependency quality checks, all-actor usage, latency and fixed wall-clock conditions. Preserve history/corrections and in-place implementation policy. This is a literature/static checkpoint in Plan49, not an experiment or a completed optimization round; prior exhausted gates remain closed.

## Prior result discovery

Query `compaction reasoning room context quality`: 304 scanned, partial=true, 25 errors; five hits and exact record hashes are in inputs.json. Metadata inspected only; none supplies a matched real coding-quality/all-cost comparison. No empirical reuse. Partial lexical discovery does not prove absence. 2609.32961 was already partially read in token-r6-close-20261014 and receives no new credit. Current tracked agent_doc contained no 2610.25516 record before this reading. Recoverable recent-body chain:18→19, one new body; old lost records not reconstructed.
