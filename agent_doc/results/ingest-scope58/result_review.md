# INGEST-SCOPE-58 independent result verification

## Decision and scope

**usable-with-scope** — accept the narrow entries-only staging change and its exact plugin mirror for the tested local import contract. No blocking implementation or data-integrity finding remains.

Accepted claims: unrelated root-local files are no longer copied into the validation stage; root-local dangling links and FIFO objects no longer break otherwise valid import; existing entries validation, attachment retention, candidate/provenance behavior and pre-commit mutation detection remain exercised. Logical copy payload is reduced by the reported amounts for the declared fixtures. **No general wall-clock speedup is accepted.**

Reviewer: `/root/ingest58_review`, separate from producer `/root`. This review reused the independently established plan context, inspected actual source/data and executed its own checks after the producer explicitly confirmed all main testing had stopped. It is not a producer pass-label replay. No source, test, guide, TASK or external repository was changed by this reviewer.

Frozen plan: `plan_v1.md`, SHA-256 `b9ed2eda610c8001d9b2542702ff24d295e613ebaafc5bd92b09b5d7846935f2`. Baseline: `cacbee7663282bcd17b8e08de6b4a00945a0a9fb`. Current canonical and mirrored ingest SHA-256: `9e56a59b94feae3ae95bcfcd04aff9752fbbdb8b219b9bb0ec2344d95c58e7c8`.

## Independent procedure and actual observations

I read the production diff, `KnowledgeStore` consumer, seven regression tests, complete measurement harness, raw result structure, original failures, post-change successes and draft report. Only the first `copytree` source/destination changes: `store.root`/`stage` becomes `store.root/'entries'`/`stage/'entries'`. The final copy, snapshot comparison, guard calls, rename and cleanup remain unchanged. The distributed script has identical bytes.

Executed `python agent_doc/results/ingest-scope58/independent_checks.py` twice, both exit 0. The first execution established the result; the second captured its complete JSON output to `independent_checks.json`. These are correctness/data checks, not two new benchmark rounds or selected timing samples. The independent script does not import the producer measurement harness.

Independent checks passed:

- Loaded the original ingest from the fixed Git baseline, verified baseline/current/consumer/harness source hashes, and checked exact plugin equality.
- Recomputed all three profiles' copy sums, all 48 timed observations including warmups, pair identity, alternating order, input/output equality, positive finite times, seven-sample medians and min/max ranges. Checked no copy instrumentation appears in timed samples and no duplicate traced file paths exist.
- Constructed a separate old/new oracle using the real 115-entry corpus, an 8192-byte root attachment and a nested 17-byte entries attachment. Compared complete records, snapshot, return receipt and provenance after removing only timestamp. Results match exactly. Both copied the entries attachment; the root attachment remained unchanged.
- Observed independent total logical bytes 910408 before versus 707309 after, a difference of 203099 bytes. Independently calculated that difference as 194907 original root-sibling bytes plus the added 8192-byte root file. Subtracting the 17-byte entries attachment from the new total reproduces the recorded 707292-byte base workload.
- Independently reproduced baseline errors for root-local dangling links and FIFO, then observed successful candidate imports on the new implementation. A patched `os.scandir` rejected any scan of the corpus root during the successful imports, so this check does not merely infer absence of sibling traversal from final output.
- Independently confirmed entries-local symlink and FIFO rejection with no candidate destination created.
- Ran the distributed plugin through `python -I`, from a separate temporary working directory, against a corpus with a root-local dangling link; candidate import succeeded.
- Reran all seven focused regression tests, including invalid dependency, repeated ID, orphan Markdown, entries attachments, special-file cases and the deterministic corpus-mutation fence. All passed.

## Six acceptance dimensions

| Dimension | Verdict | Evidence and reasoning |
| --- | --- | --- |
| Implementation | pass | Actual minimal diff and full ingest/consumer paths inspected; source hashes match measurement bindings; mirror equality and isolated entrypoint exercised. Entries-only staging retains relative paths, all subtree contents and subsequent validation/commit logic. |
| Reference and boundaries | pass | Independently loaded baseline, exact semantic comparison, independently calculated byte-difference oracle, root versus entries special-file checks, nested attachment preservation and all seven regressions. This is not solely comparison against duplicated production logic. |
| Data integrity | pass | All source bindings, 3 profiles, 8 pairs per profile with exactly one warmup, alternating order, trace/timing identity, complete sums and medians checked. Initial 6-test failure set and later 7-test set are correctly distinguished; no failed evidence was overwritten. |
| Numerical sanity | pass | All 48 durations are finite and positive with explicit ms units; trace bytes are positive integers; sums and medians recompute exactly. Output hashes match before/after and trace/timing within each profile. Logical byte accounting is not called physical I/O. |
| Measurement validity | pass with stated scope | Timers surround the entire ingest and exclude fixture copying/hash preparation and later semantic comparison. Copy instrumentation runs separately. Inputs are warmed by hashing, and timing scatter plus negative medians are retained. Evidence supports observed warm-local durations only, not robust production acceleration. |
| Reproducibility | pass with stated scope | Actual independent source/data cross-check, old/new functional reproduction, exact payload-difference reproduction, isolated plugin test and seven-test rerun all passed. I did not rerun the complete 1297-test suite or reproduce wall-clock medians; neither is claimed. |

No dimension is silently marked N/A. The publication consumer must carry these limitations and the accepted claim scope.

## Independently recalculated measurements

| Fixture | Logical bytes before / after | Median ms before / after | Range ms before / after |
| --- | ---: | ---: | --- |
| Plain 115-entry corpus | 902199 / 707292 | 152.440482 / 181.760385 | 143.096708–212.321391 / 136.429228–206.927654 |
| Root-local 16 MiB attachment | 17679415 / 707292 | 162.132385 / 166.060706 | 137.710099–180.637804 / 129.805824–209.251159 |
| Root-local SQLite index | 4453431 / 707292 | 171.307428 / 157.828079 | 167.689894–211.107738 / 146.781577–180.312632 |

The first two medians increase. The third decreases, but the run is not evidence for a universal latency improvement, cold-cache behavior or end-to-end model performance. The report correctly states these negative/mixed results. The SQLite case applies only to an index deliberately inside the corpus root, not the documented default project cache outside it.

## Broader regression evidence and report review

The producer's full raw suite log exists at `/tmp/ingest58-full-tests.log` and at `/workspace/scratch/5d3e4236a5b4/agent-audit-56/.git/worktrees/agent-audit-58/full-tests.log`. Both independently hash to `47d21b879692e95c75137c0a882adf61d2fa11210920eb1afb621d878b7e0431`. I checked its summary, focused-test entries and skip records: 1297 tests, 98.891 s, OK with 8 skips. Seven skips concern unavailable visualization dependencies; one is the opt-in real tmux integration test. No skipped feature is promoted to a successful deployed capability. The short committed tail matches this summary. Reader log reports 3 tests passing in 1.580 s. These are producer executions whose evidence was inspected, not suite runs performed by this reviewer.

`git diff --check` returned success. Independent `nproc`/`lscpu` readback supports the report's 9 visible logical CPUs, AMD EPYC 9V74 model and virtualized x86_64 environment. Report revision inspected here has SHA-256 `1912e8ff89c194be7bafba9c390193a620a28567a94753b7e7db5a23632672d4`. It correctly separates previous reading from new research, prior-search limitations, real testing from deployment, and outstanding publication. Its external literature/background is not independently re-certified by this implementation review.

## Immutable evidence bindings

`independent_checks.json` records hashes for the changed source, consumer, index helper, write guard, reuse helper, mirror, seven-test file, original/post-change logs, plan, harness and measurements. Additional principal bindings:

| Evidence | SHA-256 |
| --- | --- |
| `independent_checks.py` | `2922c25304896ea93f830ed228885328608e661c39671403c480fe4d544aa12e` |
| `independent_checks.json` | `efe14789b9c65c31232ebf41df85960534816f738225e30d2322393fe9a1d493` |
| `measurements.json` | `48860533c7b1c4ace43a942bf9747be46b7f4e25befc1267fa4757a37d4dbd04` |
| `measure.py` | `a3187018a0965e0b1dc195ee5261715445663e0f50502fa416a6b6f58b489574` |
| `before.log` | `bda584073583a05ce899b4db1194e2260e3328cb984b316d9736e9a4f6502312` |
| `after.log` | `4511ea93734ad0e50177af02c110536e7a19b86115cfefd78cbce17176b566c4` |
| `full-tests.log` (short tail) | `10495b8503fe92d2c0e85b0bf342785ede0850365084b586bac669c3eab73510` |
| `reader-tests.log` | `3d2c56ace0d1c06fa8a6700bbc44943e886d64321bce710d3d38d0643912d04e` |

## Limitations and release boundary

This is bounded local engineering acceptance, not a universal bug-free guarantee or machine-authenticated `ResultValidationHandler`/`ReviewSession` receipt. No trusted managed-runtime adapter or tmux deployment was established. Existing single-writer expectations and check-to-rename race limitations persist. Root sibling bytes do not represent physical disk work, memory savings or token savings. Exact historic SQLite database bytes depend on generated path/environment; acceptance is paired equality within each frozen fixture plus inspected generation logic, not cross-host byte-for-byte recreation of that temporary index.

No remote publication was performed or verified by this reviewer. Main must still fetch/integrate current upstream, re-evaluate affected source/evidence changes, preserve these scoped claims and confirm the ordinary publication result with remote SHA/tree readback. Documentation may append the actual acceptance and later publication status without pretending the reviewed draft already contained those future facts. Changes to tested code, raw data or substantive claims require revalidation.
