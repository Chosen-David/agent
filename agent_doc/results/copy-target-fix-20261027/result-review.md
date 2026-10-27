# Independent source and result review

Decision: **ACCEPT the local Linux repair evidence as usable-with-scope**. The full frozen cross-platform result contract remains **pending**: its reproducibility criterion additionally requires actual successful execution of the new module in all five native CI jobs, and the public manifest/archive has not yet been assembled at this review point. Do not relabel those requirements N/A. Native trusted-provider/ReviewSession status remains unknown/pending independently of this actual delegated review.

Reviewer: actual delegated `/root/copy_target_fix_review_2103`. Read full baseline/fixed/independent stdout, stderr and meta, actual modified helper/error class/import, native shared implementation, installer and CLI consumer paths, frozen test methods, validation criteria, Plan52/stageAH and workflow. Executed precisely one approved independent phase and one sync check; no retry, extra case, old diagnostic rerun, source/guide/git/backend action occurred.

## Actual phase outcomes

| Phase | Actual result | Interpretation |
| --- | --- | --- |
| Baseline |79 methods,7 assertion failures,1 explicit capability skip,0 errors, child exit1 | Three new methods fail: six claimant subcases across publication/rollback plus one real installer recovery method. These include missing typed-recovery/retention contract outcomes; they are not seven overwrite bugs. Existing lifecycle/normal/EIO controls pass. |
| Fixed |79 methods,79 pass,0 skips/errors/failures, child exit0; sync exit0 | All seven new methods and all six frozen modules execute successfully on this native Linux host. |
| Independent |79 methods,79 pass,0 skips/errors/failures, child exit0; sync exit0 | One independent execution of the exact same frozen argv confirms the fixed local result, including the four real full-catalog CLI child commands and actual single-skill installer recovery/retry/uninstall fixture. |

Independent started1793107094.136492 and finished1793107103.031271, before the original shared deadline1793108435.3530695, using the approved120-second phase timeout and30-second sync timeout. CLI child timeouts remain30 seconds. Environment matches producer Linux6.18.55 x86_64/glibc2.39, Python3.12.14; ANTHROPIC_BASE_URL was removed. Timestamps are deadline bookkeeping, not a performance comparison. No evaluated model/backend was invoked; review-role usage/cost is unknown, not zero total actor cost.

## Six canonical checks

| Criterion | Verdict | Evidence and assessment |
| --- | --- | --- |
| implementation | pass for local implementation | Actual setup imports the sole existing native helper; no duplicate syscall or public-target ordinary-rename fallback. Materialized snapshot and resource bounds remain before private new→ready capability rename; old-copy snapshot still precedes backup move. Publication and rollback both use no-replace. RecoveryError retains backup path, original/rollback error objects and chained publication cause; retained=True prevents automatic stage deletion. Actual CLI catches its ValueError superclass. |
| reference_boundary | pass for tested Linux schedules | Property assertions compare within-case claimant and original identities, claimant listing/bytes, previous snapshot and retained ready candidate, rather than reproducing the production algorithm as a reference. Empty/nonempty/file targets exercise both publication refusal and injected-EIO rollback refusal. Normal, uncontended EIO and capability-before-old-move controls pass; real installer observes unchanged manifest, needs_setup, manual owned-fixture restoration, retry/check and uninstall. No new native safety case skips. |
| data_integrity | pass for local raw data | All three commands use the same six frozen test modules and hashes, including aligned old fixture; no silent rerun or changed assertion. Read all actual raw outputs and child returns. Before/after independent source and test hashes match. Baseline1/fixed1/independent1 and two plan-review cycles are spent, without reopening old budgets. stdout is empty because unittest reports to stderr; raw baseline exit1 is preserved. |
| numerical_sanity | pass |79 is unittest method count, not claimant subcase count. Baseline7 failures occur across3 methods;1 skipped capability method and75 methods without failures account for the total79. Six claimant subcases are explicitly distinct from independent root causes or race frequencies. Identity comparisons are within each case, not inferred from inode values reused across fixtures. Exact content/snapshot and manifest assertions hold in fixed and independent phases. |
| measurement_validity | not_applicable, preauthorized | Correctness only; no timing, memory, throughput, accuracy, frequency, model quality, token or cost benefit was measured. Logged duration and timestamps only support timeout/deadline compliance. |
| reproducibility | pass locally; inconclusive for full frozen scope | One independent exact-suite run and sync reproduce all fixed local outcomes. Native five-job CI requirement is still pending actual runs/readback. No Windows/macOS execution may be inferred from native-dispatch mock tests or workflow text. Manifest/archive acceptance is also pending assembly; this report does not authenticate a runtime verifier. |

## Cleanup and retention analysis

The ordinary cleanup branch moves the owned stage using os.rename into a newly created TemporaryDirectory's otherwise absent child, then delegates deletion to TemporaryDirectory's portable read-only cleanup. This differs from public publication: the destination is inside that invocation's unique private trash directory, not the contested skill target. It preserves the prior read-only cleanup mechanism and avoids a Path.rename mock swallowing private cleanup. A failed recovery sets retained before raising, so neither that rehome nor its recursive deletion runs against the retained original/candidate.

There is no additional cleanup when no owned backup exists and new publication refuses; only the private candidate is discarded and the claimant is preserved. On uncontended rollback success the original error is re-raised and the empty stage is cleaned. Existing earlier install writes are not rolled back. Target identity changes between old-copy check and backup move, hostile parent/stage substitutions, cleanup errors/identity, arbitrary same-user mutation after observation, EXDEV/filesystem changes and full installation transaction remain outside the accepted scope. Capability preflight does not guarantee every later syscall succeeds.

The successful CLI lifecycle dynamically covers install/check/repeat/uninstall with explicit EMPTY_INVENTORY. Recovery-error CLI exit2 compatibility is established by source inspection of the ValueError class and existing main catch; no recovery-error CLI child was executed. The manual recovery action deletes only the fixture's known empty claimant and restores its owned backup; no automatic production recovery is claimed.

## Evidence bindings

All paths below are relative to the project. Hashes bind inspected bytes, not their correctness or trusted identity.

| Artifact | SHA256 |
| --- | --- |
| setup.py repaired | `f1d87894a7d6de6f87007443a0bfb4fe50dc0005108eeec386f53343ad2deefc` |
| setup.py baseline from preserved phase metadata/prior inspected source | `d5273177d6bb1dc6dcdc63168505367b6114bb18919c27c2945c297e305cbfcd` |
| agent_runtime/knowledge_ingest.py | `5349e9c44f3be03d1a7dbc291562dfe98a71f1c532d302c49a8ffd5aa381e039` |
| tests/test_setup_publication.py | `5602545ca24a61c9e9c7b101ba07d335a6770fc4371def48954a02e41bde81ce` |
| tests/test_setup_portable.py | `a39f722b0bade4f87a6468df1fa71e7a4ce8463320e56b24bd47011fe3e006f9` |
| .github/workflows/portable-install.yml | `81e7c694acbbda218421aa62b1976e44bd3386fb77e7fc157fd17f5e8ad2eb17` |
| .agent-runs/copy-target-fix-2103/plan-v2.json | `6b59f82500597b0da73c1c61bf1cf875935394e55ddfb65224b8603606accfd6` |
| .agent-runs/copy-target-fix-2103/validation-plan.json | `d705c253a4908702e26ad3a3249b2763861e00766d6b21c1549fc6458a20e37b` |
| .agent-runs/copy-target-fix-2103/baseline-meta.json | `691254fd059d5e76c07e754c3675fce843fa2b1eeadd085c057bde160212cf7c` |
| .agent-runs/copy-target-fix-2103/baseline.stderr | `a8076df8ac3f645c2b58285cd7f307be3342d828bd358df19e06af43ded2ddf7` |
| .agent-runs/copy-target-fix-2103/fixed-meta.json | `77ab95c460b416421b3b14669d1094da90cebd4925b1f3369baa253ecb4bdf8d` |
| .agent-runs/copy-target-fix-2103/fixed.stderr | `8023d5e53fe5543b938178d51d713f1e7c8e2c1c4576517a4c7016f9b1df187f` |
| .agent-runs/copy-target-fix-2103/independent-meta.json | `37d8293cca0494527fffd5d46e0b5e1da3e044e8ee26d77d644151d14d52fadc` |
| .agent-runs/copy-target-fix-2103/independent.stderr | `6a1d65629da50b1c90d8145e965d944c5611e000e259776cf4190594b94b9ff0` |

All three phase stdout files and both independent-sync stdout/stderr files have the empty-byte SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. Full six-module before/after refs and actual argv are retained in independent-meta.json. The parent owns public manifest/archive and CI/readback completion; SYSTEM-99 remains unfinished.
