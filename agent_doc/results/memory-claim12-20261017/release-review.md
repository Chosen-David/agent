# Independent release review — MEM-CLAIM-12

Decision: **approve** the inspected implementation, regression evidence, archive and report for final manifest/registration/staging preparation. This approval does not assert a future staged tree, commit, push or remote readback already exists. Final exact metadata/hash confirmation and publication remain root-owned.

## Actual final integration checks

Read the actual private regression_runner.py, final-regression.json, tests-full.log and apps-paper-reader-tests-full.log. The runner discovers test*.py in each target directory, executes real unittest suites serially, stores failures/errors/skips/counts and checks production source before and after. Raw log confirms1243 repository tests,8 skips, no failures/errors; Reader confirms3 tests, no failures/errors. The JSON records69.986s/1.577s total wall time; raw runner test times69.760s/1.567s are narrower unittest intervals, not a contradiction. Inspected all3 private log paths, byte counts and SHA256 bindings in integration-log-index.json; all match, including the empty final-runner stdout log. Logs are expressly indexed as private/unarchived, not misrepresented as public raw-log copies.

Production source remains SHA256 `6e1057ce0c76d576898996011bb5ec39a6acad4b821388954a143c9d33fe0aaa`; permanent tests remain SHA256 `62007760eb224330b241bec37ac87f88c722bbebbde6f4299fe1fbb648081f1f`. These match the independently accepted source/test versions. Four permanent tests cover deep identity/nonmutation, invalid dependencies, custom operation traces and multi-error behavior. Prior ordinary/-O unittest evidence is retained; no redundant performance or full-suite repetition was needed. git diff --check passed.

## Archive and public claims

Compared every public archive file that has a corresponding private run artifact: **25 byte-for-byte matches**, consisting of the24 frozen input/evidence artifacts plus final-regression.json. Public-only report.md and integration-log-index.json were separately inspected. This count is based on actual files rather than assuming the handoff's archive count. Original private-reference strings in immutable files remain historical identity/navigation; current public manifest must bind their real public copies, not claim those strings are relocatable paths.

Read Chinese report.md against raw producer/independent/analysis evidence. All six rounded percentages and independent millisecond medians agree with the independently recomputed data. Chain/shared traced peak increases67016/32904 bytes and invalid fallback regressions6.20%/5.12%/3.84% are disclosed accurately. Five non-primary controls includes shared256; all meet the frozen15% threshold. Environment.json supports the additional CPU model/visible9-CPU details. Shared CPU/no affinity or frequency isolation, Python allocations rather than RSS/VRAM, synthetic full claim_graph rather than full Mailbox/request or model KV/QA/TTFT, no universal speedup, unknown production graph frequency and open parent scope are explicit. Plan revisions, late six-criterion projection and reviewer harness failures are preserved rather than rewritten as clean original passes.

Reproduction instructions correctly copy baseline.py and unmodified check.py into `.agent-runs/claim12-replay/` before execution. At this depth check.py's RUN.parents[1] resolves to the repository root, so its original path assumption is satisfied. Instructions require matching current production source SHA before replay and keep serialization/construction outside timed calls. Other frozen reviewer scripts preserve their historical placement assumptions; the report does not claim they are directly executable from the public archive directory.

## Scope and publication boundary

Inspected git diff and status: source adds the compact residual helper and guarded loop; new permanent test file is the previously reviewed four-test file. Canonical MEM-STORAGE-01 changes only append9 lines under Progress; existing stable Plan, TASK index and guide are unchanged. The append preserves the parent task's open state and scoped evidence/remaining work. No other repository, guide edits, alternative active TASK list, hidden performance claim or unrelated source change appears in the inspected diff/status.

Accepted experiment evidence remains **usable-with-scope**, with six-criterion independent review already in independent-review.md. No managed ReviewSession, deployed verifier, monitor or service is claimed. Root may now generate manifest/registration metadata, stage only owned scoped files and provide the exact staged tree/metadata for final confirmation. Fresh fetch/integration, nonforce main publication and actual remote SHA/tree/content readback remain required; this file does not pre-certify those future actions.

## Reviewed artifact hashes

- `agent_runtime/handoff_basis.py` — `6e1057ce0c76d576898996011bb5ec39a6acad4b821388954a143c9d33fe0aaa`
- `tests/test_claim_graph_residual.py` — `62007760eb224330b241bec37ac87f88c722bbebbde6f4299fe1fbb648081f1f`
- `agent_doc/task/task_details/MEM-STORAGE-01.md` — `1d0ccd5ba6cf65b9cb7176875e32462b547738dcfaf1f1a08eb4d3860fc40a34`
- `agent_doc/results/memory-claim12-20261017/report.md` — `8554e67a93c20a7e73b7b453a32e2b95f1f5803f54426dc0380076ccefa96a09`
- `agent_doc/results/memory-claim12-20261017/final-regression.json` — `23315ddb72eb7ef60d9ba58c2791202877fb1985a67cbe4fb9de3bd6ffd618f1`
- `agent_doc/results/memory-claim12-20261017/integration-log-index.json` — `9ff07da592cd06339a67753270bede65a32078624023572d97c1a76f9ef6e30b`
- `agent_doc/results/memory-claim12-20261017/independent-review.md` — `9eb7498d129f79b8518e24214911a31203bf4b8523b2afe2483333ddd8edefb1`
- `.agent-runs/memory-claim12-20261017-0802/regression_runner.py` — `38165385d048c15eb77a9223e5b897fced5d56edc4c24a1be0b1734ba79565b2`
