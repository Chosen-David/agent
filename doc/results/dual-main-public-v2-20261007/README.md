# Dual-main public evidence

This pack is a newly versioned publication view of genuine implementation and finite validation work. Original execution logs, operational plans and host/controller records are retained privately with exact hashes. They are not dependencies of the public checker.

## What is public

- `history/derivations.json` distinguishes original file hashes, original canonical plan hashes and newly published view hashes. Original labels identify archived evidence; they are not public file locations or download endpoints.
- Complete historical model-review feedback and verdicts are preserved in the review views. Each review applies only to its original plan. Redacted historical plan views are explicitly non-executable and cannot authorize a new plan or a current release.
- Structured log views preserve actual testcase identities, counts, failures and terminal outcomes, while omitting raw traceback locations and environment diagnostics. `history/failure-fix-outcomes.json` distinguishes source-inspection findings from pre-fix executable counterexamples and records the fixes.
- `data/finite-cpu/` contains byte-identical public algorithm, inputs and historical raw values:15 unique samples and aggregate6603. Relocation and original/public hashes are explicit. This is not a new producer/model execution.
- `source-freeze.json` identifies the current reviewed source scope. Runtime, tests, live-reference updates and existing upstream work are distinguished.
- `verify_public_evidence.py` checks public content hashes, structural facts and finite arithmetic using only public files. It cannot authenticate a host, model invocation or publication authority from JSON labels or hashes.

## Limits and current acceptance

The original complete regression ran783 tests:782 passed and one real-tmux opt-in was explicitly skipped; Reader3/3. The real tmux binary was unavailable. No service, model/API, GPU, credential or user-machine deployment is claimed. Token/cost measurements are unknown; no model-quality or performance gain is inferred.

Current live-reference checks, correctness review and privacy review are recorded separately under `independent/` and in the final publication evidence. Operational approval and repository publication remain trusted-host actions outside this public content verifier. The actual repaired candidate requires a fresh publication-purpose review; an old approval is never rebound to sanitized bytes.


## Review the export before any upload

Privacy and permission review applies before every object upload, not only before updating a branch. Unattached content-addressed blobs can still be retrievable by their object hashes; absence of a commit or branch update does not make an upload private.

Inspect the exact export bytes and destination. Distinguish real recorded execution/environment details from harmless generic path examples in public documentation. Do not export private controller receipts, archive locations, user-provided private material or credentials. If a view changes, preserve its original identity and bind a newly reviewed public version; never relabel an old approval as approval of changed bytes. This is an export/review requirement, not another runtime service.
