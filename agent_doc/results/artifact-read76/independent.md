# Independent result review — ARTIFACT-READ-76

Date: 2026-10-20. Reviewer: host-dispatched `/root/artifact76_verify`, separate from implementation and plan reviewers. Decision: **usable-with-scope** for the frozen v1/v2 Python-allocation and exact tested byte/error contract. All six applicable criteria pass. This is independent review evidence, not a fabricated ManagedEngine receipt, deployed supervisor, trusted callback registration, or universal bug-free certification. No production/TASK edits, commit or push were performed by this reviewer.

## Identity and evidence

- Baseline commit: `a55a3d14d8ebf0f840c4bdd9477562fdc369fe44`.
- Baseline `agent_runtime/result_validation.py`: `0c583d8fab12fcfaa4c7482ac4b696da687f5c9b1733459eb32dd2a6413610f4`.
- Accepted candidate source: `430f3a421a8b2b305cdb8da916f4ac8fdf8c977131449c49310e1bb69a69661d`.
- Independent probe: `26855e2bbc7e8c9d02e17d09ce43f2c96469c4c498193206bd7913b2213783d3`.
- `independent-raw.json`: `609ba0087353642118ffde48785ad6f1cca3851e7fa65d64a2478da67e28bb38`.
- Producer `raw.json`: `27fee4396da30930220aa7f25fccab2de62c3e8ed43fce68d4e719735acb8d5a`.
- Plan v1/v2: `3040dad85e1cd7f4c2f93b925e6bc12be3e3851a7941cc234d4480e027d6dcb4` / `4d5d9af9ad68bc570dcd704c0ea2e934fbddc871b486560173019b9c6cebbd47`.
- Independent targeted log: `0a7491a63ff4045668eec84af7ddc97705611f6e58a816c0b1cadfa78119bcce`.
- Preserved first probe diagnostic: `9e29552d6536e17072b7aec446c78ae61b7c4ba68c43ca37ab8fd77b01b7f5f5`.
- Independent descriptor diagnostic JSON: `5c86152b12110c75f3556e963d93f663e6e627ff288412c26065b997334f55ea`.

`independent-raw.json.artifact_hashes` additionally binds actual dispatch, legacy relocation, fixture/test and producer harness sources, both plan versions, plan review, before/after logs and full/Reader logs. Full-suite logs were inspected locally and hashed; they may remain private and are not claimed to be bundled with publication. Producer pre-change small-allocation test fails at 16,782,929 bytes; post-change targeted 41 tests pass. These observations were checked as evidence, not accepted solely from a JSON `accepted` label.

Read AGENTS, decision-review, project-document, result-reuse and result-validation workflows, empty read-only GUIDE, current TASK/detail, frozen plans, plan review, actual diff, `_bytes`, `_bound`, `_snapshot`, dispatch and artifact/source/validation-context/contamination consumers, legacy relocation and digest checks, producer harness/tests and raw results. Current search evidence is partial and returns unrelated lexical candidates. Direct prior negative review at `/workspace/scratch/6416f20dc59b/agent-audit74/agent_doc/results/artifact-read74/independent.md`, SHA-256 `0f1aecf0e95aee38ba06461474634eebcbcd67f01d004f495453a0bffc229b52`, was read unchanged. Its concatenating candidate doubled growth allocation; its acceptance cannot transfer to this different implementation. No historical data were rewritten or represented as newly measured.

## Independent observations

Executed after main explicitly confirmed its full/Reader runs had exited; no main tests or measurements overlapped. Environment: CPython 3.12.14, Linux 6.18.55 x86_64/glibc 2.39. Baseline `_bytes` was AST-extracted from the fixed Git source into unchanged helper globals; candidate was the actual imported production function. Patching `rv._bytes` exercises the real `_bound` called by complete `prepare_dispatch`, not a substitute dispatch model.

Commands:

```text
PYTHONDONTWRITEBYTECODE=1 python agent_doc/results/artifact-read76/independent_probe.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_result_read_allocation tests.test_dispatch_context tests.test_result_validation tests.test_result_gate_acceptance -v
PYTHONDONTWRITEBYTECODE=1 python agent_doc/results/artifact-read76/independent_fd_probe.py
```

All measurements are **tracemalloc peak bytes**, with two warmups followed by five baseline/candidate pairs; fixture/import/payload construction is outside tracing, GC precedes each interval. The deterministic file mutation operation itself is included in each side's interval using the same preconstructed bytes; neither side performs payload construction there. All raw samples, input/output hashes and medians are retained. Paired order was baseline then candidate each repetition. No sample was dropped.

| Independent case | Baseline median bytes | Candidate median bytes | Candidate/baseline |
| --- | ---: | ---: | ---: |
| Complete held-out dispatch request | 16,787,810 | 10,612 | 0.0006321253 |
| Stable 17-byte binary file | 16,784,692 | 7,461 | 0.0004445122 |
| Stable 65,535-byte file | 16,784,752 | 73,071 | 0.004353416 |
| Stable 65,536-byte file | 16,784,752 | 16,784,752 | 1 |
| Growth 1 byte to 16 MiB | 16,784,840 | 16,784,840 | 1 |
| Growth 65,535 bytes to 16 MiB or 16 MiB+1 | 16,784,872 | 16,784,904 | 1.0000019065 |
| Initially oversized 16 MiB+1 rejection | 7,834 | 7,842 | 1.001021190 |

Each of the five observed samples equals its row median for these cases. Complete dispatch allocation reduction is **99.93678746662013%**, exceeding the frozen >90% gate, with exact packet equality on all calls. The held-out instruction differs from the producer fixture; original producer request and normalized packet hashes were separately recomputed and match. All **23** independent stable/growth/shrink cases pass <=1.01 median nonregression; worst ratio is the already-oversized rejection's eight-byte difference. All **17** producer rows also recompute correctly from five raw pairs, including input/output/source hashes and fixed median gates.

Held-out payloads contain all 256 byte values, rather than producer repeated ASCII. Stable sizes include 0, 2, 17, 65,534, 65,535, 65,536, 1 MiB, 16 MiB and 16 MiB+1. Deterministic fstat-before-read growth starts at 0, 1, 37, 65,535, 65,536 and 8 MiB and ends at 16 MiB or 16 MiB+1; shrink includes 65,534 to 17 and 16 MiB to zero. Every returned byte or exception type/message matches the original baseline.

Fifteen additional exact semantic comparisons cover empty/escaped/absolute/missing paths, final and ancestor symlinks, FIFO, directory, good/stale bound digest, valid/stale/symlink/colliding legacy paths and nonseekable binary input. Nonseekable wrapper records only the original `read(LIMIT+1)` in both versions. Large stable-file wrapper records only that original request. A seekable wrapper with deliberately failing rewind raises its explicit OSError rather than returning truncated data; this is the newly specified failure path, not an assertion of baseline equivalence for a broken seek implementation.

Independent targeted suite: **41 passed**. Main full-suite log: **1314 run, 8 skipped, remaining passed**; skips are seven optional visualization-dependency checks and one opt-in real tmux check. Reader log: **3 passed**. Test durations are not performance evidence. No new full-suite failures appear; skipped optional integrations remain unverified.

## Six-criterion acceptance

| Criterion | Verdict | Basis |
| --- | --- | --- |
| implementation | pass | Only `_bytes` read selection changes. Same open descriptor, regular-file/initial-size guards, final-length check, relocation digest and `_bound` hash remain. Small seekable probe is released before bounded rewind/read; no concatenation or unbounded read. Large/nonseekable branch is original. Actual consumers and exact diff reviewed. |
| reference_boundary | pass | Fixed original source, held-out binary/stable/threshold/limit/growth/shrink cases and 15 exact path/hash/legacy/nonseekable comparisons; seek failure explicitly checked; targeted regression suite passes. |
| data_integrity | pass | Source/protocol/harness/log bindings retained; 17 producer rows and request/output hashes independently recomputed, 23 independent cases preserve all five samples, fixtures outside tracing, no mixed candidate or missing rows. |
| numerical_sanity | pass | Peaks are nonnegative integer bytes; finite ratios derive from nonzero medians; exact byte outcomes and error bounds hold; formulas reproduced directly. No RSS, wall-time, token, model-quality or inference claim. |
| measurement_validity | pass | Full call boundary, same process/input/CPU scope, two warmups/five paired intervals, no main overlap, all samples retained. >90% dispatch reduction and <=1.01 per-case median gates met without changing protocol. |
| reproducibility | pass | Independent original-vs-production execution and new held-out probe reproduce both primary improvement and growth nonregression. Actual 41-test rerun and inspected full/Reader logs agree; old negative preserved and its failure mechanism is absent from this candidate. |

## Limitations and pre-existing follow-up

The first independent probe stopped before measurements because directory rejection messages embed descriptor numbers: consecutive original/candidate calls showed fd 3 versus fd 4. The preserved attempt documents this. The corrected semantic harness reclaims only descriptors it opened between calls, preserving exact-message assertions. A separate bounded diagnostic then confirmed **both baseline and candidate** leak one descriptor on each `os.fdopen(directory)` error: `/proc/self/fd` count 4 → 6 after two errors → 4 after owned cleanup. This is a reproducible pre-existing defect, not introduced or fixed here; follow-up requires separate authorized repair and validation. No claim of universal resource safety is accepted.

The accepted optimization concerns small stable seekable files and the declared deterministic mutation fixtures. It does not prove arbitrary concurrent-interleaving equivalence, atomic snapshots, pathname-race elimination, wall-time/throughput/RSS improvements, or model behavior. Rewind fallback can repeat up to 64 KiB of probe reads; cumulative I/O is not asserted to remain LIMIT+1. File sizes >=64 KiB intentionally retain original allocation behavior. Changed source, protocol or evidence invalidates this candidate-specific acceptance and requires revalidation. No optional integration skip is represented as a pass.
