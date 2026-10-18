# MEM-DISPATCH-DOC-19 independent review

Verdict: **usable-with-scope**, no blocking finding in the frozen candidate. This is manual independent source/result review, not a deployed managed verifier or ReviewSession receipt.

Inspected the actual production/test diff, document snapshot/check implementation, and raw producer logs. The change adds the existing project-document guard after `current()` and the memory/knowledge guards, directly before handler dispatch. Current=False still returns the prior claim-gate reason. Stable Plan changes invalidate snapshots while Progress appends remain allowed.

The initial producer baseline retains a real test-fixture error (legacy and canonical active indexes in one temporary root). Corrected fixtures separate those roots: 15 tests, 5 expected baseline failures, no errors. Each failure checks that the handler was already called once when it should remain uncalled. Candidate producer normal/-O logs each show 15 passes.

I independently loaded the exact baseline module from git in an isolated process and ran the frozen 15 tests plus six newly authored cases. Baseline: 21 tests, 8 failures, no errors; all eight failures are handler-call count failures. Candidate: 21/21 normal and 21/21 optimized pass. Additional cases cover changed adopted advice, deleted canonical detail, invalid UTF-8, current=False priority with document deletion, no-ref legacy compatibility, and changed unadopted advice. No guide file was created or modified by these fixtures.

Frozen runtime SHA256: `b9ec8f8881e26265fec368570bfb2b9fde2aed01ae6643ee0dab7f4543cd0e41`. Frozen regression test SHA256: `620eb4fda1dec3385112d1f521ee2fad028b98ccfea17f342163281a8e23d33d`. Exact code, logs, test-script hashes, commands and environment are bound in independent-review.json.

Scope is deterministic callback-induced document invalidation before handler work. The final guard and external action are not atomic; concurrent mutation after the check remains possible. Added I/O/hash cost is unmeasured. Guide mutation was not exercised. No performance, live model, KV, GPU, QA or TTFT claim is accepted. Full repository/Reader regression remains a separate main-agent gate, and MEM-STORAGE-01 remains open.
