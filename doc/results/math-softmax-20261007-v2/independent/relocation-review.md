# Actual independent revalidation after canonical result-directory correction

Actor: `/root/independent_math_verifier`; producer `/root`. New actual verification run: `math-softmax-20261007-independent-relocation-v2`. This is a fresh check, not reuse of the former accepted JSON.

Read current moved manifest, contract, plan and current card/metadata. Scientific equations, assumptions and counterexamples match the reviewed content; the card evidence path now uses `doc/results/math-softmax-20261007-v2/`. Frozen verification script SHA remains 3fde613d4d186e6ff56f3197b548ee4d2118b67f0d4ecdd1945de090186b2550; producer raw SHA remains 59176032311a004be5064572a571cba529e128acc1f6b860efd1f60f3a42fe76. New _snapshot checks all current eight artifacts and plan against the corrected paths.

Actually reran `python doc/results/math-softmax-20261007-v2/verify.py doc/results/math-softmax-20261007-v2/independent`: 416/416 pass, duration 0.026153933999012224 seconds, and all numerical records/config match the producer exactly. Reran independent/reference.py: all 12 Decimal/reference checks pass. New independent timing/environment artifacts are evidence for this run; old review.md records the earlier review. The new review.json binds the current manifest/proof and fresh rerun evidence, with source/math limitations retained.

Supplementary count correction checked: legacy-comparison.json now explicitly says 8 public queries. The prior supplementary-review.md describes the discrepancy as observed historically; it no longer blocks this corrected count. No change to numerical accepted scope.

All six domains pass for finite CPU float64 development checks. No formal verification, arbitrary extreme-subset production stability, model A/B, GPU, indexer performance, token savings or e2e quality claim. A trusted main host must authenticate this actual delegation/completion before injecting a provider; JSON alone does not self-authorize acceptance.
