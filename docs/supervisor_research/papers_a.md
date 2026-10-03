# Supervisor research: primary-paper reading A

Run: `supervisor-upgrade-2026-10-03`; decision: EXECUTE, authorized research only. Read repository `AGENTS.md` and `prompts/decision_review.md`. No implementation, platform supervision, SGLang, credentials, or private data changed. The research-explore skill root was read; its referenced workflow resource returned an unavailable-resource error, so it is not claimed as read.

## Retrieval and scope

All five versioned **original PDFs** below were retrieved and read through the web PDF reader, including the indicated method, algorithm, experiment and limitation sections; these are not title/abstract-only entries. Page numbers are one-based PDF pages. Terminal `urllib.request.urlretrieve` attempts for the same PDFs failed with `Tunnel connection failed: 403 Forbidden`; consequently no local PDF hash or successful local download is claimed. The failed download log is ephemeral at `/tmp/supervisor-papers-a/downloads.json`. No complete paper is committed. The JSON manifest records exact URLs, versions, page counts and reading locations. This is targeted deep reading of key sections, not a claim of having inspected every appendix page. All numerical results below are **author-reported**, not locally reproduced experiments.

## A1 — ReAct

[Original PDF, 2210.03629v3, 2023-03-10](https://arxiv.org/pdf/2210.03629v3). Read §2–3, PDF pp.3–6, Tables 1–2; §4 opening p.7.

Method: interleave model decisions, tool actions and actual observations; observations support plan revision. PaLM-540B Table 1 gives HotpotQA exact match 27.4 for ReAct versus 29.4 for CoT; FEVER accuracy is 60.9 versus 56.3. Thus the paper does not establish universal superiority. The manually examined HotpotQA failures include repetitive actions and uninformative searches; the hybrid fallback uses bounded step counts. These are benchmark findings, not evidence that a perpetual worker will eventually succeed.

Transfer decision (engineering inference): preserve tool-result provenance separately from model assertions; record repeated action signatures and no-progress evidence; require a bounded retry/diagnostic transition. Do not treat the model's finish action as verified completion. Durable scheduling, authorization and crash recovery remain separate engineering requirements.

## A2 — Reflexion

[Original PDF, 2303.11366v4, 2023-10-10](https://arxiv.org/pdf/2303.11366v4). Read §3/Algorithm 1, pp.3–5; programming evaluation/Tables 1–3, pp.7–8; §5, p.9.

Method: actor, evaluator and reflection model feed bounded episodic feedback into later attempts, without weight updates. Coding generates and executes internal tests (at most six); memory can retain one experience. Python HumanEval reports 91.0 versus GPT-4 baseline 80.1; Python MBPP instead falls to 77.1 from 80.1. Internal-test false positives explain premature acceptance risk; API, impure and concurrent functions are named evaluation limitations. Algorithm 1 prints an `or` condition between failure and trial budget: copying that guard would not enforce a hard attempt cap.

Transfer decision: persist concise failure diagnoses with attempt/evidence IDs, but distinguish hypotheses from measured causes. Require an independent acceptance gate, hard budgets and explicit failed/blocked states. Implement retry eligibility as conjunction of unmet acceptance, remaining attempts and authorization. Episodic memory does not establish transaction durability or exactly-once effects.

## A3 — Tree of Thoughts

[Original PDF, 2305.10601v2, 2023-12-03](https://arxiv.org/pdf/2305.10601v2). Read §3 algorithms, pp.3–4; §4.1/Table 2, pp.5–6; §6, p.9.

Method: generate candidate intermediate states, evaluate them, then perform bounded BFS/DFS with pruning/backtracking. Game of 24 evaluates 100 comparatively hard instances (indices 901–1000), using GPT-4, temperature 0.7; width-five BFS reports 74% success versus 4% CoT and 49% best-of-100 CoT. Success requires a valid equation using each input number once. The authors restrict evidence to three small task families and note increased resource cost and unnecessary search for already-easy tasks.

Transfer decision: permit isolated alternative branches only after an authorized baseline and under fixed branch/attempt/cost budgets; retain candidate evidence and rollback identity. A model's heuristic score must not substitute for an executable terminal predicate. This study supports bounded search, not unlimited replanning, paid-compute authorization, or a choice of wall-clock supervision interval.

## A4 — LLMCompiler

[Original PDF, 2312.04511v3, 2024-06-05](https://arxiv.org/pdf/2312.04511v3). Read §3–4/Figure 2, pp.3–5; Table 1–2/experiment setup, p.6.

Method: planner produces a dependency DAG with output placeholders; a non-LLM fetching unit dispatches ready tasks and substitutes completed outputs; executor runs independent work concurrently. Intermediate results can trigger replanning. Table 1's GPT Movie Recommendation results: 5.47 seconds/77.13% for LLMCompiler versus 20.47 seconds/72.47% for improved-prompt ReAct. GPT HotpotQA is 62.00% versus 62.47%, so faster does not imply uniformly more accurate. The comparison uses benchmark-specific tools/prompts; latency headlines are not general service guarantees.

Transfer decision: separate planning from deterministic DAG validation/readiness and adapter execution; preserve independent ready branches when another blocks. Replanning should version the graph without replaying completed side effects. The paper's depicted memory/queue does not prove leases, durable recovery, event deduplication, cancellation or external scheduler readback. Those must be separately implemented and tested.

## A5 — Plan-and-Solve

[Original PDF, 2305.04091v3, 2023-05-26](https://arxiv.org/pdf/2305.04091v3). Read §2, pp.2–3; §3–4/Tables 1–4, pp.4–6; §7, p.9.

Method: first elicit a task decomposition, then solve it; PS+ explicitly tracks variables/calculations before answer extraction. Main experiments use text-davinci-003 with temperature zero across ten reasoning datasets. Six arithmetic datasets average 76.7% for PS+ versus 70.4% zero-shot CoT and 77.6% few-shot manual CoT; GSM8K alone is 59.3% versus 56.4%. Authors identify prompt sensitivity and remaining semantic misunderstandings; plan refinement is future work.

Transfer decision: require explicit subtask inputs, dependencies and acceptance criteria before execution; validate the decomposition rather than accepting fluent plans. Do not market a static prompting result as autonomous recovery or proven long-horizon planning. For this repository, a typed plan accepted from the host AI is an honest adapter boundary; unsupported model access must remain a detected capability gap.

## Cross-paper implementation requirements (our design, not paper-proven results)

1. Store task IDs, DAG version, prerequisites, authorized action scope, attempt budget and evidence predicates. Reject unknown dependencies and cycles before dispatch.
2. Use durable transitions and a transaction/lease boundary around ownership. Crash recovery must distinguish a lost worker from confirmed task failure; uncertain external side effects need reconciliation before replay.
3. Completion requires all required tasks' acceptance evidence and successful teardown/readback of the owned monitor. Blocked, failed and canceled are not synonyms for completed.
4. Persist scheduler identity and verify readback before reporting active supervision. A local process only runs while its host lives. These papers supply no authority to install a daemon or deploy infrastructure.
5. Let the host AI propose interval plus rationale from expected duration, event changes and risk; enforce backend and policy min/max limits, no-progress backoff, and retry caps deterministically. None of these five papers validates a particular wall-clock policy.
6. Fault-injection acceptance should cover restarts, duplicate event/tick IDs, stale leases, two workers, missing evidence, permission blocks, independent branch progress, user cancellation and terminal monitor stop. Label synthetic scheduler/handler tests separately from live integrations.

## Minimal falsifiable evaluation proposal

Use an identical finite DAG and deterministic fake clock/handlers for a serial baseline and the supervisor. Inject a crash after dispatch, duplicate ticks, overlapping worker claims, and one authorization-blocked branch. Required outcome: no unauthorized dispatch, no false done, preserved completed evidence, independent branch progress, bounded check count, and no owned active monitor after successful convergence/cancel. Measure dispatch count and recovery outcome; do not infer model quality or production availability from these synthetic tests.
