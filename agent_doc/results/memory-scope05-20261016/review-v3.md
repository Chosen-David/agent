# MEM-SCOPE-05: candidate1 negative data and candidate2 plan review

Two separate decisions:

1. Candidate1 primary data are **usable-with-scope as a negative adoption
   result**. Candidate1 fails its unchanged all-match control gate and must not
   be promoted. This is not acceptance of candidate1 or an independently
   reproduced performance benefit.
2. Candidate2 plan v3 is **adopt / approve for the final bounded attempt**.
   No remaining plan blocker identified. No candidate2 source or benchmark was
   executed by this reviewer. Root remains the sole production/task writer.

This is a manual independent collaboration review, not an authenticated runtime
result-verification or ReviewSession receipt. Previous plan reviews remain intact.

## Exact inspected objects

- Candidate1 actual source SHA256:
  `542e59295a75322e286a4a26d2d5381a8b4916b608497b87119e584d376e99a7`.
- Pinned reference commit: `ab8a368746233996cb39233036a1631de1d911f2`,
  source `c3f41593b64b09d2af190d9ddcb64bbf784720083f4b718a5bdaf5318109f159`.
- Actual runner: `7de92aba6e41d3424352b586f7335faeae754a8b24d415e3a0ffb04a525d5d65`.
- Config: `7d04df14f3fdccb957cc801a502a23a6418ddf99f5e96b8d4d9f3c2bda0ee550`.
- Candidate1 raw-primary.json:
  `5141b31f87a1d28422f6dfbfe507df2a06f0f3e2771095b5134cf36866e90fc2`.
- Complete plan-v3.md:
  `ce221e2092f9d3a83316ec2a69609203be82d693d75664deb4f8074c016bd82c`.
- Canonical TASK after root's new-entry-only newline repair:
  `1d5bf4b4ee4b790d796afd7912b48276f9601b2e969ac7e7a3186e4d1b0f603d`;
  entry words/status unchanged; reviewer read back the same pending SCOPE-05
  entry and observed clean `git diff --check`. Stable detail remains
  `fc3c7270b564e689e88ed1c2e85e5948a531cc4e3461017a5db14430694cd486`.

Read actual candidate1 diff, runner implementation, complete raw JSON through
independent machine parsing, benchmark-primary.log, red.log, targeted.log,
new tests, result_validation_workflow, and complete plan v3. Candidate1 production
diff only broadens the entry predicate by exact builtin-string scope; original
metadata and final filtering code remains unchanged. No timing or full suite
was run by this reviewer; the only new checks were bounded correctness and raw
integrity diagnostics in fresh temporary databases, with no retained production
data changes.

## Independent negative-result verification

| Check | Assessment |
| --- | --- |
| implementation | pass within measured scope: inspected actual source and exact full-list runner; no schema/cache/API modification; source hash matches raw. |
| reference_boundary | pass for bounded checks: pinned base loaded in separate namespace, 120 independent small-fixture full-packet/error comparisons passed across four homogeneous statuses, five query statuses and six scopes. Read main's actual 37-pass log and red four-subtest failure log; these are producer executions, not independently rerun here. |
| data_integrity | pass: config/raw exact equality; seven ordered cases; 21 samples per arm per case; reconstructed seeded orders exact; independently rebuilt all seven fixture SQLite files and matched every DB hash and expected returned count. |
| numerical_sanity | pass: all 294 samples finite positive milliseconds; every median and `1-median(after)/median(before)` recomputed exactly; printed log summaries exactly match raw. |
| measurement_validity | pass for primary warm-local synthetic observation: actual timed entry includes path/connection/transaction/JSON/returned packets; equality checks outside timing; explicit plus correctness prewarming symmetric; fixed random paired order/all samples retained. Virtual-host noise/exclusivity is not removed or claimed absent. |
| reproducibility | pass for this narrow data-integrity/negative-diagnostic scope: independently reconstructed all input hashes, seeded orders, aggregates and 120 small correctness comparisons. No independent timing reproduction was run, so this review cannot certify stable universal regression or positive speedup. |

| Case | Before median ms | After median ms | Time change |
| --- | ---: | ---: | ---: |
| all-active-scope-small | 16.231196 | 4.046352 | -75.070525% |
| all-active-scope-large | 30.556862 | 10.408014 | -65.938865% |
| all-active-all-match | 18.305889 | 21.228612 | +15.966026% |
| all-active-no-scope | 17.182600 | 17.243901 | +0.356762% |
| tiny-all-match | 0.290562 | 0.304002 | +4.625519% |
| mixed-scope-sparse | 3.974135 | 3.997950 | +0.599250% |
| mixed-no-scope | 11.463402 | 11.476652 | +0.115585% |

Both target observations pass >=25%; all-match control exceeds allowed 15%.
Candidate1 therefore fails adoption regardless of other cases. Preserve its
source/patch, raw/logs and failed gate. Do not discard samples, rerun candidate1
until a favorable result, or characterize it as an accepted improvement.

## Candidate2 routing review

v3 adds a general raw-scope heterogeneity check only to the newly enabled
homogeneous-status branch. The original mixed-status predicate must continue to
short-circuit before this added query. The query returns a routing boolean only:

`SELECT 1 FROM entries WHERE scope IS NOT (SELECT scope FROM entries LIMIT 1) LIMIT 1`

For valid uniform raw scopes, every row has the same decoded membership result;
metadata-first decoding cannot select a strict subset, so retaining eager fallback
avoids redundant work without changing valid outputs. Uniform no-match cases
deliberately remain slow. Empty/uniform NULL/BLOB scopes also fall back rather
than using SQL membership; actual JSON decoding/Python membership stay authoritative.
Different JSON encodings of equivalent scopes, or heterogeneous scopes that all
contain the requested key, can still select the new path; v3 correctly does not
claim a complete selectivity estimator or a general no-regression guarantee.

The unindexed guard may scan all N raw scopes for uniform stores. It is O(N),
adds a query, and its practical overhead is still unknown until final measurement.
That uncertainty is properly handled by unchanged primary/independent target
and control gates, not by assuming the guard must solve all-match overhead.
No fixture-name/hash-specific routing is proposed. Existing API/isolated-metadata
contract and arbitrary-corruption exclusions remain binding.

## Seven plan dimensions

| Dimension | Check | Basis |
| --- | --- | --- |
| intent | pass | Same authorized local-ledger goal; no promotion of failed candidate1. |
| guide | pass | No changed guide requirement or guide writes; previous identity remains applicable. |
| assumptions | pass within scope | Conservative raw equality routes only; decoding/membership/filter order unchanged; heterogeneous all-match limitation explicit. |
| prior_results | pass | Candidate1 failed control is valid diagnostic evidence, preserved and used to motivate a new algorithmic guard rather than changed thresholds. |
| acceptance | pass | Same seven fixtures,21 pairs,>=25% targets/<=15% controls, main+independent runs required; candidate2 correctness adds guard branches. |
| risk | pass | No cache/index/schema change; guard is not SQL JSON semantics; unknown overhead must pass unchanged gates. |
| resources | pass | Second/final candidate, same serial CPU policy and original 30-minute validation deadline, approximately00:35UTC; no budget reset or new external resource. |

Before final candidate freeze, root must preserve canonical stable task alignment
with this v3 reconciliation and bind the final exact source/tests/config/runner
identities. Candidate2 must independently check raw-uniform vs raw-different
branches, empty/all/no matches, NULL/BLOB/deep/invalid JSON, all four homogeneous
statuses, base/subclass/status/scope fallbacks, corrections and retained-traceback
writer release. Do not merely keep candidate1's varying-scope structural test:
also prove uniform fallback hydration and mixed-status route preservation.

No remaining blocker to this final bounded attempt. Stop on failed gate,
deadline or exhausted revision count; no threshold relaxation and no candidate3
under this approval. Candidate2 results remain pending until actual independent
code/data review and serialized independent timing acceptance.
