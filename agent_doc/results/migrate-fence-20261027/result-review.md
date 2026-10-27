# MIGRATE-FENCE-01 independent source and result review

Verdict: **usable-with-scope**. The exact local migration-consumer repair and frozen regression are accepted within the fixture scope below. No blocking findings. Native CI, final publication-tree audit and remote readback remain separate and unverified by this record. SYSTEM-99 remains unfinished.

## Object and observations

Project `/workspace/scratch/6416f20dc59b/agent-run-1303`, base HEAD `56cb758a0a0116fec98e8d0f6fdcc079f1f9db7a`. Approved plan SHA256 `ebae1564de81e8cf8e21411c85e2efc8ca13ba588bf697e1ea08849a1edd7fc1`; separate static review SHA256 `11c8705f61aa5d03762f8b4331c45d0e8f3e4d8ec01bcb118cee325e77e7649f`.

| Input | SHA256 |
| --- | --- |
| Baseline project_docs.py | `c461724efbbe58692e9940dcfca466ba5f40f2a4101ef249037e2358310e24d6` |
| Fixed project_docs.py | `3e4190d4c256fb59ad456849ab00dd80534b096c4a29a52c081ae9d117395be5` |
| Unchanged new test | `0af0c2e25bbb291659487f6fb79571243df2b18b829464e4b7f544f51dd1749c` |
| Unchanged runner | `0f23ed34b8d046ec620a32b883342682b6aaf16bf734eb30a7ff36af549e1b97` |
| CI file after one new module step | `a9362b355d7a6ef1c9cdaa0709ed1b87be68c64f80385491caea96e870fd87a9` |
| Frozen environment/input record | `9392999f72408d012c696ef09698e2c77411c7a6f1e77c7d8130921d69b09371` |

Observed environment: Python 3.12.14, executable `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python`, Linux 6.18.55 x86_64 / glibc2.39, as recorded in frozen-inputs.json. No model, performance or paid-resource experiment is involved.

I read the source diff, complete changed migration function, helper/physical-line/requirement interfaces and CLI path, full frozen test and runner, baseline/fixed metadata, all baseline subcase failure headers and terminal messages with representative full tracebacks/diffs, classification and full fixed/independent logs. The initial combined baseline display was truncated; subsequent bounded reads and complete extraction of every failure header/message resolved coverage rather than treating the truncated display as full evidence.

Exactly one independent execution was performed:

`python .agent-runs/migrate-fence-1058/run_checks.py independent`

The actual command returned exit 0. Its unittest child executed all seven frozen modules: test_migrate_fence, test_project_docs_acceptance, test_project_docs_init, test_repository_task_integration, test_task_navigation, test_task_navigation_regressions and test_task_source_snapshot. **81 methods passed, no skips**, unittest elapsed 6.733 seconds, runner elapsed 7.016613 seconds, shared branch elapsed 100.048153 of 900 seconds. Production/test hashes before and after match the fixed inputs above. This consumed the sole independent label; no further tests or probes were run.

## Baseline classification and causal interpretation

The single baseline executed 81 methods and ended with 11 assertion failures plus 59 KeyError error subcases in four new methods. The 75 existing methods and two new control methods passed. All 70 failing subcases are accounted for:

| Observed class | Count | Interpretation |
| --- | ---: | --- |
| `KeyError: NEXT` | 32 | Invalid closer accepted by the older migration scan exposes example date/ID, then its later state misses the real NEXT date/block entry despite requirement parsing admitting NEXT. |
| `KeyError: CORRECT` | 27 | Invalid opener accepted by the older migration scan hides CORRECT from its dates/blocks map although the requirement parser admits it. Cases span nine markers and LF/CRLF/CR. |
| CLI return-code assertion, actual exit 1 | 3 | Each stderr traceback is the same missing CORRECT mapping through the real scripts/project_docs.py migrate entry. This is not a CLI import or encoding failure. |
| Successful migration, incomplete derived KEEP block at EOF | 8 | Two marker types times four invalid closer forms prematurely end the retained block before the fake example row and following evidence. |

These counts are subcase outcomes, not 70 independently established defects. There are no import/fixture/timeout exceptions in the recorded failures. In the eight EOF migrations, archive byte equality, pointer checks, canonical set/date and index-hash checks precede the failing preserved-block assertion. Consequently the observed defect is incomplete derived detail content; **the original raw content-addressed archive was preserved**, and no raw-data deletion claim is supported. The test's TemporaryDirectory cleanup is expected fixture lifecycle, not production evidence loss.

The same unchanged test and runner then passed all 81 methods in the single fixed invocation, with no skips. Fixed runner elapsed 5.839745 seconds, branch elapsed 42.658097 seconds. Timings establish budget compliance only; no speed comparison is accepted.

## Six-domain validation

| Domain | Verdict | Independent reasoning and evidence |
| --- | --- | --- |
| implementation | pass | The production diff is solely migration's local transition replacement with `_fence_transition(line.rstrip('\r\n'), fence)` and deletion of its duplicated lstrip/token state logic. Marker lines still append their original raw line to the current block and continue. Existing helper, parse_requirements, outside_fences, task_view, archive construction, rebasing, detail/index generation, identity checks, conflict guards, source rechecks and pointer-last publication are unchanged. New CI change is one module step in the unchanged four-job matrix. Diff and source hashes bind what was tested. |
| reference_boundary | pass | Literal expected source slices, task IDs and dates do not invoke the fence helper to produce expected answers. Cases cover both marker types, invalid four-space/tab/NBSP/LS and backtick-info openers, 0–3-space valid openers, longer valid closers with space/tab tails, invalid closer indentation/type/length/tails, fake dates/IDs/evidence, EOF and LF/CRLF/CR. Normal/default dates, idempotence, conflicting details, duplicate and unidentified rows remain checked. The oracle matches existing `rstrip()` and CRLF-to-LF derived normalization; CR-only interiors remain CR and the raw archive remains byte-exact. Full Markdown containers/HTML are outside the contract. |
| data_integrity | pass | All baseline failure classes map to actual subcase messages and source paths. The 81-method denominator consists of six new plus 75 existing methods; the unchanged baseline/fixed fixture hashes and matching before/after production hashes prevent silent source mixing in recorded runs. Archive SHA/bytes, canonical ID/date tuples, exact snapshot detail set/index SHA, pointer and each complete retained block are asserted for successful fixtures. Conflicts/invalid sources preserve preexisting file bytes. Raw log hashes independently match metadata. No old empirical pass was reused as migration evidence. |
| numerical_sanity | pass | This is discrete correctness: exact task/date identities, expected set membership, exact source-block strings, byte inventories and SHA equality. No floating-point tolerance, aggregate accuracy denominator, model metric or statistical claim is involved. Baseline 32+27+3+8=70 subcases agrees with 59 errors+11 failures. No failures are hidden as skips in fixed or independent runs. |
| measurement_validity | not_applicable | Preapproved correctness-only scope makes throughput/latency/performance measurement inapplicable. Elapsed values are resource-accounting observations. No hardware speed, token, cost, model-quality or optimization-round claim is accepted. |
| reproducibility | pass | A separately delegated reviewer actually executed the sole independent frozen command, observed child exit 0 and read the full 81-method passing log. All six new methods executed, including three separate real CLI fixtures under PYTHONIOENCODING=cp936/PYTHONUTF8=0 with 15-second limits. Runner used the same seven modules/environment path and unchanged test/runner, under the original 900-second branch budget and 180-second command bound. No substitute labels, retry or old runner/native CI replay occurred. |

## Retained evidence bindings

Paths below are relative to `.agent-runs/migrate-fence-1058/`:

| Evidence | SHA256 |
| --- | --- |
| baseline.log | `5c35ceec5def233dc2c58ba9186f59b8875ac24ace93d860b50694c22b172de2` |
| baseline.json | `e0c68459000d3f592e65d6b09e7429bcee52b33a5907124bbcca203c327b358e` |
| baseline-classification.json | `1c30049facb15c99bd229bc51cb89c3058058d230650114e828bb4828c827e09` |
| fixed.log | `f71e1af97f4c4d0b897cdacd40b0b1a43a2cc1672497a1393e44c3387266136f` |
| fixed.json | `93d26374b70962ab908df0a10d3d9b55f60d876584add4c2127a7a9c44ea89ac` |
| independent.log | `671e4e51f85069bf242e0888571a2acd8005661ca9da3fa424bde8d1791bd84e` |
| independent.json | `32ded21a124ca7c7c6b7afa3143733e075b99a664d6bfe2858c89966d6a076cf` |

## Scope and limitations

Acceptance supports this existing migration consumer's literal top-level fence grammar and the exact API/CLI fixtures and adjacent local regressions. Temporary generated projects are cleaned by the tests; retained source and complete test logs record assertions, rather than persistent copies of every generated project. Finite fixtures do not prove universal correctness, adversarial filesystem race safety or complete Markdown semantics. Native Windows/Ubuntu CI remains unobserved in this review; portability is a source-level design assessment plus Linux CLI execution until actual job outcomes are read back.

Current guide bytes and TASK/SYSTEM-99 Version48 bytes match static review bindings at this check. Root's planned Version49/progress/public report final audit is still pending. I did not alter source, tests, CI, task documents, human guide files or foreign zip. Only the explicitly authorized runner produced its independent log/metadata, and this review file was authored. All baseline evidence and old closed/exhausted gates remain intact.

This separate invocation is independent source/result review and a real bounded rerun, not an authenticated runtime ReviewSession or deployed verifier claim. Historical catalog registration remains discovery-only unless separately validated. Final candidate publication and native CI must retain the source/test identity and explicit limits above. SYSTEM-99's real-host/input/quality/all-actor usage/cost/cross-store and earlier unresolved gates remain open; no new paper credit, performance gain or completed optimization round follows.
