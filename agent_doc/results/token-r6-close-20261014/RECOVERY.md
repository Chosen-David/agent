# Round06 continuation, 2026-10-14

Status: **candidate only; do not push while required project-doc validation fails**.

Tested source: `0f1383788fa31c759b8279fd5f7590a28420958f`, isolated checkout; original checkout untouched. No local commit or main push was made. The only tracked candidate changes append scoped evidence to TOK-FIFTY and fifty_rounds; new diagnostics live under this result directory. Runtime code is unchanged. The complete candidate, patch, raw logs and this recovery note are preserved together.

The old Round06 implementation commit is `76ca7b134dcdc4462ea354f99d54d5eecd0e7b0a`. All its 94 delivery paths match fetched main byte for byte; see historical-remote-readback.json. This is a source-delivery check, not proof that current repository validation passes. Four archived dependencies have CRLF while current files have LF; normalized content is identical, and git diff from the implementation commit is empty. Never rewrite the archived bytes or label those four snapshots byte-identical to current files.

Measurements: trace-audit.json is a fresh audit of **old** October 12 provider observations, deduplicated by native thread/turn IDs, not a new paid experiment. There are no provider internal request IDs. The two observed turns total 31,160 tokens (input 30,782, output 378; reasoning 52 is already included in output; cached input/cache-write 0). Native durations are 10,448/10,891 ms, single observations only. All-role cost, all-role latency, receiver history attribution and internal provider retries are unknown. No real author → figures → visualization → review chain is available in this scoped evidence; no hotspot ranking is justified. Existing Mailbox usage is explicitly stored-envelope bytes, not model billing, and EFF consumer-owned gates remain unchanged.

cpu-raw.json is new local CPU data: 432,269 source bytes, 2,048 ordered IDs, nine transport assertions; full/dictionary frame lengths 440,814/155,224 bytes in the original temporary root. This is neither tokenizer evidence nor LLM semantic/citation QA. Median complete encode/serialize/fresh-source restore costs are 5,754,430/7,865,444 ns; retain the added CPU overhead. Independent replay confirms all assertions with separate timing samples, which do not replace the producer's raw data.

Required regression: unittest.log reports 1,182 completed, 1,181 passed, one existing opt-in tmux skip; reader.log reports 3 passed; sync.log is empty with successful exit. project-docs.log records exit 2. Independent review reproduced this on the untouched main TASK. task-format-blockers.json names two malformed checked rows; a complete repair must also check index/detail coverage and identities, not merely fix those two links. No checks were weakened. No optional runtime/supervisor was installed to eliminate the pre-existing opt-in skip.

CI observation: no .github/workflows paths in the tested tree; connected combined-status lookup returned an empty statuses list. Direct Actions API returned Forbidden. This is **not CI green** or proof that no external check exists.

Resume:

1. Read AGENTS, current decision/project-document protocols and current canonical TASK. Fetch main into a clean isolated checkout. Preserve other owners' changes and all old result bytes.
2. Apply the bundled candidate patch with `git apply --check` first; if current evidence/paths have changed, reconcile rather than overwrite. The archive also contains exact candidate files and hashes.
3. Reconcile an explicitly bounded TASK-format/coverage repair with the current task owner and independent reviewer. Do not mark unknown historical tasks completed. Do not weaken the parser or drop orphan details to make validation green.
4. Recheck source/evidence deltas, rerun project_docs validation and any affected required checks. Old local CPU timings do not certify a new implementation; remeasure only if influencing code changes.
5. Independently verify the full candidate and mandatory checks. Only then fetch/integrate/retest as needed, stage exact authorized files, commit, ordinary non-force push main, and read back SHA/content/CI. On push timeout inspect remote before retrying.

This run counts zero new mechanisms and zero new verified savings. Original R6 short-pair savings remain limited to the frozen old model fixture. Continuous TOK-FIFTY remains unfinished.
