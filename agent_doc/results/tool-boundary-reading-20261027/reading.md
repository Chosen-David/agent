# Tool-boundary reading and source audit

Artem Trofimov/Boris Novikov, [When Tool Calls Succeed but Workflows Fail](https://arxiv.org/html/2609.15397v1), **2609.15397v1**, 2026-09-14. Actually read HTML main §§1–6, Tables1–4; references only incidental, no PDF/artifact execution.

The effect-history model separates outcomes from observations. Eight anomalies cover uncertain retries/commit/compensation, residue/timing/dependency, and concurrent/exogenous effects. Contracts need authoritative outcomes, lifecycle controls and coordination; declarations alone do not enforce protocols. Profiles are not a cumulative hierarchy; coverage/minimality/independence and four boundary proofs remain future work. Runtime coverage is stated-assumption analysis, not verified deployment. The 2026-07-27 census lists 98,291 tools from reachable remote servers: 4,838 tool-bearing, 4,318 connection failures, 74 timeouts, four empty; package/stdio targets excluded. No tool was called. Annotation presence/defaults do not prove actual safety. The paper evaluates a pinned annotation vocabulary, not today's entire MCP implementation ecosystem. No agent-quality/speedup experiment or causal ablation is supplied. Defer new transactional schemas; retain unresolved effects as unknown.

## Repository relationship

Static source reading at b93adfd0; no tests, model calls, tool census, effect experiment or production edits. The same unfinished SYSTEM-99 batch continues.

- `Mailbox.consume_handoff` revalidates envelope refs, loads the manifest from hash-bound bytes, checks independent consumer scope and declared knowledge/memory/claim basis, then stores immutable record/request identities. It returns without ACK.
- `prepare_context` consumes first, then builds the complete budgeted packet. Consequently a later hydration/budget refusal may leave a validated-handoff basis record; this is distinct from delivered model context or task execution. Existing contract labels that usage stage narrowly. No defect is confirmed merely from that ordering.
- `acknowledge` records handling; it does not call or grant scientific/task acceptance. `impact` reports stale declared users without mutating their historical ACKs or raw results.
- `basis_context` retains required claims, ancestors and candidate/rejected claims; artifact bodies stay as path/hash refs. Knowledge hydration checks its acquired snapshot; built-in dependent memory closure uses one read transaction. Neither this nor a source hash proves current provider possession, semantic use, hidden dependencies or an external action's lasting effect. Direct low-level builder use is not the documented Mailbox host chain.
- Preserve the existing inbox→prepare_context→actual review/idempotent action→ACK contract. Do not infer exactly-once effects, rollback of outside observers or cross-store/action atomicity from local SQLite transactions or a host idempotency flag. No new shared chat pool, task list, memory layer or directory migration is proposed.

Recent recoverable fresh body chain16→17; no old reading is credited. This checkpoint adds a conceptual boundary and actual source coverage, not performance evidence or round completion. Earlier global blockers and exhausted test/probe gates remain unchanged.
