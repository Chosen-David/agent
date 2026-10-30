# 2610.31778v1

Read main1–5, Appendix6.1–6.11.2, six prompts, Tables1–3 and Figures1–11 captions; exact HTML/text hashes: source.json. No visual QA or author-code reproduction.

Method: fixed OpenCode, shared token trigger; self-summary versus output pruning, disk offload, old-reasoning removal and Haiku summaries. Appendix retains ten recent reasoning turns.

Experiments: three PaperBench papers use Code-Dev grading without reproduction; ProgramBench accuracy uses two tasks, erosion adds Lua; PostTrainBench uses two bases×three targets. Two successful runs/configuration; attempts continue until enough successes. Main scores condition on valid submissions; PostTrain violations excluded. Thresholds160–380K cover different model-relative windows. Wide intervals do not establish noninferiority; some offload/thinking/small-summary settings regress, Gemini rarely compacts.

Constraints: summary retention differs from obedience; hacking starts before compaction. SWE-chat44sessions/269validated constraints has judge-dependent loss19%/24.5%; three contradictions count dropped. Figure11 excludes one no-majority case, denominator268. Constraint-level Wilson intervals do not establish session-level independence or downstream compliance.

Repository: retain existing authority/dependency closure and test actual loading, corrections, constraint compliance, final quality and all-role costs separately. Disk availability is insufficient. No new pool, compactor, backend retry or migration adopted; existing negative StageI evidence remains. Cost/performance and deployed-host benefits are unmeasured.
