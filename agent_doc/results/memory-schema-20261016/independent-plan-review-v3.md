# Manual independent v3 repair plan and static review

Verdict: **ACCEPT the bounded v3 repair plan and inspected static implementation**, subject to the unchanged independent result-validation and publication gates. This is manual review by the separately dispatched plan-review agent, not managed ReviewSession approval, execution-budget authorization, result acceptance or publication permission. Scope is exclusively Chosen-David/agent; TwoLevel remains paused. No fourth candidate is permitted in this batch.

## Actual review and identity

Read `.agent-runs/memory-schema-20261016/repair-plan-v3.json`, the current implementation and schema regression test, the preserved v2 source/test snapshots, the complete v2 independent result review, and the exact v2-to-current source/test diffs. Prior original/revised/static reviews remain unmodified in `independent-plan-review.md`. The only write in this follow-up is this assigned private review output. No test, experiment, timing run, source edit or publication action was performed by this reviewer.

| Artifact | SHA256 |
| --- | --- |
| repair-plan-v3.json | bb8e6d6d1c22b9f25d0baae0ff40d5447196d90f314d38c7d762febadf718829 |
| agent_runtime/project_memory.py | 6daa9f90425763bfc03287b4a68d3dee3dde36068115d9f4791112c50ad65580 |
| tests/test_memory_schema_check.py | 88053d49cdd74adf9836dc992a9de5a047c184135a20a5a835de6f318d3fbfb3 |

## Plan judgment

The v2 result reviewer found an actual compatibility failure: `_connect` assigns the dynamically resolved `sqlite3.Row`, and v2 compared the connection factory with that same mutable attribute. A replacement callable could therefore pass the supposedly standard-factory guard and execute same-connection DDL while a cached table-existence result remained present. V2 ordinary differential and timing successes do not cure that counterexample. Preserving its source/test snapshots, raw data and explicit rejection is required and the repair plan does so.

The v3 change directly repairs that finding without changing the goal, traversal algorithm, schema, hydration order, fixture, metric or threshold. It captures the original factory identity in `_BUILTIN_SQLITE_ROW` and checks `db.row_factory` against that immutable captured reference. `_connect` still assigns the current sqlite3.Row attribute; therefore a later replacement is detected and takes the uncached compatibility path. This preserves the pre-existing behavior for customized factories instead of silently removing that customization. The ordinary owned path still receives one fresh schema-state list per public check.

The versioned repair explicitly acknowledges exhaustion of the initial two-candidate limit rather than treating v3 as an accepted initial-budget candidate. The parent instructs review of this one bounded repair under existing same-goal implementation authority, with no fourth candidate. This manual technical review does not itself grant or reset any managed budget. The parent must preserve the actual authorization rationale and verify the original 30-minute wall bound before any remaining execution. If that bound cannot be established or is exhausted, stop dependent execution; this review supplies no extension.

## Exact static implementation assessment

The v2-to-v3 implementation diff contains exactly two changes: `db.row_factory is sqlite3.Row` becomes `db.row_factory is _BUILTIN_SQLITE_ROW`, and `_BUILTIN_SQLITE_ROW = sqlite3.Row` is captured alongside the existing original-function identities. No other source difference appears against the preserved v2 snapshot.

The test diff adds one targeted regression. It retains the original Row callable, replaces the sqlite3.Row module attribute with a factory returning original Row objects, and drops document_dependencies when ancestor `a` is hydrated. On the diamond, the root is hydrated before `a`, so v2 would cache table-present before that DDL; the uncached fallback can rediscover absence after the drop and complete the original check. The test expects successful public check, directly addressing the independently reported failure. This is meaningful behavioral verification rather than a test mirroring the new identity comparison. This reviewer inspected the test without executing it.

Earlier instance `_check`/`_connect` exclusions and direct class `_walk` dispatch remain intact. Direct `_get` and `_check` are still uncached by default. No handoff call coalescing, node skipping, cross-call schema state, document-validation shortcut or hydration-order change is introduced by this repair. The previously identified mutable Row alias bypass is closed for replacements after module initialization. This does not certify arbitrary mutation of private captured constants, interpreter builtins or trusted initialization before import; those are outside the stated ordinary-path and supported-customization scope.

No new correctness blocker was identified in this static review.

## Seven review criteria

| Criterion | Verdict | Reason |
| --- | --- | --- |
| intent | pass | Same bounded Agent schema-discovery optimization; corrected project focus preserved. |
| guide | pass | No human-only guide modifications or new guide conflict. |
| assumptions | pass within scope | Captured original Row identity closes the demonstrated custom-factory eligibility error; ordinary lifecycle and prior override guards remain. |
| prior_results | pass | V1/v2 defects and rejections remain historical evidence; their timing is not reused as v3 acceptance. |
| acceptance | pass as prospective protocol | Same complete-output/error/freshness contract, >=10% improvement for both primaries, <=15% control regression and 21 fixed randomized pairs. |
| risk | pass within scope | Exact minimal source delta and behavioral regression; no architecture, schema, model service or publication scope change. |
| resources | conditional | One additional fixed repair only, no fourth candidate, same original 30-minute local bound; actual elapsed-budget compliance remains parent-owned and was not independently audited here. |

## Limitations and downstream gates

The parent reports repaired-source primary reductions of 15.01% and 12.16%, with a one-item control regression of 8.16%, within the unchanged 15% cap. These are producer-reported numbers in this review: I did not inspect or validate the v3 raw measurements, recompute aggregates or independently reproduce them. They must bind the exact v3 source/test/config/inputs and be independently reviewed before becoming usable-with-scope result evidence. The result reviewer must verify the custom Row counterexample now agrees with pinned baseline, confirm ordinary/fallback regressions and data integrity, and keep all v1/v2 negatives.

Full appropriate regressions, source/evidence freeze, remaining wall-budget check, explicit result acceptance and publication/readback remain parent obligations. Any new correctness blocker or failed timing gate stops this batch with preserved negative evidence and no publication; there is no fourth-candidate path in this review. This acceptance is limited to the repair plan and static code assessment, and establishes no model KV, QA, token, TTFT, GPU, RSS or general production performance benefit.
