# CONTEXT-SCHEMA-83 independent review

Verdict: **usable-with-scope**. Candidate meets the frozen synthetic CPU performance gates in both producer and independent runs, and the inspected compatibility boundaries pass. This is an independent host-agent review, not a ManagedEngine/ReviewSession receipt or a universal correctness guarantee. Publication remains the main agent's responsibility after its required integration checks.

Reviewer: `/root/schema83_review`, independent execution context; baseline `fad3bd48ba108b90a8e36ecafd5bf2462207c8bd`. Read AGENTS, decision review, result validation and project document workflows, frozen plan, production diff, measure.py and new regression tests. Prior-result query/read: previous context81 review and current memory-context/schema tests informed compatibility checks; old timing numbers were not reused as acceptance data. Writes limited to this directory's independent* and review.md; no production/TASK edits or push.

## Implementation and reference boundaries

The 10-line production diff adds an original-reader identity sentinel and supplies a local schema-state list only when that reader and an ordinary transaction/row/text factory are present. Existing closure routing guards remain. A custom reader receives schema_state=None through _walk, which invokes _get and then its original two-argument call. The context81 two-argument and same-connection DROP TABLE counterexamples therefore retain uncached behavior; new regression tests explicitly execute both. State is local to each _context_closure transaction, including cached absence; entry values, status and document validity checks are not cached. Normal SQLite read transaction prevents external schema changes from being observed midway through this closure.

Independent commands (all with PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.):
- `python agent_doc/results/context-schema83/measure.py > agent_doc/results/context-schema83/independent.json`
- `python -m unittest discover -s tests -p 'test_memory*.py' -v`: 60 passed, independent-tests.log.
- `python -m unittest discover -s tests -p 'test_handoff_basis.py' -v`: 20 passed, independent-handoff.log.
- `python agent_doc/results/context-schema83/independent-boundaries.py`: 10 baseline/candidate differential cases passed; complete outputs or exact exception class/message compared. Cases: diamond/shared parent, table absent, unknown ID, empty refs, duplicate refs, malformed scope before stale status, stale ancestor, malformed document binding, cycle, missing dependency. Script and JSON retained.

Existing tests also cover custom public check, custom walk legacy signature, Row fallback, known leaf/ancestor inclusion, correction freshness, current document validity and present/absent/cross-call schema freshness. These checks preserve declared behavior; they do not prove compatibility with arbitrary monkeypatching of every Python/SQLite dependency. Public check's existing caching behavior is outside this diff and unchanged.

## Measurement and data checks

The harness extracts baseline _context_closure from the pinned Git source, while other code is identical for both arms. Timing covers complete basis_context calls, synthetic linear chains/content128/max_chars200000; warmup3, seed83 randomized AB/BA order, 21 samples/arm, five calls/sample. Entire output compared before timings and the last call of every sample; not every one of its five calls. All three accepted measurement files (original raw.json, serial.json, independent.json) contain 21 finite positive ns samples/arm/case, matching input hashes and candidate SHA. Independently recomputed medians, reductions and threshold results match the recorded values. No failure samples omitted by the harness (exceptions abort it).

| Nodes | Serial producer reduction | Independent before ns | Independent after ns | Independent reduction | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 | -2.705% | 586290.2 | 577643.2 | 1.475% | pass >= -10% |
| 32 | 5.218% | 1488516.6 | 1507004.2 | -1.242% | pass >= -10% |
| 256 | 6.068% | 5618999.0 | 5217205.8 | 7.151% | pass >= 5% |
| 512 | 7.622% | 10221706.4 | 9563697.8 | 6.437% | pass >= 5% |

Numerical sanity/data integrity/reproducibility: pass for these recorded runs and thresholds. The 1-node case does not invoke closure and is a noise control. The 32-node difference changes sign and 512-node magnitude varies across runs; no confidence interval or statistical-significance claim is made. These are warm local synthetic measurements, not production workloads, network/model/API benchmarks, or a guaranteed production benefit. The initial independent run overlapped the main agent's full test suite. It is retained as independent-concurrent.json, SHA256 3308dba50b25f0e84efec6c0e9ff9735f7afc1baa428a3e6bbebd0891689c993, and excluded from acceptance. After the main agent reported all 1321 tests complete and paused other work, the reviewer reran the identical frozen command sequentially; this table and independent.json use that clean rerun. This was an interference correction, not selection on outcome; both runs met the fixed gates. Environment versions/platform are recorded in both JSON files; detailed CPU allocation/interference controls are absent, limiting extrapolation.

## Frozen evidence hashes (SHA256)

- project_memory.py: `7e27062b2c37f6116337de2f399b10072820fc2fe1763b16769691ebb4ce6fc2`
- handoff_basis.py: `b2355dab0b097b54ad9c4818ce955b3e46a3f4b11c3175f169d717f2166ac50b`
- test_memory_closure_schema.py: `4baf026fb03b3bb727823b9e7700730f7432d5a8f26c6369d4c17b3b87096783`
- plan.md: `4b1c8ebd7f9ec26473169f773aa307bc4d04465ffdb634e5d9c2c69d8f049c54`
- measure.py: `e5d7dc8891d45c6de6853cffaa56ef766f8ea9dce70903f6cb93deb301f01b57`
- raw.json: `42fefd507ca98ff3891c7d5164527ebf75c683d22bb13c9be8a669b08396234f`
- independent.json: `dc0df19170bbe57fcc0fd1262604e32a0f0c711e94ad7d1259a8b63617b301a2`

## Final serial producer check

Main agent subsequently reran the frozen harness without concurrent tests as serial.json; independently recomputed all 21-sample medians/reductions, compared input and candidate hashes, and verified all four unchanged gates. The table uses serial.json and the clean independent.json. Original raw.json remains preserved; the main agent reports it preceded the full test suite, but its timing ordering was not independently observable. Acceptance does not need that ordering because the two later serial runs both pass. serial.json SHA256: `1e31026207dcfe1cef718aaf0abf23456bffad12f1e594f5f28c377ef3b2a2b4`.

Read main full-test log ../schema83-full.log: 1321 tests, 8 skipped, OK. Main reports Reader3 and optimized-Python memory60 passed; those are additional main-agent checks, not reviewer reruns. `git diff --check` passed. Final scoped verdict remains usable-with-scope for the source hash above and these declared compatibility/performance boundaries.
