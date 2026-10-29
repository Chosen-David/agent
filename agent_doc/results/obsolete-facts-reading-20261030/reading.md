# Obsolete facts: retrieval coverage is not correction adoption

**Source:** Poikarayil et al., *When Retrieval Is Not Enough: Obsolete Facts in Agent Memory*, [arXiv:2610.36308v1](https://arxiv.org/html/2610.36308v1), 26 October 2026. Read main §§1–4, appendices A–J, Tables1–20 and Figures1–2 captions; author checklistK also inspected. Cached normalized text was read in full across two continuations, not counted twice. No PDF image inspection, author-code execution, raw-output reproduction or repository performance measurement.

## Method and controlled comparison

MemoryAgentBench Conflict_Resolution uses synthetic numbered statements: higher numbers replace lower conflicting statements about the same relation. The6K source has455statements/100questions; reconstructed chains contain at most two statements, with74conflict/26no-conflict questions. The32K source has2310statements/100questions. This artificial chronology is an evaluation convention, not a source of authority for human guides or permissions.

BM25 ranks individual statements, packs to the evidence-token budget and restores chronological order. The post-hoc support audit uses benchmark gold to identify the intended latest statement; it is a diagnostic, not deployable retrieval. For each of74conflict questions, A contains latest+three unrelated statements and B substitutes the old competing statement for one of those distractors. Both contain four statements; mean prompt tokens differ by less than one, rather than being exactly token-identical. Distractors are deterministic, exclude update-chain values and have zero question content-word overlap. Their semantic irrelevance was not independently established here.

The same74questions informed prompt development/pilot and final intervention. Freezing the prompt protects the within-cohort paired contrast but does not create held-out confirmation. Models are Ollama qwen2.5:7b-instruct and qwen3:14b; final controlled and corrected32K runs use temperature0, seed42, num_ctx2048 and num_predict64, with Qwen3 think=false. Earlier full6K uses num_ctx16384; question-only, oracle and6KBM25 use4096. The exact GPU and quantization metadata were unavailable; model tags are not immutable weight digests.

## Findings and qualifications

| Comparison | Reported result | Acceptance limit |
|---|---|---|
|6K BM25 budget64/128/256/512|45/40/36/32 correct out of100; latest support100/100 at every budget|Old and latest already present in all74conflict contexts at every budget. Growth does not newly introduce the competitor.|
|6K paired64vs512|14losses,1gain;29always correct,49always wrong across all four budgets,22mixed|Aggregate decline is not monotonic deterioration for each question.|
|Qwen2.5 equal-size A/B|74/74vs33/74;41A-only,0B-only|Official substring metric/classifier; same development cohort.|
|Qwen3 equal-size A/B|74/74vs65/74;9A-only,0B-only|Same family and different model size/decoding mode; not a controlled cause of robustness.|
|32K corrected BM25 endpoints|69/100vs58/100;18losses,7gains|No valid full-history32K baseline; evidence alone~37.5Ktokens exceeds attempted8192 and advertised32768context.|

Conflict-stratified6K accuracy25.7→12.2%, versus no-conflict100→88.5%, is observational because conflict status is a question property. A97% gold-assisted isolated diagnostic uses different selection/prompt and must not be called a deployable97% solution or compared as a fair method improvement. Question-only19% versus fullhistory37% also changes prompt; the authors reject a causal memory-effect interpretation.

Earlier abstaining-prompt experiments are exploratory: latest-only53/100, latest+three unrelated65/100, old+latest11/74 and old+latest+two unrelated9/74. High UNKNOWN rates motivated the final prompt. These results cannot be pooled with the frozen non-abstaining intervention.

At32K, automated chain support98/100 and99/100 differs from direct literal gold support100/100 at both budgets. The validated63conflict questions have chain support63/63; two ambiguous template attachments are excluded only from clean subgroup/sensitivity analyses. Clean no-conflict35questions yield34/35→35/35. Overall sensitivityn98 gives69/98→57/98 with18losses,6gains,51both-correct and23both-wrong; it does not replace official100question scores.

## Scoring, exclusions and uncertainty

The official normalized substring metric has both a false negative (goalie/goaltender) and a false positive (rugby union contains gold rugby while matching the obsolete value). Correcting the latter would change32K margins to68/100 and57/100, without changing paired discordance because the response is the same at both budgets.

The manual audit selected20cases, including13principal harmful flips; all13sampled flips directly selected old values. This is not a manual audit of all50officially classified flips. A subsequent line review found two mixed Qwen2.5 answers: France-capital in A and Our Mutual Friend in B contain both old/latest strings and are officially classified latest. Strictly counting mixed answers non-latest gives73/74vs32/74, retaining41A-only/0B-only and the same exact McNemar value, but changing discordant membership: the mixed France-capital A case drops out and the mixed Our Mutual Friend B case enters. Under that strict comparison one of41discordant B answers is mixed, not pure stale. Thus “all50stale flips” requires the official-classifier qualification.

Initial Qwen3 thinking-mode outputs exhausted the64token allowance before usable final answers and are excluded; corrected20b disables thinking. Context-overrun full-history32K is also excluded; corrected21b contains BM25 only. Gold-assisted audits and earlier UNKNOWN experiments remain diagnostic/exploratory. J.2 describes the authors’ raw/summary consistency checks; we did not reproduce them.

Exact paired McNemar tests describe this benchmark instance, whose questions share a history. They do not establish population-level independent-history effects. Only two same-family models, deterministic decoding, synthetic single-hop chains and lexical retrieval were tested. Old values often match familiar pretrained knowledge while newer synthetic values contradict it; temporal obsolescence alone is not isolated. No attention-allocation, prior-strength or decoding mechanism is proved. Dense retrieval, multi-hop dependencies and full systems such as Mem0 remain untested. No complete compute bill or repository latency/cost improvement follows from the paper.

## Relationship to this repository

Current MemoryLedger already records corrections as new revisions, marks old entries superseded and descendants stale, and preserves raw history. correct documents that source must identify the actual user statement; its visible implementation validates source text but does not authenticate the user. accept records caller-supplied acceptance rather than independently judging scientific truth. reconcile reports health signals without deleting records.

Adopt only a future evaluation distinction: current evidence retrieved, obsolete evidence co-retrieved, final version actually used, semantic/mixed-answer validity, paired gains/losses, and complete input/output costs for all roles. Existing claim selection preserves declared dependencies and candidate/rejected claims; exact payload budgets do not certify semantic relevance or actual provider inputs. No new repository defect or performance gain was established by this reading.

Defer automatic memory deletion/retirement, a new memory store, default context shortening or agent_doc migration. Do not turn numbered recency into permission, discard dissent/dependencies to imitate the diagnostic, or count retrieval/hash validation as final task success. SYSTEM-99 real-host loading, full-input capture, final task quality, all-role costs and concurrent recovery remain open.

Formal ID search scanned341directories with25errors, partialfalse/statusincomplete and no hits; this is not exhaustive proof of absence. Knowledge lexical candidates matched generic “memory” topics (QLoRA/HNSW/FlashAttention) and were rejected as inapplicable; knowledge_refs[]. Historical registration remains unknown, not a trusted runtime receipt. Partial and completed reading together count at most one paper after independent acceptance and publication/readback.
