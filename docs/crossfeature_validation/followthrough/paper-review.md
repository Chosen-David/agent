# Paper completion gate: independent follow-through review

Reviewer: `/root/eval_research`, independent of implementation author
`/root/paper_code_cases`. Original crossfeature results and frozen paper run are
unchanged. This follow-through reviews enforcement of trustworthy completion
records, not a new general-purpose plagiarism/genre detector.

## Trust and success boundary

The new module checks an externally supplied controller decision, canonical
record hash, declared file hashes, per-language snapshot and independent reviewer
binding. Missing acceptance and inline worker-supplied acceptance must not permit
completion. Semantic judgment still belongs to the real independent reviewer.
Manually setting a test verdict to fail proves gate propagation; it is not a
model detection result. Real host semantic judgments must remain a separate
evidence layer.

An external file path, actor string, matching hash or unique event ID does not
authenticate a person/process. The CLI's external-to-artifact-root restriction is
an accidental trust-boundary guard, not OS isolation: a malicious same-filesystem
worker may still forge an external file unless the host protects it. The API is
only for a trusted controller. No cryptographic authenticity, model context
isolation, actual reading or controller honesty follows from this module.

## Initial independent probes

Executed against the initial implementation, using program-only fixture data:

- Missing acceptance, list instead of object, boolean schema version, empty
  accepted versions, writer as reviewer and malformed evidence all reject.
- The complete positive fixture with explicitly `synthetic: true` receipts
  **accepted**. This contradicts using those receipts as actual-role completion
  evidence; synthetic provenance in a test must not authorize real completion.
- Receipts naming an unrelated run/task/attempt **accepted**, because only
  actor/role/revision were compared. This left task association entirely to the
  controller even when mismatching fields were explicitly present.

Both issues were reported directly to the author and controller. The agreed
correction rejects synthetic/fixture/mock receipt markers, requires started and
produced states, binds receipt run/task/attempt to task bindings and run identity,
and rejects acceptance paths within the artifact root. Positive unit-test event
payloads remain simulations; their test-layer provenance must say so explicitly.

## Corrected-source review and independent retest

**The two initial defects are resolved for the declared protocol.** Independently
read the revised `validate_role_events(binding, root, expected_run_id)` and CLI:
both events bind nonempty actor/role/revision/run/task and positive integer
attempt; binding run matches the record, start requires `started`, completion
requires `produced`, and event IDs remain globally unique. Explicit synthetic,
fixture-only and mock-adapter markers reject. CLI resolves the acceptance path
and rejects one within the artifact root, including symlink resolution.

Executed independently after the correction:

- `test_semantic_acceptance.py`: **14/14 passed**, including the actual CLI's
  missing/internal/external acceptance cases and byte/record/snapshot mutations.
- `test_paper_delivery.py`: **32/32 passed**, retaining positive completed and
  honest partial-delivery controls as well as old scientific/visual constraints.
- `test_crossfeature_delivery.py`: **2/2 passed**. These are regression tests,
  not new host-role execution results.
- Additional direct validator probes regenerated the controller's acceptance for
  each changed record, so a stale-hash rejection could not mask event validation:
  `synthetic=true`, `fixture_only=true`, `adapter=mock`, wrong run, wrong task,
  boolean attempt and queued start all rejected for the intended event reason.
  Unchanged protocol-shaped control accepted. Seven additional malformed
  acceptance values rejected without exception (null, bool, integer, string,
  list, null version, non-string language).

The new module has no keyword-based paper classifier. A correct trusted reviewer
decision is still a prerequisite; an arbitrary fabricated external acceptance
cannot be detected if the controller wrongly treats it as trusted. This is
documented, not a claimed authenticated security boundary. Actual host semantic
rechecks on the pinned new implementation remain a separate next step and are
not credited by these program tests. Original run outcomes are unchanged. No
production code edited by this reviewer; no further blocking protocol defect
found within this bounded inspection.
