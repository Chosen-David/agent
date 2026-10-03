# Round r2: host-driven evaluation pipeline

Baseline: e72e0cfc0d9223f5d5b0dc273f3a5d41a12c5e3b; fast-forward pull completed before modification. Read-only research at 4439900 remains valid for upstream mechanisms; code-reading and paper delivery entry points changed and are re-read/retested on new main.

User aligned implementation after the ten-paper design report and explicitly requires validated direct main publication to complete this round. Scope: add a stdlib host-driven evaluation lifecycle (freeze → host execution → collect → independent grading → fixed-denominator report), not an external runtime or modifications to role prompts. This closes the concrete gap where prepare-only cannot distinguish prepared, executed, graded, and accepted.

Pre-registered acceptance: immutable source/input hashes, complete required criteria, distinct executor/grader, actual host receipts, fixed task denominator; empty/missing grading and edited outputs cannot pass. Independent boundary cases must reject invalid evidence and accept valid controls. Run all 13 registered roles, two general-main cases and a new coordinator→writer chain plus new travel revision case. All required checks must pass before publishing. Retain failed attempts and their causes; unknown model identity/token counts remain null, no performance claims.

Budget: this implementation/validation stage <=120 minutes target, <=40 executor episodes and <=20 grading episodes, <=3 model workers concurrently (implementation/review workers separately tracked); no new paid provider/GPU/runtime. Host time limits advisory unless cancellation confirmed. New experiments beyond this bounded pipeline are queued.

Baseline tests: existing root and reader suites; new program tests distinguish lifecycle and evidence handling. Infrastructure change does not alter agent prompts: do not invent a model-quality A/B. Report new model smoke separately from historical or source-paper results. Role failures must be investigated; no changing original rubric to manufacture success.

Publication: reread remote main, preserve concurrent commits, rerun impacted validation if tree changes, non-force fast-forward push main, then read back SHA and content. No PR or extra upgrade branch.

## Concurrent main update, 2026-10-03 07:15 UTC

Fresh fetch/pull advanced main to a223ffca305cd7dac1b6b5195c04c532179b84a4. It adds task supervision, experiment contracts, exemplar guidance and code-organization (14 roles). Earlier e72 runs remain historical, including process-evidence ungradable verdicts; they are not reused as latest-source passes. Freeze a new full 19-case suite (14 roles + 2 main + 2 handoff nodes + 1 travel holdout), retaining the same criteria for existing cases. The new code-organization case receives a synthetic directory because upstream's zero-fixture prompt did not identify an actual target. Preserve the original upstream criteria.

The snapshot explicit allowlist now includes agent_runtime and the new locally referenced validation scripts; no runtime backend/monitor is claimed active. Execute required process actions through a contemporaneous trusted-host tool proxy when raw worker tool export is unavailable. This changes observation, not role instructions or score thresholds. Retain raw proxy results, failed attempts, and first/final distinction. All execution remains within the original 40-episode / 120-minute bounded target; no additional automation created.

## Final concurrent-main check

Another fast-forward to a3906ead554ab8ae84b9e3e777732e2f9d94c460 preserved the optional GPU adapter. Independent impact review verified 19 task/input records and 89 declared loaded dependencies. Only implementation loaded changed rules; rerun that case on the new pin with unchanged rubric, CPU tests and a fresh grader. The remaining 18 cases retain a223ffc provenance. Root tests on the integrated candidate:221 passed. A subsequent pre-publication pull reported main up to date. Final publication still uses a non-forced update and remote content verification.
