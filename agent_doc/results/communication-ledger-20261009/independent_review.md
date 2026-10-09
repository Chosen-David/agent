# Independent code and result acceptance

Date: 2026-10-09. Reviewer: `/root/communication_review`.
Verdict: **usable-with-scope** for the frozen local mailbox accounting candidate and measured synthetic workloads. No blocking candidate-code findings remain.

This review was performed in an actual separate host collaboration context. It is not an installed runtime verifier, authenticated `ReviewSession` receipt, supervisor event, or general bug-free certification. The machine-readable evidence and SHA-256 bindings are in `independent-validation.json` and `independent-checks.json`.

Frozen plan SHA-256: `2fc7909788a969c9c5bd8248a27c84680f6cf02aaa195548742f4770f67e86fb`.
Reviewed production code SHA-256: `eecfe2b16a40d6118db8d7c99f9a89311eaaf491a55a51b6ac65c924d2ae115e`.

## Six validity dimensions

| Dimension | Result | Actual independent work |
|---|---|---|
| Implementation | pass | Read the production diff, entire benchmark and added tests. Triggers update exact event/body and fanout totals in the existing write transaction. Migration table creation, backfill and both triggers remain inside `BEGIN IMMEDIATE`; no inner `executescript` or durability downgrade. Public methods preserve routing, envelope/ref validation, duplicate-before-cap behavior, ACK semantics, inbox ordering and consumer checks. |
| Reference/boundary | pass | Ran 57 communication, accounting, basis and selective-context tests. Reviewed their independent SQL/body-byte oracle. Extra reviewer checks cover zero-event legacy runs, legacy ACK, duplicate after ACK, changed retry rejection and simultaneous distinct publishes reaching an exact event cap. Added tests cover concurrent byte cap, multibyte strings, multiple runs, old preopened connection, concurrent first migration, failed migration retry and rollback after partial fanout. |
| Data integrity | pass | Compared frozen baseline bytes with `git show` at the approved baseline SHA. Verified all benchmark code and plan hashes, all 16 unique workload cells, 11 recorded arm orders per cell, 9 retained samples per operation, matching final counts across arms and fanout conservation. Producer raw files were not overwritten. |
| Numerical sanity | pass | Independently recomputed all 1,296 producer timing summaries and primary/supporting ratios; every retained timing is finite and positive in milliseconds. Checked event/delivery counts and exact byte relationships. Sample p95 equals the largest of nine observations, so it is descriptive, not a service-tail estimate. |
| Measurement validity | pass with limits | Every arm invokes the full publish API, including artifact validation, connection, transaction and commit; usage is timed separately. Identical synthetic legacy histories are copied before each case. Index construction, first-open migration and reopen are separately recorded. All arms use DELETE journal mode and synchronous=2. Random arm order is retained. Cases grow by 11 appended events across warmups/repeats; backlog labels describe initial history. |
| Reproducibility | pass | Independently reran all eight backlog 1,000/10,000 combinations and recomputed their summaries. The final run started after the parent confirmed all owned test processes had ended; no concurrent owned tests ran during it. Primary and supporting acceptance reproduce with identical bound code, baseline and plan. Other cloud-host interference cannot be excluded. |

## Measured acceptance

Publish medians in milliseconds; speedup is scan median / candidate median.

| Measurement | Baseline | Covering index | Candidate | Baseline speedup | Index speedup |
|---|---:|---:|---:|---:|---:|
| Producer primary: 10,000 initial events, fanout 8, byte cap enabled | 24.969339 | 71.134868 | 1.366794 | 18.27× | 52.05× |
| Independent primary replay | 24.267330 | 65.425788 | 1.039915 | 23.34× | 62.91× |
| Producer support: 1,000 initial events, fanout 8, byte cap enabled | 2.894030 | 6.237080 | 1.039980 | 2.78× | 6.00× |
| Independent supporting replay | 3.456679 | 6.473711 | 1.199705 | 2.88× | 5.40× |

Both primary ratios exceed the frozen >=1.25 threshold, and the supporting candidate remains within the allowed 10% regression limit. This supports the narrowly preregistered accumulated-history optimization. The tested covering index is a specific simple alternative, not a claim to have exhausted SQLite indexing strategies.

Producer publish regressions versus the original scan are retained: backlog 0/fanout 8/no byte cap +3.95%; backlog 100/fanout 1/byte cap +0.89%; backlog 100/fanout 8/no byte cap +32.54%; backlog 1,000/fanout 8/no byte cap +11.80%. The last regression also appears in the independent replay (+18.27%). The candidate is not uniformly faster.

Other small-case costs also matter. At initial backlog 0, usage regresses by 16.87% (fanout 1/no cap), 34.14% (fanout 8/no cap), and 1.41% (fanout 8/cap). Reopen medians regress in several cells, reaching +32.25% at backlog 100/fanout 8/no cap. Full samples and all operation summaries remain in the raw artifacts.

At the producer primary case, first open costs 119.817285 ms for the candidate versus 0.820184 ms for baseline; the alternative's index build costs 165.040101 ms separately. Candidate database size after initialization grows from 45,285,376 to 45,293,568 bytes (+8,192); indexed history uses 91,377,664 bytes. These are single migration/storage observations on this fixture, not repeated migration distributions. The first-use penalty must accompany steady-state speed claims.

## Retained failures and limits

- The first reviewer test invocation named nonexistent `test_revision_delivery`; 57 real tests passed and one loader error was preserved in `independent-tests.log`. The corrected actual-module invocation passed 57/57 in `independent-tests-corrected.log`. The parent clarified revision delivery is workflow behavior and historical fixtures, not that module. Current publish/ACK/rollback behavior is covered; no historical real-model experiment was replayed.
- The initial independent timing run overlapped reviewer tests and the parent's full suite. It is preserved as `independent-raw.json`; acceptance reproducibility uses `independent-clean-raw.json`. Nonprimary timing variability, including the 1,000/fanout 1/byte-cap cell, reinforces the shared-host noise limitation.
- Parent full regression log records 861 tests, one generated-reference sync failure and eight skips. The parent identifies the stale reference as preexisting and owns mechanical regeneration and targeted recheck. This review does not mislabel that original run as clean. Candidate-specific acceptance is not a substitute for closing the publication gate.
- Supported legacy behavior is append through the existing Mailbox APIs plus receipt updates. Arbitrary SQL history UPDATE/DELETE/REPLACE, missing/dropped triggers, table corruption and adversarial same-user writers are excluded. No stronger compatibility claim is accepted.
- Scope is Python API calls over synthetic local `/tmp` SQLite histories with fixed approximately 2 KiB summaries and fanout 1/8. No CLI startup, real filesystem fleet, live model latency, communication quality, token savings, distributed exactly-once side effects or remote deployment benefit was measured.

The engineering improvement is a conventional transactional materialized aggregate adapted to this mailbox's precise budget accounting. The accepted result is an engineering scaling benefit in the stated cells, not research novelty or a model-quality result. Publication remains the parent's separately authorized action after its remaining generated-document/regression and remote-integration checks.
