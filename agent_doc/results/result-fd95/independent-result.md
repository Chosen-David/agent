# RESULT-FD-95 independent result acceptance

Date: 2026-10-20. Reviewer: separately invoked `result_fd95_review`, independent from the source/test producer. Verdict: **usable-with-scope** for local descriptor-ownership repair in `result_store._read`, `_check_ref`, and `ResultStore._save`, with the limitations below. No blocking implementation findings.

This is actual tool-backed independent code/data inspection and execution. It is not a ManagedEngine/ReviewSession authenticated machine receipt, deployed supervisor, remote publication verification, or universal correctness claim. Main owns final document/publication checks and remote readback.

## Actual executed evidence

Read the complete affected source and public show/search/register/register_history/decide_run paths, inspected the exact diff and producer test helper, then reviewed before/after/optimized/full/Reader raw logs and the draft report. The diff changes only the three planned ownership sites: immediate try/finally after acquisition, borrowed fdopen(closefd=False), hash initialization before acquisition, and inner fd close before outer _save publication/temporary unlink.

Independent `independent_matrix.py` obtains baseline source directly with read-only `git show e30dfce8424f7912a3716dd6ef035f648808e2f7:agent_runtime/result_store.py`, loads baseline and candidate into separate modules with the same unchanged supporting dependencies, and runs fresh disposable fixtures. It holds real streams alive to prevent finalization from hiding entry-failure leaks, observes each actually acquired fd via real fstat before cleanup, and cleans only those descriptors afterward. Failure assertions use explicit checks, not Python assert, so optimized runs retain all oracles.

Commands (repository root):

```text
PYTHONDONTWRITEBYTECODE=1 python agent_doc/results/result-fd95/independent_matrix.py
PYTHONDONTWRITEBYTECODE=1 python -O agent_doc/results/result-fd95/independent_matrix.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_result*.py'
PYTHONDONTWRITEBYTECODE=1 python -O -m unittest discover -s tests -p 'test_result*.py'
```

All four exited 0. The independent regression runs each executed 103 passing methods. Full-suite producer log reports 1347 methods, 8 skipped (1339 passed); Reader producer log reports 3 passed. Those broad logs were inspected and hashed, not misrepresented as independently rerun full suites.

| Independent matrix | Scenarios per version | Baseline leaked fds | Candidate leaked fds | Candidate actual acquisitions / raw closes |
| --- | ---: | ---: | ---: | ---: |
| Normal | 38 | 12 | 0 | 33 / 33 |
| Python -O | 38 | 12 | 0 | 33 / 33 |

There are 76 raw observations per mode, 152 total, not 152 distinct scenarios. Each baseline leak is one descriptor: _read directory/construct/interrupt/enter (4), _check_ref those four plus hash initialization (5), _save construct/interrupt/enter (3). The producer's 12 failing subcases are a different measurement and are not the source of this leak count. Producer repeated-search baseline exits on its first failing iteration; its planned four iterations were not all executed on baseline.

The matrix also covers normal read/check/save, fstat/read failure, rejected nonregular input, initial size limit, growth limit, stale hash, stream exit failure, open failure, mkstemp failure, save write/flush/fsync/link failure, and a real FileExists race at link. Candidate failed acquisition paths make no raw close call. Link is only reached with all owned fds already closed and exact expected serialized bytes present. A concurrent writer's target bytes survive unchanged and FileExistsError remains the cause of ResultStoreError. Every save path removes temporary names; failed save paths do not create a target. Paired exception class/message, injected exception identity, target bytes/hash and temporary cleanup are preserved across the matrix.

## Six fixed acceptance criteria

| Criterion | Verdict | Actual evidence and scope |
| --- | --- | --- |
| implementation | pass | Exact diff and complete call-path inspection; original validation, bounds, hash comparisons, no-follow flags and immutable link semantics retained. Three explicit owners now close on all inspected successful-acquisition branches, including BaseException. |
| reference_boundary | pass | Independent real-fd oracle, real directory rejection and real concurrent FileExists outcome; 38 paired scenarios covering acquisition, construction, entry, body, exit, limits and publication. Existing public API regression tests also rerun. |
| data_integrity | pass | Frozen Git baseline, candidate/test/script/plan/log hashes below; deterministic binary fixture hash in raw JSON; separate fixture per scenario; leaks measured before cleanup; all failures kept in producer before.log. |
| numerical_sanity | pass | Counts are nonnegative integers; raw rows sum to baseline12/candidate0 each mode. Candidate33 acquisitions equal33 closes; no aggregate process-fd heuristic, timing-based inference or omitted failing case. |
| measurement_validity | pass | Claim is resource release under declared cases, measured on each acquired descriptor after return/error. Ordinary and optimized code agree. Timing/throughput/RSS/token/model-quality claims are not applicable and were explicitly excluded in the fixed plan; test durations are not speedup measurements. |
| reproducibility | pass | Independent normal/-O paired runs and103-method regression runs pass; producer full/Reader logs inspected. Script captures interpreter/platform/source/input hashes and reconstructs inputs without external services. |

## Frozen bindings

| File | SHA-256 |
| --- | --- |
| baseline result_store source | `3da82814e44acdc8ff8aa26e4b5d103825713d515c688e0ca06e63518cb02c1b` |
| candidate agent_runtime/result_store.py | `6ef04bd8497e196dd728bc480afba11f192c29c43282b663aa410db3afdfefaf` |
| tests/test_result_store_fd.py | `564940de12e0e1cf3a5912c76cc427f5f9ce54cb10b4e18f5f8e6d0e4f851701` |
| plan.md | `0bfe1645759c3cb845b313e54c9703ef596a20b93d5790df96d8a93fd826ce07` |
| independent_matrix.py | `627ce1e6571e8481a86cc22650206f14706719d32489d03c321e6d04074712fa` |
| independent-raw-normal.json | `66430f30e0b739ad0baeb071a05f1afbe9090a15649d8e8fe60ef2644d1bf95b` |
| independent-raw-opt.json | `8c6fdf2937e55d68dfda1e4501f915cf87dbbff36770b615c15df8f328d5e62d` |
| independent-regression.log | `42a9071123d75189e2b7f943e5ad36b1358be1536bfe625f08f3fb94546bd3e6` |
| before.log | `c43156217515e340a68ec7395cc254911d977450fe4791f0a686172d4b0be727` |
| after.log | `eab9680fbd37dfa6b5fff2c0383d88cf581659e049cd7d507940c9f2e50db8e9` |
| after-opt.log | `5d2951f613ea09c453b85e4dc1f3489c8473e42a09c4fabb83c440b607c22088` |
| reader.log | `ea152184377bbf17aa0e9e4f8b64d18e21fb3933626fe01fd918410b6d0505c6` |
| .agent-runs/result-fd95/full.log | `0d0262cfd63e31bc820ef7f12c8d7976d7ba6fac9707df9db518aca7e6c8ce4b` |
| agent_runtime/project_docs.py | `a2712d093f4012350f6654401a15aa1d22e442d6993482025996b63183477a57` |
| agent_runtime/legacy_result_paths.py | `b82622cd42e0824f4e6d064e2c4e9a6cea464e0761ec7c0b32adfc5e86751525` |
| agent_runtime/result_validation.py | `ede93a1c5e1d044d20cc33643d61fd9a360d94e38af4e8653fb1f22ca1febb31` |

Bindings were rechecked after independent runs. Git diff showed no changes to the three supporting dependency files. The draft report accurately separates observed descriptor closure from unmeasured throughput/model benefits and does not claim publication complete.

## Limits and handoff

CPython3.12.14/Linux local standard-library synthetic testing; no GPU/model/API work, cross-platform guarantee, live production exhaustion demonstration, or generic concurrent-fd ownership guarantee. Injected constructor/entry/hash-factory failures establish exception-path behavior, not their real production frequency. Raw os.close failure, OS crash and malicious same-process descriptor reuse are outside this acceptance. Hashes bind inspected bytes but are not correctness/identity proofs.

The stable implementation/test/plan bindings must remain unchanged or dependent acceptance must be revisited. Main may summarize this scoped acceptance and complete authorized publication checks; this reviewer did not stage, commit, push, edit source/tests/TASK/guide, or claim a remote SHA.
