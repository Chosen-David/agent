# CompactionBench reading

Version: Microsoft Research October2026 preprint, official PDF SHA256 `58a3d5c6e0e817f59d7345973dba8fb3b7abe0819e2f66b0be3667cb445029b5`; no verified arXiv identifier. Title/authors/URL are in source.json and the frozen PDF.

Coverage: all15 logical pages; §§1–7, A/A.1/B/B.1, Tables1–6, Figures1–6 captions/extracted labels, Algorithms1–3, Equations1–3, references. Only page7 was visually inspected.

Method: APEC asynchronously summarizes contiguous snapshots into an epoch-local append-only prefix, retaining recent/post-snapshot history. Soft/hard thresholds and synchronous epoch reset govern overlap; summaries started but unapplied still cost money. Budget B excludes earlier summaries and later growth.

Evaluation: eight release transitions/four repositories/315 predetermined requests, five trials; final source-patch tests, task accuracy weighted by test count. Local Git-history shortcuts and generated test changes are excluded. Main400K/128K context/output settings, GPT5.6Sol extra-high; GPT5.4 and budget/1M sensitivities differ in coverage.

Ablations/limits: PEC costs less; Prune-H finishes sooner; APEC has highest main accuracy. No reported paired noninferiority/confidence intervals. Single-epoch analytical assumptions exclude variable growth/retries/eviction/behavior changes. Page7 snapshot equality and tail-budget wording conflict with appendix/other definitions; preserve ambiguities. No author-run reproduction or exact implementation correspondence established.

Repository decision: retain cache-aware, multi-turn executable acceptance questions; defer new compaction/backend policy. Existing dependency-bound memory, lossless packets and frozen resource gates remain authoritative. No repository speed, quality, cost or completion claim.
