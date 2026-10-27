# TASK-FENCE native fixture correction: independent plan review

Decision: **approve** the exact bounded Version48 correction plan SHA256 `531922fb448dd457ad652e0de6ba547fadc027e2263b322c3ceda108864ba62c` and proposed test SHA256 `4dc993809aa9056cee9f43bb2218bfbc1520c683d8293014f1e5d32aed929c79`. No blocking findings. Result acceptance is pending the one newly committed candidate's native four-job CI evidence. No tests, probes, subprocess CLI calls or models were executed in this review; only documents, source/diff and saved failed logs were read. The only reviewer write is this file.

The earlier static plan review missed task_supervisor's unconditional fcntl import and wrongly found no platform issue in the proposed combined native CLI fixture. That assessment is corrected here. The prior local Linux140-method evidence remains a valid observation for its old test/source hashes; it did not establish Windows native supervisor support, and the failed native run remains failed. No prior review or raw result is rewritten to hide this mistake.

## Identity and evidence

Production repair commit: `5e6b4ee9735ccc616521c189208cd2e592f0fd49`. Failed native run:40437432153. Read full saved raw job entries in `.agent-runs/task-fence-native-1000/failed-job-logs.json` for Windows3.12 job121969361295 and Windows3.10 job121969361391, and extracted their target-step failures. Each target module ran7 methods with one failure in the combined CLI method's command0; its subprocess exited1 during task_supervisor import with ModuleNotFoundError for fcntl. The failure is not an ingestion assertion, UTF8 serialization defect or task_view CLI failure. Other new methods passed. Root's Ubuntu success summary is not promoted by this static review into independently read current four-job results.

Read task_supervisor's actual import/locking code, the original/current fixture diff, the proposed plan, and workflows/task_supervision_workflow.md Linux/server and tmux entry contract. fcntl is imported before command dispatch, and the module also relies on POSIX lock/process primitives. The proposed test correction reflects an existing platform scope; it does not introduce runtime support or fix the supervisor. No fcntl shim, import workaround, matrix reduction or production change is proposed.

## Seven domains

| Domain | Verdict | Reason |
| --- | --- | --- |
| intent | pass | Fix the newly introduced fixture's incorrect platform assumption while retaining the TASK correctness repair and portable API/view guarantees. Preserve the failed native evidence and unfinished SYSTEM-99 rather than relabeling old acceptance. |
| guide | pass | Same project and explicit parent authorization. Entire human-only guide directory and foreign zip remain excluded; main is the sole source/task/public writer, reviewer writes only this private review. No new task index or guide advice is installed. |
| assumptions | pass | Actual failed logs and unconditional fcntl import establish that native task_supervisor prepare cannot run on Windows. Existing workflow limits the tmux-managed entry to Linux/server work. task_manifest.prepare API and task_context CLI remain separately portable and are still unconditional tests. |
| prior_results | pass | Original baseline/fixed/independent140-method records bind the original seven-method fixture and remain intact. Failed nativeCI40437432153 is the new directly relevant evidence. The correction does not reuse that old pass as proof of the modified fixture, delete failed Windows runs or replay an exhausted old runner. |
| acceptance | pass | Split into a POSIX native-prepare method with explicit Windows skip and an unconditional portable native-task-view method. The original draft, IDs, placeholder/action, input bytes, exact view text/positions/omissions and side-effect checks remain, with sourceSHA and exact inventory checks strengthened. Expected new target module:8 methods discovered; Linux8execute, Windows7execute plus1 explicitly scoped skip. One new commit-triggered native four-job CI run supplies modified-fixture evidence; independently inspect its exact SHA/jobs/raw logs. |
| risk | pass | Only tests change; no parser, production helper, guards, schemas, native CLI behavior or CI matrix is altered. Skip is confined to unsupported supervisor CLI, rather than skipping canonical/legacy prepare API coverage or the portable view. Windows native-supervisor prepare remains unverified/unsupported, explicitly stated. Old model/quality/fee/fullsuite claims remain absent. |
| resources | pass | No local regression or probe is authorized. One necessary commit-triggered Ubuntu/Windows×3.10/3.12 CI run only, with existing workflow limits and15second nested CLI limits. No rerun, cancel/retry, old labels, old-runner replay or budget reset. On new failure, stop this correction and retain evidence; further work requires explicit replan. |

## Exact fixture assessment

The former combined method had two sequential subprocess commands in subtests. Because unittest subtests continue, Windows command1 portable view could pass after command0 import failed, but the aggregate method still failed. The new structure accurately separates their platform contracts without suppressing portable checks. The skipIf decorator tests os.name=='nt' only on native supervisor prepare; its reason expressly names fcntl and retained portable prepare API testing.

New POSIX prepare assertions retain the same temporary canonical fixture, three real IDs, protected plan_review field, configure_host_action placeholders, returned draft path/count, empty stderr, original-byte preservation and no extra artifact except requested draft.json. It adds sourceSHA validation and replaces the old conditional artifact expectation with unconditional exact expected output, strengthening behavior. Windows canonical/legacy API prepare tests are unchanged and still execute.

New task_view CLI remains unconditional, uses fresh canonical fixture and original cp936/PYTHONUTF8 environment and15second timeout, verifies exit0/empty stderr, exact source lines1/3/4/5/6, full selected text and omissions2. It adds exact source path/hash and whole-fixture after==before inventory checks. Parsing stdout JSON preserves original newline oracle behavior. This method cannot accidentally inherit the POSIX skip decorator because it is a separate method with no decorator.

The test import list already contains os/unittest and neither modified method adds a platform-specific top-level import. Existing direct prepare API import is unchanged and succeeded in the failed Windows jobs. The diff adds no production change, helper replacement, dependency or test-only fcntl emulation. The previously accepted source hashes remain the governing production identity and should be rechecked in the new CI/result audit.

## Required later evidence and reporting

Before approving modified-fixture results, inspect the single new native run bound to the new exact commit, require all four jobs and all configured steps complete successfully, read target-module logs to establish Linux8pass and Windows7pass/1explicitskip, and confirm canonical/legacy API and portable view actually ran in Windows. A green workflow summary alone cannot show the skip reason or target coverage. Preserve the original40437432153 job logs and old reports unchanged and report this as a platform-fixture correction, not a production bug fix or new Windows supervisor support.

Version48 and separate evidence should bind the corrected plan/test hash and explicit native scope. No old140-method acceptance is transferred to the new hash; native evidence is the new reproducibility observation. Immutable registration remains unknown trust; host reporting audit is not a repository-authenticated ReviewSession receipt. Fresh remote-head/normal publication/readback is separately root-owned. Bodycount18 and SYSTEM-99 unfinished status remain.

Compact verdict: approve; intent=pass; guide=pass; assumptions=pass; prior_results=pass; acceptance=pass; risk=pass; resources=pass. No additional execution is authorized by this review beyond the plan's single necessary new nativeCI run.
