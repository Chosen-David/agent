# Independent integrated acceptance

Final local release readiness is accepted for base `e7a908aaa2198d740dd4fcfc835b8e2931db16e5`: 109 task IDs, unchanged tested code, preserved source archives and no guide files. See the [final task-only supplement](final-task-only-supplement.json). External publication and remote readback remain separate gates.

The combined candidate passed **73 independent tests**: 33 document-architecture, 15 result-validation and 25 prior-result-reuse tests. There were no failures, errors or skips. Reviewed source hashes did not change during the run. Generated package references also passed `scripts/sync_plugin_references.py --check`.

## Verified migration

The canonical index contains the exact union of 96 prior requirements and 90 upstream requirements: 106 unique IDs. Titles and prior checkbox states are retained. At initial union reconciliation, all 96 prior detail files were byte-identical; subsequent closeout changed only Progress sections for AIK-01/02/03 and DOC-01/04, retaining all 96 stable planning hashes; both original task archives match their recorded hashes. All 206 inspected relative detail links resolve. The root TASK is navigation only, and `doc/guide/` contains no files. Later approved Progress-only updates and nine functional completion marks are distinguished from this migration snapshot; stable Plan hashes remain unchanged. The final task-only upstream update adds INDEX-01..03, producing 109 IDs.

## Verified data reuse

The real local CPU case contains 12 complete input/repeat rows with sum of squares 42. Independent source inspection, exact reference arithmetic and frozen-file checks accepted only that scope. Exact reuse completed with the producer invocation count unchanged at 1. Six cheap validation callbacks made zero producer subprocess calls. Changed inputs require `verify_delta`; explicit reproduction requires `rerun`. No raw/result/record bytes were changed.

The original execution receipt came from the producing process and was checked for consistency; this is not OS-level attestation. No speed, model-benefit or universal correctness claim is made. Guards apply to supported application entry points, not arbitrary shell access or an OS ACL.

## Evidence

- [Review and closed defects](review.json)
- [Test results and source hashes](test-results.json), [test log](test-results.log)
- [Migration union and preserved detail hashes](migration-union.json)
- [Current real-result audit](actual-result.json)
- [Markdown test-interpretation correction](markdown-test-correction.json), [current knowledge integration](knowledge-integration-review.json)
- [Progress-only phase](progress-only-closeout.json), [final task-only acceptance](final-task-only-supplement.json)
- [Portable read-only audit](audit_integrated_cpu_result.py)

From the repository root, the audit can be rerun without executing the producer:

```bash
python docs/document_architecture_validation/independent/audit_integrated_cpu_result.py --root . --output /tmp/project-result-independent-audit
```

This audit accepts only the already reviewed frozen demonstration. The broader full-suite and external publication checks are separate gates. Prior failed checks were retained during the work; the current report records the defects and their independently retested fixes.

## Final integrated checks and scope

On the `18e0904c9e2b9343cf7163bd2cb38cb14c362ec6`-based candidate, the full suite passed 729 of 730 tests with one environment-specific tmux skip; the reader suite passed 3/3. The original two link-scanner failures were preserved, then corrected as Markdown interpretation errors. Independent controls still reject real missing, outside-package and symlink-escaping dependencies. This is not a runtime or model-quality gain. See [scanner correction](markdown-test-correction.json).

The 74→76-entry knowledge supplement was independently checked against the preserved baseline and actual recorded per-query results: all 148 baseline files and four approved added-card files remain byte-identical; 72 old query/backend comparisons have zero new regressions. Current development context hits are 21/24 by default and 23/24 with explicit domain filters. Three known misses recover only with explicit informed selection, within 14,118 characters; this does not fix automatic ranking or establish blind/model gains. See [knowledge review](knowledge-integration-review.json).

[Later Progress-only updates](progress-only-closeout.json) are distinct from the immutable initial migration proof. A newer upstream head requires an affected-dependency check before this acceptance is reused for publication; this report does not claim that later or external publication is already verified.
