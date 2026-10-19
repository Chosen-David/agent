# CONTENT-COPY-60 independent candidate result review

Decision: **usable-with-scope** for the one-pass local CPU candidate feasibility measurement. Reviewer `/root/copy60_review` independently read the executed probe and all raw samples, recomputed aggregates/gates and reran 70 correctness comparisons. This is not production acceptance or managed engine authentication.

## Evidence bindings

- `agent_runtime/knowledge.py`: `9ee261d0e5ab8c803bc12a524308d783bdf18a259ce4c2ed06b0ca53f2c56770`
- `agent_doc/results/content-copy60/probe.py`: `878ecd5cc078f51857d2c1689fcbe11e25ce744495a8740287beb66070a09900`
- `agent_doc/results/content-copy60/raw.json`: `b05c94c4adeae2518f171c227dcb5708262a1995dc84104f5ec48c1f0a4bff68`
- `agent_doc/results/content-copy60/plan.md`: `a194027598d5ce02fb247e1f0e1e6c3c8b8daf404d444d6a927254cb361e541c`

## Checks

- Implementation: pass. Baseline and candidate are separate native classes compiled from the same current source; exactly one clone expression is replaced. Native `_metadata` class identity is preserved. Eligibility checks exact dict, exact ASCII string keys and exact surrogate-free string body. All other records use the original clone. Metadata stays JSON-normalized, nested objects remain isolated, and original key order is rebuilt. Closure, validation, status and custom-get paths remain unchanged.
- Reference boundary: pass within tested scope. Producer's 135 checks comprise 115 current corpus records, 15 body/order combinations, three error/key cases and two hook checks. Reviewer independently compared all 16 context cases using unsorted JSON (including order), plus 54 body/metadata combinations covering control characters, Unicode, lone/pair surrogates, string subclass, non-string body, numeric/string key collisions, tuple normalization, surrogate metadata keys, infinity, unsupported sets and nested mutable values. Outputs or exception type/message matched.
- Data integrity: pass. Current source and plan hashes equal raw bindings; raw candidate equals exact probe replacement; live baseline/candidate snapshot equals saved snapshot. All 16 input/output hashes were independently reproduced. Each case has exactly 11 positive samples per implementation. Source paths and hashes above bind actual candidate construction and results.
- Numerical sanity: pass. All ratios were independently recomputed as median(candidate)/median(baseline); all finite/positive. Primary matrix/5/related ratio is 0.8322693027 (16.7731% reduction). Ratios across 16 cases range 0.646965–0.975518. Peak ratios range 0.509873–0.817514; every case meets its 10% increase cap.
- Measurement validity: pass for bounded local observation. Timing contains 10 complete context calls per sample, two explicit warmups and alternating order. Search is outside timing, peak tracing separate. Primary baseline median 2.4684909 ms/call, candidate median 2.0544492 ms/call; primary sample ranges 2.3434–2.8579 ms and 1.8592–2.3091 ms respectively. Primary traced peak 97034→49475 bytes. These are Python traced allocations, not RSS or model memory. CPU independently observed as AMD EPYC 9V74 80-Core Processor; Python/platform are in raw. No hypothesis tuning rerun was performed.
- Reproducibility: pass within scope via independent source reconstruction, 16 input/output-hash reproductions and 54 additional boundary comparisons. Independent timing replication was not performed under the frozen single-pass budget; no cross-host or durable speed guarantee is claimed.

The reported initial import-path failure occurred before any measurement according to planner and is not a second timing pass; final code has an explicit project-root import path. The raw file does not independently capture that failed invocation. No measured data has been discarded or rewritten by this reviewer.

Limitations: one local timing pass; no controlled CPU affinity/load record; one traced peak per case; no full-regression or deployed-production result yet. Arbitrary monkeypatched JSON functions or adversarial side effects in user-defined nested objects are not exhaustively verified. Approval supports only this frozen candidate/corpus/environment and proceeding to integration checks.

## Integration plan review

Decision: **approve** integration v1, SHA-256 `efd5f72f878c295f43140f374d3f053bbad274525f6265ec243549cc93580f25`.

The plan applies exactly the measured replacement to canonical source and identical standalone mirror, retains line endings, adds semantic regression tests and requires full repository/reader tests plus independent production-diff/log review before ordinary main publication. Source equivalence must be verified byte-for-byte after normalizing only the intended CRLF-preserving replacement. Fresh upstream reconciliation and remote readback remain main-owned. Seven planning dimensions pass within this narrow phase: authorized intent, guide protection, measured assumptions, scoped prior/candidate evidence, explicit acceptance, reversible isolated change risk and CPU-only resources. This does not itself approve publishing an unverified integration.
