# Independent primary-source and code review: ICR reading checkpoint

Task: SYSTEM-99, ongoing Plan54. Project root: `/workspace/scratch/95d615402a52/agent-run-1202`. Reviewed HEAD: `489f299f99515a70be4cf65a34bdf1e75aa8d9af`. Review completed 2026-10-28, before the dispatched deadline 2026-10-28T15:21:32Z.

## Decision and boundary

**ACCEPT, usable-with-scope: the frozen reading record accurately represents the inspected paper and the inspected implementation. No blocking correction to these two frozen reading artifacts was found.** This accepts a literature/source-reading checkpoint, not SYSTEM-99 completion, experimental results, a production change, or a protected runtime plan approval. The system-level real-host, full-model-input, all-actor-cost, task-quality and ownership requirements remain unfinished. Runtime authentication and total role cost remain unknown. This report is not a trusted ReviewSession receipt or evidence of a native host integration.

Reviewed immutable artifacts:

- `agent_doc/results/icr-reading-20261028/reading.md`: SHA-256 `041867ea81845de0a635e498f18d502649b4230b7b7b176035858db1b72b4590`.
- `agent_doc/results/icr-reading-20261028/inputs.json`: SHA-256 `ad62fef48d416087ef19e562cbf4e6f529e2aa99b21a9a54a92ca1aa276c7c6e`.

The earlier 2200 partial read and 2300 completion concern **one paper**, 2610.01042v1. Subject to the main author's accepted public publication/readback, the existing same-batch count may move from 30 to 31 exactly once. This review neither writes that count nor starts a new batch. The requirement is ten fresh bodies in the same ongoing batch, not ten per wake. No old consumed/paused full-suite, PID, alias, role, codex or model gate is reopened. No missing prototype is rebuilt.

## Independent source inspection before comparison

I first read the actual cached primary-paper text, then formed the following findings, before opening the frozen reading.md/inputs.json for comparison:

1. Section 3 specifies frozen independent initial trajectories, three agents/six directed pairs, and single-hop revisions without propagation. Independence of generation is not independence of errors. CR and PR condition on different initial correctness strata; SR/SCR describe the remaining strata. SI gives equal weight to CR/PR and is not an internal truth-recognition certificate. Aggregate accuracy requires all four stratum weights on the same population.
2. No Message is another reasoning opportunity with the same receiver prior, not Keep Initial. Paired gain/loss counts are needed to identify net communication-associated differences. A high correction rate alone can hide damage to correct receivers.
3. The channel adaptations differ in exposed information, delivery and computation. Full Text excludes thinking; LatentMAS teacher-forces the complete trajectory including thinking and adds ten latent steps; StateBridge uses at most 64 selected hidden states with documented fallback/alignment. These comparisons cannot isolate an intrinsic representation effect or reproduce complete native systems.
4. The strongest descriptive Full Text versus Answer Only pattern is higher correction and lower preservation across four main tasks. All four SI-difference intervals include zero. The GSM8K CR-difference interval touches zero; four PR decreases exclude zero. Neither unresolved SI differences nor random-mixture differences establish equivalence. Sender answer matching is observational, not proof of message adoption.
5. The 4B retained audit is 430 questions/2580 directions across four tasks, with 840 mixed directions. MedQA/ARC-C/GSM8K/GPQA-D CR and PR denominators are respectively 116/98/92/114 each. The 8B experiment measures only model-specific mixed directions, with 92/108 events per stratum on MedQA/GPQA-D, so cross-model paired claims would be invalid. Six directions are correlated views, not six independent replications.
6. Full-set accuracy is imputed. The 4B estimates extrapolate incomplete all-correct observations; MedQA StateBridge has none. The 8B estimates instead assume unchanged receiver correctness on every unobserved direction, including both-incorrect and both-correct directions. Historical A↔B sampling and interrupted GPQA coverage are not documented probability samples. Full-set confidence intervals would be unjustified under the available information.
7. HumanEval+ uses a custom subprocess/test-field scorer with a ten-second whole-question limit, not the official EvalPlus harness. A post-hoc serial execution changes correctness on one question while published strata retain original scores. Its 28 CR and 28 PR directions are small; it also provides an exception to the main-task pattern that all communication reduces PR versus No Message.
8. Logged receiver times and prompt tokens are incomplete cost observations. Worker concurrency/contention differs, latent-prefix work is omitted from prompt accounting, construction timing is incomplete, and exported zero LatentMAS payload conflicts with actual KV-prefix delivery. No controlled throughput, speedup or end-to-end cost ranking follows.
9. Bootstrap intervals preserve question clusters and condition pairing but do not cover unseen generation seeds. Historical token limits changed during collection; exact execution source snapshots are missing; MedQA subset selection/source IDs and GPQA option-permutation provenance are unavailable; no separate documented development split exists. Truncation exclusions describe selected populations, with revision-truncation exclusions being post-revision selection.

The frozen reading subsequently proved consistent with these findings. In particular, it preserves negative outcomes and differences between the 4B/8B imputation assumptions, distinguishes marginal versus paired bootstrap analyses, and rejects universal prompt/channel/performance adoption.

## Actual inspected source scope

Primary source: *Beyond Final Accuracy: Auditing Communication in LLM Multi-Agent Systems*, arXiv 2610.01042v1, by Shixuan Li, Wei Yang, Peiyu Zhang, Anzhe Cheng, Heng Ping and Paul Bogdan. The cached abstract metadata and submission-history text confirm 2026-10-01 04:34:59 UTC.

I read the cached `paper.txt` sequentially over **Unicode character offsets [0,37202) and [47922,104706)**, including abstract, main Sections 1–5, appendices A–J, Tables 1–24 and figure captions in those ranges. The file is 104706 Unicode characters/105697 UTF-8 bytes; these are character offsets, not byte offsets. Reference-list prose between the body and appendix was not credited as body reading. The declared old/new reading ranges in inputs.json jointly cover these body/appendix ranges. The end range includes the HTML conversion/footer text; that boilerplate is not additional scientific reading.

I verified the bytes/hashes of cached primary HTML, text and abstract HTML against inputs.json and the dispatch:

- `.agent-runs/continuation-2200/paper.html`: `bade3a6b84d92e903d0bd8360be91d4781a8f46e3fe47561a3601f7183f263d1`.
- `.agent-runs/continuation-2200/paper.txt`: `82f9c23e41f06039af3a33e2574ff429e1381962b4303b41688483258a419b61`.
- `.agent-runs/continuation-2200/abstract.html`: `32d740d58ede49075923d46e0c1a00324b2c1211f9cdd0c4b2ad0d6e6347e74b`.

The substantive paper reading used the actual cached text; HTML was hash-checked, and abstract HTML metadata/submission history were parsed. I did not visually render HTML/PDF figures, inspect the author code, obtain raw per-question model records, or reproduce any generation, scoring or bootstrap experiment. Hash consistency establishes frozen identity, not correctness of the authors' experimental data or the remote origin independently of the cached evidence.

Repository inspection comprised AGENTS.md, prompts/review_main.md, prompts/decision_review.md, workflows/dual_main_workflow.md, workflows/knowledge_access_workflow.md, the relevant authority/ownership portions of workflows/project_document_workflow.md, the communication workflow text, TASK's SYSTEM-99 entry, SYSTEM-99 Plan54 identity/initial requirements and relevant recent Progress. I did not conduct a complete scientific/operational re-review of every historical SYSTEM-99 stage or the full execution DAG.

The guide inventory contains an empty GUIDE.md (SHA `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`) and README.md (SHA `f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261`). I read README.md; it explicitly describes its one-time AI origin and does not supply project-specific requirements. I did not invent human approval/content for the empty guide. The entire guide directory was read-only.

Actual code inspected: communication.py lines 271–479 (inbox, inbox_index, read_pending, acknowledge, status, consume_handoff, impact, prepare_context, usage); handoff_basis.py lines 88–350 (claim validation, basis requirements, dependency impact, selected-context closure and hydration checks); project_memory.py lines 179–229 and 284–344 (dependency/status checking and correction/acceptance behavior). Definitions were also located with rg. This was static source review, not test execution.

- consume_handoff revalidates event references, loads the manifest with the expected SHA, checks run/producer/input and independent consumer scope, checks basis, and binds parsed record/request immutably. ACK is separate.
- ACK is immutable handling evidence and does not set task completion. impact reads registered consumed bases and reports affected recipients/claims; it sends no correction or task action.
- Inbox pagination/filtering retains message kinds; it does not establish global clearance, cross-page snapshot consistency or single-consumer ownership. The frozen text explicitly leaves these responsibilities with the host.
- Basis checks validate declared dependencies/premise records, not scientific truth. Context selection preserves selected ancestors, required claims and all candidate/rejected claims. Memory checks reject stale/superseded dependency chains; correction preserves historical evidence and stales descendants.
- The workflow requires saved revision intent, successful publish before needs_revision ACK, and subsequent semantic revalidation; it expressly disclaims transaction atomicity/exactly-once external effects. No new defect requiring a second implementation was established in this reading review.

All seven repo_refs and both supporting query/search artifact hashes in inputs.json matched the current files. The TASK and SYSTEM-99 pins identify the pre-publication snapshot, not a promise that a later authorized Progress append will retain the same whole-file hash.

## Independent knowledge and prior-evidence checks

I actually invoked the existing local corpus interface, without tests or model/backend probes:

`python -m agent_runtime.knowledge --root knowledge search 'communication revision correction preservation paired bootstrap cost' --limit 5`

The command returned files-lexical-v1 snapshot `767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18`. Short candidates/assumptions were inspected and rejected for this task: infra.speculative-acceptance v1 `d713b2280b1b43dc109b635df3a522f92a5f3fc657dc719137402f8877c05b6a` and ai.speculative-decoding-cost-bound v1 `b292c27e53687be2f8f04ad8e19be77db1eb4a286b3218df6621fc97cd861c5f` concern speculative token decoding, not semantic multi-agent communication; math.finite-menu-selection v1 `12a6934e379b7392d9272dcec55abdbc148464d435ed4ae437955b0f5dfa85b8` requires a frozen calibrated iid candidate menu absent here; math.paired-bilinear-risk v1 `0afa7f23f4b80cf3865ab01cd8d33296885bd2e093898f3b878ec27609824c8b` concerns bilinear score risk, not paired categorical answer transitions; ai.speculative-sampling-residual-exactness v1 `3014215db96bf6ed7a00d522bf68663e58c4d1e98bdc2b88efe85ccd1a012331` concerns token-distribution residual correction, not semantic correctness. None was adopted as a guarantee, so **knowledge_refs=[]**. Candidate summaries suffice to reject these mismatched mappings; no full theorem/dependency application is claimed.

I independently checked the recorded producer knowledge query and result-search artifact hashes/content. The existing result search reports query 2610.01042, 325 scanned directories, zero hits, 25 missing-record errors, status=incomplete and partial=false. This is not evidence of corpus completeness or absence of old readings. No prior empirical result was adopted or used to bypass validation. I did not rerun or repair this historical catalog search.

## Checks and remaining blockers

| Domain | Checkpoint assessment | Evidence/limit |
|---|---|---|
| intent | pass | Continues one paper in the same unfinished batch; no changed goal or production action. |
| guide | pass | Empty guide not treated as approval; directory read-only; unique TASK and project paths preserved. |
| assumptions | pass within reading scope | Channel interfaces, audit population, imputation, scoring and statistical limitations retained. |
| prior_results | pass within reading scope | Incomplete search correctly disclosed, no empirical reuse; actual independent knowledge query rejects mismatched candidates. |
| acceptance | pass for manual reading only | Actual paper and selected code support the frozen prose; no experimental reproduction or protected runtime approval claimed. |
| risk | pass within reading scope | No production edits, tests, backend/model probes, migrations, retries, new subagents, messages or lock operations. |
| resources | unknown for runtime/total billing | One actual independent-role invocation; total input/output/reasoning tokens and monetary cost unavailable. This cannot certify a hard all-role budget or runtime dispatch. |

Blocking issues for this **reading checkpoint**: none. Blocking/unfinished issues for broader SYSTEM-99 acceptance remain real-host integration, complete actual model input, all-actor usage/cost, final task quality and concurrent ownership/recovery evidence. Those are not closed by this review, hash matches, ACK semantics or the paper's benchmark results. No new authorization, service, performance claim or budget reset is inferred.

Only this assigned review file was intentionally written. Parent-held lock 61993 was not touched. No tests, experiment/model/backend probes, subagents or messages to other roles were started. The independent reviewer is an actual AI invocation and is not zero-cost; exact all-role token/cost accounting remains unknown. This complete response is preserved for the main author to consume without replacing it with a bare pass label.
