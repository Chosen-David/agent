# Fail-closed followthrough

This follows the original synthetic failures without editing paper drafts or old evidence. Implementation commit: `5d220eb`. The original `b4fc439` archive and paper/runtime outcomes remain byte-identical; they are historical failures, not rewritten passes.

| Original false acceptance | Current deterministic enforcement | What remains judgment-dependent |
|---|---|---|
| Audit disguised as research prose | Missing externally supplied, bound independent `artifact_fit` acceptance leaves completion unverified; a failed review cannot certify completion | Reading the argument and deciding genre/fit |
| Copied manuscript body | Missing/failed independent `originality` review leaves completion unverified; stale record/artifact hashes reject | Establishing copying, attribution and provenance beyond supplied sources |
| Queued dispatch used as role start | Parse current receipt bytes; require started/produced kinds/status, matching actor/role/revision/run/task/attempt, unique event IDs; reject explicit synthetic/mock/fixture markers | Authenticating host events and actual historical execution |
| Producer v1 consumed by v2 request | Trusted consumer version is separate API/CLI input; exact mismatch rejects; missing version is unverified in completion mode | Authenticating producer labels, byte content and scientific correctness |

Hash binding is not a signature. This implementation does not cryptographically authenticate a host or reviewer and does not automatically classify manuscripts. The trusted controller must actually start independent review, inspect its returned evidence and protect the acceptance from worker writes. The CLI rejects acceptance paths inside the artifact root; merely moving a forged file elsewhere does not make it trusted. An untrusted caller can still lie about its inputs. Without a real trusted controller boundary, do not supply acceptance and do not claim completion.

## Current callers and migration

- `scripts/validate_paper_delivery.py RECORD --root ARTIFACT_ROOT --acceptance CONTROLLER_FILE`; API `validate(record, root, acceptance=trusted_object)`. Missing acceptance for requested completion returns `completion_status: unverified`. Partial/blocked records remain explicitly non-complete.
- `scripts/semantic_acceptance.py` binds canonical entire record, every declared file hash, each language snapshot, independent reviewer identity and explicit evidence for artifact fit/originality. Schema and actual role event requirements are in `workflows/paper_delivery_contract.md`, synchronized into all four paper roles.
- `scripts/validate_handoff.py RECORD --root OUTPUTS --require-complete --expected-input-version CONSUMER_VERSION`; API `validate(record, root, True, expected_input_version=trusted_version)`. The producer's inline expected-version field is never trusted. Without completion mode the legacy local integrity inspection remains available, with `completion_verified: false`.
- `scripts/agent_eval_pipeline.py` snapshots the new helper; ordinary tasks still do not run development evaluations. These completion checks are normal task QA, not a benchmark trigger.

Do not migrate old records by fabricating host events or recomputing an old review's hash. Observe missing execution, obtain current independent review, then create a new bound record. Existing untrusted synthetic control records now show **unverified**, not semantic false positives for good prose. Positive protocol tests use clearly designated simulated controller fixtures, never reported as real model events.

## Executed program evidence

[program-results.json](program-results.json) records 18 actual test methods (14 semantic gate, four consumer context) with logs and source hashes. Tests cover positive acceptance, canonical ordering, missing/inline/self review, stale target/snapshot/file hashes, reviewer rejection, missing evidence/language coverage, dispatch/queued events, wrong actor/task/run/revision/attempt, duplicate IDs, synthetic/malformed markers, alternate version IDs, and real CLI path boundaries. Test methods may contain multiple explicit subcases; do not equate this count with independent statistical samples.

[runtime-results.json](runtime-results.json) records 38 actual program cases, now bound to a separately frozen followthrough rubric. Historical rubric/results remain untouched. [Paper review](paper-review.md) and [handoff review](handoff-review.md) include independent probes and trust limits. Initial test failure after the report vocabulary change is retained in [full-tests-initial.log](full-tests-initial.log); corrected [full-tests.log](full-tests.log) has 275 passed, [reader-tests.log](reader-tests.log) has three passed. Offline reference synchronization and original archive replay also succeeded.

The tests with explicit reviewer fail values prove enforcement, not semantic detection accuracy. Actual new host material judgments and their independent acceptance are recorded separately; no finite synthetic result certifies full paper generation, real published-exemplar learning, or broad plagiarism detection.

## Fresh real host recheck

One new blinded host batch pinned `5d220eb` used separate neutral material/consumer inputs. It accepted the bounded group-count mechanism brief, identified byte-identical borrowed material and inventory-only substitution, ran four actual handoff CLI commands, and kept missing semantic acceptance/queued dispatch unverified. An independent context reread material and actual outputs, recomputed the grouping example, checked hashes and replayed the four commands. All four frozen criteria passed; [per-item records](host-items.json) retain observed raw fields and distinguish correct unverified from semantic pass. This is one correlated synthetic batch, not a reliability estimate.

[Grade](host-grade.json), [replay report](host-reports.json), and [archive hashes](artifact-manifest.json) preserve the actual run. Replay with:

```sh
python evals/crossfeature/replay_host.py docs/crossfeature_validation/followthrough/host-evidence.tar.gz
```

The real role read the paper acceptance implementation, but did not run a complete paper-delivery CLI record or create a submission. Actual paper CLI gate execution is covered by separate synthetic program controls. No paid API, paper draft changes, universal semantic detection claim or manufactured trusted historical event is involved.
