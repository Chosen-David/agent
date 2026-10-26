# Independent literature and static-source review

Decision: **approve, scoped to this literature/source checkpoint**. Reviewer: independently dispatched `/root/memory_cost_review_1455`, 2026-10-26. Project root: `/workspace/scratch/6416f20dc59b/agent-run-1303`; baseline `31a5b9c1607219db0947b4b5a2120f65395a07b3`.

No substantive correction is required in the reviewed reading note or inputs. This is neither an empirical result acceptance nor authorization to implement a new memory layer, run an experiment, reset a budget, or close SYSTEM-99.

## Actual reading coverage

Read AGENTS.md, the project-document authority/write-boundary workflow, decision-review protocol, result-validation workflow, the empty current GUIDE.md, relevant SYSTEM-99 Plan/Progress and its complete baseline diff, the current SYSTEM-99 TASK index entry, and the final reading.md/inputs.json. Historical SYSTEM-99 claims outside this checkpoint were not independently revalidated.

Read the preserved text of MemoryTax 2610.29823v1: abstract, full §§1–6, Tables 1–4, Figure 1–4 captions, Appendix A full results, B protocols and C answer/agent/judge prompts. Inspected HTML title, version/date, section and caption anchors against that text. Read Nano-Memory 2604.11628v1: abstract, full §§1–6 and ethics statement, main Tables 1–4, Appendix A.1–A.3 including Tables 5–6, B.1–B.3 including Table 7, C prompts, D.1–D.2 and E disclosure, and Figure 1–12 captions; inspected HTML title, version/date, section and caption anchors. No PDF page or image-pixel review was performed. Missing-label/blank table references in Nano-Memory B.1/B.2 were read as missing references, without invented numerical results. Reference lists were not independently followed.

Static source coverage: complete handoff_encoding.py, basis_context in handoff_basis.py, complete test_memory_tables.py and the referenced cache/parent test plus adjacent cache assertions in test_handoff_basis.py. These test bodies were read only, never executed.

## Claim checks

- MemoryTax versions/date, seven methods × three models, conv-26/419 turns/152 questions, single run per cell, writer-reader cross comparison and rounded Opus Pi 99%/$6.95 versus full context 95%/$17.84 match the source. These are author reports, not measurements in this repository.
- The caption confound is preserved: agents received captions while memory methods did not; 64 photo-evidence questions and 88 other questions are separate strata. The one-answer difference on the latter does not establish globally equivalent inputs or a general superiority claim. The note does not claim either.
- MemoryTax §2/Table 2 include store construction, LLM and embedding calls and cache pricing, exclude judge costs, and exclude embeddings from token counts. Appendix B explicitly reruns failed/answerless trials and counts only the accepted trial. The note correctly prevents treating the published amounts as the cost of all attempts, and its proposed all-actor/all-retry accounting is explicitly future methodology.
- Nano-Memory TIR scores sessions by the maximum query-turn similarity; QDP uses an additional filtering model and an original-token extraction prompt. Default generator/retriever/top-3 setup matches §4/A.3. Table 4 and Table 7 both give LoCoMo F1 15.76 → 19.62 → 22.66 and tokens 2348 → 2685 → 1403. Table 2 defines Avg.Tokens as generation-phase consumption; these numbers cannot establish complete pruning/construction/judge/all-call token costs. The note correctly preserves that boundary rather than inheriting the paper’s broader efficiency rhetoric.
- Nano-Memory Table 2 gives LongMemEval-s 4o-J 57.20 for Nano-Memory and 60.20 for MemGAS. A.2 defines Full History as the most recent 128k tokens; it is truncated on the million-token benchmark. §3.2’s zero answer-token overlap is a lexical statistic and cannot prove semantic irrelevance. The note accurately states both limitations and retains sequential pruning latency and privacy/interpretability limits.
- MEMORY_COLUMNS retains kind/content/source/scope/evidence/status/created_at/document_refs/deps/id, with strict exact field sets. Format selection retains complete decodable JSON candidates and observes caller budgets. basis_context reports serialized-payload usage only, checks memory freshness, retains candidate/rejected claims and declared ancestors, and treats known_memory_ids as a host assertion about already-held context. Source inspection cannot certify actual host possession or natural-language consumer behavior. The note makes that distinction.
- Read test bodies support the note’s description of mailbox round-trip/closure, correction invalidation and retaining an uncached parent when only the leaf is cached. No current runtime pass, semantic quality or performance is inferred from those bodies.

## Baseline and write-boundary checks

Every baseline_refs entry in inputs.json was independently hashed from `git show 31a5b9c1607219db0947b4b5a2120f65395a07b3:<path>` and matched. Current AGENTS, TASK, both source files and both referenced test files remain byte-identical to those baseline blobs. SYSTEM-99 differs only by one added paragraph after `## Progress`; its entire pre-Progress stable Plan is byte-identical. The empty guide was read, not edited. The foreign untracked zip was not opened or changed.

This review ran only file/source reads, git-show/diff/status and hash/document processing. No tests, model/backend/PID/ALIAS/role/Codex runs, budget reset or production change was performed. A failed optional BeautifulSoup import during HTML inspection produced no artifact or runtime conclusion; HTML anchors were inspected directly instead.

The root may register reading.md, inputs.json and this review through the existing register_history interface solely for discovery with contract null and validation unknown. Registration must not confer empirical trust. Reading-count recovery and historical installation CI claims in SYSTEM-99 remain outside this review; no ten-paper threshold, quality/cost gain or completed round is accepted here.

## Frozen reviewed bytes (SHA-256)

| File | SHA-256 |
| --- | --- |
| reading.md | bbc3b3a8e28e057fa1f5120307b767b16be9d7379f734723c9c5e99c34a9b4a8 |
| inputs.json | 143506c797d4fdc1809b0c6f76a9510c831c9f071cba3e405c4a05acc6358ed2 |
| current agent_doc/task/task_details/SYSTEM-99.md | 48d0c4eb569e0e5f86fa8679443a94483b462128421fb9534b689dbf52654e6a |
| 2610.29823v1.html | d3576e6f51512f5995304b97cc9eac942507cc97f14529824d92b777910d7b1c |
| 2610.29823v1.txt | 0e0d9da4fc919370adf47d2d4565f51c0b6f4e2d8177a36af8ef3f6109384af6 |
| 2604.11628v1.html | 3b7e85e1d5c921f6ac267521410c21c5e2f85d701a93dbb30b7eaa0bd579847d |
| 2604.11628v1.txt | 15d9bf478fbe22a13c2c2c1716ef9bc2d3836455ab960adf6e78a2ff0170709b |

Approval applies to these bytes and this scope; substantive later edits require renewed review.
