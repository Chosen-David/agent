# ATX-BOUNDARY-62 independent result review

Reviewer: actual separately invoked agent `/root/atx62_result_review`, 2026-10-19. Project `/workspace/scratch/5d3e4236a5b4/agent-audit62`; baseline `b69b4150e41492183433b1061add742aaa44510b`. Verdict: **usable-with-scope for candidate v2**. Candidate v1 is historical, rejected for publication because of its avoidable long-whitespace scanning risk despite passing the finite semantic cases.

This is an actual independent bounded code/data review, not a managed `ReviewSession`, authenticated runtime receipt, running supervisor or publication confirmation. No managed adapter is available. The main agent still owns final document reconciliation, exact staging, fetch/integration, authorized push and remote-SHA readback. This review does not manufacture those events.

## Bound sources and evidence

Read AGENTS, decision-review, project-document, knowledge-access, result-reuse and result-validation workflows; canonical ATX task/detail; original plan and independent plan review; actual production implementation, mirror diff, tests, producer probe and complete parsed raw JSON. Independently opened CommonMark 0.31.2 §4.2 at <https://spec.commonmark.org/0.31.2/#atx-headings>, including raw-space/tab and empty-title semantics. Inline rendering is not the oracle.

- Plan SHA-256: `de9d7fe073133206964b51e54f38cce78edde9831aea8163e0f0b58696f0825a`.
- v2 revision record SHA-256: `d6c68b33707792708c9a69f2e6660772a18ac436994da241dd7b3848dc98a0f0`.
- Actual candidate and byte-identical mirror: `ab45ef3d0a9005741951a1e8c114366533338c861373cbdd78ac1efd41558a8c`.
- Current tests: `25c518f7b44bcc55c027a25f072a5f7b4a751e1df68428097ead10b0425501f3`.
- Original candidate/test snapshots independently hash-checked at `candidate-v1.py` / `tests-v1.py`: `9ae7016563e11bc2ac74fd9ea7863cb704d5744b023229ceedd8fca46346558b` / `253ad42cb0cf8a22155d508e09935fe5e472641ce8e3b8f2e148a20273cb112d`.
- Accepted producer `raw-v2.json`: `d28ef80fb0ea4d7a4c9619a9f83942df20d55b3167eeafa93b6f6d27bc8d7252`; `raw-v2-O.json`: `b2ad7dcea5a897f927d1d7abdf1b7d7ec3197cb55bd1e4544922581b6bd0793d`.
- Accepted independent complete raw: `independent-raw-v2.json` SHA `f346386e81c89c59e1ca8cda9ec1a108e7803e4116210bb3f7863b2908363b97`; `independent-raw-v2-O.json` SHA `bb8f22caa606bbb829c07b6196bd3bd5385bbccdb65cd429ac05236726847a76`.
- Independent regression record: `independent-regression-v2.json` SHA `97ea529e9320421155606fb97b302c46bef818a7e779608f2800de829aa9f46f`.

All four roughly 1.9 MB independent full raw JSON files are deliberately **local-only and excluded from Git publication**. Their `*.summary.json` indexes retain exact full-file SHA/byte count, source/input bindings, every corpus ID/hash/node count and equality/reassembly outcome, all failure lists, environment and full cache transition evidence. Summaries are transport indexes, not a claim that full raw files are remotely persisted. The original full raw files remain unmodified. Scripts and compact records may be committed; replay generates fresh full evidence using a new output filename. Temporary full-suite/before-fix logs likewise are not claimed to be published.

Prior-result discovery: read the current task's producer results and independently searched historical `knowledge-fence-20261014-0705/independent*` for `v5|sections|knowledge-fence`. Those old results concern fence behavior and supply methodology only, not acceptance for the new ATX repair. Actual knowledge CLI query `ATX heading parsing boundary` returned normal-mixture, speculative-decoding and Schur-complement cards; all are inapplicable to raw Markdown syntax, so `knowledge_refs=[]`. The relevant reference is the primary syntax specification, not those mathematical matches.

## Six required gates

| Gate | Verdict | Independent evidence and scope |
| --- | --- | --- |
| implementation | pass | Read the full real module and entry points `sections`, `build_index`, `indexed_search`, `navigate`; checked unchanged tokenization/tree/fence/body algorithms. Opening marker requires 1–6 hashes plus ASCII space/tab or line end. Fixed-width lookbehind permits closing hashes only after ASCII whitespace; raw escaped/attached hashes and Unicode spaces remain literal. Engine v6 invalidates old caches. Canonical/mirror bytes agree. Source/dependency hashes checked before and after runs. |
| reference_boundary | pass | `independent_probe_v2.py` uses a character-by-character scanner, not the production regex, and compares complete node dictionaries on 37,212 cases in each ordinary and `-O` run. Exhaustive tail alphabet `#`, ASCII space/tab, backslash, x, NBSP through length 4, several valid/invalid prefixes, EOF/LF/CRLF/CR, empty input and explicit raw inline/Unicode controls. Six additional long whitespace/hash/alternating cases reach 100,000-character runs. The fixed hierarchy/fence oracle also passes independent unittest runs. |
| data_integrity | pass | Independently replayed every producer row with fixed baseline full source and actual candidate. Exactly 72 unique inputs, no missing row, boolean outcomes recomputed from complete expected/actual dictionaries. Original 24×3 matrix is unchanged. Both producer modes have identical records except `optimized`; their module/test/probe hashes and corpus snapshot match actual bytes. All 115 unique corpus IDs have complete old/new node comparison and exact source reassembly. No changed corpus node dictionaries. |
| numerical_sanity | pass | Exact discrete equality/counts, not floating tolerance: baseline 33/72 and candidate 72/72 recomputed from raw rows. Independent failure lists empty; all 115 baseline/candidate reconstructions exact. Correctness is dimensionless and limited to these inputs. Cache counts reconcile one rebuilt entry and subsequent one unchanged entry. No numerical-model or physical-unit claim. |
| measurement_validity | not_applicable (performance), pass (fixed correctness protocol) | Plan explicitly allows N/A because there is no speed/throughput/model-quality claim. Same frozen inputs/oracle and denominator are used for baseline/candidate correctness. v1 timing is only a bounded defect diagnostic (three samples per length, no warmup), not a benchmark or v2 speedup claim. No statistical generalization from the synthetic matrix is accepted. |
| reproducibility | pass | Independently executed ordinary and `python -O` probes, current ATX tests in both modes, 16 index tests, and 3 Reader tests. Actual source stays at the bound hash. Genuine full v5 module constructs SQLite cache, v6 public search rejects it, unchanged source snapshot rebuilds corrected chunks, next build is no-op, and public search/navigation identify the corrected empty section. Full v2 suite log independently inspected: 1304 tests, OK with 8 explicit skips. |

## Actual reruns and cache transition

Commands from repository root (use new `--output` paths; scripts reject overwrites):

```bash
python agent_doc/results/atx-boundary62/independent_probe_v2.py --output agent_doc/results/atx-boundary62/independent-raw-v2.json
python -O agent_doc/results/atx-boundary62/independent_probe_v2.py --output agent_doc/results/atx-boundary62/independent-raw-v2-O.json
python agent_doc/results/atx-boundary62/independent_regression.py
```

The complete independent regression record preserves the executed interpreter/arguments, stdout, stderr and return codes: ATX 3 tests; ATX `-O` 3 tests; index 16 tests; Reader 3 tests, all passing. The probe checks with explicit conditionals, so optimization does not remove checks.

Cache fixture is independently chosen: attached `Attached#`, empty `##`, invalid NBSP opening and a legal closing marker. The **complete baseline module** is loaded from `git show b69b415...:agent_runtime/knowledge_index.py`; no engine-marker spoof is used. Old build metadata actually says v5; old/new chunk rows differ; v6 search emits `stale index engine; run index to update`; rebuild has `engine_changed=true`, `updated=1`, `unchanged=0`; reconstructed source snapshot equals the initial snapshot; next build has `engine_changed=false`, `updated=0`, `unchanged=1`. Search returns `s2` for the empty-section term and navigation titles are `Attached#`, empty string, `End`. Full rows and metadata are in each compact summary as well as full raw.

Inspected historical before-fix log `/tmp/atx62-before.log`: 2 tests, 40 failures, consisting of 39 single-line mismatches plus the hierarchy failure (not 40 independent test methods). SHA `07601941207873c72e961104f71400c5da4d2f940fe8b3612d1f2b4d9df3380e`. Fixed-source replay independently confirms the 39/72 single-line mismatches; producer status is not accepted by itself.

Inspected v2 full log `/tmp/atx62-full-v2.log`: 1304 tests in 92.403 s, `OK (skipped=8)`, SHA `9e63eb2664a199bab66ecad53f5b4bb39cbdab9f6c357e4f313d0402c6a7f01d`. Seven optional visualization/dependency tests and one opt-in real-tmux test were skipped. This log was produced by the main agent and independently inspected, not falsely claimed as an independent second full-suite run. The former v1 full suite (1303 tests) is not used to certify v2.

## Rejected candidate history and limitations

v1 ordinary/`-O` independent probes passed 37,188 finite boundary cases each, 115 corpus checks and genuine v5 migration. They did not establish safe long-input scanning. `independent_suffix_diagnostic.py` reproduces the exact rejected v1 suffix regex on 1k/2k/4k/8k trailing spaces: three samples are approximately 0.005/0.020/0.08/0.30 seconds, consistent with the repeated-start scan visible in the code. Samples and script hash are retained in `independent-suffix-diagnostic-v1.json`. No formal complexity proof or cross-platform speed claim is inferred from those few timings. v2 removes that variable-length left whitespace match, preserves all old oracles and passes added long-boundary controls; acceptance applies only to v2.

Remaining limits: raw top-level ATX extraction only; no complete CommonMark container/HTML/setext/inline-renderer conformance; existing Python `splitlines` contract is retained rather than generalized. Corpus nonregression does not prove natural-document improvement (there were zero changed corpus records). Python 3.12.14/Linux/SQLite CPU checks do not establish all-platform behavior, LLM compliance, retrieval relevance, live plugins, deployed supervision, GPU results, throughput or publication success. Finite tests cannot prove absence of all bugs. Changing bound source, tests, inputs or acceptance scope requires renewed validation.

No production, mirror, tests, guide, TASK, frozen producer raw or unrelated archive was edited by this reviewer. Only assigned `independent*` evidence and this review were written.

## Exact review-owned publication allowlist

The main agent may stage these 12 files under this result directory, after its final checks:

- `result_review.md`
- `independent_probe.py`
- `independent_probe_v2.py`
- `independent_regression.py`
- `independent_suffix_diagnostic.py`
- `independent_summarize.py`
- `independent-regression-v2.json`
- `independent-suffix-diagnostic-v1.json`
- `independent-raw-v1.summary.json`
- `independent-raw-v1-O.summary.json`
- `independent-raw-v2.summary.json`
- `independent-raw-v2-O.summary.json`

Do not stage the four full `independent-raw-v1.json`, `independent-raw-v1-O.json`, `independent-raw-v2.json`, `independent-raw-v2-O.json`, any `__pycache__`, or `/tmp` logs. Their local-only status is intentional and cannot be represented as remotely persisted complete evidence. v1 replay requires its archived v1 production/tests in an isolated baseline checkout; the present checkout's frozen replay entry point is `independent_probe_v2.py`. If local full raw is later unavailable, rerun against exactly bound sources into fresh filenames; do not pretend the summary restores every node's text.
