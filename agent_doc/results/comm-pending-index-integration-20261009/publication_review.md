# Independent publication reconciliation review

Decision: **evidence-only merge appropriate**. Keep upstream implementation, tests and benchmark unchanged; publish the independent historical evidence with its explicit scope. No performance rerun is necessary for this evidence-only publication, and no new current-snapshot speedup is claimed.

Reviewer: actual Work collaboration context `/root/comm_review`. Current checkout commit: `ab6cc593e69b9361bac1b799a96e71e90287889a`.

## Actual checks

- Compared archived candidate bytes with current production communication.py. Archived name `communication_pending_recipient_seq` occurs exactly once. Replacing that one index identifier with `communication_pending_recipient` makes the entire files byte-identical; recipient/seq columns, NULL predicate, query, usage ledger and all other behavior are unchanged. This is a static implementation-equivalence observation, not a fresh timing measurement.
- Verified current production source, both communication test files and benchmark bytes exactly equal the current HEAD versions. No runtime/test/benchmark delta is introduced by this evidence-only merge.
- Independently ran `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p "test_communication*.py" -v` against current upstream: **24 tests passed in0.461s**. These are the upstream tests; prior25-test results remain tied to the archived candidate test suite.
- Read publication_reconciliation.md and the report’s publication notice. They retain archived numerical findings as historical candidate-vs0498816 measurements, distinguish source/index-name hashes, avoid a second improvement claim and give isolated-checkout replay guidance.
- Re-read both original manifest byte hashes: original run `3b5894a95e7241f85e0936b47db425455c54302b2e0dfd7ee60c80a7a20a6a26`; integration run `f712719dda9410fc81ee225af703c6ea2687b4a4d616e1d795cfe1f7f733d12b`. They remain unchanged. Frozen verification/manifest/record files were not edited by this review. Their old live-path source bindings are historical/stale relative to the current checkout and are not relabeled as fresh acceptance.

## Hashes

Archived candidate communication.py: `c02b577228f9625e7bcb641e7be1448c2733b8de480c574efcc11617b327ebad`.

| Current upstream file | SHA-256 |
| --- | --- |
| agent_runtime/communication.py | `c322cdb7d61dbc98bb8e6139bb817b1825742aa3aca9285b35609556384dd975` |
| tests/test_communication.py | `25ca7b8b6f64c38571b778f6aa37fa1095856d4d674fc691198854a22d782b0a` |
| tests/test_communication_usage.py | `0e6a8606b6f7ec4bdd5252668fbce414b44740417184cdd62912cb62a1725c37` |
| scripts/benchmark_communication_inbox.py | `4208cc9d64b23f835ec71ab39aed1ea1d8aff853cbe9d0663f88bac7e1c19931` |

## Boundary

This review accepts the reconciliation and current focused regression outcome only. It does not reauthenticate stale historical result contracts against current paths, establish exact performance equivalence from the index name, claim a new full-suite run, or certify runtime deployment. Existing user publication authorization and expected-head/concurrency checks still govern the actual merge. Preserve concurrent upstream work and avoid installing duplicate equivalent indexes.
