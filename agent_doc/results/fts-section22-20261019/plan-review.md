# FTS-SECTION-22 independent manual plan review

Current decision after Plan v2 follow-up: **approve for the bounded manual engineering plan only**. The initial revise decision and its complete findings are retained below. Native managed/runtime approval remains blocked, not approved.

This is a bounded, separate-context advisory review by `/root/fts22_plan_review`, not a native ReviewSession receipt, authenticated runtime gate, experiment validation, publication approval, or claim that tmux supervision exists. Native host integration remains unavailable. No code edits, tests, benchmarks, or guide writes were performed in this review. Only this assigned report was written.

## Initial frozen review target (v1)

- Project: `/workspace/scratch/88c3234ecfbc/agent-memory`.
- Observed HEAD: `de05d95c725029cca53239f0eb6e0f63d4fb9c19`.
- Task: `agent_doc/task/task_details/FTS-SECTION-22.md`.
- Whole task file SHA-256: `5ca3115369ea520f14d306228093aa97666b6c9acbf39c7af045879b49558599`.
- Stable task prefix before the `## Progress` line, including its trailing newline: `974f45865d8128d57b7a555fc042e3f8192e3b5370bf4fa3cf68239ded8a6fe4`.
- TASK index SHA-256: `0c8b9274cf532343b198db4c5f2c1e328a7bf581b61ba11de6b825488f50ce1c`.
- `agent_runtime/knowledge_index.py`: `5266ec9a760ecd34419b2bc0b574a199d2901daee7f217b7f627ca2ba95a9e7e`.
- Empty human-only `agent_doc/guide/GUIDE.md`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Read-only `agent_doc/guide/README.md`: `f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261`.
- Retained `agent_doc/results/memory-storage-20261015/research.md`: `58b505a0847363c5e79ce33c90537fe3058467794a9034eb2afe2b9f2bde6315`.

Reviewed AGENTS, decision_review, project_document_workflow, dual_main_workflow, result_validation_workflow, current task/index entry, guide files, full knowledge_index implementation, relevant knowledge.py tokenization/get/ref paths, current knowledge-index tests, existing build benchmark pattern, and the retained 12-paper matrix. User authorization is supplied in the parent handoff; this review does not independently authenticate the underlying user message. The worktree already contained main-owned TASK/detail edits. Guide diff was empty.

## Seven gates

| Gate | Verdict | Reason |
| --- | --- | --- |
| intent | pass | A same-interface, exact-result CPU optimization is consistent with the supplied authorization to publish only measured gains. No GPU, SGLang, TwoLevel, model or retrieval-policy changes are proposed. |
| guide | pass | GUIDE is empty, README states directory governance rather than project objectives; both were read without mutation. The task preserves human-only ownership and main-only TASK/source authorship. |
| assumptions | pass | `_terms` is a pure NFKC/casefold/set operation; baseline computes it once per section for sorting and again for the selected at-most-two sections. Reusing that overlap is semantically justified. Exact top-two selection can preserve `(-overlap,start_line)` ordering. Benefit remains a hypothesis until full-search measurements. |
| prior_results | unknown | The retained 12-paper matrix exists and distinguishes prior reading from new work. Current prior-result/knowledge-search outputs and new source notes were not present as reviewable artifacts. Parent reports actual queries and promises persistence, but those messages do not substitute for pinned evidence. |
| acceptance | fail | Numerical thresholds, full-output differential oracle, warmups, whole-search timing, boundary coverage and independent reruns are suitable. However, the required pre-measurement six-criterion validation-plan artifact and common result contract/independent owner are not frozen. Timing sample/summary terminology also needs one unambiguous definition. |
| risk | pass | Scope is a small local implementation with unchanged schema/index engine, no cross-request cache or knowledge mutations, measured non-regression, preservation of failed data, and no publication of a failed implementation. Alias-only, empty-body, ties, Unicode and fence boundaries are included. |
| resources | pass | Bounded 45 minutes, at most two local candidates, CPU/SQLite and no paid API are proportionate. This is only manual-work feasibility; native ReviewSession/tmux capability is explicitly blocked and this report cannot clear that block. |

## Blocking revisions

### R1 — Persist and bind the evidence inputs

Location: task Plan paragraphs on prior results and research; result directory.

Before implementation/measurement, save actual result-store and knowledge-search query/response evidence, including `partial=true`, missing-record errors, candidate IDs, and explicit applicability/rejection reasons. Parent supplied the queries `knowledge indexed search section ranking latency` (`--limit 3 --max-scan 500`) and `bounded top k exact heap selection` (`--limit 3`). If the original outputs cannot be recovered, label a new read-only invocation as a repeated search; do not imply its timestamp is the original planning-time search. Persist the current official heapq and MemScope source notes with precise versions/locators and distinguish source observations from local hypotheses. Bind these exact paths/hashes in the reviewed plan evidence. The historical 12-paper document may be reused as historical research, not claimed as 12 newly read papers or proof of local latency benefit.

Recheck: independently read the saved bytes; confirm partial results remain partial, no nonmatching historical run is used for present latency acceptance, and no contradictory new candidate changes the implementation premise.

### R2 — Freeze the executable acceptance contract before data

Location: task Plan acceptance paragraphs and a new validation-plan artifact owned by main.

Create an `experiment-validation-plan/v1` artifact with the declared scope and all six required criteria, each carrying procedure, acceptance and `allow_not_applicable`. Bind its actual SHA-256 into the common producer/validation/consumer contract; identify producer and a distinct real independent verification owner, manifest/result identity, and preserve raw data as pending until that verification. Manual evidence must not be labelled as a native authenticated receipt.

Specify whether the protocol is seven alternating AB/BA pairs or seven four-call ABBA blocks, the exact order, and whether the primary statistic is ratio of per-arm medians or median paired ratios. Freeze this before the first sample. Include all per-sample observations, dispersion/order effects, environment and current dependency/source hashes. The task's target thresholds remain unchanged: both 512-word 1/2-section scenarios must improve at least 15%; each other timed scenario satisfies the stated `max(1.15 * baseline, baseline + 0.5 ms)` allowance. Full JSON equality remains mandatory for every comparison; no aggregate score can hide a failing case.

Recheck: read the frozen contract/plan and confirm it agrees with task and runner before any measurement. Independent result review must inspect actual runner/control flow and rerun the required real plus synthetic 1/2/256-section cases; producer exit status alone is insufficient.

## Nonblocking implementation cautions

- Keep only overlap counts, not all token sets, if possible. A decorated tuple that can fall through to dictionary comparison on exact ties should be avoided; an explicit key preserves ordering safely.
- `sections` provides monotonically increasing start lines, but preserve stable tie semantics rather than relying on accidental object comparison. Zero-overlap filtering and the 900-character literal excerpt truncation must remain unchanged.
- One/two-section large-body cases are the most direct duplicate-tokenization benefit; 256-section cases test whether heap overhead/selection scaling causes regression. No claim of universal speedup follows from these synthetic cases.
- The existing build benchmark has a different timing contract. A dedicated full-search runner is appropriate; baseline imports shared current dependencies only if they remain unchanged and hashed.
- Both current and mirrored copies must pass isolated-package checks. The plan's phrase 'mirror sync' should be verified by actual changed-path inventory, not assumed.
- A 45-minute cap is a stopping condition, not permission to skip independent acceptance or publish an inconclusive candidate. Any second candidate must preserve the first result and receive separate identities/hashes.

## Next owner/action

Planner-main closes R1/R2 and returns the revised stable task/evidence hashes for a bounded follow-up review. No source-code alternative or broadened scope is requested. Native managed dispatch/publication integration remains blocked until a real trusted host adapter exists; this manual report must never be replayed as such a receipt.

## Plan v2 follow-up — current advisory decision

Read the complete revised task, saved search responses and new research notes before any production-code edit was reported. Frozen identities:

- Whole task file: `9e021acb75c3be577d1c3ddde0dd51e35d9bf4ba195fc43171276b97fb93014c`.
- Stable prefix before `## Progress`: `571697b18cd6139400ba791993db5c757d46790df1dc17a7be10d7d11799065e`.
- TASK index remains `0c8b9274cf532343b198db4c5f2c1e328a7bf581b61ba11de6b825488f50ce1c`.
- `.agent-runs/fts-section22/prior.json`: `57da19383d3c7ef0e785dfd34b2a1c655c4ce1a312d0fcf2e2de4dc8ce8ff06c`.
- `.agent-runs/fts-section22/knowledge.json`: `f4931bb3489edfeac35e2dda3bb542b92f3ac6ead1d904b930adc161cb80d54b`.
- `agent_doc/results/fts-section22-20261019/research.md`: `fb73cbd44243a17ffb8531edc4d305a00f2aa9615d6311bf874f1ca004dbcb88`.

R1 is closed for this bounded review: actual saved search lists 231 scanned directories, three stated candidates, `partial=true`, and the missing-record errors. Research notes explicitly distinguish the earlier 230-directory search from the later persisted search, reject the old measurements, and do not claim the historical twelve-paper reading occurred anew. Retrieved knowledge is learning/vector-search material, not direct evidence for this lexical optimization. Source notes provide exact primary-source versions/locations; this reviewer inspected those notes, not the external pages, and does not certify their paper interpretation.

R2 is closed **for manual engineering acceptance only**: Plan v2 itself is now the frozen, hashed manual validation artifact. It declares producer, distinct future review owner, pending-to-scoped-acceptance dependency, all six procedures/acceptances with no N/A, exact seven-pair order, and ratio-of-medians statistic. The independent result review must still happen before consumers/publication. This is deliberately `manual-result-validation/v1`, not the repository's machine-readable `experiment-validation-plan/v1`; it is not a substitute for that native contract, manifest or trusted provider and cannot pass an Engine/ReviewSession gate. R2's machine-contract portion therefore remains part of the explicit native-host blocker, not silently represented as implemented.

Current seven-gate verdict for the explicitly manual scope: intent **pass**, guide **pass**, assumptions **pass**, prior_results **pass**, acceptance **pass**, risk **pass**, resources **pass**. No remaining blocking finding in the local optimization/measurement design. All nonblocking implementation cautions above remain relevant. Keep actual performance claims pending until independent data/code validation and all required regressions; this approval provides no measured-gain claim or publication acceptance.

Next owner is planner-main for the already-authorized bounded implementation and measurement, subject to the user's authority and host permissions. The absent native host adapter remains a separately reported capability blocker. A changed stable Plan, threshold, input scope or interpretation requires another versioned review rather than reuse of these hashes.

## Final pre-measurement binding follow-up

Planner-main then supplied the requested actual `experiment-validation-plan/v1` file and explicit evidence bindings. I read the changed stable-plan suffix and complete validation file. It contains all six required criteria, each with procedure, acceptance and `allow_not_applicable=false`; the thresholds and exact comparison protocol agree with the reviewed design. The task clarifies that its earlier manual schema label describes the review record and does not replace this file. Producer, validator and consumer are explicitly required to bind the same validation-plan hash.

Current **approve** decision for bounded manual engineering is reaffirmed against these final bytes:

- Whole task SHA-256: `6a13b9c86593dfdbcd33be95d1bdc0ac15734142a0d2eee881df3cdc5ba3f3b2`.
- Stable prefix SHA-256: `b1318599c07a88bc45f384c0a6dd382926fbd3e3e7fadc5dc2b117ab66d4232e`.
- Validation plan SHA-256: `ecb9e58363d3d2071c38170ded5a91a219784b6c2bb95f7a8b6760f95dbf0808`.

R1 and R2 are now fully closed as plan/evidence-document findings. The preceding note about an absent machine-readable validation-plan artifact is superseded by this observed file; the actual trusted host adapter, runtime receipt, result manifest, executed independent validation and performance outcome remain absent/pending rather than implied by its existence. All seven manual-scope gates remain pass. No experiments were run or production sources edited by this reviewer.
