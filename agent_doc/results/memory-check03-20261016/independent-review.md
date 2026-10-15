# MEM-CHECK-03 independent actual code/data review

Verdict: **usable-with-scope**, for the frozen synthetic warm-local-SQLite
`MemoryLedger.check` cases only. No failing checks were observed. This was a
separate review-agent invocation with actual independent executions, not a
producer self-report or trusted runtime provider/managed ReviewSession receipt.
The ongoing MEM-STORAGE-01/model-KV task is not completed by this result.

## Identity and evidence

Baseline exact Git revision: `9b6cc775a900f2c0d26d97f88de5622129eec014`.
Independent checker retrieves that actual Git source and asserts its hash before
loading it in a separate module namespace. Exceptions are compared by class name
and full message (module-local MemoryError identities necessarily differ).

| Artifact | SHA256 |
| --- | --- |
| Baseline project_memory source | `914229446d705343ef71d81c79b20b7119652a376aa180e9eff54e83a7d1d450` |
| Reviewed candidate project_memory source | `b9f939410eee1e7c7477982ff9b0a1c95bd7d952ec706b5b179707d0d598ccf6` |
| scripts/bench_memory_retrieval.py | `7de92aba6e41d3424352b586f7335faeae754a8b24d415e3a0ffb04a525d5d65` |
| tests/test_memory_check.py | `66458465bb7a42e8def4711ddd000ac641b96856dfdfc88b3e6360ec658ae06e` |
| config.json | `a02199c4894bf47c6ea385390d2f2d8fba92776b92fcd2c2e72ff786d5b5cfe9` |
| raw-primary.json | `44d20a80063b15602bac391d4873bf2947a02ac601c90acbb080f9e61fc9ebe8` |
| independent-raw.json | `805d48e0842bb5765b2f651639cf3c7978ce88e3508f3cb4abf9d8fad91ae4eb` |
| independent_check.py | `1792c996a7db10e4d18739fc96a3942ff32da99b3d073e12fa043a87a2b8600c` |

The actual source hash was checked before and after the independent checker.
The result config hash equals the privately reviewed pre-timing plan config.
Both raw files embed that exact parsed config and the exact baseline/candidate
hashes. Each of their six database SHA256 values matches the corresponding
independently recreated fixture; the before/after benchmark shares one DB.

## Actual executions

Executed serial independent timing first, after planner confirmed primary timing
was over; only after that completed did correctness/regression execution begin.

```bash
PYTHONPATH=. python scripts/bench_memory_retrieval.py --config agent_doc/results/memory-check03-20261016/config.json --output agent_doc/results/memory-check03-20261016/independent-raw.json
PYTHONPATH=. python agent_doc/results/memory-check03-20261016/independent_check.py
python -m unittest tests.test_memory_check tests.test_project_memory tests.test_memory_retrieval -v
```

- Independent differential: **4306 complete outcome comparisons**, zero mismatch.
- Additional freshness assertions: **5**, passed.
- Additional structural/call/document-validation assertions: **3**, passed.
- Raw arithmetic/config/sample/identity/gate cases checked: **12**, passed.
- Focused existing and new regression tests: **33 tests**, all passed, zero skipped.
- Checker exit0; regression exit0. No failed or omitted timed samples.

Differential coverage includes all ordered nonempty root subsets of a four-node
diamond against64 ancestor-status assignments; malformed refs, missing IDs,
reordered tuples, root/dependency overlaps, root/ancestor JSON corruption and
unusual JSON values/BLOBs, missing entries/dependency tables, legacy absent
document table, dangling edges, cycles/self-cycle, failed-then-repaired checks,
correction between calls, caller mutations and real task-document changes then
restoration. No human project-guide file is changed by this independent checker.

## Six validity checks

1. **implementation — pass.** Read the actual diff and complete relevant source,
   tests and benchmark. Only root-local `requested`/`roots` are added; status and
   document checks, checked-set placement, recursive dependency validation and
   root iteration stay ordered as before. Return order follows refs. A requested
   root visited first as a dependency is retained. No instance attribute/schema,
   cross-call cache, SQL validation shortcut or document-check bypass is added.
   Observed get calls for roots[d,a] were[d,b,a,c], exactly once per reachable
   entry. Live root maps contained only requested roots, not every ancestor.
   Candidate ledger attributes were unchanged across check().
2. **reference_boundary — pass.** Exact pre-change Git code, not a reimplementation
   of the optimized algorithm, is the differential reference. Complete results
   or normalized exception class/full message agree in4306 cases. Returned scope,
   deps/content mutations do not affect future calls. Documents are actually
   checked again on later calls and task-document edits invalidate dependent
   memories; restore succeeds. The legacy accepted cycle behavior is preserved,
   not silently redefined as new graph validation.
3. **data_integrity — pass.** Config and source identities match. Every raw case
   has21 samples for each implementation and21 ordered pairs. Exact seed1603
   order is independently reconstructed and agrees. Config dimensions, counts,
   case order, returned root counts, and DB hashes agree between runs. There are
   no discarded samples or post-result threshold changes in reviewed artifacts.
4. **numerical_sanity — pass.** All252 timing values in each raw file are finite
   and strictly positive, units milliseconds. Every stored median and reduction
   is exactly recomputed from raw samples. Reduction is1-median(after)/median(before),
   not median of paired ratios. Both runs meet all predeclared thresholds.
5. **measurement_validity — pass with scope limits.** Timer encloses one public
   check call, including path validation, connection, BEGIN/read/validation/JSON/
   packet hydration/return/commit/close. Fixture setup, Git loading, correctness
   comparisons, warmups, hashes and statistics are outside timing. Calls return
   complete packets and equality is checked after timer stops. Normal Python
   assignment/disposal overhead is included symmetrically. Pair order is randomized;
   both versions use the same local SQLite bytes and receive warmup. No document
   hashing workload is timed. Shared virtual-host noise/outliers remain in raw
   data; no CPU isolation/affinity or cold-disk claim is made.
6. **reproducibility — pass with limits.** Independently reran the inspected frozen
   runner with all21 pairs/case, preserving its exclusive-create output. The
   checker independently verifies raw arithmetic and baseline differentials;
   benchmark runner implementation itself is shared, not a wholly independent
   timer implementation. Targeted regression was actually executed afterward.

## Paired timing outcomes

Positive reduction means faster; negative means regression. Each value uses21
samples/implementation on the frozen case, no setup/equality timing.

| Case | Primary reduction | Independent before→after ms | Independent reduction |
| --- | ---: | ---: | ---: |
| 512 roots,128B content | 44.79% | 8.948634→5.022791 | 43.87% |
| 512 roots,8192B content | 36.06% | 13.073390→7.940937 | 39.26% |
| One root control | 4.49% | 0.272585→0.242470 | 11.05% |
| Eight root control | 14.02% | 0.418772→0.345333 | 17.54% |
|128-node chain/one requested leaf | -0.53% | 1.499568→1.535501 | -2.40% |
|32 requested roots/shared parent | 30.73% | 0.881600→0.589115 | 33.18% |

Both large cases exceed the frozen20% reduction threshold in both runs. Worst
control regression is0.53% primary/2.40% independent, below15%. Small control
differences are not promoted as reliable general speed claims.

## Environment and limitations

Observed by `lscpu`: x86_64 AMD EPYC9V74 80-Core Processor, KVM virtualized host,
9 visible logical CPUs, one visible socket/NUMA node. Raw environment records
Python3.12.14, Clang22.1.3, SQLite3.53.1, Linux6.18.44/glibc2.39. The benchmark
uses one serial process; host-exclusive CPU allocation is not established.

Acceptance is bounded, not universal correctness. No RSS/peak-memory benchmark,
large-graph recursion scalability, arbitrary adversarial SQLite/FS concurrent
mutation, cold storage, service deployment, model-KV tensors, LLM task quality,
token cost, TTFT or GPU benefit is established. O(requested roots) packet
retention is an implementation property, not an RSS measurement; existing checked
set and recursive traversal still scale with reachable graph size/depth.
Full repository regression, final candidate binding and publish/remote readback
are the planner's remaining work; this report does not itself authorize a push.
