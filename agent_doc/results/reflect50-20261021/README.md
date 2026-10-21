# REFLECT50 — 2026-10-21

50 distinct source/behavior iterations address file ownership, Markdown loading,
memory navigation, retrieval, evidence IO and opt-in storage. Final v3 is independently usable-with-scope: 54 tests passed with zero skips.
`final-status.json` and `final-verification.zip` retain the observed native review.
Historical group acceptance does not grant acceptance to a later source snapshot.

| Iterations | Concrete behavior |
| --- | --- |
| R01–05 | Close failed file/SQLite setup; stream artifact digests. |
| R06–10 | Respect fenced examples and physical Markdown lines; invalidate old section indexes. |
| R11–15 | Select tasks, bound summaries, page exact snapshots, count complete output, read details once. |
| R16–20 | Defer memory page projections, stream canonical hashes, avoid growing-packet reserialization and release omitted bodies. |
| R21–25 | Isolate UTC overflow, bound tiny-file allocation, stream literal search and retain bounded top-k. |
| R26–30 | Handle deep DAGs, share ancestry bitsets, verify unique references once per fresh snapshot, stream hashes and accept finite large integers. |
| R31–35 | Reject malformed paths/digests, preserve explicit unbound checks, guard diff scope and bound actual indexed bytes. |
| R36–40 | Bound immutable parsing cache keyed by fresh bytes, validate write flags, read one SQLite snapshot and reject oversized parser input early. |
| R41–45 | Navigate and retrieve SHA-bound literal Markdown blocks, page headings and include caller-declared global blocks. |
| R46–50 | Check complete-output token budgets, compact new immutable JSON receipts/registry records, observe storage metadata and adopt verified interfaces. |

`iterations.json` records actual per-ID before/after hashes. `history.zip` stores
114 historical protocol, source and reviewer files once with lossless ZIP
compression (564,743 bytes versus 1,154,247 uncompressed). Failures and repairs
remain distinguishable; no historical evidence or memory was deleted.

Packaging limitations are explicit: G01 archived all runtime modules rather than
only affected modules; G10's before ZIP omitted three script/workflow inputs,
independently reconstructed from immutable Git blobs plus verified newline rules.
Old gate references inside ZIP retain original runtime paths. They are historical
observations, not a portable trusted verifier adapter or a cache of acceptance.

The current test suite covers 54 regression tests including the auxiliary
measurement-harness output guard. Broader existing-suite
logs are retained separately, including Windows privilege/platform limitations,
test SQLite cleanup failures and isolated-process locale issues. The pre-existing
knowledge ingestion UTF-8 storage/output defects and Windows locked-file read
difference remain unaccepted; see `agent_doc/advice/REFLECT50-WINDOWS-UTF8-20261021.md`.
They are not all dismissed as environment-only failures. None is
silently recounted as a pass. R39's default-bound compatibility regression was
identified in that run and repaired under a fresh result protocol.

Reproduce into a **fresh** directory; never overwrite frozen data:

```bash
python -X utf8 scripts/measure_reflect50.py prepare --out agent_doc/results/reflect50-reproduction-NEW
python -X utf8 scripts/measure_reflect50.py run --out agent_doc/results/reflect50-reproduction-NEW --tokenizer-path /absolute/existing/isolated/dependencies
```

Optional measurement dependencies are tiktoken 0.12.0 / o200k_base; no model call
or package installation occurs. Frozen raw wires are stored once in payloads.zip.
An independently repeated temporary project path changes metadata bytes, so
reconstruction compares literals after normalizing only that declared root field;
counts and hashes for frozen original wires are always recomputed exactly.

Navigation is an explicit selection, not a lossless encoding of omitted source.
Read required source, global sections and memory dependencies before use. Tiny
documents can cost more through a navigation wrapper; direct full reading is
appropriate then. Physical JSON compaction preserves all values and changes byte
SHA/immutable filename; use new records and rebind evidence. No result here proves
whole-session token, monetary cost, latency, QA or blanket correctness benefits.

Frozen synthetic observations (o200k_base): large selected literal packet 44,072 → 205 tokens; tiny packet 55 → 158 tokens. Receipt whitespace compaction preserves complete JSON values: 17,884 → 15,774 stored bytes. These are scoped observations, not overall agent-cost savings.

`history-delta.zip` preserves the subsequent R39 compatibility repair and stale final-v1 evidence; final-v2 was also left unaccepted after the auxiliary output guard changed. Final-v3 supersedes both.

Implementation main commit: `b928a253da2586255bceedd0bb1a32fb71eb0f51`; GitHub/native tree readback and committed-source setup/check passed (16 skills, 531 files). `publication.json` records scope and preservation checks. The final bookkeeping commit changes no tested source.
