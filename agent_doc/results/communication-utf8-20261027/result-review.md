# Independent result review — COMMUNICATION-UTF8-01 v1

Decision: **usable-with-scope** for the local UTF-8 transport fix and frozen targeted regression set. No blocking findings. This is an actual independent code/log review plus one independent run, not a protected ReviewSession authentication/deployment claim.

## Actual work and frozen identities

Read actual installed source/test, helper, fixture, producer metadata and logs, CI diff and Version46 stable-plan diff. Reviewed candidate source SHA-256 is `6ba4e5b12e92e3fb70c7ad21a105d9fc33b6083e47ecf3eb957a0eea5e6afd59`, exactly the approved proposal. Installed test is `d071609898540a32edc3885e3a479933988d3f6715e31cb2fa5d65964469fd74`; runner is `1e495e0077f2e68c3807266878845c67f774e05338986be54bb3fa85f50f5160`, both unchanged from plan review. Plan remains `2563788e16d9ac81d0bbeef9d67bde5380b5138f5c2114d597fe44f97876f853`.

The production diff is exactly the existing configure_utf8_output import and main-entry call. Native CI adds exactly one discovery step for installed `tests/test_communication_output.py`; resulting workflow hash is `1c92830684b80f4589124a6baf41779e4ac5fe72850baf5c5f2cb80ee07d42a8`. Matrix and other steps remain unchanged. SYSTEM-99 changes version45→46 and adds the reviewed stageAB stable paragraph; no old gate is reopened. Source-location cwd/PYTHONPATH and baseline stack paths confirm the real installed test and repository module were executed, rather than the private proposal copy.

Unchanged helper hash: `2606666cf723af13cb2b8a4a0934848f233ffb16c50728fc4a43da01ff26453d`; unchanged shared fixture: `232f4bad46429e8408c902ff486bb8023fde7b0715f9b233cb3a522b1293f442`. GUIDE.md remains empty with `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; git diff shows no guide/helper/fixture changes. No foreign zip was touched by this reviewer.

## Observed executions

| Run | Result | Runner elapsed | Shared branch elapsed at finish | Raw log SHA-256 |
|---|---|---:|---:|---|
| producer baseline | 80 methods; 24 failed subcases, no errors/skips; exit1 | 31.790257s | 31.790416s | `03d4ec7a10365d0382ccc9cb77dbee07bd9bc3d8ef631f3437eab94a7c54d39e` |
| producer fixed | 80 methods pass, no skips; exit0 | 30.454850s | 73.749809s | `e098633287f45de41e6573c7cb25a16fb5ed04c00f7e3ca0b664a1bc465a13c1` |
| reviewer independent | 80 methods pass, no skips; exit0 | 23.703562s | 102.124598s | `63cdbe021e20d0209aeaab7623d792da48dcc9a873dbb5a94162140a6ac2b917` |

I launched exactly once, after fixed.json was finalized:

`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python -B .agent-runs/communication-utf8-0703/run_checks.py independent`

The frozen runner invoked the same eleven installed unittest modules listed in the plan. Independent metadata SHA-256 is `5d2c00260174c4cb80193f742c132a2a10e85159d8ff6d90dc749a224678ceee`; producer baseline/fixed metadata hashes are `d4f46e5d564af87716a343fb32779fa8a20152d6b8a0ed75cead001f6c87500c` and `6ea0353bd9bbecb468648771105d04f3a40b0ef96cd39dfa5378903cda3d0c69`. Actual raw-log hashes match metadata. Before/after code/test/fixture/helper/CI hashes remain stable in each invocation. Independent execution finished at 102.125 seconds of the original 600-second branch budget; no reset, retry, extra full suite or old gate invocation occurred. Elapsed values are budget bookkeeping, not performance comparisons.

## Correctness and contextual validity

Baseline produced 24 ordinary failing subcases across all three new methods: eight consume/context, twelve Unicode read/status, and four Unicode-error cases. The four ASCII-index controls did not fail. The success-path traces point to communication.main's original print with gbk/ascii UnicodeEncodeError. In all eight consume/context baseline traces, failure occurs at test line91 `output = self.decode(run)`: the earlier row existence, full persisted record/request, unchanged receipts and unchanged source-file assertions had already passed. Thus the evidence supports the specifically claimed failure after validated basis persistence, without treating persistence as ACK, dispatched model input or external effect. Read/error baseline traces likewise occur after their DB/file invariance checks. Duplicate-key error stderr is abbreviated by unittest's assertion display; preserve that raw log as observed and do not claim a complete standalone child-stderr recording.

The unchanged test now passes all 28 new CLI combinations in both fixed runs. It captures native bytes under PYTHONUTF8=0 and cp936/ascii, checks return/empty-stderr/UTF-8 JSON, and checks full event/status/manifest or complete parsed basis payload against independent fixture/literal expectations. JSON comparison accommodates LF/CRLF and whitespace; it does not establish identical raw pretty/compact text bytes or fully compare every context wrapper metadata field. State assertions separately verify unchanged receipts/source JSON, full persisted consumption record/request, and logical SQLite read/error invariance. Expected successful output cannot be rescued by lossy encoding or Unicode escaping changes because the production serializers were unchanged and JSON values are compared. The original Unicode duplicate-key error JSON, exit1 and empty stderr all pass after the fix.

The surrounding 77 existing methods pass in baseline and fixed runs, covering handoff provenance/consumer scope, duplicate/batch/usage/route/budget behavior, snapshots and knowledge/memory dependencies. They are bounded regressions, not a proof of unrestricted correctness. The two-line fix changes terminal encoding only and does not reinterpret stored basis/receipt semantics, relax budgets or change schemas.

## Six validation domains and limits

- Implementation: pass; actual diff, hashes, invocation paths and error/success branches reviewed, with independent execution.
- Reference/boundary: pass within scope; independent fixture/literal Unicode values, ASCII-index control, both layouts/encodings and duplicate-key rejection; unrelated encodings/commands are not exhaustively tested.
- Data integrity: pass; exact frozen test/runner, raw hash bindings, retained baseline failure, same module set, no skips, state assertions and pre/post source hashes.
- Numerical sanity: pass for discrete counts/invariants; 28 CLI combinations and 80 methods correctly distinguished from 24 baseline failure subcases; none are defect or model-sample counts.
- Measurement validity: not applicable to performance/quality, as predeclared; runtime durations enforce budgets only. No statistical, speed, token, cost or model-quality inference.
- Reproducibility: pass for the same local environment; one real independent fixed invocation completed. Native Ubuntu/Windows ×3.10/3.12 CI remains **separately pending**, and must be checked from actual new jobs rather than inferred from these Linux results or old CI.

Prior search remains partial with errors and no empirical reuse. Historical registration must remain unknown/untrusted; this review does not fabricate a machine-authenticated experiment contract. Ordinary publication, fresh remote integration/readback and new native CI are the main owner's next actions under existing authorization. SYSTEM-99, full-library/host/task-quality gaps and all old exhausted gates remain open/unchanged. No new paper credit, global completion, model-quality, performance, real-runtime deployment or round-completion claim is accepted.

## Producer report check

Also read the producer's `agent_doc/results/communication-utf8-20261027/report.md` and `inputs.json` after the independent run. Their bounded claims match the observed tests, frozen source hashes and this review: the context payload/wrapper distinction, persistence versus semantic completion, partial prior query, separate native CI and retained SYSTEM-99 blockers are explicit. The runner snapshot is correctly described as execution code archived from its original private location, not a relocated runnable entry. No report-scope correction is required. This acceptance applies to this reviewed draft; subsequent claims of native CI or remote publication require actual new readback.
