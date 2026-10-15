# MEM-CHECK-04 independent actual code/data validation

Verdict: **usable-with-scope** for the frozen manual CPU fixture protocol.
The measured candidate meets both frozen acceptance gates. This review is an
actual separate agent-context code/data inspection and rerun, not a managed
ReviewSession/ResultValidationHandler receipt or a universal correctness claim.

## Frozen evidence

| Artifact | SHA256 |
| --- | --- |
| agent_runtime/project_memory.py | c3f41593b64b09d2af190d9ddcb64bbf784720083f4b718a5bdaf5318109f159 |
| scripts/bench_memory_check.py | d819010dd4358a2c34e4f252718818023da5e5154b2d58f39bbe546155d1a45b |
| tests/test_memory_check.py | 1b896588139185091418b8df997e5ba8b33a5740e3dbe55aceec85bce589c5ad |
| plan.json | 6f6cf437db52ff9c39935edf4505ae43d4d43467e2a62cf718b9b1d62c0f671f |
| raw-primary.json | b72dff6d6c58bfa4ed6ef3d497433ff04e3db554530c630f6345e0297d682b64 |
| reviewer/raw-independent.json | a46e36c6806b2e093d8315a5687b1baedc67c74fa2e609ecbd9e72c05943daa6 |
| reviewer/verify.py | 40e36a26ebc0de40a44e69dc58dd84eac73bb19b0f9b65e1b89184246901d873 |
| reviewer/check_protocol.py | 9c7df50848334266823c8034b5856a257ab7c1bf5a7d51d3605933dc30b9ef33 |
| reviewer/checks.json | ca060037dcaa9e57d77a3b1ea6f59da1ef965cb8a6dd9f2003871e6fb54363fa |
| reviewer/protocol-checks.json | cdb4786b1761c29714a51b6e7ec8d8f6246e38a47090024e27a3fe54c4b8ac80 |

Paths above are relative to the repository or this run directory as appropriate.
Baseline is git2d7ddc46b13b24ecc0c3611b1d8dcb63df7e6b10, source hash
b9f939410eee1e7c7477982ff9b0a1c95bd7d952ec706b5b179707d0d598ccf6.

## Six validation criteria

**Implementation — pass.** Read the actual baseline/candidate _check and shared
_get/_insert/callers. The only runtime change replaces recursive visit calls with
explicit dependency iterators. It checks status/documents, marks checked and
retains requested roots at the same point before descending; requested return
order remains refs order. Non-requested packet is explicitly deleted while its
deps iterator survives. No schema/SQL, connection, persistence cache or document
shortcut was introduced. Wide fanout remains lazy. Baseline import is compiled
from the pinned git source in its own globals, avoiding candidate-class leakage.

**Reference/boundary — pass.** Independently executed verify.py:7733 ordinary
cases compare complete successful packets or exception class/message and all
_get call order. This includes all512 directed three-node graphs (including self
edges and cycles) times15 root subsets/permutations, plus invalid/empty/duplicate
refs and str subclasses; status-first errors; isolated malformed scope/document
JSON, missing tables, dangling edges, NULL/integer/BLOB parent values, duplicate
edges and missing legacy document table. Four additional check_protocol cases
compare combined _get/document-check event order with an injected failure at each
position. Actual document edits/restoration, caller-result mutation, correction
and symlink path replacement are rechecked between calls. These are fixtures,
not a new promise of arbitrary corrupted-database support. Independent1024/1200
chains: baseline raises RecursionError, candidate succeeds with exactly one read
per node. This is a separate reliability extension, not ordinary numeric parity.

**Data integrity — pass.** Both raw files bind matching frozen config/source,
seven case IDs,21 wall pairs and7 traced pairs per case. Independently rebuilt
every deterministic fixture's complete rows/edges/refs and verified all7 input
hashes, and replayed every randomized order from seed41016. All samples remain
present. Reviewed exact data-creation code and exclusion of construction/equality
work from measured windows. Main-suite execution is producer-owned evidence;
this review does not relabel it as reviewer execution.

**Numerical sanity — pass.** Independently recomputed per-arm medians and all
reductions from both raw files; stored summaries agree exactly. Positive finite
wall nanoseconds and traced bytes have distinct units. Primary peak medians in
both runs are4,522,288→119,862bytes, a97.3495275% reduction, exceeding70%.
The values are consistent with releasing256 large ancestor packets and retaining
one requested output plus traversal metadata. Wide/multi-root cases retain
required result/dependency data and show little traced reduction, as expected.

**Measurement validity — pass within scope.** Read the full benchmark: each arm
calls public check through validation/connect/BEGIN/_get/commit/close/return;
temporary fixture construction and result equality lie outside timing. Three
warmups per arm, gc.collect outside each measurement,21 seeded randomized wall
pairs and separate7 traced pairs match the approved plan. tracemalloc starts
before and stops after the whole public call; returned packets are alive at peak
readout in both arms. No traced wall times are consumed as latency. After the
producer confirmed its full suite had ended, reviewer ran benchmark serially
without another owned CPU workload. Wall samples are noisy (for example one
independent deep_short baseline sample is9.81ms versus2.40ms median); all samples
remain included and the fixed median rule was not changed. No broad latency
speedup claim is needed to accept this memory-focused change.

**Reproducibility — pass.** Commands executed from project root with PYTHONPATH=.:
`python .agent-runs/memory-check04-20261016/reviewer/verify.py`;
`python .agent-runs/memory-check04-20261016/reviewer/check_protocol.py`;
`python scripts/bench_memory_check.py --config .agent-runs/memory-check04-20261016/plan.json --output .agent-runs/memory-check04-20261016/reviewer/raw-independent.json`.
Independent run records Python3.12.14, SQLite3.53.1, Linux6.18.44 x86_64/glibc2.39,
same source/config/input hashes, and passes both gates. No candidate tuning or
rerun selection occurred during this review.

## Independent measured medians

| Case | Before wall ns | After wall ns | After/before wall change | Traced peak reduction |
| --- | ---: | ---: | ---: | ---: |
| deep_payload | 3887264 | 3732665 | -3.98% | 97.35% |
| small | 305003 | 307436 | +0.80% | 4.27% |
| chain64 | 883963 | 822612 | -6.94% | 59.07% |
| wide | 4550380 | 4607645 | +1.26% | 0.15% |
| multi_roots | 1296245 | 1325569 | +2.26% | 0.06% |
| layered | 1416103 | 1449093 | +2.33% | 33.44% |
| deep_short | 2397521 | 2354648 | -1.79% | 75.35% |

All seven independent wall medians satisfy the<=15% regression guard; worst is
2.33%. The producer's worst regression is4.65%, also within the frozen guard.

## Limitations and downstream obligations

Acceptance covers Python-traced peak allocations and the exact local synthetic
warm-store SQLite/check fixtures only. It does not measure RSS, SQLite native
cache, GPU/model KV, QA, token counts or TTFT. Absolute Python allocation peaks
and latency depend on environment. Exhaustive small graphs and targeted errors
do not prove correctness for all Python objects or every malformed SQLite file;
concurrent hostile filesystem mutation remains outside the existing contract.
Broader MEM-STORAGE-01 is still incomplete without real model service/data.
The main agent owns final full regression, TASK reconciliation, publication and
remote byte/SHA readback, which are not claimed completed by this review.
