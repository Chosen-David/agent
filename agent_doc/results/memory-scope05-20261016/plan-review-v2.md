# MEM-SCOPE-05 independent follow-up plan review

Decision: **adopt / approve for bounded implementation and validation**.
No remaining blocking finding in the manual plan-review scope. This is not a
performance result, publication acceptance, authenticated ReviewSession receipt,
or grant of new authority. Original v1 review is preserved unchanged.

## Reviewed identity

Read original plan plus complete `plan-v2.md`, canonical MEM-SCOPE-05 stable
detail/index, exact seven-case config, and actual benchmark runner. Rechecked
baseline source and guide bytes; no tests or benchmarks were executed.

| Object | SHA256 |
| --- | --- |
| plan.md v1 | 8a12ab07f19116eca18dc15f000178d90871bbb148ef710e8e1016afbeb27c21 |
| plan-v2.md | 07cf892a84d960de399817ac0c80afc57277dd9a22edb04e8fd136b98809acf5 |
| config.json | 7d04df14f3fdccb957cc801a502a23a6418ddf99f5e96b8d4d9f3c2bda0ee550 |
| scripts/bench_memory_retrieval.py | 7de92aba6e41d3424352b586f7335faeae754a8b24d415e3a0ffb04a525d5d65 |
| agent_doc/task/TASK.md | 6416b646842442b62d0b32bb43fcd92ec35c90e960963ff0db8f77cd1cdbec72 |
| agent_doc/task/task_details/MEM-SCOPE-05.md | fc3c7270b564e689e88ed1c2e85e5948a531cc4e3461017a5db14430694cd486 |
| agent_runtime/project_memory.py baseline | c3f41593b64b09d2af190d9ddcb64bbf784720083f4b718a5bdaf5318109f159 |

Base remains `ab8a368746233996cb39233036a1631de1d911f2`. GUIDE.md is still empty
with SHA256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855;
guide README hash remains f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261.
No human-guide file changed. This review pins actual bytes, not human provenance.

## Closure of v1 findings

- F1 closed: canonical unique MEM-SCOPE-05 index/detail now carries the intended
  newly homogeneous-status path, base, contract, frozen acceptance and single
  source/task/report writer. Previous task states remain distinct. The manual
  review/run limits and absent managed service are explicit.
- F2 closed: API-valid full-packet/order/freshness parity and isolated metadata/
  missing-table probes are now distinguished from arbitrary raw-TEXT/schema and
  injected-hook combinations. Those excluded combinations must remain visible
  limitations, not be counted as successful universal differential checks.
- F3 closed: exact seven fixtures are fixed, two candidate revisions maximum and
  a 30-minute local CPU-validation ceiling are explicit. Both arms use the same
  pinned runner; its aggregation is exactly `1-median(after)/median(before)`.
  Both main and independent runs retain every sample and order, use same input
  hashes, and must satisfy unchanged >=25% target / <=15% control thresholds.

The runner performs one correctness call for each arm before its explicit one
warmup call; therefore the actual premeasurement preparation warms each arm
twice. This is symmetric and acceptable for warm-local-cache claims. Report
that actual behavior rather than asserting only one total premeasurement call.
The final amendment was re-read in full after its update: it now pins runner/
config hashes and aggregation, discloses that warming, provides exclusive pending
output paths, starts the 30-minute ceiling after plan acceptance, clarifies query
limits, and explicitly excludes empty-entry/malformed-document-column schemas.
Phrases about required probes being “tested” or summary math being “checked” in
this prospective plan are not new execution evidence: no experiment has run.
If the 30-minute validation budget or two-candidate ceiling is exhausted, stop
this dependent validation branch without resetting it; retain failed evidence.

The v1 search-hit note is not an actual planner error: root used limit4, whereas
this reviewer independently used limit5. Each count is valid for its own bounded
query; neither is exhaustive. Preserve the exact limit/partial/error context in
final evidence rather than silently reconciling to an invented common result.

## Seven dimensions

| Dimension | Check | Basis |
| --- | --- | --- |
| intent | pass | Authorized local ledger efficiency, parent model-KV/QA task remains incomplete. |
| guide | pass | No substantive empty-GUIDE conflict and no guide mutation. |
| assumptions | pass within scope | Exact built-in guard, no cache/schema change, current baseline oracle, isolated error contract explicit. |
| prior_results | pass | scope02 deferral/known boundaries inform design; old timings not reused as new improvement. |
| acceptance | pass | Full values/order/freshness, error/type/fallback probes, two sparse targets and five controls fixed before results. |
| risk | pass | Excluded arbitrary-corruption errors explicitly bounded; invalid selected metadata remains fail-closed; original mixed-status path must remain unchanged. |
| resources | pass for bounded local work | Fixed 21 pairs, serial main/independent timing, max2 candidates, 30-minute validation ceiling, no paid/model/GPU/service expansion. |

Nonblocking v1 correctness recommendations still apply: test homogeneous
candidate status as well as active, empty/no-match/all-match and missing-table
cases; preserve status/ledger/scope subclass fallback; test held tracebacks with
immediate writers; prove structural hydration reduction on a homogeneous store.
Do not claim stronger concurrent snapshots, O(K) total work, RSS, model TTFT,
token, quality or GPU gains. Any code/contract/config change outside this bounded
reconciliation requires versioned review, not post-result threshold tuning.

Proceed to the authorized red structural test and candidate implementation;
new results remain pending until independent actual-code/data verification.
Root retains publication/CAS/readback responsibility after final regressions.
