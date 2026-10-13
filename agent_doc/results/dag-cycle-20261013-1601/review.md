# Independent sparse-cycle plan review

Plan verdict: **approve** for the bounded direct local CPU candidate and measurement only.
Plan SHA-256: `5578f0f317d9597eeddaad60b7e9eb8afd3dee15cc6c65dad9434ca239f6c4aa`. Baseline: `56ccc46d1458dd7df257b68d296616eb34014c58`.
Reviewer: separate host-dispatched agent `/root/cycle_review_1601`; no production edits.

- Intent: pass. Preserve the public validate/Store.create contract while improving sparse graph validation; continuous optimization remains unfinished.
- Guide: pass. Read both guide files, canonical TASK and T11; GUIDE.md contains no substantive requirement. Human-only guide paths remain excluded.
- Assumptions: pass within scope. Admission inspects only already-materialized graph keys/dependency sets after the original construction, exact builtin str only, >=64 vertices and <=4V deduplicated edges. This avoids additional user object accesses and preserves legacy behavior for exotic inputs. No real-workload or model/GPU transfer claim is allowed.
- Prior results: pass. Relevant membership result is a different optimization and not reused as cycle timing; partial historical search limitations are disclosed.
- Acceptance: pass. Frozen public validate timing includes serialization; primary chain gains and tiny/star/dense guards apply to producer and one independent sequential replay. Independent oracle and baseline differential tests address threshold/density, duplicate/error ordering and unusual string behavior. A failed gate retains baseline.
- Risk: pass. Same interface, bounded candidate, ordinary publication only after independent acceptance, preserve raw failures and unrelated work. Final review must bind actual code and data hashes.
- Resources: pass for direct synchronous CPU work; no timing concurrent with tests. Managed supervisor/host-result adapter is absent and must remain explicitly blocked, with no runtime-gate or monitor deployment claim.

No blocking plan findings. Approval does not constitute a protected runtime ReviewSession receipt or acceptance of an implementation not yet produced. Candidate review and one independent replay remain pending. Any admission, benchmark, threshold or code change after freeze requires re-evaluation rather than retrying for a pass.

## Plan v2 review

Verdict: **approve** for the new candidate. Plan-v2 SHA-256: `42c290f85fd39b739046b25ec6f066c0a659f2114dd1fd9e65e7a78b7e8df6d0`. The rejected v1 data remain historical negative evidence; this is a changed algorithm, not a repeat of v1 for a favorable sample. Intent/guide/prior-results/risk/resources remain as above. Assumptions and acceptance pass with the following implementation obligations: perform two unchanged legacy scan rounds before admission; define V as the original materialized vertex count for the original deduplicated edge guard, or document a stricter residual bound; include already-visited vertices when checking dependency membership and subtract them from indegree; exact builtin str guard must include visited members. Tests must exercise incoming edges from both peeled levels, removable prefixes followed by cycles, and residual threshold 63/64/65. Same frozen gates and one independent replay apply to new producer-v2 data. No blocking findings.

## Independent v2 code/data acceptance

Verdict: **usable-with-scope** for this exact candidate and frozen synthetic local CPU validator workload. Independent full replay occurred once, after producer completion; no correctness suite ran concurrently with timing. No timing retries were made. Normal and `python -O` correctness-only replays both exited 0 with 762 baseline differential cases and 727 graphlib oracle checks, identical outcome hashes. Reviewer-designed additional 66 cases passed: exact residual density 4V-1/4V/4V+1 for residual V=63/64/65 with and without cycles, plus seeded permuted DAGs/guaranteed cycles at66/128/256.

Implementation: pass. Read actual validate and Store.create path; original field checks/materialization and final supervision/packed call remain ordered. Two legacy rounds run unchanged. Admission uses the explicitly stricter residual density bound, includes visited exact-str guard, validates all remaining dependency names, subtracts visited dependencies, and counts each residual vertex/edge through Kahn; cycle error remains exact. Legacy fallback never calls additional task getters. No input mutation was observed.

Reference/boundary: pass. Git-loaded pre-change baseline, graphlib distinct oracle, exhaustive 512 three-node directed graphs, threshold/density/deep-prefix cycles and malformed inputs passed. The additional reviewer cases target the actual residual guard, since producer original graph density cases alone do not imply exact residual boundaries.

Data integrity: pass. Producer/reviewer candidate, baseline, input and outcome hashes match. All five workloads retain nine raw paired samples; no failed samples removed. Recomputed medians/gates match JSON. Rejected v1 producer.json remains negative evidence.

Numerical sanity: pass. Units are milliseconds per validate invocation; small sample divides1000 invocations, other samples1. Positive finite timings and expected graph outcomes; no numerical approximation is introduced.

Measurement validity: pass within scope. Public validate including JSON serialization is timed; construction is outside both timings, two warmups per implementation, alternating order across nine pairs. Noise/outliers remain visible: reviewer chain1000 candidate maximum23.711ms versus median3.243ms, dense candidate range130.418–194.025ms. Median gates are the predeclared criteria and all pass. Nine pairs do not certify every invocation or all real graphs.

Reproducibility: pass within scope. One independent full replay and normal/-O correctness replay reproduce frozen gate outcomes on Python3.12.14, Linux6.18.44x86_64/glibc2.39. Producer and reviewer chain reductions agree strongly; tiny/star/dense median guard passes both cohorts.

| Workload | Reviewer baseline ms | Reviewer candidate ms | Reduction | Frozen gate |
| --- | ---: | ---: | ---: | --- |
| small | 0.006804 | 0.006851 | -0.69% | pass |
| chain512 | 12.667863 | 1.604065 | 87.34% | pass |
| chain1000 | 45.855008 | 3.242512 | 92.93% | pass |
| star512 | 1.122988 | 1.131441 | -0.75% | pass |
| dense1000 | 140.557385 | 149.292426 | -6.21% | pass |

Frozen artifacts SHA-256:

- `agent_runtime/core.py`: `ebb82f1b5f2529f7ebf89ba64a2e61dc3938ef437b9ce9d20c7cb49dc677b158`
- `agent_doc/results/dag-cycle-20261013-1601/check.py`: `cbc5fbb7bfda141696e628516de701a791dc1e730dd651d0b41833843d25d428`
- `agent_doc/results/dag-cycle-20261013-1601/plan-v2.md`: `42c290f85fd39b739046b25ec6f066c0a659f2114dd1fd9e65e7a78b7e8df6d0`
- `agent_doc/results/dag-cycle-20261013-1601/producer-v2.json`: `0adac1fa8f21bf146d64d8e063adcd019750bca48dbfbd1d2987b9bf2d873c11`
- `agent_doc/results/dag-cycle-20261013-1601/independent.json`: `c22200dce6c7dcdcf060d0f734188d46b551fa1d55148c3726669b44237157e9`
- Git-loaded baseline core.py: `d137bd76e938283611e47acad4eec5bf8b706f9f3e3dcf9d0b264ba5df4196d8` from `56ccc46d1458dd7df257b68d296616eb34014c58`.
- Correctness outcome vector: `275ddf715397ddf10ed6192715135c6fc0fba236094c37e2ebf734530ea90ab8`.

Input SHA-256:

- small: `abbc3bea50542109da2d9a93e80e8a20daca759a4f6c0dcb60feb2af2fbbe76c`
- chain512: `b36bfe3f55343f0cbcf4608910fcf471c215647596b3cadf68bad969e523e945`
- chain1000: `12c5a417b67e132acda0870fb84d2bdf23cfae44346f4a7abf87dd124ef76772`
- star512: `6bfce143ec0bade2ffa50294ed79657703cffb0ca2fd263f246fb4bb83a29578`
- dense1000: `35d7d2fd5a9f25208eaf7bedaa5345201455c300ab0656642f5452af2e2f2748`

Limitations: finite synthetic workload acceptance, no real-workload, model/token/cost/GPU or backend deployment conclusion; noisy shared local CPU environment, no dedicated machine guarantee. This direct host-dispatched separate reviewer is not an installed ResultValidationHandler/ReviewSession/supervisor. Full repository and Reader regression plus integration/publication review remain required. Further production-code or harness changes invalidate these exact code/data conclusions.

## Final integration and publication-scope review

Verdict: **approve** exact bounded change for ordinary publication after main freshness/integration checks. Read the final two persistent regressions and report/T11 Progress; independently executed both new regressions (2/2 pass), with no further performance run. Actual full-suite/Reader logs match test-summary SHA and summaries:1179 total,1171 pass/8 skipped; Reader3/3. core.py and check.py remain identical to independently measured artifacts. Report matches raw producer/reviewer medians, rejects v1, preserves noise/fallback costs, leaves broader continuous goal unfinished and makes no model/GPU/backend claim.

The supplemental-file reference initially pointed to absent files; faithfully exported the already-executed inline source and observed exit0/output to supplemental.py/supplemental.json under explicitly expanded write authorization. Their JSON identifies an export, not a fresh execution. No invented or additional timing data. Report reference is now supported.

Publication scope: core.py, the two tests, T11 Progress and this run's explicitly listed evidence/report/source files only; preserve unrelated research checkpoints, exclude human guide/SGLang paths and avoid publishing full logs when only test-summary is intended. No remote main publication/readback has yet been accepted by this reviewer; root owns freshness checks and exact remote SHA/tree verification.

Integration artifacts SHA-256:

- `agent_runtime/core.py`: `ebb82f1b5f2529f7ebf89ba64a2e61dc3938ef437b9ce9d20c7cb49dc677b158`
- `agent_doc/results/dag-cycle-20261013-1601/check.py`: `cbc5fbb7bfda141696e628516de701a791dc1e730dd651d0b41833843d25d428`
- `tests/test_task_runtime.py`: `4819c53745f2f1299f5829bd9ac5e5543c41f842ce7bd6a140b98d3b5b367589`
- `agent_doc/task/task_details/T11.md`: `8fcc503c3ad82f86ecaa9e2f501c8d1b03db90b368dbb627018a78e90ce5945f`
- `agent_doc/results/dag-cycle-20261013-1601/report.md`: `18db6a9541896ed5d2e593bb51529b194d5677aa834f6b5323d1b15cddc3980f`
- `agent_doc/results/dag-cycle-20261013-1601/test-summary.json`: `5f5640fabb2deccc029af46d600177be14a9f5a7b4ef75209255920c3b2433c7`
- `agent_doc/results/dag-cycle-20261013-1601/supplemental.py`: `9073fb521d7015cd76c19c5c44beab6eee970500f564c41c28a1ce3a82352302`
- `agent_doc/results/dag-cycle-20261013-1601/supplemental.json`: `8e2b914edc90113a6eb243fb0914da0f29401e8e06e0e25435fab6edaf56439b`
