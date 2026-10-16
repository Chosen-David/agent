# MEM-SCOPE-05 independent code/data verification

Verdict: **usable-with-scope** for candidate2's frozen local SQLite retrieval
change, bounded semantic checks, and the seven synthetic warm-local timing
fixtures. Both target gates and all five control gates pass in the primary and
single independent runs. No blocking finding remains within this scope.

This is a real separate collaboration-context review by
`memory_scope05_result_verify`, not an authenticated `ReviewSession`, native
`verify_experiment_result` receipt, deployed supervisor, or publication approval.
Root owns source/tests/tasks/reports/publication; this reviewer wrote only its
assigned review/evidence paths. No candidate revision or timing retry was made.
The original approximately00:05–00:35UTC budget and final-candidate limit apply.

## Frozen identities and prior evidence

| Object | SHA256 / revision |
| --- | --- |
| Reference Git commit | ab8a368746233996cb39233036a1631de1d911f2 |
| Reference project_memory.py | c3f41593b64b09d2af190d9ddcb64bbf784720083f4b718a5bdaf5318109f159 |
| Candidate2 project_memory.py | 2f2b7b9c439333438be982a8200d0ed213352c76707d2b07454b113855821e98 |
| Retrieval tests | 1bf7745339740cb4a896467f1691a304eb88debba40a755282bb1f9734d66ebd |
| Original benchmark runner | 7de92aba6e41d3424352b586f7335faeae754a8b24d415e3a0ffb04a525d5d65 |
| Config | 7d04df14f3fdccb957cc801a502a23a6418ddf99f5e96b8d4d9f3c2bda0ee550 |
| Plan v3 amendment | ce221e2092f9d3a83316ec2a69609203be82d693d75664deb4f8074c016bd82c |
| Canonical detail, full bytes at review | ff68d19b81c1bb863e6610355948064231f7d1306e31fcda6cc9ffeb3f9b13f5 |
| Canonical detail, stable Plan via project_docs | 8a577496224dbba818f21f42e2c4fc116f94e4ff923c756c78d6b3df116c87f5 |
| Primary candidate2 raw | 96b717f71c27803207cf93fb2d156f511b137466705e00ebbf2ea79f1d365180 |
| Independent candidate2 raw | ebed6d71af00497bbb3075a89fdff0f216555add04bd5e0fd0900d094a2ec2fb |
| Independent executable check | a1313ec95eae12ae6ce08a48452bf68c7fb8c8297c0cf03ec4dd71adc64972ba |
| Independent generated checks | df913ae4346a0755ef7168f3764819bd0727101aa03dc569b48e67d51cc9a471 |

Read AGENTS, decision-review, result-validation/reuse, project-document/memory,
and knowledge-access governance; original/v2/v3 plans; both prior review
amendments; canonical task/index; actual candidate and pinned reference source;
runner/config; complete raw JSON through independent parsing; production
connection, hydration, membership, correction, acceptance and CLI paths.
The CLI's list branch directly invokes `MemoryLedger.list`; task memory validity
consumers invoke the unchanged `check` path, not this retrieval optimization.
`project_docs.guard_write_path` remains in the timed connection path.

Independently executed prior-result search before new checks:
`python scripts/result_store.py --root REPO search 'memory all active scope hydration' --limit 5 --max-scan 200`.
It scanned200, was partial, and reported60 missing-record errors. Relevant
scope02/check03 records were historical/unchecked; three corpus hits were
irrelevant. Read scope02's actual independent report: it explicitly defers
all-active optimization. Its older source/baseline/config are not this run and
its timings were not reused. No mathematical/scientific knowledge theorem is
needed for this implementation/data review; historical paper claims are not
revalidated here.

Candidate1 remains a rejected negative observation: retained raw SHA256
5141b31f87a1d28422f6dfbfe507df2a06f0f3e2771095b5134cf36866e90fc2
and prior review document its +15.966026% all-match regression against the
unchanged15% gate. Candidate2 acceptance neither deletes nor promotes that run.

## Six required validation criteria

1. **implementation — pass within scope.** Independently read actual source,
   not just a patch/pass label. Only the entry predicate changes: the old
   mixed-status query still short-circuits first; newly homogeneous stores need
   exact built-in string scope and heterogeneous raw scope values. Raw `IS NOT`
   controls routing only; Python JSON decoding and membership remain decisive.
   The same ordered metadata decode, selected-ID hydration, final filter,
   transaction and close/finally execute. No cache, migration, index, API,
   correction, acceptance, validity-check or permission change exists.
   Exact source hashes matched before and after independently executing checks.
2. **reference_boundary — pass within scope.** An independently written check
   compiles the exact current pinned base in its own namespace, preserving its
   actual `type(self) is MemoryLedger` behavior. It performs **10,021 complete
   packet/error/subclass outcome comparisons**, plus72 writer checks,4 structural
   hydration checks and1 bounded SQL NULL/BLOB truth-table check: **10,098 total**,
   zero failures. Coverage includes0/1/4 rows; four homogeneous statuses and mixed
   statuses; status=all/unknown/None/string subclass; built-in/nonbuilt-in scopes;
   T1/T10/substrings/empty/no match; uniform/mixed raw scopes; dependencies,
   tied sorting and complete document JSON packets; public accept/correct and
   invalidation; mutation of returned lists/content/deps followed by fresh reads.
   Isolated scope/document null/number/bool/string/dict/list/malformed/UTF8-BLOB/
   deep JSON match class-name and message. Later bad scope/document JSON wins
   over early selected-null membership errors. Missing document table and
   missing/renamed dependency columns, including empty/no-selection, match.
   Retained candidate errors allow immediate writers; exact-base structural
   checks prove only matching IDs hydrate for heterogeneous homogeneous/mixed
   stores and all IDs hydrate for uniform all-match/no-match fallback.
   Independently reran15 retrieval tests and15 project-memory tests:30pass,
   no skips. Their document snapshot checks cover public bound-memory behavior.
3. **data_integrity — pass.** Independently parsed both complete raw files;
   every one of seven ordered cases matches every frozen config field. Both
   arms have21 samples per case and21 valid paired orders. Recreated the seeded
   RNG sequence exactly, reconstructed all seven SQLite fixture files per run,
   and matched every full-database hash. Returned counts independently compute
   to20,20,2000,2000,8,10,1000. Source/config/reference identities match; database
   construction and complete output equality checks are outside timing; the
   runner rehashes unchanged DB bytes after measurement. No samples are dropped.
4. **numerical_sanity — pass.** All294 samples per run are finite positive
   milliseconds. Independently recomputed every median and exactly
   `1-median(after_ms)/median(before_ms)` with equality to stored aggregates.
   Both target reductions exceed25%; every control reduction is at least-15%
   in both runs. Raw min/max ranges are retained in `reviewer/checks-v2.json`;
   there is visible timing variation, not an invented noise-free result.
5. **measurement_validity — pass for the stated local warm synthetic scope.**
   Actual `perf_counter_ns` timing includes full list invocation, path validation,
   SQLite connect/transaction, routing query, metadata decode, hydration, final
   complete list assembly and close. It excludes fixture creation, expected
   comparison and hashes. Each arm gets a correctness call then one explicit
   warmup, so both are actually prewarmed twice. Seed51610 fixes all21 paired
   random orders. Before-first counts across seven fixtures are11/12/11/8/12/9/11;
   the complement is after-first, with no post-hoc balancing. Root explicitly
   confirmed full-suite completion/no owned timing before the independent run;
   independent timing began00:11:11UTC and finished before subsequent correctness
   checks. No tests/fixture reconstructions ran concurrently with that timing.
   Host-global isolation and CPU pinning are not established or claimed.
6. **reproducibility — pass within scope.** Independently invoked the same frozen
   runner/config exactly once, using new temporary databases and exclusive
   `reviewer/raw-independent-v2.json` creation. The separate observations pass
   all original gates and reproduce the target effect without selecting a best
   run. Both environments identify Python3.12.14, Clang22.1.3, SQLite3.53.1,
   Linux6.18.44/x86_64/glibc2.39. Host readback exposes9 vCPUs, AMD EPYC9V74,
   KVM; `reviewer/host-cpu.txt` preserves that observation, not dedicated-host
   ownership. `reviewer/hashbindings.json` binds execution dependencies and raw
   evidence. No second performance run, tuning or threshold adjustment occurred.

## Timing readback

Positive change means slower; negative means less elapsed time.

| Fixed case | Primary change | Independent before ms | Independent after ms | Independent change |
| --- | ---: | ---: | ---: | ---: |
| all-active-scope-small | -74.6861% | 16.356241 | 4.073231 | -75.0968% |
| all-active-scope-large | -65.7524% | 31.609342 | 11.002417 | -65.1925% |
| all-active-all-match | +1.2756% | 17.017209 | 17.154463 | +0.8066% |
| all-active-no-scope | +1.1868% | 17.167131 | 17.166810 | -0.0019% |
| tiny-all-match | -1.7491% | 0.296311 | 0.300226 | +1.3212% |
| mixed-scope-sparse | -0.7920% | 3.801266 | 3.923118 | +3.2056% |
| mixed-no-scope | -0.6831% | 11.338302 | 11.327295 | -0.0971% |

Tiny/mixed control changes are not interpreted as reliable improvements.

## Exact independent commands

```bash
PYTHONPATH=. python scripts/bench_memory_retrieval.py --config .agent-runs/memory-scope05-20261016/config.json --output .agent-runs/memory-scope05-20261016/reviewer/raw-independent-v2.json
PYTHONPATH=. python .agent-runs/memory-scope05-20261016/reviewer/independent_check.py --root REPO --evidence-dir REPO/.agent-runs/memory-scope05-20261016
python -m unittest discover -s tests -p test_memory_retrieval.py -v
python -m unittest discover -s tests -p test_project_memory.py -v
```

`REPO` means the absolute repository root. After archival, the same independent
check accepts `--evidence-dir REPO/agent_doc/results/memory-scope05-20261016`;
it does not depend on `.agent-runs` directory depth. The JSON output preserves
the actual measured/read paths rather than pretending historical paths changed.

Read root's actual complete regression tails:1205tests/63.164s/8skips,
Reader3tests/1.569s/pass, and project-document validation snapshot. These are
root executions, not this reviewer's independently rerun full suite. The stable
canonical Plan-only hash matches v3; full detail and index were pending at review,
so root still owns final progress reconciliation and publication byte readback.
The human guide hashes match prior review and no guide file was changed here.

Read root's drafted public `agent_doc/results/memory-scope05-20261016/report.md`
against actual raw/checks. Its seven-case numbers, input hashes,16-to1 structural
distinction versus2000/20 timed fixtures,10098 total-check wording, failed
candidate1,38 ordinary/optimized producer tests, remaining parent work, corruption
exclusion and no-model/RSS/TTFT boundaries agree with inspected evidence. This
does not independently validate its external paper claims or publication state.

## Explicit exclusions and remaining limitations

The contract excluded arbitrary raw-TEXT/schema and injected-`_get` combinations
**before** tests. One separate exploratory probe intentionally makes unmatched
content invalid UTF8: base raises `MemoryError`, candidate returns the matching
packets because it does not read that content. Its actual outcomes are retained
under `exploratory_excluded`, not counted as a successful parity check. Arbitrary
malformed document columns, empty-entry malformed document schema, and NULL scope
requiring a non-API relaxed NOT-NULL schema are not universal parity promises.
The SQL NULL/BLOB check only validates conservative routing logic; it is not a
claim of supporting NULL scopes through the public API. No injected-hook combined
error-priority guarantee is inferred. Selected bad scope/document metadata is
not silently ignored in the tested supported schemas.

The guard is not a complete selectivity estimate: heterogeneous raw encodings
can all decode to matching scopes and still take the new path. Uniform no-match
stores intentionally retain eager work. Thus the five measured controls do not
establish a universal15% regression ceiling. Metadata and routing remain O(N),
not O(K) total time; no stronger concurrent-snapshot guarantee is established.
No RSS/native-allocation, disk-cold, model/GPU/KV integration, memory-QA, token,
TTFT or general production-workload benefit is accepted. External papers and
parent research completion remain outside this code/data verdict. Manual review
evidence does not install an independently authenticated runtime validation
backend. Publication, remote-CAS integration and remote byte readback remain root's
separate responsibilities, with all current permissions/budget limits intact.
