# Frozen real model role regression — 2026-10-06

**Latest attempts: 17/17 pass. First collected attempts: 15/17 pass.** All 14 roles in the frozen role registry were actually dispatched, plus a main-general task and a real coordinator→writer pair. There were 19 fresh worker contexts (`fork_turns=none`), not 19 Python test fixtures. The independent controller graded collected bytes against the original fixed rubrics. No rubric was supplied to workers.

Candidate: `2bc1fc5d41920d4c82edc6233c31956b37f6a2b8`; Git tree: `6803cefca363c97c07798231826c38ceaaebae21`. The existing `scripts/agent_eval_pipeline.py` was copied exactly from that revision and used for prepare/start/collect/grade/report. The full denominator was frozen before dispatch; the writer run was prepared only after the actual coordinator files were collected and copied unchanged. See `summary.json`, both manifests/reports, and `handoff.json`.

## Outcomes and retained failures

| Case | First attempt | Latest | Evidence / caveat |
|---|---|---|---|
| research-assistant | pass | pass | v2 dependency invalidation, actual CPU arithmetic/plot, independent DAG and Decimal check |
| research-explore | delivery failure | pass (2) | First worker wrote all files in attempt root, leaving outputs empty; wrong-location originals retained. Fresh context used exact output path. |
| research-implement-optimize | pass | pass | Corrected full-window boundary; actual CPU execution of independent deque/Fraction oracle, 9,047 checks |
| research-figures | pass after QA repair | pass | Missing CairoSVG first render; installed PyMuPDF fallback initially lost arrowheads and overlapped a label; explicit arrows/label repair. All logs and before-images retained. |
| research-write | pass | pass | Both prose artifacts and evidence table correct; loaded/execution metadata was misplaced in attempt root, retained as a protocol deviation, not silently moved |
| research-review | pass | pass | Universal 2× claim rejected; appendix-disclosure concern explicitly withdrawn |
| research-read-pdf | pass | pass | All three full physical page images actually opened; PDF-hash-bound coverage includes appendix |
| paper-reading-companion | pass | pass | Correct calculation, saved physical page 2, real embedded offline HTML; static integrity checked, browser runtime not tested |
| explain-research-concepts | pass | pass | Correct fixed-V Jacobian and CPU finite-difference check; local versus finite perturbation distinguished |
| travel-planner | pass | pass | Both revisions preserve independent 75-minute rest and 16:00 booking; actual CPU consistency check |
| research-data-visualization | pass | pass | All eight values, both timing scopes, regression retained; final color/size/grayscale images actually opened |
| research-diagrams | pass after QA repair | pass | Six nodes/five edges; first superscript overlap repaired using readable transpose notation; before-images retained |
| code-reading | pass | pass | Controller observed read-only source access; static caller/data trace closes at original-vector full_score |
| code-organization | fail | pass (2) | First proposal lacked a usable rollback method. Independent fresh retry supplies exact document backup/hash/concurrency-guarded rollback and empty migration allowlist. |
| smoke-main-general | pass | pass | Roommate owes user 11 CNY; direct ordinary answer and natural reminder |
| chain-coordinator | pass | pass | Actual CPU aggregation of all 18 raw rows; medians 32/24, 56/58, 96/80; real source/aggregate hashes |
| chain-writer | pass | pass | Actual coordinator bytes copied unchanged; writer requested and received real SHA verification before writing claims |

The recorder reports one semantic wrong→correct transition and zero correct→wrong transitions. The empty-delivery recovery has no semantic verdict, so it is counted separately. First-attempt success means the first collected task attempt; it **includes tool-proxy assistance and bounded visual QA repairs**. It is not an unassisted first-try metric. No failures, retries or pre-repair images were removed.

## Observable process and limits

Start receipts contain the actual `collaboration.spawn_agent` returned task names. Completion records are controller transcriptions/summaries of observed final messages, not fabricated agent self-receipts or verbatim transcript exports. Host records retain requested commands, actual tool results and exit codes; visual records bind opened image hashes to concrete observations. Code-reading/organization targets were read through the controller and never executed. Workers and grader used separate contexts but shared a filesystem; this is not OS isolation or cryptographic attestation. The controller also supplied process feedback, so results describe assisted synthetic smoke execution.

Exact model identifier and cost are **unknown**. Workers inherited the host model; no model override was requested. Frozen adapter initially recorded concurrency 3; the parent later authorized a peak of 4, documented in `run/host/concurrency-change.json`. No paired baseline/model-matched trial was performed. These results do not establish improved research accuracy, better aesthetic quality, general success rate, production/backend integration, or a latency/cost advantage. The real local effects established are the recorded artifact correctness and retained recovery behavior on this fixed catalog.

Remaining interface follow-ups: make absolute output destinations unambiguous in future host dispatches, and keep concrete rollback examples close to organization handoff requirements. The original skill already requested rollback; the first worker still omitted it. A passing recovery does not erase that reliability limitation.

## Restore and replay

The archive stores one shared snapshot, both complete case trees with all attempts, inputs, outputs, host records, the exact pinned pipeline, initial manifests and real handoff evidence. `archive.json` records its SHA-256 and size; `archive-files.json` inside records every payload file hash. Historical absolute paths remain unchanged for provenance.

From this directory, choose a new destination:

```bash
python restore.py --out /tmp/agent-model-eval-2026-10-06
```

The script checks the archive hash, restores exact files, verifies payload hashes, expands the same snapshot into both runs, and replays the frozen recorder's integrity and grade records. It refuses to overwrite an existing destination. Replay verifies retained records; it does not rerun models or independently recreate the semantic reviews. It requires only standard-library Python for replay; original worker plotting/rendering used the versions recorded in artifacts.
