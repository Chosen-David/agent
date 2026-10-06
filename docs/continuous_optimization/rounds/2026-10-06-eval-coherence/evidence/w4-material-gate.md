# CO-020 bounded material-review gate

2026-10-06. Implemented in the existing `scripts/agent_eval_pipeline.py`; focused tests in `tests/test_eval_material_gate.py`. No external runtime, model invocation, worker launch, historical-record modification, commit or push by this task. Overall release and actual final-candidate role acceptance remain root-owned and incomplete here.

## Fixed decision and observed baseline

The original round preregistration remains authoritative. Before edits, the acceptance plan was frozen at scratch `coherence-design/acceptance-plan.json`, SHA256 `216a1e9f0263d89141dea6739b2dc102db8b486c7bdc53fe2b311f1a55c817c5`. Its fixed suite contains four historical development contracts, ten direction/parity/unit/settlement-equivalence/behavioral heldouts, and missing/malformed/duplicate/stale/tampered/identity controls. Existing baseline source was preserved separately.

W1's actual historical preparation replay accepted both defective and corrected writer/settlement rubrics, with zero byte-integrity errors. The historical writer inputs have medium parity and large regression; its old rubric instead required medium regression. The old settlement illustration yields unequal net costs, although its equivalent-answer clause could rescue a correct response. Their original records remain unchanged.

A new isolated baseline probe copied the current task-specific material preflight and fixtures, then changed only two rubric claims to contradict those fixtures. All 25 input-fact groups still passed, all 60 criteria/19 cases remained, and the contradictory strings were copied into its generic criterion map. This demonstrates the missing correspondence/gating boundary; it does not say the manually reviewed current run is wrong. Probe records remain in scratch `coherence-design/probe-result.json`.

## What changed

`prepare_run(..., require_material_review=True)` records an explicit protected-run policy. Preparation can freeze unreviewed materials, but does not authorize dispatch. Legacy calls preserve their previous API/behavior and are not advertised as satisfying CO-020.

The controller calls `authorize_dispatch` **before** invoking its host's worker-spawn operation. This checks all frozen task/input/rubric and manifest bindings, exact case/criterion coverage, supported factual/behavioral judgments, external evidence hashes and a separately supplied independent reviewer identity. `record_start` repeats the checks before creating any attempt directory and binds the trusted review reference to the actual worker actor. Subsequent collection/grading/report validation rechecks that reference. The recorder cannot prevent a controller from invoking an unrelated host API without first calling the gate.

Task-specific executable oracles remain outside the generic pipeline. They calculate numerical truth; an actual independent reviewer must additionally check whether **each exact rubric criterion** agrees with that truth or is a legitimate behavioral requirement. The gate verifies that trusted review's status and bindings. It neither parses arbitrary prose for truth nor treats an evidence file's existence as independent semantic verification.

The host supplies expected review SHA256 and reviewer identity separately from the review JSON. Passing a worker-authored JSON object alone is insufficient. Honest host protection of those arguments/files is required; this is not cryptographic reviewer authentication or OS isolation. A dishonest controller or same-user adversary that can replace both trusted arguments and artifacts remains outside the guarantee. Release controllers must explicitly enable the policy; legacy mode cannot be substituted for a protected run.

## Interface and portable storage

```python
manifest = pipeline.prepare_run(repo, revision, run, tasks, rubric, fixtures, adapter,
                                require_material_review=True)
# Independently review the exact frozen materials; controller freezes the result.
trust = {
    "path": "controller-evidence/material-review.json",
    "sha256": controller_observed_review_sha256,
    "reviewer_actor": actual_independent_reviewer,
}
pipeline.authorize_dispatch(run, case_id, planned_actor, material_review=trust)
# Only now invoke the actual host spawn operation and observe its start receipt.
pipeline.record_start(run, case_id, actual_actor, receipt_path, material_review=trust)
```

Review schema:

```json
{
  "schema_version": 1,
  "reviewer_actor": "actual-independent-reviewer",
  "material_hashes": "Use pipeline.material_bindings(run, manifest), an object",
  "cases": {
    "case-id": [{
      "criterion": "Exact frozen rubric criterion",
      "kind": "factual",
      "status": "supported",
      "verification": "executable_oracle",
      "reason": "Located explanation of how this criterion agrees with its source facts",
      "evidence": [{
        "path": "controller-evidence/oracle-result.json",
        "sha256": "actual-sha256",
        "location": "Actual result field or source position"
      }]
    }]
  }
}
```

The displayed `material_hashes` string is explanatory, not valid input: the API supplies the exact object containing manifest SHA256, task/rubric hashes and each case's prompt/input hashes. `kind` is `factual` or `behavioral`; `status` is `supported`, `not_supported` or `unreviewed`. Only supported authorizes dispatch. Verification is `executable_oracle`, `source_review` or `task_requirement`; factual assertions cannot use the last. Each criterion needs a reason and nonempty external evidence with a location. All cases/criteria must be covered exactly once; duplicate JSON fields are rejected too.

Relative review/evidence paths resolve from `run.parent`, contain no `..`, and must stay outside the run. Recommended portable bundle: `bundle/run/` plus `bundle/controller-evidence/`. Explicit absolute controller paths remain supported. Symlink leaves and ancestors, inside-run review/evidence, missing files and changed hashes are rejected. No review answers are copied into worker inputs or Skill snapshots. Archive both sibling directories for replay; do not edit immutable hashes to compensate for moved absolute paths.

CLI mirrors the API: `prepare --require-material-review`; `authorize-dispatch --run RUN --case CASE --actor ACTOR --material-review controller-evidence/material-review.json --material-review-sha256 SHA --material-reviewer REVIEWER`; pass the same three review flags to `record-start`. The controller must obtain the reviewer identity and hash from actual independent review, not accept values merely claimed by the reviewed worker.

## Measured outcomes

| Check | Actual result | Scope |
| --- | --- | --- |
| Restored historical writer and settlement, wrong + corrected | 4/4 expected outcomes; defective 2/2 rejected, corrected 2/2 accepted | Actual historical task/rubric/input files through current authorization and recorder; arithmetic-derived synthetic controller judgments, no model execution |
| Predeclared direction/parity/unit/settlement-equivalence/behavioral controls | 10/10 expected outcomes, zero false rejection among 6 valid controls, 4 invalid rejected | Frozen test cases, executable arithmetic and explicit criterion mapping; no generic NLP claim |
| Focused material gate tests | 19/19 test methods passed | Includes missing/malformed/duplicate/stale/tampered/forged-identity/self-review, changed material, symlinks, pre-spawn rejection and no attempt directory on negative cases |
| Existing pipeline suite, unchanged | 40/40 passed | Legacy compatibility, recording, grading and denominator behavior |
| Portable archive restoration | Passed | Copy run + controller-evidence to a new parent, authorize and then collect/grade/report without editing bindings |
| Historical preservation | Hashes unchanged | Read-only restored input/catalog inspection |

The conservation-only settlement heldout permits a zero-net cycle; the historical task asks for minimal transactions and its accepted corrected example has two. The test does not incorrectly equate net-cost equivalence with satisfying a minimum-transfer requirement.

For rejected controls, the pre-spawn spy was never called and record_start created zero attempt directories. Accepted controls invoked a spy only; **actual host/model calls were zero**. Test reviewer identities and review events are synthetic controller fixtures, not real independent-agent receipts. Root must independently inspect these oracle correspondences and obtain actual review for release-run materials; 25 fact checks alone cannot auto-award criterion-level support.

Reproduction:

```bash
python -m unittest discover -s tests -p 'test_eval_material_gate.py' -v
python -m unittest discover -s tests -p 'test_agent_eval_pipeline.py' -v
```

Actual historical replay source/results and logs are under scratch `coherence-design/`; `historical-gate-replay-v2/result.json` binds current source and historical hashes. No historical rubric was rewritten. Candidate program SHA256: `1446cefb2225e00d47fad8ca1c921e4c3a030b1f628fb456686fd906c4596428`; focused test SHA256: `639b330908fdc050e0cf9426deb4921dca8cc49a79e3316d4b42b2c01f5db2c1`.

These results establish the bounded program boundary and fixed-control behavior. They do not establish general prose truth verification, model-quality gains, full current-role execution on the final candidate, deployment or release completion.
