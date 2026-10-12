# Independent artifact lower-bound result review

Verdict: usable-with-scope for the declared artifact comparison CPU optimization. All six frozen validation-plan criteria pass. Complete repository regression is separately owned by the parent; its initial full-tests.log failure is preserved and its repaired rerun was still running when this report was written.

## Actual implementation and proof

Reviewed actual compare_artifacts source and all changed/new artifact tests. The guard executes only for non-full, multi-edit, changed-text comparisons with token_counter=None. The hypothetical patch reuses the already calculated base digest, shares the actual target reference and representation/schema keys, and contains exactly one edit with one-digit nonnegative coordinates and empty insert. Every real eligible edit candidate has at least one edit, its nonnegative integer coordinates cannot serialize shorter than one digit, its string cannot serialize shorter than the empty string, and extra edits only increase length. Therefore its serialized-character length is at least the bound. The current winner is replaced only by strictly shorter candidates; target <= bound safely preserves the winner, including ties. The hypothetical candidate is never emitted or restored. The prior unique-single-line guard remains available when the size bound does not apply. Counter mode bypasses both guards; full/disabled/equal modes retain their eligibility behavior. The selection metric remains JSON character count, not UTF-8 byte count.

## Independent checks and raw results

Read measure.py rather than trusting its exit code. Its baseline source is read from git commit f8c92dc15bd948f0b50f748991cac782a913af0a and loaded as a separate module. The full public entry includes current file reads, hash verification, serialization and selection. The 1229 input cases comprise 225 binary-line exhaustive pairs, 1000 fixed-seed randomized changes, and four 2048/2049-line and 65536/65537-character boundary cases. Each runs character selection and two callback modes. A separate-process rerun generated independent-measurement.json: all 3687 comparisons matched exact packets and restored both original texts.

A separately authored independent-oracle.py constructs full/splice/edit/identical candidates directly, computes splice prefix/suffix independently, uses SequenceMatcher for edit opcodes, and minimizes complete serialized packets with stable ties. It exhaustively checks 169 pairs containing Unicode, CRLF, quotes and backslashes across eight full/multi-edit/reuse flag combinations and two selection metrics: 2704 exact packet/recovery checks passed. Explicit equality-at-lower-bound and counted-mode edit preference assertions passed. This oracle shares Python's standard SequenceMatcher and serializer, so it is independent selection/guard verification, not an independent diff algorithm or JSON implementation.

Seven alternating warm complete-entry timing pairs use exactly old='x\n'*2048 and new='x\n'*2046. Source and workload hashes match both measurement files. Independently recomputed all medians, finite positive samples, reduction fractions and thresholds. Producer medians: 407.541182 ms baseline, 0.627848 ms candidate. Independent rerun medians: 386.892123 ms baseline, 0.592301 ms candidate; reduction 99.84690797129514%. Both pass candidate median <= 0.5 baseline. No sample was omitted.

Independent artifact test execution initially failed 1/42 because an old small changed-content fixture expected a dominated matcher invocation. The failure remains in independent-tests.log. Reviewed the subsequent change: that fixture now supplies a custom counter, making matcher eligibility its explicit contract; the separate localized fixture increases insert size to exercise character-mode fallback. Re-execution in independent-tests-final.log passes all 42 tests. Production source did not change during this correction.

## Scope and limitations

Evidence establishes exact parity on the declared finite inputs, the current lower-bound proof, counter exclusions, existing artifact tests, and synthetic repeated-deletion CPU improvement on this Python/Linux process environment. The lower bound is conservative; it does not establish speedup on all inputs and introduces small serialization overhead when it cannot prune. No universal bug-free guarantee, model quality, token savings, cash savings, GPU improvement, installed runtime adapter, live monitor or deployment is claimed. Repository-wide acceptance must consume the parent's completed repaired regression evidence rather than the preserved failed run.

## Frozen hashes

- `agent_runtime/artifact_context.py`: `6bacce144f71a9c162681a4bd7929f0614119009ac96a52e0a38bb9da2616168`
- `tests/test_artifact_bound.py`: `237576b7f9c7b26d87469af3670260b3db180cde331a7731f5d005b1cf98ee76`
- `tests/test_artifact_identical_fastpath.py`: `69093b749defe2e8a6a8961715814c58fb900d5bae13af029fc640a4d1dc44f0`
- `tests/test_artifact_localized_diff.py`: `e0c01cec43377b4e27428b594b65983092aa9c3bb739aa725549fdc55e6c8bc6`
- `agent_doc/results/artifact-bound-20261012-2221/validation_plan.json`: `c26aca9d3a5d7420d2f0aac8be336506cb5895ad3ca592ec70445889b3be8c28`
- `agent_doc/results/artifact-bound-20261012-2221/measure.py`: `6c030a5747e60399b628a3f8e28b92e41c25db18b9f14c9ed7a6e89805811634`
- `agent_doc/results/artifact-bound-20261012-2221/measurement.json`: `64d9a14e557899244b91cc415518ed4fdeb89d065baab39d01f7ed7c0573ef60`
- `agent_doc/results/artifact-bound-20261012-2221/independent-measurement.json`: `71fafb3e8c81e4ebfe9842bae248c7930d1f1263113acd8302ca067566e1bd4c`
- `agent_doc/results/artifact-bound-20261012-2221/independent-oracle.py`: `172f181a80aae702ec11df517ae7846d5da4fad799c961741495fce842bee237`
- `agent_doc/results/artifact-bound-20261012-2221/independent-oracle.json`: `c92fbb4a8c211003ae9ccb617888999814237d1a480fdbd87da02c510c01bf08`
- `agent_doc/results/artifact-bound-20261012-2221/independent-tests.log`: `55a8699ec84a3a39e6095226eeb487405229101296e02478d1bdd57e5c52dbde`
- `agent_doc/results/artifact-bound-20261012-2221/independent-tests-final.log`: `f4ae677bb3ddc5e39398a5b59315cd00e2c0c95d077f84409d70d6a39c67c513`

## Final closure (appended after repaired repository regression)

Independently verified every manifest artifact and validation-plan path/hash against actual bytes, all previously frozen review source/test/evidence hashes against unchanged bytes, and manifest metrics against the reviewed measurement data. Final focused producer log passes 42 tests; full-tests-final.log reports 1175 tests in 75.448 seconds, OK with 8 skips; reader-tests.log reports 3 tests, OK. Skipped tests are not claimed as executed. Initial failed logs remain preserved.

Publication acceptance: usable-with-scope for the exact frozen implementation agent_runtime/artifact_context.py and tests/test_artifact_bound.py, tests/test_artifact_identical_fastpath.py, tests/test_artifact_localized_diff.py, plus the reviewed evidence artifacts. No new implementation changes were made by this verifier. All pending regression conditions in the earlier review are now resolved; prior scope limitations continue to apply.

Final manifest SHA-256: `db5f0028d95b0de90a59928a85cabe0bffe8278453dbd364770dd9dd8507772a`.
- `agent_doc/results/artifact-bound-20261012-2221/full-tests-final.log`: `5888edde3d7877c1447abb9a7c42e2df64b0a3961f394dcc586b80e032676db9`
- `agent_doc/results/artifact-bound-20261012-2221/reader-tests.log`: `1334e43ba06a8bc72004401fb4c124ac243784ec578ace1344a4f32f47292c27`
- `agent_doc/results/artifact-bound-20261012-2221/tests-final.log`: `e6731b9d628575c5ad0d9c41de3c53f9807212c2927ef8e5a94be519c8de50cc`
