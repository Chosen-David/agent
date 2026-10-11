# TOK-MAILBOX-PAGE: complete pending navigation

Tested base: `3b3c41483a56dbcdcf614f61d44436418c6ee7f9`. One bounded change adds `after_seq` to existing inbox/index/CLI and returns the last included sequence. Both query branches apply the cursor before LIMIT. Routes, body versions, all message kinds, budgets, ACKs and evidence consumption are preserved. Cursors are scope-bound navigation, not global clearance; each page is a separate snapshot.

## Evidence

The fixed synthetic dossier contains120 long messages, three senders/two recipients, all event kinds and a tail revision contradicting an earlier fact. Baseline source is loaded from the exact git revision. Six20-row pages plus one retained page retry cover only20/120 events on baseline, versus120/120 after the fix, with zero ACKs. Exact bodies and hashes are checked. Repeated navigation rows are120 versus20 (the candidate's20 are the explicit retry). Missing/wrong-version bodies, stale artifact retry, restoration, restart, appends and recipient-specific ACK are covered by regressions.

All setup publishing, navigation, exact-body recovery and publish/page retries are included in local replay call traces with unique local operation IDs, input/output UTF-8 bytes, output hashes and per-call latency. Baseline148 calls transfer191778 input/61812 output bytes; candidate248 calls transfer202905 input/220370 output bytes. Coverage differs and candidate recovers100 additional bodies: **no savings ratio or speedup is supported**. The optional tokenizer is absent, so token estimates are null. Initial `*-screening.json` traces exclude fixture setup and remain diagnostic, not the final comparison.

`native-audit.json` separately checks existing real COMM05 handoff evidence:4 unique run/event IDs and4 artifact hashes, implementer→reviewer twice, reviewer→implementer once, reviewer→writer once, one documented revision round. The newer hourly archive contains one thread/two turns, one command summary and3 unique usage snapshots after overlapping snapshots are deduplicated. Neither archive exposes a complete provider request ledger, role costs, charged-history attribution, retries/fan-out billing or latency. Those fields remain unknown; synthetic statistics in historical messages are not model latency. No hotspot ranking, cache benefit, token/cash saving or LLM-quality claim.

Official mechanisms were checked on2026-10-11: [OpenAI app-server source pinned at a07c8eb](https://github.com/openai/codex/blob/a07c8ebd57feedc4cf5dfe854c8e9101de54186b/codex-rs/app-server/README.md), [OpenAI cache usage guidance](https://developers.openai.com/api/docs/guides/prompt-caching), and [SQLite seek pagination](https://www.sqlite.org/rowvalue.html#scrolling_window_queries). Access/version/hash availability and limitations are in sources.json; research mechanisms are not local measured benefits.

## Acceptance

Affected61 tests passed. Full required suite:1040 run,1039 passed,1 opt-in tmux skip,0 failures. Reader3 passed; generator --check passed. The pre-fix new-API failure and all raw logs remain. Independent review reran7 new tests and both replay modes, checked stable coverage/byte results and historical audit hashes. Final review and source/evidence bindings are recorded alongside this report.

No model backend, paid probe, GPU, Claude, scheduler or restricted session was accessed; no SGLang, paper/knowledge-source or oldc535330 candidate changes. Existing hourly ownership and success count stay unchanged. Connected GitHub GET shows main unprotected, required checks off/empty and no rulesets. Native fetch still matches the tested base before publication; final commit/remote readback is reported separately.
