# Independent source and repository review — Trust Layer reading

Decision: **accept, usable only within the reading scope below**. No blocking correction to frozen `reading.md` / `inputs.json` is required. This accepts a paper-reading record, not the paper's unresolved data, an empirical reproduction, a trusted runtime ReviewSession, production quality, publication, or completion of SYSTEM-99.

Task: SYSTEM-99 / Plan54, same logical batch. Project: `/workspace/scratch/95d615402a52/agent-run-1202`; dispatched HEAD `2ec7fcd597c458a11438fa4eaf90af88a125d6a3`. This independent invocation read the primary first and formed the findings below before opening the frozen producer record. Preliminary findings were sent to the parent before that comparison. No second reviewer, retry, delegation, test, model/backend experiment, monitor, or lock operation was performed. Parent retains the single-writer task/publication responsibility and lock ownership.

## Exact inspected source and identity

All supplied hashes and all six repository pins in `inputs.json` matched actual bytes. Text length is **58,580 Unicode characters / 58,961 UTF-8 bytes**; the two measures are different and are not token usage.

| Artifact | Actual SHA-256 |
|---|---|
| `.agent-runs/continuation-0200/paper.txt` | `d5689007d86c6568974cc36e9e66885893a5f0c7e3fed328611c05abd7259520` |
| `.agent-runs/continuation-0200/paper.html` | `ab72802feff7a8e95af71d7b446477a710188390a1eb9363e57bc705e80ccdcb` |
| `.agent-runs/continuation-0200/abstract.html` | `4345ea58939d766adcdcec11d340ffea46315903d8ddb71d676f76ee97a3de5f` |
| `agent_doc/results/trust-layer-reading-20261029/reading.md` | `96c0e088f8bafa3d63830803d474927929c3bba6ea62a13a94cd4b850b8bc7e4` |
| `agent_doc/results/trust-layer-reading-20261029/inputs.json` | `6300586de31558a915735ae750df623238c8b561102a4319c2f8f82a72358ddc` |

Actual primary: *A Trust Layer for Agent Evaluation*, arXiv:2610.07274v1, https://arxiv.org/html/2610.07274v1. Saved abstract submission history independently identifies v1 as 2026-10-05 19:15:37 UTC. Inspected normalized text across [0,58580): main §§1–5 and Limitations end at 38606; references [38606,43694) were inspected only as bibliographic material; appendices A–F occupy the remaining source before the HTML footer. This covers methods, experimental claims, Tables1–14, and Figure1 caption. References, navigation, and footer do not become body-reading credit. HTML was checked for identity and the exact disputed §4.2/all108 and §4.6/deterministic-dimensions passages. No PDF, image rendering, author implementation, raw per-task trajectories, original graders, underlying model runs, or statistical reproduction was inspected or claimed. The primary says code will be released upon acceptance; no repository lead is upgraded into inspected author code.

Producer range accounting combines the 0200 partial [0,25000) and 0300 completion [25000,42500), [42500,58580) as one paper. They overlap references/footer only as disclosed; they do not create extra papers. Current recoverable public count remains32 until accepted review plus actual public readback; that can establish33, not an additional independent-review count or a new-batch credit.

## Independent primary findings and comparison

1. **D1 is conditional on model labels.** §3.1 uses majority-of-three LLM gate typing, including critical/process/administrative distinctions, before deterministic re-execution/matching/challenge rules. Gate agreement (1078 gates;94.1% unanimous;96.8% across two passes) is consistency, not human-ground-truth accuracy. AppendixA preserves strict upgrade conditions; no experimental upgrade occurred. The reading correctly distinguishes partial-score threshold disagreements from pass/fail grader disagreements and does not relax required output formats. Calling D1/D4 wholly judge-free from Table11 would be wrong; the reading explicitly rejects that interpretation.

2. **Unresolved D1/D2 cohort-band mismatch is real in the supplied v1.** Table6/Table8 D1 bands versus Table9 **assessed** bands are MetaMuse22/37/38 versus19/41/37; GPT-Sol23/36/38 versus21/38/38; Opus24/33/40 versus22/36/39; Gemini18/25/54 versus16/27/54. Sonnet15/36/46 matches. Table9's separate Tasks column totals108 and is not the comparator used here. These differing97-task band compositions are unexplained under §4.1's same97/same11-excluded description. The reading preserves the exact discrepancy instead of inventing snapshots, exclusions, threshold repairs, or reconciled raw IDs. That is the proper scoped treatment.

3. **§4.2's all108 statement remains unresolved.** The paper says five grader executions on each saved output yield identical verdict/band on all108, while §4.1 says11 cannot be graded offline. This could involve identical no-verdict outcomes, but the actual scope is not established. The reading correctly retains the uncertainty;108 valid re-grades cannot be inferred.

4. **D2 establishes limited provenance evidence.** Reference answers select values offline; literal/untraced values are reviewed, task-permitted direct answers may clear, and fabrication dominates convictions. Executed constants/file-level arrays can look derived. The36/38 versus2/45 injection result demonstrates this blind spot; it does not prove authentic computation for cleared runs. Sonnet14 hand-checked gamed cases do not validate precision across all five configurations; no-verdict3–28 must remain visible. The reading correctly keeps denominator/missingness, judge dependence, laundering, and lack of author code limitations.

5. **D3 measures an operational false report.** It compares terminal claims with D1 re-grading; unknown re-grades do not establish a confirmed false claim. D3 depends on D1, and its second judge stage is an adjudication, not independent truth. The Sonnet annotation statistics are limited validation. Neither a false statement nor a no-confirmed-lie result establishes intention or actual task success. The reading preserves these distinctions.

6. **D4 is a conditional and sampled stability predicate.** It excludes classified infrastructure failures; the exact excluded counts, classification errors, and zero-valid-repeat behavior are not established here. The50-task set was drawn from Sonnet's87 five-repeat completions and independently rerun; it is not a direct subset of the same repeat outcomes. Sonnet25.3% versus46% must both remain. Stable only means surviving repeats occupy one band:16/181 stable cases occupy a different band from the original, including four original passes. That is not reproduction of recorded success or infrastructure-inclusive end-to-end reliability. Band-conditioned drift is partly constrained by endpoint bands. The reading's cautions are appropriate; no missing handling rule is invented.

7. **Conjunction and ablation are reported with their actual scope.** Table5's19/84=22.6% and author Wilson95%15.0–32.6 describe recorded passes among the selected50×five configurations; they do not establish an independent84-unit population experiment. Same-task cross-model dependence, completion selection, and differing band mixes prevent a global deployment CI claim here. D1 alone50→D1+D4 34→all19 is a sequential overlapping-filter result, not15 independent causal additions nor wholly label-free34. Per-model intervals overlap; these data do not justify agent rankings. The reading is explicit on all these points.

8. **Transfer and cost limits are preserved.** One ALE study plus accessible artifacts is not validation on SWE-bench/other benchmarks or this repository. D1–D3 are not zero-cost merely because agent execution is reused; judges and offline work still cost resources, and D4 adds agent runs. No all-actor billing/usage evidence establishes total cost or a repository benefit. The reading correctly adopts evaluation distinctions only and defers new scoring infrastructure, default three-judge calls, automatic five-run retries, or architectural migration.

No source issue above is repaired by the reading; all remain limits on the paper's claims and on future use. They do not block an accurate reading record that preserves them.

## Repository code and workflow review

Read applicable root AGENTS, project-document, dual-main, knowledge-access and result-validation guidance; inspected current empty `agent_doc/guide/GUIDE.md`, TASK SYSTEM-99 status and corresponding detail material. The human-only guide directory remains untouched. Current task index marks SYSTEM-99 unfinished and preserves Plan54/consumed-gate limitations. This review writes only its assigned runtime artifact.

Actual inspected code: `agent_runtime/result_validation.py` (contract/dependency validation, snapshots, artifact roles and hashes, independent review checks, inspect_result, live binding checks, consumer hooks, handler) and `scripts/validate_experiment_result.py`; actual inspected protocol: `workflows/result_validation_workflow.md`. Their hashes match `inputs.json`.

The reading's mapping is supported: the declared producer→independent verify_experiment_result→consumer chain must carry the same contract; producer and gate owner differ. Snapshots require code/inputs/config/raw_data/outputs/environment roles, contextual six-domain criteria, scope and exact bindings. `inspect_result` uses the host-supplied callback; unavailable/exception/pending callbacks cannot grant usability. Review schema/actor fields are necessary structural conditions, not authenticated independence by themselves. Bindings and revocation are checked around review and subsequently, but reads do not form an atomic action fence. Durable proof alone cannot reinstate callback trust. The CLI imports only an explicitly selected trusted adapter, not a worker JSON command; context display does not grant acceptance. These are framework controls, not implemented paper-specific grader replay, answer provenance, claim truth, or repeated-agent evaluation. No test or runtime deployment claim follows from static reading.

## Independent knowledge and prior-result handling

Actual independent command: `python -m agent_runtime.knowledge --root knowledge search 'independent validation repeated measurements dependence uncertainty provenance' --limit 3`. Real corpus snapshot: `767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18`, files-lexical-v1, applicability unchecked. Hits were math.hoeffding-bounded-mean, math.paired-bilinear-risk, algo.rl-spurious-reward-regimes. Independently opened `math.hoeffding-bounded-mean` with the existing show CLI; its version1/hash is `5da6b4040a6e6a838eb37d080b36b230e91ffc22d752146b888604f77a3aea0a`, no strong dependencies. Its independent fixed-sample bounded-variable assumptions are not established for selected repeated task×model observations. Rejected as a quantitative guarantee; paired-bilinear and RL training objects mismatch this audit and were not used. Adopted `knowledge_refs=[]`. No knowledge theorem certifies majority voting or five-run stability.

Read the actual saved prior-result-search JSON; its pin `597bc8727dc1e9132e14cf2fd45027cf4094f010d8c267085a6ce7243ebf122d` matches, query2610.07274 scanned327 with0hits,25missing-record errors, status=incomplete and partial=false. This does not prove historical absence; no old pass or empirical result is reused. Did not rerun the old catalog. The producer knowledge-query pin also matched; this review's independent query was separate rather than relying on producer relevance judgments.

## Seven checks and final limits

| Check | Result | Reason |
|---|---|---|
| intent | pass within scope | Accurate source-reading completion supports the same unfinished SYSTEM-99 goal without replacement work. |
| guide | pass within scope | Empty pinned guide read; entire guide directory and unique TASK ownership preserved. |
| assumptions | pass within scope | Unknown labels, cohorts, sampling, dependency and cost are disclosed, not assumed valid. |
| prior_results | pass within scope | Actual incomplete saved search inspected; no historical acceptance reused. |
| acceptance | pass for reading only | Frozen body/appendix coverage, source identity, selected source-code mapping and unresolved issues independently match. |
| risk | pass within scope | No production change, automatic retry, model experiment, invented data repair or architecture migration. |
| resources | pass for bounded manual review; total cost unknown | One actual independent invocation; no resource reset/probe. No claim of measured all-role usage or budget-valid runtime receipt. |

This manual review is not an authenticated host ReviewSession and cannot approve protected dispatch or certify hard total-cost budgets. SYSTEM-99 real host/full inputs/final task quality/all-actor cost/ownership and concurrency/recovery remain open. All old full-suite/PID/alias/role/Codex/model/backend gates remain consumed or paused, not retried or reset. Public readback is still the parent's separate next action; this file alone does not advance the public count. Only Chosen-David/agent, in-place scope and unchanged historical failures remain binding.

A convenience HTML inspection script encountered missing optional bs4 before its hash/metadata section ran; no package was installed and no test was executed. The subsequent actual source/hash/metadata reads used standard-library operations. This tooling limitation does not concern author experiments or alter evidence.
