# Release dependency impact: a223ffc → a3906ea

EXECUTE: rerun research-implement-optimize only; retain other 18 cases as qualified pinned evidence.

Reviewed 19 current cases and 89 declared snapshot dependency reads. All task/input hashes and declared old-source hashes match; zero verification failures. The only changed loaded dependencies belong to `research-implement-optimize`.

## Scope and recommendation

- Execution and experiment contract were actually read by research-implement-optimize. Added optional runner capability changes model-visible rules even though this particular task is CPU-only. Reusing its old result as current-rules evidence would silently substitute changed instructions.
- All 18 other cases have byte-identical task-relevant loaded dependencies at target, and task/input hashes still match their manifests. No role registry, entrypoint, existing CPU runner or smoke harness change appears in the ten-file diff.
- Research-assistant and chain-coordinator handle supplied measurements and downstream planning/handoff, with no new experiment authorized. Their loaded execution/data-visualization paths are unchanged. Unloaded implementation fallback and experiment contract are not relevant to these fixed task intents; same broad package ownership does not mandate rerun.
- Chain-writer consumes the unchanged coordinator handoff; both delivered files match byte-for-byte. It has no dependency on implementation-case outputs. Rerunning the implementation case does not invalidate this writer.
- The new adapter remains separate: CLI actions only plan/scaffold, trusted Python run checks host authorization and capabilities before observation; performance requires scheduler exclusion and resource admission. The optional addition does not itself request GPU work in any current case.

## Exact changed files

| Status | Path |
| --- | --- |
| A | `docs/experiment_evidence/gpu-adapter-tests.log` |
| M | `docs/experiment_execution_upgrade.md` |
| M | `plugins/research-assistant/skills/research-assistant/references/experiment_execution_contract.md` |
| M | `plugins/research-assistant/skills/research-assistant/references/research-implement-optimize_execution.md` |
| M | `plugins/research-assistant/skills/research-implement-optimize/references/execution.md` |
| M | `plugins/research-assistant/skills/research-implement-optimize/references/experiment_execution_contract.md` |
| A | `plugins/research-assistant/skills/research-implement-optimize/references/gpu-request.example.json` |
| A | `plugins/research-assistant/skills/research-implement-optimize/scripts/gpu_adapter.py` |
| A | `tests/test_gpu_adapter.py` |
| M | `workflows/experiment_execution_contract.md` |

Exact old/new SHA256 values, per-case loaded source hashes, task hashes, and every input hash are in `main-impact-a3906ea.json`. Added files have a null old hash. Both local HEAD and origin/main were observed at the target revision; no network was used.

## Per-case disposition

| Case | Declared reads | Changed reads | Disposition |
| --- | ---: | ---: | --- |
| chain-coordinator | 7 | 0 | Qualified reuse at original pin |
| code-organization | 3 | 0 | Qualified reuse at original pin |
| code-reading | 4 | 0 | Qualified reuse at original pin |
| explain-research-concepts | 3 | 0 | Qualified reuse at original pin |
| heldout-travel | 4 | 0 | Qualified reuse at original pin |
| paper-reading-companion | 7 | 0 | Qualified reuse at original pin |
| research-assistant | 9 | 0 | Qualified reuse at original pin |
| research-data-visualization | 4 | 0 | Qualified reuse at original pin |
| research-diagrams | 5 | 0 | Qualified reuse at original pin |
| research-explore | 3 | 0 | Qualified reuse at original pin |
| research-figures | 6 | 0 | Qualified reuse at original pin |
| research-implement-optimize | 4 | 2 | Rerun |
| research-read-pdf | 3 | 0 | Qualified reuse at original pin |
| research-review | 3 | 0 | Qualified reuse at original pin |
| research-write | 3 | 0 | Qualified reuse at original pin |
| smoke-main-general | 3 | 0 | Qualified reuse at original pin |
| smoke-main-route | 11 | 0 | Qualified reuse at original pin |
| travel-planner | 4 | 0 | Qualified reuse at original pin |
| chain-writer | 3 | 0 | Qualified reuse at original pin |

## Changed rule evidence

| Path | Old SHA256 | Target SHA256 |
| --- | --- | --- |
| `plugins/research-assistant/skills/research-implement-optimize/references/execution.md` | `fd9a1d210c36a6bab7e58864a6b568aee8a857cdf82fa32754937881f11b0726` | `b2d819f8f5e5f38bb509b431b8d48801c7fd210e74667eebe714607b41e3a69a` |
| `plugins/research-assistant/skills/research-implement-optimize/references/experiment_execution_contract.md` | `332c81342ab89b8f165c702a32962b879199f82af811459d16adc23f29a27f9f` | `38cc2cbb3cc4846ee872b53bc046eeb5dc3b2c9a0650e376047cecfdec97a081` |

## Rerun acceptance

- Use a fresh a3906ead554ab8ae84b9e3e777732e2f9d94c460 snapshot/run namespace for research-implement-optimize; preserve old records.
- Keep the exact existing task and buggy.py/measurements.csv input hashes; record actual loaded SHA256 values including the changed execution and experiment contract.
- Run only bounded CPU correctness checks for moving_average and descriptive analysis of supplied CSV. No GPU probe, GPU/model run, new timing or benchmark is required or authorized by this audit.
- Grade the new attempt through the existing independent review procedure; label reused cases with original a223ffc provenance plus this impact audit, not as freshly executed at a3906ea.

## Handoff evidence

| File | SHA256 at coordinator and writer | Match |
| --- | --- | --- |
| analysis.json | `1ae4b8e86c83a75879e8b6a64a22703df7c2e38274ec16c9cead5dd00853537f` | True |
| aggregate.csv | `ecdd7ddb5671baf99449eba1336b559f40a3fef08fe3b785cd60a85d0557cb7b` | True |

## Limits

- loaded.json is an execution attestation, not a complete operating-system read trace. This audit verifies declared reads against snapshot bytes and git blobs; it does not prove undeclared context was absent.
- Reuse is limited to these exact tasks, inputs and recorded dependencies. A coordinator task routing into implementation/GPU execution, changed input, newly loaded contract, or later commit requires a new impact decision.
- This is not a fresh model rerun or full semantic regression proof for reused cases. Host model identity/temperature/seed are not exposed according to run manifests.
- Adapter source/tests and checked-in log were inspected, but this audit did not execute those tests, a GPU probe, a model, or a benchmark. Existing CPU/mock evidence cannot establish real GPU integration or performance.
- origin/main is the locally observed reference; this subtask performed no network fetch. Parent is responsible for fresh remote synchronization and any later-commit impact check.
