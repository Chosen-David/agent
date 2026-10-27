# Independent plan review v1

Decision: **REVISE**. No execution/probe has occurred in this review. This is an actual delegated fresh-context review, not an authenticated ReviewSession receipt or runtime dispatch authorization.

Reviewed frozen plan SHA256: `68ddc584e44463f081c715e81fcd92c0a5da691f34a2f60d0b5fe970f454a6d7`.
Project: `/workspace/scratch/6416f20dc59b/agent-run-1459`; SYSTEM-99 stable Plan Version51.
Source setup.py independently read, SHA256 `d5273177d6bb1dc6dcdc63168505367b6114bb18919c27c2945c297e305cbfcd` matches plan.
GUIDE.md is empty, SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; its directory remains human-only. This review does not authenticate its provenance or enlarge user authorization.

## Seven checks

| Check | Verdict | Reason |
| --- | --- | --- |
| intent | pass | Four tiny deterministic native helper diagnostics fit reliability/concurrency audit; no repair, full installer transaction, performance or system completion claim. |
| guide | pass | Empty current guide adds no substantive requirement; read-only human guide boundary retained. SYSTEM-99 remains unfinished. |
| assumptions | pass | Exact `replace_skill_copy` path does move previous into private backup before `staged.rename(path)`; on OSError it blindly renames backup to the destination. Creating an empty claimant at that boundary is a plausible schedule of ordinary pathname operations. Native rename performs the relevant effect. |
| prior_results | pass with scope | COPY-STAGE expressly excludes target changes after validation; COPY-RESOURCE excludes same-permission writers after validation and has consumed review3/3. DIRECTORY addresses source logical fingerprints and modified copies, not this target publication schedule; INSTALL-RECOVERY excludes concurrent multi-file transactions. Existing positive rollback coverage without competitor does not answer claimant preservation. My targeted report-name/content search found no matching report. No old acceptance/budget is reused. |
| acceptance | fail | Declared experiment-validation-plan/v1 does not contain the six required canonical criteria or identical result contracts on producer, verifier and consumer. See blocking findings. |
| risk | pass | Temporary fixture-only writes, native real renames except narrow scheduling hook, no source/guide edits, no model/backend calls. Failure means a scoped witness against a proposed preservation property, not proof of frequency or a previously promised universal no-clobber contract. |
| resources | pass | producer1, independent1, 30-second command bound, common fixed deadline, no retries, review2-cycle cap are finite. v1 counts as first review; revision cannot refresh deadline or spent budgets. Runtime provider remains unavailable and must stay pending. |

## Blocking findings and concrete correction

1. At `criteria`, retain the actual diagnostic checks but express the mandated keys from workflows/result_validation_workflow.md: `implementation`, `reference_boundary`, `data_integrity`, `numerical_sanity`, `measurement_validity`, `reproducibility`. Each needs procedure/acceptance/allow_not_applicable. Data integrity must require four unique case IDs, one hook hit where expected, complete raw stdout/stderr/exit, source/probe/config/environment hashes, and no silently omitted/error/skipped cases. Numerical sanity can check finite exact integer counts and device/inode identity; no statistical inference. Measurement validity may explicitly permit N/A because there is no timing/performance/accuracy claim. Reproducibility must freeze exact command/probe bytes before execution and permit only the single independent repeat.
2. At `dag`, bind a single identical result contract as producer `experiment_result`, verifier `result_validation`, and report `required_result_refs`. It must identify result ID, producer task/actor, manifest path, fixed validation-plan path/SHA and precise scope. Missing future raw hashes are not to be invented. Because embedding the plan hash into that same plan would be self-referential, keep the immutable validation-plan file separate from the outer execution contract/DAG or use a separate contract sidecar binding the frozen plan hash. Preserve v1 and produce an immutable v2.
3. Bind the actual current task index, SYSTEM-99 stable Plan, empty guide and four boundary details as evidence_refs/document refs (actual hashes), and specify allowed runtime output paths/owners. This is a scoped native diagnostic contract; do not present it as a complete protected project runtime DAG. The stated missing trusted runtime provider is a capability blocker for runtime acceptance, unaffected by this review.

## Method/oracle assessment

The claimant check must compare lstat device/inode and emptiness after the operation to those captured immediately after claimant mkdir. A live keeper descriptor is preferable to exclude inode recycling ambiguity. Normal replacement must confirm new content; uncontended EIO rollback must confirm original prior identity and content. Publish claim must record whether rename refused and what actually occupies target; rollback claim must record the original EIO path and resulting identity, without converting that controlled EIO into an unexpected test error. A safety assertion failure is expected negative evidence, not a passing production test.

The hook must hit only actual `Path(stage)/new -> exact owned destination`, once per applicable case, with all other renames delegated. Native empty-directory replacement is the fact being measured; do not mock the rename result. This is not multiprocess/stress testing. Do not label two failures as two independent broad bugs if both share the same pathname-overwrite mechanism.

## Re-review and stop conditions

Second and last review may inspect minimally corrected v2 within the original deadline. No probe runs until that is approved and actual probe bytes/command frozen. Any source/hash drift, unexpected exception, missing schedule, deadline expiry, exhausted invocation or unavailable execution capability stops dependent work with raw evidence preserved. No source repair, old gate restart, budget reset, backend call, git action or publication is authorized by this review.
