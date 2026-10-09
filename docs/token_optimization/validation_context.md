# Recoverable validation display

For coordination that needs the validation decision but does not inspect every provenance hash, the existing CLI supports an explicit display option:

```powershell
python scripts/validate_experiment_result.py --root ABSOLUTE_PROJECT_ROOT --contract controller-contract.json --context-dir agent_doc/results/RUN_ID/validation_context
```

It still invokes the normal live gate and preserves its exit code (pending remains 2). The default full output is unchanged. The new display preserves status, scope, errors, next action, verifier, limitations and every other proof field. Only `proof.artifact_hashes` and `proof.review_evidence` move out of the visible payload. Complete original JSON is stored immutably with project binding and a content hash. Unknown result fields refuse instead of being silently dropped. Human guide guards run before writes; records stay under the selected project's results, never an installed skill's project or its ordinary doc directory.

Use returned `record_ref` to restore details when the next task needs them:

```powershell
python scripts/validation_context.py --root ABSOLUTE_PROJECT_ROOT --path RECORD_REF_PATH --sha256 RECORD_REF_SHA256
```

Restoration rejects changed bytes, unsafe paths and records copied from another project. It returns an observed history, not current acceptance. Always obtain the existing trusted independent verifier for scientific use, resume or reuse; status stored in either display or complete history grants no permission. This adds neither an automatic history rewrite nor a persistent acceptance cache. Small/no-proof outputs may grow, so compatible callers opt in only when details are not needed; needed-detail retrieval and further turns have costs.

Research: [DTOC, arXiv 2609.26121v1](https://arxiv.org/html/2609.26121v1), methods §3 and results/ablation §5, retains full outputs with reversible visibility. Its small benchmark reports mixed model-dependent outcomes; retained details and recovery motivate this display boundary, while its percentages do not establish our savings. We do not implement its learned visibility policy.

TOK-004's one real pending CLI observation (38 references) used total provider input+output 21,635 → 19,695, saving 1,940 (8.97%). Input alone decreased by 1,940; both outputs were 68 tokens, and both blocked consumption with identical status/errors/action/scope. Paired spend 41,330; caches not subtracted. Actual non-task plaintext, tools, model and question/schema matched. Full source snapshots precede dispatch; independent complete restoration, 6 Windows display tests and 18 WSL result-gate tests passed. [Artifacts](../../agent_doc/results/token-004-context-20261010/) record scope. No retrieval, long-horizon/full-workflow, statistical or cash-cost saving claim; development/chat/research usage is excluded. Main verification is tracked separately in progress.json before counting.
