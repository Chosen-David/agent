# Independent experiment acceptance — MEM-CLAIM-12

Verdict: **usable-with-scope** for the exact frozen local CPU claim_graph implementation and six synthetic workloads below. No blocking code/data finding. Root may consume these scoped results for integration, subject to its remaining full regression and publication gates. This is an actual separate reviewer-context code/data inspection and execution, not a managed ResultValidationHandler, ReviewSession, deployed verifier service or universal correctness certificate.

## Scope and immutable identity

Task MEM-STORAGE-01 remains open; this candidate changes claim-graph validation within Agent handoff evidence gates, not model KV storage, model QA, token use, complete basis_context/Mailbox latency or TTFT. Runtime source is SHA256 `6e1057ce0c76d576898996011bb5ec39a6acad4b821388954a143c9d33fe0aaa`; baseline SHA256 `43b6c6d0c281d833d22f32d9497e4d46947957b7620297592dfc82b49781d15a`; check.py SHA256 `4e6d1bf64df1d14879125b2dbdf6ec0d55e73d44aad6b3518af7fd5b76cdb3a9`. Independently compared baseline.py bytes against actual `git show 4e4199d789812c6964329c02231733472d65a700:agent_runtime/handoff_basis.py`; exact match. Source/baseline/script hashes matched before and after verification. Production source and tests were not edited by reviewer.

Plan-v3 was approved before producer timing. validation-plan.json is a six-criterion projection created after producer execution but before independent acceptance, explicitly disclosed by producer; it changes none of plan-v3's thresholds, workloads, timing or semantics. It is not represented as an original pre-producer file. Current plan/validation/raw-data/code/input artifacts are bound in independent-analysis.json and the review-hashes.json generated with this report.

## Six validity criteria

| Criterion | Verdict | Evidence and conclusion |
| --- | --- | --- |
| implementation | pass | Inspected actual source diff, whole baseline, schema/_ids path, producer harness, permanent tests and consumption/context/impact callers. Helper validates only successful residuals, shares original schema validation, performs exact builtin checks before new hashes or custom operations, checks complete-graph parent existence/status, and counts only pending edges. Unknown parents, unsupported edges and cycles return False; original pending/ready loop still emits diagnostics. Attempt occurs once at round2; original claim identity, insertion order and inputs are retained. |
| reference_boundary | pass | Producer's659 cases reproduced independently, including512 exhaustive three-node directed graphs checked against graphlib. Added252 reviewer cases: actual helper admission residual63/64/65; density391/392/393 against limit392;100 mixed-error placements; tuple dependencies;24 baseline-relative custom operation traces at early/late/peeled objects;120 new valid DAG/self-cycle cases. All passed. Four permanent unittest cases passed ordinary and -O, including nonmutation, deep1200, invalid dependencies, custom traces and multi-error parity. |
| data_integrity | pass | Independently rebuilt all six canonical input hashes; exactly21 pairs/workload; source/baseline/script identities agree across producer/independent. Recomputed each median and percentage from finite raw observations. Harness asserts input canonicalization unchanged; semantic checks verify serialization, order and original object identity. Baseline is actual pinned main bytes. All observed negative controls retained. |
| numerical_sanity | pass | Positive finite millisecond raw measurements; recomputed medians/percentage reductions agree. Tracemalloc peaks are bytes and positive. No numerical approximation introduced in graph validation. Allocation growth is a cost, not a memory saving. |
| measurement_validity | pass | Timed complete claim_graph calls including unchanged schema checks; construction, output serialization and comparison outside timing. perf_counter_ns,3 warmup batches,21 alternating pairs; chain/shared/star/dense batch1, small100, empty1000. Reviewed actual harness loops. Parent held other tests/timings until reviewer signalled all performance measurements complete. Both actors pass chain>=25% reduction and every non-primary regression<=15%. CPU is shared/unpinned; observed medians do not imply individual-call or production guarantees. |
| reproducibility | pass | Independently executed `PYTHONHASHSEED=12 python .agent-runs/memory-claim12-20261017-0802/check.py --out independent.json`, same659 checks and frozen21-pair protocol. Python3.12.14, Linux6.18.44 x86_64/glibc2.39, hashseed12 recorded in independent.json; exact hardware frequency/load isolation not established. Supplemental executable source/results are retained. |

## Recomputed performance

Positive percentages mean reductions; negative percentages mean regressions. Main and independent observations both meet all frozen gates. Independent full-call medians are milliseconds.

| Workload | Producer reduction | Independent baseline → candidate ms | Independent reduction | Gate |
| --- | ---: | ---: | ---: | --- |
| chain512 | 87.099% | 25.422438 → 3.052468 | 87.993% | pass |
| shared256 | 47.556% | 3.552219 → 1.892848 | 46.714% | pass |
| small8 | 0.147% | 0.044925 → 0.045297 | -0.829% | pass |
| empty | -0.029% | 0.000585 → 0.000596 | -1.877% | pass |
| star512 | -6.665% | 2.601389 → 2.627457 | -1.002% | pass |
| dense256 | -0.718% | 168.811232 → 169.193711 | -0.227% | pass |

The shared fixture has64 layers of4 claims, with each layer depending on the preceding four. The star fixture is one root with511 children. Dense256 is the complete forward DAG. Therefore these controls exercise materially different depth and density. Input hashes are in both raw result files and independently regenerated by independent-analyze.py. Raw ranges are retained in independent-analysis.json; no observations were trimmed.

## Costs and maintenance

Independent single-call Python traced peaks: chain48,568→115,584 bytes; shared25,704→58,608 bytes. These increase about2.38x/2.28x. The temporary indegree/children maps deliberately exchange O(V+E) memory for reduced repeated scans; the other workloads retain nearly equal peaks. Tracemalloc is one untimed observation per path, not RSS, GPU/VRAM or stable process-memory evidence. These costs should appear beside latency gains in the public report.

Separate invalid-fallback diagnostics (100-node graphs,3 warmups/21 alternating pairs, no acceptance threshold) observed median regressions unknown-parent6.203%, unsupported-edge5.120%, cycle3.835%. Those additional preliminary checks have a real cost; no all-input acceleration claim is warranted. Raw diagnostic pairs are retained in independent-analysis.json. The small helper plus unchanged legacy path is maintainable in this scope; no generalized graph framework or duplicated schema validator was introduced.

## Failures and limits retained

Independent analysis harness initially used the wrong repository root when hashing artifacts and raised FileNotFoundError after diagnostic measurements but before saving output. No product defect was found; path-only harness repair and complete diagnostic rerun were performed. Initial unsaved diagnostic numbers are not used as evidence. Exact failure description/path retained in independent-harness-failure.md. A supplemental invocation with -O had ordinary Python assert statements disabled and is explicitly excluded; the ordinary252-case supplemental run was rerun and passes, while -O evidence comes from unittest assertions, which remain active. No performance gate was changed or measurement selected to overcome a failure.

Full repository/Reader/final-source integration checks remain root-owned downstream work. This result does not certify live model access, managed supervision, deployed service behavior, actual graph frequency in production or whole-task speed. Baseline-relative custom-object checks cover representative deterministic operations, not arbitrary concurrent self-mutating user objects. Error precedence remains baseline-relative in the same process/hash seed, not a promised cross-seed global ordering. No old pass label was used to certify this result.
