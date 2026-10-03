# Runtime and coordination executable coverage

Run from the repository root:

```sh
python evals/crossfeature/runtime_execute.py --out /tmp/runtime-results.json
```

`runtime_rubric.json` was frozen before executing the new cases. The runner imports existing test suites instead of copying their fault logic. Each output case contains the actual unittest result/log and the tested source hash. It uses actual temporary SQLite databases, files and bounded subprocesses, with named synthetic clocks and handlers. It never records these as host model outputs.

The initial execution in `runtime_results.json` has 37 passing program cases, zero failures/skips, and one explicit consumer-version semantic gap. This sample contains four new bounded cases: exact lease expiry across restart (holdout), actual absent/matching/tampered artifact bytes, intentionally declared empty-file bytes (holdout), and handoff integrity before/after byte corruption. Legacy cases cover duplicate ticks/restart, process claims/crash recovery, stale leases and fencing, permission denial, cancellation, evidence dependencies, retry budgets, scheduler races, authorization service failure, non-regular/oversize artifacts and owned-monitor cleanup.

The handoff gap is deliberate reporting of an existing boundary: `validate_handoff` accepts intact v1 output despite an independent consumer requesting v2. It validates local integrity and has no consumer-version argument. The recorded semantic false negative is **not** a unittest pass and is not evidence of model behavior. The blinded host fixture/catalog is `coordination_inputs/` plus `coordination_tasks.json`; `coordination_rubric.json` stays with the independent acceptance evaluator. Both the producer's actual result bytes/hash and the consumer's version must be read. The host needs to reject current-input consumption while accepting intact original bytes, preventing a blanket rejection strategy from satisfying the rubric.

No archive/move/comment-reduction engine exists here. Codeorganization remains a host semantic task owned by the main evaluation catalog, not certified by filesystem hashes alone. No test touches SGLang, private papers, user directories or external APIs. No daemon is installed.

Remaining boundaries: multi-host/NFS, large clock jumps, database loss, arbitrary external side-effect cancellation, semantic adequacy of hash-matching/empty artifacts, and artifact changes after terminal completion. Distinct new deterministic holdouts are not a training set or a generalization estimate. This runner does not claim an installed supervisor or a running monitor.
