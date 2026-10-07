# Prior-result registry validation

This directory records implementation-owned CPU checks for the immutable result
registry, bounded search and scoped reuse decision. It is not a claim that every
historical project result was migrated, that an external verifier was deployed,
or that lexical retrieval has complete semantic recall.

## Implementation and checks

- Runtime: `agent_runtime/result_store.py`
- CLI: `scripts/result_store.py`
- Contract: `workflows/result_reuse_workflow.md`
- Tests: `tests/test_result_store.py`

Run from the repository root:

```bash
python -m unittest discover -s tests -p 'test_result_store.py' -v
```

The 21 focused tests use real local CPU integer-square-sum outputs and distinct
closed-form/boundary checks in an explicitly trusted test callback. They cover:

1. Native central registration remains pending before independent verification.
2. Exact scoped acceptance, explicit reuse handler, revalidation at consumption.
3. Explicit reproduction/new claims, including top-level task flags, never skip.
4. Changed scope, code, input hashes, hardware description or units require delta checks.
5. Missing information and unknown-equals-unknown do not prove compatibility.
6. Stale raw data, registry condition tampering and accepted-proof changes fail closed.
7. Persisted pass labels and producer self-review do not authorize reuse.
8. Measurement freshness is not replaced by registration time.
9. Duplicate IDs fail and identical producer replay preserves the same record.
10. Historical files remain byte-identical and explicitly referenced, not migrated.
11. Bounded scans report partial results and malformed records.
12. Missing stores are read-only; no files are created by search.
13. Chinese paraphrase lexical overlap retrieves a candidate, without certifying it.
14. Protected guide roots, aliases, symlink paths and traversal are rejected.
15. CLI decisions without a trusted verifier stay unaccepted.
16. Real ReportingHandler registers producer output and binds current reuse proofs.
17. Actual producer subprocess counts stay at one during repeated reuse and
    decision support; authorized delta and explicit-reproduction rounds raise
    the total to three in separate directories without altering old samples.
18. A catalog-only timestamp cannot satisfy freshness; a bound execution time is required.
19. Exact-context fallback retrieves a valid candidate with no lexical query overlap.
20. Failed/partial empty scans are explicitly incomplete, not definitive no-hits.

The registry uses the existing result-validation trust boundary, rather than
inventing acceptance from stored JSON. A host callback must independently check
actual executed code/data and contextual criteria; hashes alone do not do this.
The test callback is a local fixture, not a general scientific verifier.

Integration with prepare/dispatch/report handling and independent adversarial
acceptance are recorded separately by the coordinating task. Focused unit tests
alone do not prove a live model follows reflection instructions or a host daemon
has been installed. Final aggregate checks must run after integration edits.

## Actual current-project records

`doc/results/prior-result-store-cpu-20261007/` contains one actual bounded CPU
producer execution, 12 raw rows from four fixed integers and three repeats, and
the derived sum of 42. Source, inputs, configuration, environment, command receipt
and independent-validation criteria are frozen. Its initial record remains
pending; current scoped acceptance is a separate independently obtained proof,
not a rewrite of registration history.

Two historical records reference already-existing AIK finite-math/retrieval and
VEX Softmax/RoPE numerical artifacts by exact paths/hashes. They are explicitly
unknown under the new acceptance contract. No old bytes were moved or copied,
and this is not an exhaustive migration of the repository's historical data.

`current-project-search.json` records a Chinese lookup finding these actual
records. Lexical/CJK retrieval can overretrieve or miss paraphrases; exact current
context supplies a bounded fallback for decision support. Neither route grants
acceptance without a live trusted independent verifier.

`independent/actual-result-independent.json` records a separate review of the
actual case: exact reuse succeeds, changed input requests delta verification,
explicit reproduction requires rerun, and the producer invocation count remains
1 → 1 across six cheap reference callbacks. The reviewer blocked subprocess
execution during those checks. All original run bytes remain unchanged.

The accompanying independent audit source is a byte-preserved historical
artifact with absolute paths to its original audit environment. It is not a
portable CLI or an automatically trusted adapter. A portable successor would
need a new source version and current independent evidence.
