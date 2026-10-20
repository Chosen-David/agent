# SEARCH-DEPTH-93 independent result review

Verdict: **usable-with-scope** for bounded, stored-JSON decoder recursion isolation in `ResultStore.search`, on CPython 3.12.14 local CPU. No blocking findings in the reviewed candidate. This is a real delegated reviewer run (`/root/search93_review`), not producer self-acceptance or a claimed ManagedEngine deployment.

## Frozen bindings

| Artifact | SHA-256 |
| --- | --- |
| Base revision | `d065a055cf29b10ed37717db197995283c1665d4` (Git commit) |
| Base result_store.py | `3f2a5639ac16bcb1e072f5ec06f9fbb3e2cc7cc33ff76f128acb362f2a421689` |
| Candidate agent_runtime/result_store.py | `3da82814e44acdc8ff8aa26e4b5d103825713d515c688e0ca06e63518cb02c1b` |
| tests/test_result_search_depth.py | `acb325d482318e579f2a369920dd9c6f942e7cd09781e416cfd08cf0f15a0e6b` |
| validation-plan.json | `ce0cfb9ba9411eda8253f8ddaa23e1c50078acbb65c651845361c2ee2c102151` |
| independent_probe.py | `336cf3feb743142b7809bbbccbf0893e747dd32712951eb0ddf9afcdf3ad67a8` |
| independent-normal.json | `2fc8b9ab58cdda50297bd4b083ae194974849c3a2d0f5c7b6f8fefa336d82ad0` |
| independent-optimized.json | `570a2528699a80141dc47c609c388ed6d3cd546cf87da241343373bbca3a9047` |

Approved v2 plan: `.agent-runs/search93/plan-v2.md`, SHA-256 `284d592718fe071d78cd5ead9d975a92e7303bf609eeb827438a00b9bc051157`. Full plan review is `.agent-runs/search93/review-plan.md`; v1 was revised before implementation because a broad per-record recursion catch would change unrelated exception behavior.

## Independent observations

Read the actual source diff and full added regression file. The production diff adds a private `RecursionError` subtype, wraps only `json.loads` in `_json`, and catches only that subtype in search alongside pre-existing data errors. It does not modify bounds, recursion limits, trust/acceptance, ranking, or custom-show dispatch. No extra read was added.

Ran `python agent_doc/results/search93/independent_probe.py` and its `python -O` counterpart. Each passed seven explicitly described groups (the JSON records group-specific case counts, not an application success-rate denominator). The probe executes the frozen base source obtained by `git show` and the real candidate against the same temporary files.

- Seven ordinary full-output comparisons are equal: lexical match, no match, limited results, bounded scan, exact context, unknown context, and shallow nested context.
- Two real depth-10000 files trigger the decoder in the frozen base: arrays are 20,013 bytes; objects are 60,013 bytes. Both are below the unchanged 1 MiB read bound. The base aborts retrieval; the candidate retains all three good result entries byte-for-byte at the structured-result level and reports precisely the two failed run IDs.
- Unmatched and all-bad cases return `incomplete`; bad records never become candidates. The independent all-bad enumeration is constrained to the two real bad files; the production unit test independently uses a directory containing only a bad file.
- Direct show retains `RecursionError` category and exact raw decoder message, with the original raw error as `__cause__`. Its concrete exception class deliberately changes to the private subtype, as approved in v2.
- Raw custom-show `RecursionError`, `RuntimeError`, and `SystemExit` propagate with identity preserved on both base and candidate. A separately injected raw `RecursionError` in the post-show contamination check also propagates unchanged. Over-deep caller context remains a raw error before record iteration.
- The real CLI exits zero and its parsed JSON equals the API output in both normal and optimized interpreters. All five fixture file hashes remain unchanged after the calls.

Also independently reran `python -m unittest discover -s tests -p test_result_search_depth.py -v` and the `python -O` variant: 7 test methods passed each. No use of removable Python `assert` statements in the independent probe; its checks remain active under `-O`.

## Producer evidence reviewed

| Evidence under .agent-runs/search93 | Observed result | SHA-256 |
| --- | --- | --- |
| before.log | Initial 2000-depth fixture calibration failure, not product-defect proof | `6456910a19be8561e4bf36542d8c2d33df1e3757ecb710728130f43d865365f0` |
| before-v2.log | Frozen base: 7 methods, 2 API errors and 2 CLI subtest failures | `a9c324c839fca09ced921b9f1faeabcd69670d6bd2d94bb242c3148d71e7fb24` |
| focused.log | 94 methods, OK | `08a12fc6256910229d87c3e38df2082c2795f3654da286aabf180edad5448553` |
| focused-opt.log | 94 methods, OK | `3ad0af96b4e8a69491a0204b140f3ca2547f6a755c4f7eae56d08925598fe751` |
| full.log | 1338 methods run, 8 skipped, no failures | `3241633627e494d14736af81d4f1949b7c33a5794a73b44f5e55a6a5d431c0b5` |
| reader.log | 3 methods, OK | `1403bce891d089d7563f05d0adee43dabf91914d5a75b079b354d0dde8e28496` |

The cause/message assertions were added after the original baseline run; they are not claimed to have passed the baseline. The independent differential explicitly verifies base raw exception and candidate subtype/cause semantics. Full and Reader suites above are producer runs whose logs were reviewed, not falsely described as independently rerun whole suites.

## Validation criteria

| Criterion | Verdict | Evidence/reason |
| --- | --- | --- |
| implementation | pass | Actual minimal diff and call paths reviewed; parser-origin provenance only. |
| reference_boundary | pass | Frozen-base differential, real bounded list/object files, custom and post-show propagation, shallow inputs and CLI. |
| data_integrity | pass | Source/test/probe hashes, fixture hashes before/after, original failures preserved and distinguished from calibration. |
| numerical_sanity | pass | 20,013/60,013 byte inputs are under 1,048,576 bytes; unit counts distinguish subtests and skips. No inferred service success percentage. |
| measurement_validity | not_applicable | Explicitly allowed by frozen protocol: no performance/timing claim or statistical experiment. |
| reproducibility | pass | Independent normal/-O probes and seven-method reruns; producer focused/full/Reader logs reviewed. |

## Limitations and publication boundary

Acceptance covers the pinned source/test bytes and the declared depth-error path, not universal JSON/resource-exhaustion safety, arbitrary interpreter limits, production workload success rates, or speed/model quality. The depth fixture is valid JSON syntax but exceeds this decoder's supported depth; no claim that all malformed JSON produces this exception. Parser `RecursionError` concrete subtype changes for every `_json` consumer, including non-search callers; category, message, and underlying cause are retained, and exact class-name equivalence is not claimed. A trusted custom extension intentionally raising the private subtype is outside the ordinary raw-exception preservation claim.

This review neither authorizes publication nor certifies a remote commit, installed supervisor, unrelated DISPLAY91 changes, or all historical TASK requirements. Main owns canonical TASK reconciliation, accurate publication scope, final file bindings, remote synchronization/readback, and preservation of unrelated changes. Revalidate if the pinned source/tests or acceptance change. Reviewer changed only independent evidence files and its own review documents.
