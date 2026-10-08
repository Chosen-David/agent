# Direct alias-context repair and Freedman continuation

Task-ID: EK-20261008-0915 (continued, not a replacement ID).
Budget: until2026-10-08 12:57 UTC, zero GPU/paid work.

Diagnosis: docs includes aliases, chunks includes title/summary only. Short Chinese entries discoverable through English curated aliases may lack a third RRF lane. Minimal candidate adds existing aliases to section context and bumps the actual engine version for deterministic cache rebuild; RRF/query fixtures/expected IDs/thresholds unchanged. Alias-only matches do not promise a matching body excerpt. No query-specific rule or schema-v2 claim.

DAG: safe sync + holdout/reuse -> independent plan review -> baseline complete commands and independently frozen new tests -> minimal implementation/cache+package tests -> same corpus repaired retrieval -> unchanged-science Freedman integration -> full queries/tests and independent code/data acceptance -> fetch/integrate affected reruns -> nonforce main/remote/CI. Root owns shared metadata/TASK; independent reviewer owns independent_* files. No runtime supervisor installation claimed.

Hard acceptance: original english-alias/sqlite raw Recall@3 restored and no per-query raw/context/abstain deterioration versus historical38d3764, concurrent59ad8d9 and this round's2325e3d with matching settings. Report inherited failures; raw Recall@3/MRR never replaced by context or averages. Explicit default context3 and historical supplemental context8 evaluations are separate. Existing file-backend morphology limitations stay separate from SQLite. If new regressions cannot be resolved without broadening scope, preserve candidate with full evidence rather than publish. Independent new cases frozen before execution; repairs do not become newly unseen first-pass successes.

Plan reviewer /root/retrieval_plan approved the scoped repair before edits; scientific Fre​​edman text remains identical to archived reviewed candidate. Old neuro blocked state is independent. Independent result verification still required.

## Version 2 bounded repair

Independent retrieval_plan approved testing aliases only on generic sections(d)[0], retaining old title/summary context elsewhere. V1 restored target raw rank but regressed plural-residual context1→0, saved in repair-only-comparison.json and exact implementation/patch. Unique engine fts5-porter-alias-first-section-v4 invalidates both v2 and experimental v3 caches. Same frozen cases and all168 historical/current comparisons required; no release approval implied.
