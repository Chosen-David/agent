# Independent local handoff integrity audit — round 1

Decision: pass for the bounded validator correction; no claim of LLM task-quality improvement.

## Frozen acceptance and execution

Before reading the replacement implementation, the auditor saved the baseline validator, wrote 19 independent synthetic cases in `holdout.py`, and froze `acceptance.json`. The executor was told the acceptance categories, not asked to tune the cases. The fixtures use a two-artifact/two-task delivery with extra disconnected work; they are not copies of the repository unit-test fixtures. Acceptance applies to the *listed tasks in this handoff*, not a future project backlog.

Each case runs both the direct `validate()` API and a fresh Python CLI subprocess. A passing rejection must return diagnostics without an uncaught exception; the CLI must emit JSON and the correct exit status. A valid partial record is also checked against `require_complete=True`. Runs use the same local Python, inputs, artifact contents, and validation budget; no model calls or external backend executions are involved.

- Baseline SHA-256: `7bba4afecafc939677f0b74214110c6408a347e5386c542dd42298b3c143fc1a`
- Candidate SHA-256: `f13b91e68e2dd9e82f6694fc69927d703712da08c50f3f475678f525e40730f8`
- Baseline: 6/19 pass. Ten cases falsely accept invalid records; three cases expose an API exception (two also crash the CLI; embedded NUL was already caught by CLI).
- Candidate: 19/19 pass. All six baseline-valid cases remain valid.
- Repository `test_handoff.py`: 16/16 pass in an additional direct run.

Commands executed from the repository:

```sh
python /tmp/handoff-holdout-r1/holdout.py /tmp/handoff-holdout-r1/validate_handoff_baseline.py baseline --lock
python /tmp/handoff-holdout-r1/holdout.py scripts/validate_handoff.py candidate
python -m unittest discover -s tests -p test_handoff.py -v
```

## Confirmed changes

1. A completed record cannot hide disconnected todo/doing/blocked work.
2. Task evidence uses local artifact IDs with explicit list/string checks, including non-done tasks when evidence is provided. A task ID is not interchangeable with an artifact ID.
3. Independent skipped work with a nonblank reason remains terminal; omission of the optional task array remains supported.
4. Self-referential artifact/root symlinks and embedded NUL paths produce diagnostics instead of escaping the API.
5. Relative local paths, separate artifacts per task, and valid partial recovery records retain the expected behavior.

## Code and contract review

Read `AGENTS.md`, `prompts/decision_review.md`, `docs/handoff_validation.md`, `docs/backend_handoff.md`, `scripts/validate_handoff.py`, existing tests, their diff, and repository references to this validator. The local handoff schema is explicitly distinct from backend/domain evidence objects, so this change does not require rewriting their unrelated `evidence` fields. The original long-DAG fixture incorrectly coupled pending tasks with a completed record; changing it to done tasks with artifact evidence preserves its DAG test purpose.

No blocking defect found in the bounded change. One wording correction suggested: changing an old record to `partial` alone cannot repair malformed evidence. Undelivered tasks must also become non-done, with invalid evidence removed or corrected. The implementation correctly keeps rejecting invalid evidence on partial records.

## Limits and remaining candidates

These are adversarial program checks, not representative frequency estimates or evidence that all agents now reliably finish tasks. The validator remains opt-in; it is not invoked automatically by a complete producer/consumer runtime. It cannot discover omitted tasks, judge whether a skip was authorized, or prove an artifact's semantic truth. Mutable output directories and hostile filesystem races remain outside the stated security boundary. Artifact reading still loads each file in memory; streaming hashes and large-DAG cost are candidates for later evidence-driven work, not blockers for this correction. No GPU, live backend, model quality, latency, or cost comparison was performed.
