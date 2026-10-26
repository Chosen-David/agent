# RESULT-DISPATCH-FRESHNESS-01 independent result review

Decision: **usable-with-scope** for this bounded dispatch-freshness repair. Integrated source, frozen fixtures, raw baseline/fixed evidence, and one independent relevant invocation pass the scoped review. Main retains production/test/TASK ownership; reviewer writes only this assigned private review.

## Integrated source audit

Read actual production diff for result_validation, result_store, task_manifest, and portable-install workflow. Helpers and dispatch block match approved frozen proposal; installed test SHA-256 matches private frozen module `75f32a6bc9ca3a23d7fca236e4ec63887522ee51bf233e27267cfa5252843253`.

The ordering is entry validation → actual prior lookup/review → fresh required-result/reuse independent gates → sole claim-current predicate → passive all-proof/registry/age checks → existing memory/knowledge/document checks → actual handler. Every added verifier callback precedes current. Required-result proofs are rechecked after all reuse callbacks. The existing task copy is taken before those fresh callbacks; fresh/passive dependency checks now use exactly that `dispatched_task`, which the handler receives. This avoids checking dependencies from a callback-mutated original while dispatching a different object. Entry/post-action/report gates remain unchanged.

`_check_validated_bindings` normalizes string/Path roots, verifies bound manifest bytes, all artifact hashes including validation plan, independent review evidence, and current result/run revocation. Run identity is obtained from that bound manifest. It returns metadata internally and grants no independent acceptance. Reuse pins registry SHA to both fresh decision proof and task selection, uses the fresh nested result proof, and obtains measurement completion time from the same hash-bound manifest. Nothing adds a persisted schema, acceptance cache, fake verifier, adapter loading, retry loop or stored-pass authority.

`_measurement_age_reasons` is shared/pure. `decide_run` retains upfront finite/nonnegative age validation, optional now parsing and missing/unbound/no-policy short circuits. The helper preserves future-time rejection, inclusive upper boundary, missing/unbound-time reasons, and rerun precedence. Final reuse recheck captures a fresh wall instant after current and supplies the same policy. Passive I/O is not promised instantaneous; current does not guarantee lease survival after these reads or an atomic external action.

Native workflow diff adds only the new module step; Ubuntu/Windows × Python3.10/3.12 matrix and old steps are unchanged. This is configuration/source inspection, not native4 execution certification.

## Main raw evidence audit

Read complete baseline log and baseline/fixed command metadata, runner and branch-budget file. Baseline command invokes only the frozen new module with explicit PYTHONPATH. It reports 15 methods, 15 ordinary assertion failures, no errors. Expiry/cancel/token subcases each reach the second legitimate verifier and actual invalidated state; old source then has pending work with cumulative calls1/2/3. Required/ref and reuse lookup/current mutations each start work once before post-action rejection. Independent review-only and later-verifier interference cases can return pending after work. Registry/TTL/revocation and cached current changes likewise do not prevent the old handler call. Two unchanged controls fail solely because old source invokes the verifier twice rather than the intentionally required three phases. The age boundary and missing-verifier/current-false methods pass. These phase assertions are not additional runtime defect findings.

Fixed command covers exactly seven relevant modules including the new module and result_store_fd. Metadata exit0 and log show all new methods passing and 138 tests OK in16.011s. The complete fixed log was independently read; it contains 138 individual ok outcomes and no skip/error/failure summaries. Main runner grants no old fullsuite/PID/ALIAS/role/Codex/wire reset and enforces remaining600-second branch window and per-invocation min(180,remaining) timeout. Timeout would preserve branch blocked, not authorize a rerun.

SYSTEM-99 and prior exhausted gates remain open. No model/provider/performance/usage, host deployment, global snapshot, external fencing or final lease guarantee is inferred.


## Independent invocation and final acceptance

After main explicitly confirmed fixed parent exit0 and authorized the single independent invocation, reviewer invoked `python .agent-runs/result-dispatch-0158/run_checks.py independent` once. Actual parent session65100 completed with exit0; runner output reports independent exit0. Preserved independent.json records the same exact seven modules/interpreter/PYTHONPATH as fixed. Complete independent.log was read: **138 tests OK**, no skips, failures or errors,18.377s. The recorded branch600-second window had elapsed156.125s at the post-run audit, so this invocation finished within the original window and its180-second cap. These durations are budget/completion evidence, not performance findings. No additional tests, reruns, import probes, providers or fullsuite were invoked.

Before/after SHA-256 were identical for all production files, frozen regression, native workflow and runner:

| Path | SHA-256 |
| --- | --- |
| agent_runtime/result_validation.py | `94e4e79eb3022e47169f6fa2d85022a59bdd2dddce59f979cf42b43fc1fdf228` |
| agent_runtime/result_store.py | `d4d76e7bf286375b01d0b024d4c22bd67d0abcce643acce4eb288809a3540aae` |
| agent_runtime/task_manifest.py | `69c4fe53bf09b101bdffda7e5a3d9a8b3a71ba40ddc25174402c2b7260979425` |
| tests/test_result_dispatch_freshness.py | `75f32a6bc9ca3a23d7fca236e4ec63887522ee51bf233e27267cfa5252843253` |
| .github/workflows/portable-install.yml | `29e04cf45cfa2100202f6b7fa1354022d1d64c9d594c25829d8b7326f3b5b777` |
| .agent-runs/result-dispatch-0158/run_checks.py | `8d825b10515e90dbb0fec9e66ea0ee7a943137260e3bce9b2c40df86059434aa` |

Acceptance is limited to the declared synchronous lookup/current/verifier mutation windows and captured evidence/registry/age bindings exercised by these local CPU fixtures. New negative cases now block before pending work, actual Context expiry/cancel/token loss is checked after late verification, unchanged controls permit work, and prior scientific/reuse/FD refusal contracts pass the relevant suite. Hashes alone are not scientific acceptance; actual independent arithmetic/data/boundary verifier fixtures were inspected and executed by those tests.

No blocking finding remains in this production candidate. Original naive insertion remains historical REVISE; original negative diagnosis and this new baseline remain unchanged. This does not complete SYSTEM-99, repeat old exhausted gates, certify native4 jobs, review new task/publication documents, prove real host/model behavior, or guarantee a globally atomic snapshot/action or lease survival after arbitrary passive I/O. Main owns remaining documentation, publication checks, ordinary freshfetch/CAS/readback and truthful final reporting. Reviewer edited no production, test, guide, TASK or historical evidence files.

## Documentary audit of proposed public evidence / SYSTEM-99 v44

Read draft `agent_doc/results/result-dispatch-fix-20261027/report.md` and `inputs.json`, and the v44 stable-Plan continuation plus new Progress entry in SYSTEM-99. **No blocking documentary issue found.** The report accurately separates the original rejected insertion/negative diagnosis, new15-method baseline with15 ordinary assertion failures (including subcases and deliberate phase controls), and fixed/independent138-test passes. It limits acceptance to live callback ordering and passive captured bindings, states no post-I/O lease/global snapshot/action fence guarantee, leaves native4 readback separate, and makes no model/performance/whole-batch claim. SYSTEM-99 v44 and the new Progress entry retain old gates open and body count14. Older historical entries remain correctly historical rather than rewritten as present failures.

Independently recomputed every nine `inputs.json` current source/prior-evidence binding: all match. Recomputed the three original-production hashes directly from the named base commit `f8033083dbacbb331f16a9f028dc964f6c35790d`: all match. Compared the eight copied public plan/review/log/metadata artifacts (baseline/fixed/independent raw logs+JSON, plan-v3, plan-review) to their private originals: all byte-identical. The finalized result-review file is intentionally to be copied by main after this addendum; no final-copy byte-equality claim is made here. No test invocation or production/task/public-report modification occurred in this documentary audit. Main owns nativeCI/publication verification and final exact review copy.
