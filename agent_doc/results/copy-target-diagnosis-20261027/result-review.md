# Independent diagnostic result review

Decision: **ACCEPT / usable-with-scope for the offline native diagnostic evidence**. Both production safety assertions fail as preserved negative evidence. This does not accept production safety, a repair, managed runtime dispatch, or trusted runtime result status. Missing trusted native provider remains **pending/unknown**; historical registration must not upgrade it.

Reviewer: actual fresh delegated `/root/copy_target_review_2000` invocation; reviewed actual source/probe/producer raw data and performed one independent frozen execution. This is not a ReviewSession identity proof. Task remains unfinished SYSTEM-99, Plan51. No source, guide, git or backend actions performed.

## Actual execution and observations

Producer and independent commands use the same Python executable and frozen probe, differing only owned output directories. Full argv and return codes are in their meta files. Each child returns **1**, each executes four tests with **2 assertion failures, 0 errors, 0 skips**. Two controls pass. Outer capture success does not change the child exit. Independent started epoch1793102790.6847463 and finished1793102790.8014061, before original deadline1793103191.397406 with timeout30. Producer1/independent1 and review2/2 are spent; no retry occurred.

Environment independently matches producer: Python3.12.14, Linux6.18.55 x86_64, glibc2.39. Filesystem device observed27. No runtime timing/performance comparison is made; meta timestamps record deadline compliance only.

| Schedule | Producer observation | Independent observation | Interpretation |
| --- | --- | --- | --- |
| normal-control | final27/1583651, new body, no error | final27/1583663, new body, no error | Normal replacement control passes. |
| publication-claim | claimant27/1583653 becomes27/1583651, new body, no error | claimant27/1583665 becomes27/1583663, new body, no error | Actual native publication replaces the competing empty directory. |
| rollback-claim | claimant27/1583653 becomes original27/1583647, old body; EIO5 | claimant27/1583665 becomes original27/1583659, old body; EIO5 | Controlled failure triggers native rollback that replaces competing empty directory; original EIO survives. |
| fault-control | original27/1583647 and old body restored; EIO5 | original27/1583659 and old body restored; EIO5 | Uncontended rollback control passes. |

All eight case records show exactly one publication hook, original already moved before hook and zero remaining stage directories. Each phase has four unique required IDs. Current JSON counts, raw stderr traces and captured child returns agree. Empty stdout is expected because unittest writes stderr. Repeated inode values across sequential temporary cases do not identify one persistent directory across cases; all ownership comparisons are within each case.

## Six canonical checks

| Check | Verdict | Actual review/evidence |
| --- | --- | --- |
| implementation | pass | Read actual setup.py helper, copy/snapshot path, install call boundary and frozen probe. Source/probe/plan/validation hashes recomputed before and after independent execution unchanged. Narrow Path.rename hook only schedules new-to-exact-target publication; backup move/restore and successful publication use saved native rename. No production edit or fake rename outcome. |
| reference_boundary | pass | Property uses concrete device/inode and body observations, not a copied reference algorithm. Original and staged directories already exist when claimant is created, so their observed replacement identities are distinct from claimant without relying on inode non-recycling across cases. Successful normal and unclaimed-EIO controls distinguish injection failure from claimant replacement. |
| data_integrity | pass | Read full producer stdout/stderr/meta/states and full independent stderr/states/meta. Four unique cases each, exactly one hook each, matching counters, no omission/skip/error/retry. Actual raw/input/probe/source/config/environment bindings below. Fixed ASCII fixture inputs are literal in the hashed probe; source fixtures are unique temporary trees and cleaned after full states capture. |
| numerical_sanity | pass | Integer device/inode pairs, exact within-case equality/inequality and errno5 checked against raw states; four tests minus two failures leaves two passing controls. Counts represent safety assertions, not bug frequency or two causally independent production defects. |
| measurement_validity | not_applicable | Preauthorized N/A in frozen validation plan: no speed, throughput, memory, model accuracy, race frequency or cost measurement. Timestamps only establish resource-bound compliance. |
| reproducibility | pass | Actual independent once-only invocation of the exact frozen four under original deadline reproduces all four classified producer outcomes. Native environment matches. Cross-OS and live multiprocess coverage remain unknown. |

## Causal interpretation and limits

Source first validates destination snapshot then moves the owned directory to a backup. The destination pathname becomes absent; creating an empty competing directory immediately before publication is a deterministic schedule of ordinary directory operations. Native `staged.rename(path)` replaces that empty directory without error. In rollback case the hook raises EIO before publication; source then calls `backup.rename(path)`, which replaces the empty competitor and rethrows EIO. No additional writer changes fixtures between these operations. The probe does not invoke full install/check/uninstall or claim an end-to-end manifest transaction result.

Publication's first safety assertion fails on missing refusal, but raw state independently proves identity/content replacement. Rollback's failure directly compares claimant and final identities; raw content confirms restoration of the owned body over claimant. These support the two specified schedule witnesses against a proposed preservation invariant. Prior STAGE/RESOURCE explicitly excluded this boundary; no assertion is made that prior accepted work promised otherwise. No repair design, Windows/macOS conclusion, arbitrary target protection, performance benefit, real-world race rate, model quality or system completion follows.

Reviewed role model usage/cost is unknown. No evaluated task model/backend invocation occurred in this diagnostic. Do not label this as zero total all-actor cost. Runtime provider/authentication remains unavailable and cannot be synthesized from this report. Public result may cite the offline review while retaining unknown/pending-native trust.

## Exact evidence bindings

Paths are project-relative. These hashes bind actual bytes read; hash equality does not itself establish correctness.

| Artifact | SHA256 |
| --- | --- |
| setup.py | `d5273177d6bb1dc6dcdc63168505367b6114bb18919c27c2945c297e305cbfcd` |
| .agent-runs/copy-target-diag-2000/probe.py | `c30a2cceaca920566daa5310baf72eaa7bd3e15116a0d78fda698696036eb607` |
| .agent-runs/copy-target-diag-2000/plan-v2.json | `b086984c48fe4b51ce2abe0782d433abecc7b9af45330db3e207a44969c03dc6` |
| .agent-runs/copy-target-diag-2000/validation-plan.json | `ce33960bd0f3ee82621fc111789fdd60cac44101f0da353a2b2053dd328e474e` |
| .agent-runs/copy-target-diag-2000/producer-meta.json | `356f3610dad22bbc81537ea4c7f86348315e8c4f3896616b8bbf357f1e6dbfb2` |
| .agent-runs/copy-target-diag-2000/producer.stdout | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| .agent-runs/copy-target-diag-2000/producer.stderr | `bb78effc905fe68824ddc3ee107cc75ce9544670a33c3513fa872931c331d5a5` |
| .agent-runs/copy-target-diag-2000/producer/states.json | `eadf3fddc36fd64340d9a60ed5e1bf4a06786a01ec7ee306a790618fc7d07461` |
| .agent-runs/copy-target-diag-2000/independent-meta.json | `eaaacb13c9c9198fe70a03f55c7f28ef5b0d85bee060be1e02be82d3235011a0` |
| .agent-runs/copy-target-diag-2000/independent.stdout | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| .agent-runs/copy-target-diag-2000/independent.stderr | `e3feb7f469b3fc7e84a41cbb7f696d65bb09896f2c3e5636c2cedf1f8748a3be` |
| .agent-runs/copy-target-diag-2000/independent/states.json | `40770d7273c334e5a42455abf346ea2844fd74160371c36f7a9c0dd18c273866` |
