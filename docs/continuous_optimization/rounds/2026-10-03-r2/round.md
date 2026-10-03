# Round r2 — observable host evaluation pipeline

Status: validated for direct main publication. Resolve the publishing commit with the procedure in `state.json`; this file alone is not proof of remote publication.

## Baseline and scope

Research phase read main 4439900; implementation began after fast-forward pull to e72e0cfc0d9223f5d5b0dc273f3a5d41a12c5e3b. A second fresh pull found concurrent role/runtime changes and advanced to a223ffca305cd7dac1b6b5195c04c532179b84a4. Preserve those commits, including the 14th code-organization role, supervisor and experiment contracts. Before release, another fast-forward to a3906ead554ab8ae84b9e3e777732e2f9d94c460 adds an optional GPU adapter. Independent [impact audit](evidence/main-impact-a3906ea.md) verifies all 19 task/input records and 89 declared loaded dependencies: only the implementation case loaded changed rules. That CPU case is rerun on a3906ea; the other 18 retain their explicit a223ffc provenance. This is qualified dependency-based reuse, not a claim that every role was rerun on every commit. Role instructions are not changed by this round. SGLang remains untouched.

The concrete defect was that input preparation alone did not distinguish execution, artifact production, independent acceptance and missing work. Add a stdlib recorder with pinned source/input/rubric/implementation hashes, actual host start/collection receipts, exact required criteria, collected-artifact references and a fixed denominator. Retain every attempt. The host actually invokes repository roles; the portable Python recorder does not pretend it can spawn this chat host's workers.

## Research and decisions

Ten-paper primary-source reading, method/experiment/ablation/cost limitations and pinned upstream code are recorded in [papers.md](papers.md) and the deduplicated [ledger](../../papers.json). The most useful combination is task terminal-state checks (prior τ-bench reading), task/execution/scorer separation (AgentBench/Inspect), and explicit failures/recovery rather than success self-reports. AWM's step-level gains with worse whole-task results reinforce keeping final-task acceptance separate from tool/skill activation.

Adopt CO-005 only after program and actual host-task gates. CO-006 bounded feedback repair, CO-007 selective skill loading, CO-008 accepted workflow memory and CO-009 utility/security remain hypotheses awaiting controlled experiments. Do not install upstream Agent runtimes or copy their entire prompts.

## Evidence layers

Program results and failures are in [evidence/program_summary.json](evidence/program_summary.json). Initial prototype independent checks exposed nine false accepts; a later pair exposed ancestor-directory symlinks. All failures are retained. The final 25/25 cases reject the invalid records and keep the valid control, with no unhandled exceptions. These are prototype development tests, not an old/new released-Agent success-rate A/B. After the first concurrent-main integration, 207 repository tests and 3 reader tests passed. The final GPU-adapter integration passes 221 repository tests; reader sources are unchanged and their 3 tests remain applicable. Exact logs and the independent impact review are retained.

Model-task results are recorded separately. Earlier e72 runs include ungradable process clauses when only worker accounts were available. A later reviewer replay validates an artifact but cannot prove an earlier worker action. The recovered writer used a contemporaneous host tool proxy and passed on attempt two; first-pass remained false. On new main, required process actions use actual worker requests, controller tool execution, raw results and return-to-worker records before delivery, then fresh-context independent review. Shared filesystem/context instructions are not a security sandbox; records are trusted host observations, not cryptographic attestation.

A new full 19-case cycle targets all 14 current roles, two main-AI entries, a real producer→writer transfer and an additional travel revision input. The code-organization upstream case named no target and had zero fixtures; supply a small synthetic directory and preserve its existing criteria. Real producer bytes, not a prefilled answer, become writer inputs. Missing dynamic fixture names caused one preparation to be aborted before dispatch; that record is retained and a fresh corrected manifest was made.

Final independent acceptance is **19 effective cases / 60 exact required criteria, all passed**. There are 20 accepted records: the implementation case is repeated after the last concurrent-main change and the later record is selected. All 18 other cases retain their original pin. The [case matrix](evidence/model_summary.json) names every source revision and grader. This is a finite synthetic smoke result, not an estimate of general success probability. Although the selected current manifests pass on their first attempts, historical process-evidence failures and writer recovery remain in the record; they are not erased by starting new manifests.

The complete round used 37 started/collected executor episodes plus one cancelled dispatch before start, within the 40-dispatch executor budget. Reviewers were separate fresh contexts. Exact provider model identity, token and monetary usage are unavailable. The repository's role/skill files were actually loaded by host workers; these workers are supplied by the current host, not a separately deployed model service inside this repository.

The [current archive](evidence/model-current.json) contains inputs, actual outputs, grades, host observations and local HTML screenshots; the [historical archive](evidence/model-history.json) retains superseded and unsuccessful records. Repeated source snapshots are omitted and reconstructed from pinned Git objects. [Reproduction instructions](evidence/reproduce.md) explain a replay that verifies artifact/source hashes and all three complete reports without calling a model. That replay actually passed, with [saved reports](evidence/replayed-reports.json). Archives together are about 5.4 MB and exclude papers, browser binaries and fonts.

Browser capability recovery is independent of task quality: initial Playwright browser download was invalid; an official Chrome for Testing binary was used temporarily. Missing host CJK fonts were corrected with a temporary official Noto font. Actual local HTML browser checks block HTTP(S); no live model backend or external service is asserted.

## Boundaries and continuation

No exact provider model snapshot, seed, token or monetary telemetry is exposed; unavailable fields remain null. No strict model-matched A/B, real scientific/travel success-rate estimate, GPU run or live third-party backend integration is claimed. This smoke suite is synthetic and small. General-main routing and actual cross-role handoff are covered, but a full normal/boundary/recovery/adversarial cycle for every role is not yet complete.

The existing host session performs bounded execution; no new automation or background monitor is created. The newly merged persistent supervisor has no current-chain host action adapter, so it is not represented as running. The state file remains an audit checkpoint, not a distributed lock.

Next: controlled behavior-change trials with held-out tasks and fixed model/tool/budget, plus request/version-bound consumer acceptance (CO-002). Preserve the pipeline and failure records; do not infer convergence from one passing suite.
