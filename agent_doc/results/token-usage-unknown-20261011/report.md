# TOK-FIVE parent usage reporting correction

Base: `9f1d5f61e6290384cb627d5b6b79bae7fca3da4e`. Isolated branch: `agent/usage-unknown-20261011`. This change excludes old candidate `c535330` and its request accounting module, fixtures and generated mirrors.

Before: completion/timeout without a usage event returned numeric zero. After: missing and invalid measurements return JSON null, observed zero stays zero, partial observations remain explicitly incomplete. The existing native five-counter schema is checked for integer types, arithmetic, subset relationships and nondecreasing totals. Repeated snapshots are not summed. Foreign thread/turn events cannot supply usage. Extra native fields survive in the retained full snapshot. Invalid transport interrupts the owned turn. No new backend, scheduler, quota action, ledger or billing identity is introduced.

Consumer search found only `run_worker -> tick -> receipt.json/state.last_result -> CLI JSON`; no numeric savings/ranking consumer. `usage_complete=false` and `counts_as_token_success=false` remain explicit for all monitor receipts; even successful completion does not certify that the final bill arrived. Diagnostic last-known values cannot be used as complete cost. Model-request count is unknown/null once a turn starts.

## Validation and review

- `python -m unittest tests.test_token_optimizer tests.test_turn_usage tests.test_prompt_context -v`:31 passed, including18 optimizer cases. Reviewer independently repeated all31.
- `python -m unittest discover -s apps/paper-reader/tests -v`:3 passed.
- `python -m unittest discover -s tests -v`:1022 run;1019 passed,2 failed,1 skipped. Not an all-green result.
- Both failures (`KnowledgeTests.test_bundle_exact_and_cli_without_repository`, `PluginReferenceSyncTests.test_generated_plugin_references_are_current`) reproduce on clean baseline9f1d5f6. Generated coverage.json/learning_state.json are stale on baseline and remain untouched. Full and baseline raw logs are preserved here.
- An initial test-import syntax error was corrected before execution; see development-failure.txt.
- Independent `/root/accounting_review` accepted code and complete local evidence for scoped publication, including inherited failures; see independent-review.json and artifact hashes. This conversational review is not a managed/native billing attestation.

Fixtures cover no-usage completion/timeout, real zero, normal/repeated usage, foreign identities, partial fields, malformed transport, bool/negative/arithmetic/subset/regressive counters, failed/retried/interrupted turns, budget interruption, mocked worker integration and receipt/state persistence. No provider/model/backend calls occurred in the test harness. Platform coordinator/reviewer usage and money are not exposed and are unknown, not zero. Synthetic counters are fixture inputs, not task spend or savings.

## Publication and remaining boundaries

Parent thread reports its connected GitHub checks at12:01 UTC: main9f1d5f6 unprotected, required checks enforcement off with empty contexts/checks, rulesets empty and workflows directory404. Local API Forbidden was not retried and is not evidence of required CI. Parent will independently read back the published commit and Actions status. Git fetch/main comparison is repeated immediately before ordinary non-force publication.

No existing worker or schedule was started, stopped or replaced; tracked hourly ownership remains. No private session paths were read. Actual Windows provider execution, final/retry billing semantics, complete cross-actor accounting, LLM quality and token/cash savings are unverified and not claimed. Existing tick postcondition exceptions can replace the worker summary although raw last usage remains saved; this inherited behavior is outside this narrow patch.
