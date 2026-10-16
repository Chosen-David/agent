# MEM-SCOPE-05 independent plan review

Decision: **revise**. The optimization itself is reasonable and no API-valid
semantic blocker was found by static inspection. Close the bounded plan issues
below before implementation/timing; this is not a rejection of scope pruning.
No production edits, tests, or benchmarks were performed by this reviewer.

This was a separate manual fresh collaboration context, not an authenticated
ReviewSession or managed runtime approval. It does not authorize publication or
replace independent code/data acceptance.

## Exact object and reading

Reviewed `.agent-runs/memory-scope05-20261016/plan.md` in full, SHA256
`8a12ab07f19116eca18dc15f000178d90871bbb148ef710e8e1016afbeb27c21`.
HEAD is `ab8a368746233996cb39233036a1631de1d911f2` and actual
`agent_runtime/project_memory.py` SHA256 is
`c3f41593b64b09d2af190d9ddcb64bbf784720083f4b718a5bdaf5318109f159`, matching
the plan. Worktree was clean at readback. Read AGENTS, decision_review,
project_document_workflow, dual_main_workflow, review_main, result_reuse_workflow,
causal_task_orchestration_workflow, actual list/_get/_connect/add/revise paths,
all current test_memory_retrieval.py and benchmark runner, canonical TASK,
MEM-STORAGE-01 and MEM-SCOPE-02 details, scope02 report/independent review and
check03/check04 reports. GUIDE.md exists and is zero bytes; its SHA256 is
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
The guide README explains authority/protection rather than adding a substantive
optimization requirement. No guide file was written.

Independent discovery repeated the plan's ResultStore query, limit5/max_scan200:
`memory all active scope hydration`. Actual hits are check03, scope02, and three
unrelated combined-corpus entries, not two as written in plan v1. Partial=true;
the CLI listed missing-record errors, so this is not exhaustive history. The
first two stored validations remain unknown and applicability unchecked. Reuse
their implementation history/design only, not old metrics as new evidence.
scope02 explicitly deferred all-active optimization and documents the arbitrary
corruption exclusion. Knowledge search reproduced snapshot
`767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18` and lone
ds.segment-monoid hit; reject it as inapplicable. No scientific theorem is needed
for this conventional metadata-first implementation. Papers were not re-read
by this plan reviewer, and no new literature claims are certified here.

## Seven dimensions

| Dimension | Check | Assessment |
| --- | --- | --- |
| intent | pass | Fits authorized local memory efficiency work and keeps parent real-model KV/QA work unfinished. Direct main remains conditional on acceptance/readback. |
| guide | pass | Empty GUIDE supplies no additional substantive requirement; human-only directory is preserved. Do not infer human provenance or approval from file existence. |
| assumptions | pass within stated scope | Exact built-in class/status/scope guards, existing Python decoding and single transaction support valid-data parity. Broadened branch also applies to all-candidate and other homogeneous-status stores, not only all-active. |
| prior_results | pass with factual correction | Relevant scope02 deferral and known negative/error history were inspected. No old timing can validate a newly enabled branch; query description needs its fifth hit corrected. |
| acceptance | fail pending closure | Thresholds and current baseline are sensible, but mixed arbitrary-corruption combinations need an explicit oracle boundary and the active task must carry this candidate's stable acceptance. |
| risk | pass with bounded exclusions | No cache/schema/API change. Newly skipped raw fields and malformed schema can change errors; valid-data and isolated metadata regression guarantees must not be phrased as universal corruption equivalence. |
| resources | unknown pending closure | Single CPU/serial timing/21 pairs/two candidate revisions bound work structurally, but no total elapsed budget or exact frozen case configuration is supplied. |

## Findings and minimal closure

### F1 — blocking: stable task/authority binding is absent

Target: plan v1 and canonical `agent_doc/task/TASK.md` / assigned stable detail.

The canonical index has MEM-STORAGE-01, SCOPE-02, CHECK-03 and CHECK-04 but no
MEM-SCOPE-05. The parent stable plan describes the first mixed-status phase;
Progress cannot silently expand that stable scope to the newly enabled branch.
The scratch plan has no pinned index/detail/guide/adopted-advice identity or
explicit no-relevant-advice disposition. This is a manual workflow, so an
executable DAG/authenticated receipt is not demanded or fabricated, but the
single-task-truth requirement still applies.

Requested change: root serially adds the authorized candidate as a distinct
stable task/detail (or explicitly versions the parent stable Plan), links the
candidate plan and evidence ownership, and records current document hashes and
advice applicability. Preserve all old task states and guide bytes. Acceptance:
readback of canonical task/detail maps this exact candidate, correctness scope,
thresholds, budgets, publication gate and owners without conflicting task truth.

### F2 — blocking plan ambiguity: distinguish supported parity from exploration

Target: Contract and Correctness paragraphs.

The valid API-data claim is sound in principle. However, the broad list of
malformed metadata/schema cases plus “first error ordering” can be read as
requiring parity for combinations the optimization deliberately cannot preserve.
For example, eager hydration of an earlier row with invalid raw TEXT bytes can
fail before later malformed scope/document JSON; metadata-first decoding can
reverse that order. A selected null scope may likewise become the first error
before a later raw-content read that eager performed first. A malformed document
table can fail at joined SQL compilation, even for an empty entries table where
eager never called _get. These are static code-path observations, not executed
test results, and are not grounds to require universal corruption parity.

Requested change: version the contract to guarantee complete packet/order/fresh
objects for API-created valid ledgers, plus explicitly enumerated isolated
scope/document metadata and missing-table regressions. Specify that combinations
with arbitrary raw TEXT/schema corruption or injected _get behavior are
exploratory boundary probes, not an equality oracle. Keep invalid selected
metadata fail-closed, existing mixed-status behavior unchanged, and do not hide
new discrepancies by broad exception fallback. Acceptance: differential suite
labels these two groups separately, records every observed discrepancy, and no
supported guarantee is weakened after results. If real application requirements
demand excluded corruption parity, reject the optimization instead.

### F3 — blocking before timing: freeze resource and fixture details

Target: Required sequence / Benchmark.

Requested change: add a finite total local elapsed budget and stop policy, then
freeze a config with exact entries/active/content_bytes/match_every/scope for
all seven cases, baseline/source hashes, seed/repeats, aggregation formula
`1 - median(after)/median(before)`, and runner hash. Count every attempted
candidate within max2; do not refresh budget or thresholds on failed results.
If using the existing runner, disclose that correctness calls also warm paths
before its explicit one warmup. No new timer or GC policy is required, but both
runs must use the same frozen policy, remain serial, retain all samples, and
compare the same current-baseline packets. Acceptance: readback before any
measurement fixes these values and the private pending-result output paths.

## Nonblocking independent correctness recommendations

- Red structural test must actually use a homogeneous store and demonstrate
  fewer _get calls; current mixed-status fixture cannot prove the new branch.
- Include homogeneous candidate status and query statuses with no rows, empty
  ledger, no matches, all matches, tied created_at/id, and fresh mutation-proof
  packets. Broadening by built-in scope is not literally active-only.
- Missing dependencies/columns must retain fallback including no matches;
  legacy absent document table must remain supported. Probe isolated invalid
  scope/document BLOB/deep JSON both before and after selected rows, retaining
  traceback and checking immediate writer success.
- Preserve all mixed-status scope02 checks using the current pinned baseline,
  not solely the older eager oracle. Current tests call eager; new independent
  differential tests must not falsely require old corruption behavior already
  excluded by scope02.
- For an empty ledger, malformed document schema can newly error during the
  metadata JOIN; either conservatively guard the new path or explicitly retain
  this outside-supported-schema limitation before freeze. Do not choose after
  seeing benchmarks.
- Returning API-valid packets still involves O(N) decoded metadata and selected
  re-decoding. Do not infer peak memory/RSS gains or O(K) total complexity.

## Compact verdict

decision=revise; recommended disposition=adapt.
No intrinsic API-valid semantic blocker identified; F1/F2 must be reconciled
before source edits, F3 frozen before timing. This single review is not a managed
approval receipt. Root owns any versioned plan repair, source/tests/tasks/report
and publication; reviewer owns only this file. No benchmark or production edit
has been authorized by this review itself.
