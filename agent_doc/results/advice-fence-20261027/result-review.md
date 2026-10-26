# ADVICE-FENCE-01 independent result review

Verdict: usable-with-scope for the approved bounded local advice-fence correctness repair. No blocking findings. This is a separate host agent's actual code/output review and one independently invoked regression subprocess; it is not repository ReviewSession authentication, an experiment-result contract deployment, or global SYSTEM-99 acceptance.

Plan reviewed: SHA256 `75b6b44d11e30b9cb756105fefb9b37f7ed67bbc367870ce7118c33ca5bd1d41`.
Project root: `/workspace/scratch/6416f20dc59b/agent-run-1303`.

| Check | Verdict | Actual evidence and boundary |
| --- | --- | --- |
| Implementation | pass | Read actual source diff, private reviewed proposals and advice CLI. Both installed source files equal their reviewed proposals byte for byte. _fence_transition is the original outside_fences transition extracted verbatim; marker_seen preserves original suppression of invalid backtick opener lines. outside_fences emission, offsets and EOF policy are unchanged. Advice passes physical lines stripped only of CR/LF and retains its independent unclosed-fence/comment refusal. |
| Independent reference/boundary | pass | Manually checked frozen literal chunks/ranges and offsets before baseline and rechecked baseline tracebacks against them. No expectation invokes the helper/renderer. The contiguous fourth marker in the eventual closer is a valid longer fence. Matrices exercise both marker types, supported indentation, non-openers and malformed closers, correction visibility, refusal and exact source sections. CommonMark §§2.2/4.5 were read in plan review; nested containers/HTML/indented headings remain outside scope. |
| Raw integrity | pass | Baseline/fixed/independent log SHA256 values match their metadata; each before/after source/test map is stable. Current candidate source/test hashes match both fixed maps and independently produced maps. Installed test equals the approved frozen fixture. Baseline failures are entirely in the new fence module, with expected hidden CANCEL, missing-topic CLI error, premature-closing/reopening unclosed errors and false acceptance of bad-only closers; no import/timeout/oracle contamination found. |
| Regression/reproduction | pass | Root baseline ran 113 methods with failures=29/errors=25; these include subcases and are not a bug count. Root fixed ran all 113 successfully. Reviewer invoked run_checks.py independent exactly once after fixed.json existed; all 113 succeeded, no failures/errors/skips reported. Real list/select CLI is invoked by that run with PYTHONUTF8=0/PYTHONIOENCODING=cp936, checks UTF-8 JSON/stderr/exit status, exposes CANCEL and retains complete selected Chinese correction text/source bytes. |
| Resources | pass | Baseline subprocess 14.068 seconds; fixed 18.682; independent 12.922. Independent completion at 74.353 seconds from first baseline, within the 120-second subprocess and 600-second branch caps. No retries, full suite, model calls, old probes or old gate resets executed by this reviewer. These times are regression execution records only. |
| Ownership/scope | pass | Both whole-directory guide files retain the pre-execution SHA256 values, GUIDE empty and README unchanged. Observed tracked diff is the two approved source files, single adjacent portable-install CI test step and SYSTEM-99 Version45/stageAA insertion; the installed new test is unchanged. Foreign untracked archive remains outside this work. No old result evidence edited by this reviewer. |

Frozen candidate SHA256:

- agent_runtime/project_docs.py: `245bde4052fc88e5c50f5f59adb7b3eb6437ba4c6fc20e68070fa8cc41d4843d`
- agent_runtime/advice_context.py: `bb049b3a15d2a8d733b4bb53b24d340150dd2c075b80279a6c6776b4cd5cab30`
- tests/test_advice_fence.py: `0fa8899197ecc5cf4e1a314e2cc39504296d090aa6b076f3068a48f707502518`

Raw bindings (same run directory):

| File | SHA256 |
| --- | --- |
| baseline.json | `27ae3f52d3d84dbca4fa24ed1d5e757f08e9705a49318be22f1bc473c9c31cea` |
| baseline.log | `7cab9181b674d131f7b76d68ef9e6aa29cfa67440ccefaab7b914bd426a4cc21` |
| fixed.json | `997eef24386df32111725f59c7d6d1bc0d3f7fae3ff8ab2a0600cf43a8f3450e` |
| fixed.log | `32b39cd5d7bcf6bf2442422e669e066e00fa9e84e56a24308be283fdffe67cfb` |
| independent.json | `f25fb3ce51e5f9e2c840300be2b70d76d3352d8aa7dd033b22710ca9023d5293` |
| independent.log | `b5dea8da6ce5ea6929f0fbc4543027b53399bbb617e56966a4f236b39d6d3986` |

No numerical/performance/model/token/quality inference is made; those empirical checks are inapplicable to this local correctness repair. Tests and static equivalence support only the declared literal H2/top-level fence navigation behavior and named dependent regressions, not arbitrary Markdown conformance or absence of all defects. The independent run repeats the frozen fixtures rather than adding post-result acceptance cases. Actual CI matrix execution, ordinary publication with fresh fetch and exact remote SHA/tree readback remain for the main agent; this report does not claim them completed. SYSTEM-99 and its original unresolved requirements/budgets remain open.

Producer report audit: read agent_doc/results/advice-fence-20261027/report.md and inputs.json. The claimed defect paths, unchanged test, method/subcase distinction, current fixed sources and limited scope agree with actual evidence. All seven copied baseline/fixed/plan/prior-result files equal their private originals, and runner.txt equals the reviewed private runner exactly. runner.txt is a source snapshot, not a relocated executable command; its parent-relative root resolution assumes the original .agent-runs path. The producer's earlier-commit CI/paper-count statements are inherited background, not newly independently measured by this reviewer; candidate CI remains explicitly pending. Final result-review and independent log/metadata still need copying into the producer result directory before publishing its links.
