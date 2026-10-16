# MEM-SCOPE-05 candidate v1

Repository Chosen-David/agent; base ab8a368746233996cb39233036a1631de1d911f2,
project_memory.py SHA256 c3f41593b64b09d2af190d9ddcb64bbf784720083f4b718a5bdaf5318109f159.
Authorized memory reliability/efficiency upgrade; direct main only after validation.
Human guide directory untouched. Manual independent plan/result contexts, not a
managed ReviewSession, real model host or background supervisor.

Hypothesis: current list fast path is gated on mixed status. All-active scoped
queries therefore hydrate every content/source/dependency packet. Reuse existing
metadata-first scope filter for builtin-string scope on homogeneous status stores.
No cross-call caching, schema migration, SQL JSON semantics or model KV policy.

Candidate edit: broaden the existing filtered predicate from mixed status to
mixed status OR builtin-string scope, keeping base-class/status/all guards and
missing-dependencies fallback. Existing mixed-status behavior must not change.
If needed a conservative guard is allowed only before freezing final candidate.

Contract: API-created valid ledgers return identical complete packets/order and
fresh objects; JSON scope/document decode errors precede membership errors;
legacy missing document table and missing dependency table remain observable;
None/non-builtin scope, subclasses/status subclasses and status=all keep fallback.
Do not claim arbitrary manually corrupted SQLite schemas/content bytes have
identical errors: inspect and explicitly bound any changed case before adoption.
No silent fallback for invalid selected metadata. Transaction and lock lifetime
unchanged; Python traced memory is not RSS, wall time is not model TTFT.

Before edits: actual ResultStore query `memory all active scope hydration`,
scan200/partial/60 errors; hits check03/scope02 and two irrelevant corpus entries.
Read scope02 report: all-active case explicitly deferred, old metrics only context.
Knowledge query `late materialization predicate filtering`: segment-monoid lone
low-score hit irrelevant, rejected. Earlier >=12 original memory/KV paper matrix
and subsequent directed readings inspire tiered materialization, not novel SQL.

Required sequence: independent plan review -> red structural regression -> edit
-> targeted parity -> freeze -> independent code/data reviewer and paired timing
-> complete tests/readers/docs -> fresh main/CAS -> byte readback. Maximum 2
candidate revisions; no parallel timing. No claims before independent acceptance.

Benchmark: reuse scripts/bench_memory_retrieval.py pinned to base above. Synthetic
DB, seed51610,21 randomized paired repetitions, identical DB hashes, one warmup
and complete output equality. Full list boundary includes connection/path/transaction
and returned object assembly. Primary two cases:2000 all active, match every100,
content128B/8192B. Controls:2000 allactive allmatch128B;2000 allactive no-scope;
8 allactive allmatch;2000 mixed/1000 active scope-sparse;2000 mixed no-scope.
Adopt iff each primary median wall improvement>=25% and each control regression
<=15% in both primary and independent runs. Raw orders/samples retained. No GPU,
model, disk-cold, QA, token or native allocation claims. No public commit on failure.

Correctness: current base as differential reference (not original slower eager),
scopes string/list/dict/null/bool/number/malformed bytes/deep JSON, first error
ordering, all statuses/unknown, documents table present/absent/malformed, dependency
missing/columns, empty/short/large, content sizes, subclasses, correction/acceptance,
and held traceback followed by writer. Reviewer designs independent probes.

Only root writes source/tests/config/report/task/index and publication; reviewer
owns separate independent evidence paths, no guide writes. Data artifacts become
public only with usable-with-scope acceptance; private checkpoints otherwise.
