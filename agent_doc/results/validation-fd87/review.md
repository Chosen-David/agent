# Independent review — VALIDATION-FD-87

Date: 2026-10-20. Reviewer: host-dispatched `/root/validation_fd87_review`, separate from the implementation author. Result: **usable-with-scope** for the tested descriptor-ownership repair and retained display-record semantics. No blocking findings. This is independent host review, not a ManagedEngine plan receipt, deployed supervisor, registered trusted callback, or universal correctness guarantee.

## Plan review and scope

Before implementation, reviewed AGENTS, decision-review, project-document, dual-main, result-validation, result-reuse and knowledge-access guidance; the empty human-only GUIDE and its explanatory README; the current task index; the frozen plan; baseline writer; existing `_bytes` ownership; and historical artifact-fd77 independent review. The historical review is pattern input, not acceptance of this writer. Prior result search remains partial as disclosed by the plan; this review does not claim exhaustive retrieval or independently verify literature claims. Resource ownership needs actual source/CPython behavior, not a mathematical knowledge-corpus dependency.

Plan SHA-256: `f9b675f93be38e9ca062b3aa3108a5ae25e2b7cb11c2da4670fcdbaff54d356e`. Preimplementation decision sent to the main agent: approve bounded local implementation/testing. Seven plan checks passed: intent matches reliability goal; empty guide remains untouched; constructor-failure premise is grounded in source; prior results are adapted without reusing old measurements; exact ownership/semantic acceptance is specified; risks remain local and non-destructive; CPU/temp-directory resources suffice. Approval did not grant publication authority or certify unavailable runtime adapters. The later task detail binds the same frozen plan and preserves main-only TASK ownership.

Baseline: `80e7bf3ba8de99e0aee55505091172c6a5816c40`. Actual production diff changes only the successful-open branch: borrow the descriptor using `fdopen(closefd=False)` and close its original integer in `finally`. AST comparison confirms the rest of the entire module and original write/flush/fsync body are unchanged. Open failure remains outside the ownership `try`; existing-file comparisons, serialization, paths, guards, display projection and restoration are unchanged. No unlink, overwrite, atomic-write or trust semantics were introduced.

## Independent execution

Commands, run from the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python agent_doc/results/validation-fd87/independent_probe.py > agent_doc/results/validation-fd87/independent_raw.json
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_validation_write_fd tests.test_validation_context tests.test_result_validation tests.test_result_gate_acceptance -v > agent_doc/results/validation-fd87/independent_tests.log 2>&1
```

The probe AST-extracts the real baseline function from fixed Git source and invokes it beside the actual imported candidate with unchanged helper globals. Every returned descriptor is tracked individually; real `fstat` observes its state before cleanup. The probe cleans only its own baseline leaks after recording them, retains streams to prevent destructor timing from hiding entry leaks, uses separate per-case target directories, and calls the real `fsync` on success. It does not infer ownership from process-global descriptor counts.

| Paired metric | Baseline | Candidate |
| --- | ---: | ---: |
| Calls | 20 | 20 |
| Successful opens | 19 | 19 |
| Owned descriptors still open after the call | 12 | 0 |
| Explicit `os.close` calls | 0 | 19 |

The twelve baseline leaks are ten bounded constructor `OSError` repetitions, one constructor `KeyboardInterrupt`, and one context-entry failure. Other cases cover write, flush, fsync, context-exit, denied open, and successful pending/invalid/usable-with-scope display records. Every candidate successful open has exactly one explicit close and is `EBADF` after the call; denied open has no descriptor and no close. Every injected exception propagates by object identity, including `KeyboardInterrupt`.

All paired serialized hashes/lengths, exception identities/types, completeness, actual fsync counts and retry outcomes match. Three status-success cases match an independent standard-library serialization expression byte-for-byte and round-trip the complete observed values; display status, hidden-detail counts and trust warning are retained. Empty failed records remain present; retry rejects them with `preserve and repair` without modifying them. Failures after complete bytes have reached the file (including injected fsync failure) retain existing complete-record idempotency. A retry accepting those bytes is not evidence that a failed fsync became durable.

Independent targeted suite: **47 passed**. Inspected producer baseline log: **8 tests, 3 expected ownership failures**, corresponding to constructor error/interruption and context entry. Producer ordinary and optimized runs: **32 passed each**. Inspected full raw log: **1,331 distinct test lines, 1,323 passed and 8 skipped**, agreeing with its final summary. Reader raw log: **3 passed**. Seven skips need optional visualization dependencies; one is an opt-in real-tmux integration. They remain unverified. `git diff --check` passed. No test duration, throughput or performance benefit is claimed.

## Six acceptance criteria

| Criterion | Verdict | Evidence and boundary |
| --- | --- | --- |
| implementation | pass | Reviewed actual narrow diff and AST invariance. Original descriptor has a single explicit closer even when construction/entry fails; failed open closes nothing. |
| reference_boundary | pass | Frozen Git baseline, exact-fd observation, bounded repeated faults, interruption, lifecycle errors, three valid statuses, serialization oracle and retained-file retry controls. |
| data_integrity | pass | All 40 paired observations retained in independent_raw.json; no failed sample discarded; cleanup occurs after observations; source/test/plan/probe hashes recorded and rechecked. |
| numerical_sanity | pass | Exact integers: 12 = 10 constructor + 1 interruption + 1 entry leaks, reduced to zero; 19 candidate opens = 19 closes; one denied open = zero closes. No tolerance or floating-point inference. |
| measurement_validity | pass | Real per-fd `fstat`/EBADF and real close calls directly measure resource ownership; real successful fsync exercised. No process-global count, timing or durability claim. |
| reproducibility | pass | Independent 20-pair probe and 47-test rerun match preserved baseline/after results; full/Reader raw logs inspected; CPython/Linux environment recorded. |

## Bound evidence

All following paths are repository-relative; hashes bind reviewed bytes.

| Path | SHA-256 |
| --- | --- |
| `agent_runtime/validation_context.py` | `a1cf803a2141e2bd09cc082a1da1c5722fbebe3059f4f44af7bc522047329fd3` |
| `tests/test_validation_write_fd.py` | `0a36d1f4399f7dd468de1890d218a82b5c6dea49b7890d1ae06ca8072dc3d088` |
| `tests/test_validation_context.py` | `6ad2b868df799cabbb6fb3bce3673c2e9ba45e16ff9c5aa8962cac324aca8ad3` |
| `tests/test_result_validation.py` | `79e3840fe6b39432526e4c75fcf98f9c6bf2a3aa410e58d2d281550902482377` |
| `tests/test_result_gate_acceptance.py` | `c58b912cf1851c6def90ca2da4671e671f23a0c097674214f4fe135dcf1c719e` |
| `agent_doc/results/validation-fd87/independent_probe.py` | `a0e4b41a1d373d8160bb11b0c485f8d3c13919a0481f114fa9fa2c345bb438d1` |
| `agent_doc/results/validation-fd87/independent_raw.json` | `e0d82db34ad1572710d793cc3de2ad109297e1be4f0d2f3bb8d16756626a8838` |
| `agent_doc/results/validation-fd87/independent_tests.log` | `f29992763797e50863281e27b1ef780b1950de14bf3514448ebe888f1cc4f1b2` |
| `agent_doc/results/validation-fd87/before.log` | `286679cb7481f920cd07259c90031cacce5d376e17e8eac4a4e97e6d30264526` |
| `agent_doc/results/validation-fd87/after.log` | `c9a55d2b317f15e7b38061bd5573be4e9c22ed875459f10d45f8261d18013eef` |
| `agent_doc/results/validation-fd87/after-O.log` | `3d0e358cd5b43c176dff1c12efb75c788ae543cd06a74caaf5257d5e86b29473` |
| `agent_doc/results/validation-fd87/full.log` | `66e2b73ccbf65b1084586a88a402b412014766a8e0664a4c834c7e249fa46fbd` |
| `agent_doc/results/validation-fd87/reader.log` | `42cd32abcf4f7073b2b92a3bc6b68a4d49b1966a2aade2c42e55f3a0e46917e1` |

Baseline module SHA-256: `f0022561b3c28bc6c7b03852d1bd74db615ac0df597ad5eb506094a8455a1e5b`. Source/test/plan hashes were rechecked after independent execution and full-suite completion.

## Limits and handoff

Acceptance covers observed CPython 3.12.14/Linux local-file paths, not all platforms, malicious stream wrappers, external descriptor interference, process termination, asynchronous interruption between open and the ownership try, or failure of `os.close` itself. Close failure can supersede an earlier error. Atomic publication, recovery/cleanup of partial files, fsync durability guarantees, pathname-race removal, broad I/O refactoring and performance remain out of scope. Substantive source or acceptance changes require renewed review.

The reviewer wrote only this review and `independent*` artifacts; no source/test/TASK/guide/historical result or Git mutation/push. Main owns final task reconciliation and authorized publication, with fetch/concurrent-change handling and remote SHA/tree verification still required separately.
