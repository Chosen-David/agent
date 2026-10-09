# Independent bounded proposal review

Decision: **approve** for the bounded local engineering proposal below. This is a real separate collaboration context's review, not an authenticated ReviewSession receipt, ManagedEngine dispatch authorization, result acceptance or permission grant. No experiment has been accepted by this review.

## Reviewed versions

- `agent_doc/task/task_details/COMM-INBOX-01.md`: SHA-256 `119325b5671df1f011ad2cc4f0fc9fc592d7febe0d391e31582ff4f36d16d958` (whole file, including current Progress).
- `agent_doc/results/comm-inbox-20261009/validation_plan.json`: SHA-256 `139ec3420e6995a0ac6de7753109526d192a11d2ce48cea7366cda3523a254ae`.
- Baseline `agent_runtime/communication.py`: SHA-256 `2df62b823606ca4d0ff1059c632dc567180ba816dd126f2ecd6ed84168963a7c`.
- Empty `agent_doc/guide/GUIDE.md`: SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Full review

The first supplied prose proposal was returned for revision because the exact VM acceptance cases, write/migration non-degradation criteria and resources were unspecified. The frozen proposal closes these findings: the required VM improvement applies to both one-run 20k acknowledged-history cases (empty and five pending target messages); the remaining matrix requires exact output without a universal speed threshold. Publish and ACK each use the declared median criterion (candidate <=2x baseline OR added median <1 ms), and populated legacy migration must finish below 10 seconds. Time measurements include connection and JSON conversion without a progress handler; VM measurements are separate. The budget limits variants, fixtures, samples, warmups and CPU time.

The suspected scan of acknowledged deliveries is a valid diagnostic hypothesis: current inbox joins events to deliveries, constrains run and recipient, filters NULL receipts and orders by event sequence. The present schema has no pending-recipient index. A partial pending index is a small compatible candidate; its benefit still depends on SQLite's actual chosen plan and cannot be inferred solely from schema inspection. The implementation acceptance limits the accepted candidate to the added pending index; a query rewrite or wider change would require another bounded proposal review.

The proposal preserves at-least-once delivery, exact order and limits, run/recipient isolation, immutable events and ACKs, public APIs, evidence revalidation and budget semantics. Empty history, both pending states, one/four runs and unrelated pending deliveries cover meaningful index/join edge cases. Legacy migration and reopen are explicitly included. Regression and independent result verification remain necessary downstream gates; the independent verifier must read actual source, fixture construction and raw data, recompute aggregates and rerun a case before any result is usable.

I read the actual Mailbox implementation, communication test coverage, AGENTS.md, decision/project-document/reuse guidance, dual-main workflow, review-main instructions, canonical COMM/EFF task details, the new prior_search.json, and historical communication evidence. Existing October 6 host latency diagnosis concerns tiny-scale subprocess/validation spans and explicitly cannot establish a SQLite-history bottleneck. Its separately verified 1.146 synthetic timing ratio is not measured system performance. EFF-03 measures encoded returned JSON and deterministic consumers, not inbox lookup scaling. The new lexical search is explicitly partial, includes missing-record errors and produces unrelated knowledge candidates; none supplies matching inbox scaling evidence. New paired measurements are therefore justified, with no exhaustive prior-search claim.

The original first review's requirement to freeze the threshold scope is closed by the explicit one-run acceptance; multi-run results must remain reported even when slower. The overhead rule is permissive but explicit and limits added median cost to less than 1 ms when relative overhead is large. It does not support a claim of universally unchanged latency or write cost. All cases and failures must be retained, and a failed or inconclusive candidate keeps the baseline. Two index/query variants are the maximum exploration allowance, not permission for an unreported optimization loop or broader implementation.

No new service, GPU workload, model evaluation or runtime supervisor is proposed. The local scope and declared budget are feasible with available SQLite/Python execution. Main publication remains dependent on independent accepted evidence, required regressions, fresh remote integration and ordinary push/readback under the parent's existing user authorization. This review does not close historical COMM-06, verify a cloud timer, measure LLM quality/tokens, or certify all historical project tasks.

## Compact verdict

| Check | Status | Reason |
|---|---|---|
| intent | pass | Narrow measured inbox improvement matches delegated authorization and retains communication semantics. |
| guide | pass | Guide is empty; the proposal preserves the entire human-only directory and unrelated work. |
| assumptions | pass | Acknowledged-history scanning is conditional and testable; candidate acceptance depends on measured exactness and VM benefit. |
| prior_results | pass | Partial retrieval and its failures are disclosed; inspected historical data are correctly excluded from this new claim. |
| acceptance | pass | Exact matrix, both primary cases, write/migration criteria, raw timing, regressions and independent verification are declared. |
| risk | pass | Additive local index scope is bounded; migration, restart, isolation, write overhead and evidence semantics are checked. |
| resources | pass | <=2 variants, <=20k fixture events per case, 21 pairs/3 warmups and <=10 CPU minutes per experiment; no GPU/models/services. |

Blocking findings: none for this bounded proposal review.

Nonblocking finding: the task detail says 55 records scanned while the current prior_search.json reports 56. This does not affect reuse or acceptance because the retrieval is declared partial and no hit is reused for performance. Report the actual current raw search count rather than repeating 55; preserve the raw search and errors.

Review limitations: no trusted runtime plan authentication was performed; no full executable ManagedEngine DAG was supplied or dispatched; no benchmark or candidate result was independently verified here. Material changes to scope, method, criteria or budget require renewed review.

## Publication hygiene addition review

Decision: **approve** the narrowly scoped regeneration of `plugins/research-assistant/skills/research-assistant/references/code-reading_execution.md` from its already existing source. This extends publication scope only; measurement methods and acceptance remain unchanged.

I inspected the diff: it adds one blank line and the source's existing performance-measurement/independent-validation paragraph, with package-external links rendered by the established sync mechanism. The source `plugins/research-assistant/skills/code-reading/references/execution.md` was not changed by this round. `scripts/sync_plugin_references.py` derives the execution mapping from the role registry; this is an ordinary generated-reference repair, not a new policy authored for this optimization. It preserves explicit noise checks, independent verification and the no-finding outcome.

Reviewed source SHA-256: `113149a9f316c06228210890c322081f20c52a70cf72138416e6ec5f7b52e872`. Reviewed generated destination SHA-256: `7e006c12a14a3b1df89b455f2284464f866ecae1e00e77d931a589e4f3961eba`.

Actual checks in this separate context: `python scripts/sync_plugin_references.py --check` exited 0; `python -m unittest discover -s tests -p test_plugin_reference_sync.py -v` ran one test and passed. I also inspected the inbox implementation diff, which is exactly the three SQL lines creating the partial pending-recipient index previously approved. This observation does not independently accept its performance results.

All seven proposal checks remain pass for this small scope addition: authorized publication intent; no human guide modification; established source-to-generated mapping; observed stale-reference repair rather than reuse of performance results; deterministic sync acceptance; low reversible documentation risk; and negligible bounded check resources. No blocking findings. Parent still owns fresh fetch/integration, dependency retesting, independent result acceptance and non-force publication/readback. No runtime review receipt or live supervisor claim is made.
