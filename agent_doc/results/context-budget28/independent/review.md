# CONTEXT-BUDGET-28 independent result review

Verdict: **usable-with-scope** for the frozen local CPU experiment and exact-output compatibility cases. This is manual independent review, not a native ReviewSession receipt, managed-dispatch approval, publication acceptance, or a universal correctness guarantee.

Reviewer: separate host-created agent context `/root/context_budget28_plan_review`; source author/producer is the parent context. The reviewer inspected actual implementation, baseline source, harness, unit tests, raw outputs, journals and frozen input records, then independently executed the unchanged harness. Only this independent evidence directory and its permitted adjacent log/time files were written by the reviewer.

## Execution and identity

- Baseline: `5b1765cb1e228dff27794ca067171fd2f31c0d3a`, source obtained with `git show` into isolated globals.
- Candidate `agent_runtime/knowledge.py` SHA-256: `32e4f301463d9cd57e4ced59ed3504f24778c9d1358fda242deb2f1f09091064`.
- Frozen benchmark SHA-256: `0bc3784a88d38f298911b95dd1de87868acdad31c7521dc646ed6fbb3c12e39b`.
- Executed: `timeout 900 env PYTHONHASHSEED=0 python scripts/benchmark_context_budget.py --out agent_doc/results/context-budget28/independent`.
- Bash `time`: 22.140 seconds elapsed, 21.149 user, 0.979 system; process exit 0. `/usr/bin/time` was unavailable; its initial pre-execution launch failure remains in `../independent.log`. No benchmark ran during that failed launch. Bash-time fallback evidence is `../independent.time`.
- Python 3.12.14, Linux x86_64/glibc 2.39; observed CPU Intel Xeon Platinum 8573C, KVM, 9 visible CPUs. Shared host, no exclusive-host guarantee or CPU pinning. Parent confirmed it did not run concurrent CPU tests during independent timing.
- Each case retains two warmup pairs and eleven alternating AB/BA measured pairs. Ratio means candidate median divided by baseline median; warmups excluded. Imports excluded; fresh-store measurements do not flush OS caches. Tracemalloc runs are separate from timing.

## Independent checks

| Criterion | Verdict | Evidence and finding |
| --- | --- | --- |
| Implementation | Pass | Read both implementations, `get`, constructor/link validation, and the six-line diff. Early rejection follows original seed validation and complete closure resolution. Published transitive prerequisites are validated at construction. No change to navigation, selection order, skipped structure, later-seed processing or character cost on fitting paths. Both implementation copies are byte-identical. |
| Reference and boundaries | Pass | Each run has 750 complete-output differential cases plus 11 exception-type/message comparisons. Additional independent script has 27 checks: malformed missing fields/rows, invalid types/ranges, unknown later seed under navigation on/off, partially selected chains, unpublished seed navigation, stale constructor prerequisite version and self-link. |
| Data integrity | Pass | Recomputed full current corpus file inventory and all contents against both reports, source/harness/test hashes and stable Plan hash. Verified identical producer/reviewer inputs and output hashes, all 16 unique case identities, all pair orders, raw pairs versus journals, and parity/error journal counts. |
| Numerical sanity | Pass | All durations positive integer nanoseconds. Independently recomputed medians, ratios and every gate from raw samples; no NaN/Inf. Raw sample dispersion is preserved in `extra-verification.json`. |
| Measurement validity | Pass within scope | All 16 frozen gates pass in producer and independent runs. Two target contexts meet ratio <=0.80; all fourteen controls meet candidate <=max(baseline*1.10, baseline+200000 ns). Shared-host noise is visible, so small control changes are not general speedup claims. |
| Reproducibility | Pass within scope | Unchanged frozen harness rerun under the fixed seed and timeout. Independently selected checks and recalculation script executed exit 0. No threshold, input or source revision was made after observing measurements. |

## Independent measured outcomes

| Case | Baseline median ms | Candidate median ms | Candidate/baseline |
| --- | ---: | ---: | ---: |
| chain100/context | 9.319847 | 0.258472 | 0.027734 |
| chain300/context | 57.012205 | 0.822862 | 0.014433 |
| chain100/load-search-context | 39.168433 | 29.428523 | 0.751333 |
| chain300/load-search-context | 158.272552 | 97.401733 | 0.615405 |
| real/matrix/context | 8.071571 | 6.387108 | 0.791309 |
| real/matrix/load-search-context | 94.843510 | 86.674957 | 0.913873 |
| real/量纲/context | 6.451084 | 6.198347 | 0.960823 |
| real/量纲/load-search-context | 95.079292 | 95.889135 | 1.008518 |
| real/attention量纲/context | 4.164321 | 4.391376 | 1.054524 |
| real/attention量纲/load-search-context | 112.369312 | 104.445881 | 0.929488 |
| real/zzqxnonexistent/context | 0.001721 | 0.001702 | 0.988960 |
| real/zzqxnonexistent/load-search-context | 75.743613 | 77.667050 | 1.025394 |

Target context latency reductions are 97.23% and 98.56% in this independent run. Producer target ratios were 0.021564 and 0.009577. Chain20 and chain21 context/flow controls also all pass; their complete numbers and all samples remain in the raw evidence.

Independent Python-allocation peaks, measured separately with tracemalloc: chain100 579005 -> 19214 bytes; chain300 1745206 -> 59215 bytes. These are single allocation-peak observations, not process RSS or statistically replicated memory claims.

## Scope and limitations

Valid for constructor-validated snapshots not externally mutated. Direct `records` modification, monkeypatched methods and concurrent mutation are excluded. No LLM quality, task-success, model-token, general end-to-end Agent speed, disk-cold-start, or native runtime integration improvement is established. The no-hit microsecond context control is especially sensitive to overhead/noise and has a deliberately generous absolute gate. Real controls show both increases and decreases; report them honestly rather than claim every real case became faster.

Full repository/Reader regression and publication checks remain parent-owned and are not claimed by this report. Native review/supervision adapters remain unavailable. Revalidate bindings if source, Plan, corpus or measurement code changes.

## Evidence hashes

- Producer `raw.json`: `23f5488ec824ab924a9bb2c8b4f36935146f49b1455764bb4dc25e4b9819a12d`.
- Independent `raw.json`: `63052efd37c53e77225704663cc43d343eef27866d3c5819d04a1d85d729b925`.
- Independent `progress.jsonl`: `5b68be5ca2b9520376c84b3578c708c4a663ada993dc8e1e7b3b78dce78e6bd7`.
- `extra-verification.json`: `b263e6bd69d78d8d8ef7d3e21e3208e49a74f86737d5e8211b0e0f5380c4a6fa`.
- `verify_extra.py`: `eb6c55e82f2ec9f0aee7b262cb7ef615d92a282d12e4a5a72db88c0bcb202a59`.

`extra.log` records the independent recalculation/check result. Raw reports also bind exact input files, Plan prefix hash, Python/platform, and the frozen test/harness sources.
