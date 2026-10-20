# Independent acceptance — ARTIFACT-FD-77

Date: 2026-10-20. Reviewer: host-dispatched `/root/fd77_review`, separate from implementation. Decision: **usable-with-scope** for descriptor ownership on the tested artifact-read paths and preserved byte/error behavior. This is a standalone independent review, not a ManagedEngine receipt, deployed supervisor, trusted callback registration or universal safety guarantee.

## Review boundary

Read AGENTS, decision-review, project-document, result-reuse, result-validation and knowledge-access guidance; read-only empty GUIDE and guide README; frozen ARTIFACT-FD-77 plan; actual production and test diff; and historical artifact-read76/independent.md. That historical review identifies the same directory leak but is not acceptance of this source. Current result search is incomplete as recorded in the task plan; this review does not claim exhaustive search or new literature research. Resource ownership is checked through actual CPython behavior and source inspection, with no mathematical-corpus dependency.

Fixed baseline: `91114412e26d85ae06be5421e42e11bf84fee9c6`. The probe AST-extracts baseline `_bytes` from that Git version and executes it in unchanged helper globals. Candidate is the actual imported production function. AST comparison confirms the entire module is unchanged apart from `_bytes` ownership; the original with-body, pre-open/path statements and subsequent bounds/digest checks are identical. `os.open` remains outside try; `fdopen(closefd=False)` borrows the descriptor; finally closes the original descriptor. Existing allocation tests are retained, with only kwargs passthrough added to the mock.

## Independent execution

Commands:

```text
PYTHONDONTWRITEBYTECODE=1 python agent_doc/results/artifact-fd77/independent_probe.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_result_read_fd tests.test_result_read_allocation tests.test_result_validation tests.test_dispatch_context tests.test_result_gate_acceptance -v
```

The probe uses a separate process and temporary directory. It records each exact descriptor returned by the real open, each explicit close call, descriptor state via real fstat, and cleanup. Baseline leaks are immediately reclaimed using only descriptors opened by that call. Twelve repetitions are bounded; no process-wide descriptor sweep is used. Constructors and all patches delegate to retained real functions where applicable.

| Metric / case | Baseline | Candidate |
| --- | ---: | ---: |
| Paired calls | 22 | 22 |
| Successful opens | 21 | 21 |
| Still-open descriptors after call | 13 | 0 |
| Real directory failures / leaks | 12 / 12 | 12 / 0 |
| Injected constructor failures / leaks | 1 / 1 | 1 / 0 |
| Candidate explicit closes per successful open | N/A (stream normally owns close) | exactly 1 |

Other held-out cases cover read, rewind/seek, context-exit, fstat and open failures; valid binary payload; initial oversized file; deterministic growth and shrink. Every candidate opened descriptor is EBADF after the call. Failing open records zero descriptor and zero close. All paired byte hashes/lengths or exception type/messages match. Every injected exception is preserved by object identity. Directory messages match because owned baseline cleanup permits descriptor-number reuse. The raw observations preserve the real messages and descriptor integers.

Independent targeted suite: **45 passed**. Producer baseline log has four tests with two expected failures (directory and constructor ownership); producer after log has **45 passed**. Full-suite log independently inspected: **1318 run, 8 skipped, remaining passed**. Reader log inspected: **3 passed**. Seven skips require optional visualization dependencies and one requires opt-in real tmux; skipped integrations remain unverified. Main and independent runs can overlap, but no timing, memory-performance or throughput claim is made and probe file/descriptors are process-isolated.

## Six criteria

| Criterion | Verdict | Evidence and acceptance |
| --- | --- | --- |
| implementation | pass | Actual diff and AST equality isolate ownership change. The original fd has one closer even if fdopen construction fails; open failures do not close an unassigned descriptor. |
| reference_boundary | pass | Fixed Git baseline against real candidate, 12 directory repetitions and 10 additional failure/success/bounds/mutation cases; exact byte/error and injected-exception identity comparisons. |
| data_integrity | pass | All 44 observations retained, exact descriptor ownership tracked, bounded baseline cleanup recorded, source/probe/tests/plan/log hashes bound below and in raw.json. No sample omitted. |
| numerical_sanity | pass | Integer descriptor counts: 13 baseline leaks = 12 directory + 1 constructor, zero candidate leaks; 21 successful candidate opens = 21 single close calls; one failed open = zero closes. |
| measurement_validity | pass | Exact per-descriptor EBADF and close-call observations measure resource release directly; no reliance on global counts or timing. Separate-process fixture isolation prevents cross-test descriptor cleanup. |
| reproducibility | pass | Independent probe and 45-test rerun reproduce repaired ownership and preserved semantic regression checks; preserved before/after and completed full/Reader logs agree within tested scope. |

## Bound evidence

- `agent_runtime/result_validation.py`: `ede93a1c5e1d044d20cc33643d61fd9a360d94e38af4e8653fb1f22ca1febb31`.
- `tests/test_result_read_fd.py`: `7191385c4b47e39f042fe926f54ab3c8e05953632b70d6664825e9f7a0fb87c8`.
- `tests/test_result_read_allocation.py`: `b554d33220db050a12856c840720804f5d893a912debbd6f8c9aeb2a01e56cb4`.
- `agent_doc/task/task_details/ARTIFACT-FD-77.md`: `e9fbb059d39a1b6f1194c6099a8fdfc178cb3cd793f6d3ef026a2631810d589e`.
- `agent_doc/results/artifact-fd77/before.txt`: `479c61f7ba5fa9aef8cc43ab608b5e989d2151397186453c593ee3cc13cadc56`.
- `agent_doc/results/artifact-fd77/after.txt`: `3562509aeba4bdcd3da89f2363d25d41004ee88c7f7d8eae62835277362ef9d7`.
- `agent_doc/results/artifact-fd77/independent_probe.py`: `173e5ef9a8f657853eb5507ad4ce61026ac4f2f3d9d752695dd89871d50f81fb`.
- Baseline production source: `430f3a421a8b2b305cdb8da916f4ac8fdf8c977131449c49310e1bb69a69661d`.
- `agent_doc/results/artifact-fd77/raw.json`: `6f1f0f0333293ac2add294b284509b708fe1342f3fe80499767019c3d5b27890`.
- `/tmp/fd77-reader.txt`: `0ca4a7f496f4bd6efd9a25ff3a6a06805c5495c7e266fae0781e557ca9f2d2b5` (local inspected log; full-suite raw log not claimed bundled).
- `/tmp/fd77-full.txt`: `9450e1f64019fac73ff8668042c5fcd335e49080bc7cc17db130ffed1c3e3c44` (local inspected log; full-suite raw log not claimed bundled).

The task-detail hash binds the Plan and then-current Progress; later append-only progress does not change this reviewed implementation/acceptance scope. Source and test hashes were rechecked after execution. raw.json also records environment and complete independent targeted output; its full-suite record retains summary/skips and original log hash.

## Limitations

This accepts the listed CPython/Linux paths, not arbitrary malicious stream wrappers, external descriptor interference, process termination, asynchronous interruption between open and try, or failures of os.close itself. A close failure may supersede a prior error; no new close-failure recovery guarantee is asserted. Pathname-race elimination and atomic file snapshots remain outside scope. Historical allocation improvements are not remeasured here; the existing allocation/bounds/growth tests pass on the changed source. Any substantive source, protocol or evidence change requires revalidation. No production, TASK, guide, historical result, commit or push was edited/performed by this reviewer.
