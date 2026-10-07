# fd9012 candidate-only knowledge supplement

The [concise summary](summary.json) records a minimal delta from the completed 907-based integration, not a repeated acceptance cycle. The new upstream is `fd9012ca9f953693ad59d30e63d03ac7644c599e`; the prior accepted staged tree is `a0e5731ee615a84db9041c1e5187e233f055de16`.

## Checked outcome

- All previous 156 entry files remain byte-identical, including all 77 published card pairs (154 files).
- Current corpus contains 77 published entries and two candidates. The new salamander card and existing cephalopod card remain unavailable through normal get, file search and SQLite search; indexed IDs exactly equal the 77 published IDs.
- Runtime and final index-test sources match the prior verification. Source and packaged corpus mirrors match exactly; the holdout registry is unchanged. Metadata checks preceded body loading and found no reserved source collisions. No target paper or experimental answer was read.
- Three representative queries, each tested on files and SQLite, have identical rankings and context IDs before and after the addition. Their selection is a bee natural question, the known AIK A12 gap and a no-hit control. These six comparisons are spot checks, not a new full-catalog measurement.
- The focused index suite passes 10/10 on stable source hashes. No full 730-test or catalog cycle was repeated.

The ranking inference is bounded: all published metadata/body bytes, published graph and ranking code remain identical, and candidates are excluded before scoring/indexing. The earlier default/domain results and known failures are therefore reusable within those unchanged semantics. This does not review or scientifically accept either candidate.

## Snapshot and cache nuance

The full corpus snapshot changes from `35d6a2001b51a55b5b73dee77a817e51ac04391114ca57f7abf9b93d1b41a85b` to `c3a35809513ae49e4a3858f9489f95d682852ebd64574f03e5a181bb122fbaca` because candidate records participate in snapshot identity. An old index is correctly rejected as stale. Refreshing it updates zero documents, removes zero and preserves all 77 published documents while updating the snapshot binding. Reuse must not silently bypass that refresh.

## Evidence and acceptance

Detailed [raw checks](../../../../doc/results/corpus-fd9012-delta-20261007/raw-checks.json), [native contract](../../../../doc/results/corpus-fd9012-delta-20261007/contract.json) and [manifest](../../../../doc/results/corpus-fd9012-delta-20261007/manifest.json) bind the actual code, inputs, prior evidence identities, logs and environment. Native registration is pending independent review, not self-acceptance.

The completed 907 run is unchanged. Its original metadata-bound manifest may be stale against the newest working tree; the prior staged Git tree retains those exact original bytes. This supplement binds the earlier result identities and current candidate-only delta rather than changing old measurements or relabeling their historical failures.
