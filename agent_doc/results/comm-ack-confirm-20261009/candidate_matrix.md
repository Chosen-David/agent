# Implementation landscape and pattern mapping

Checked 2026-10-09. Same locked research-implement-optimize skill and repository frozen v2 harness; no install/update.

| Route | Semantics/resources | Decision |
| --- | --- | --- |
| Current indexed SQLite public ACK | Validates envelope; BEGIN IMMEDIATE; run/recipient lookup; immutable conflict rejection; UPDATE even identical | Strongest currently adopted compatible baseline |
| Exact receipt equality branch | Same lock/trust checks and first ACK; omit redundant UPDATE only for canonical identical bytes | One prospective31+31 pair confirmation; no historical gain reused |
| UPDATE WHERE receipt IS NULL (r11) | Alternative statement still executed; must retain conflict check | Prior negative preserved; not re-experimented without new information |
| Batch ACK | Could amortize connections/transactions | New API/atomicity/failure semantics needs distinct frozen plan; not in this candidate |
| Shared persistent connection | Cross-thread and lifetime concerns; old r20 safety falsification | Reject absent redesigned ownership; no validation shortcuts |
| Coda admission/KV routing | Requires inference workers/residency/context traces | Deferred: runtime has no such serving layer or compatible benchmark |
| MASBench outcome/cost evaluation | Requires model endpoint and task-quality denominator/token units | Future quality benchmark design; no paid/model-quality runs performed |

Receipt duplicate is an exact memoized-state/idempotence pattern, not lossy communication pruning. Define n deliveries and L receipt bytes: existing composite lookup remains indexed, canonicalization/equality costs O(L), one redundant indexed UPDATE removed. SQLite work/count reductions are measured, not proof of lower wall latency: connection setup, BEGIN IMMEDIATE writer locking and commit remain. No asymptotic claim or global-fastest claim. Auxiliary Python space remains O(L). No SIMD/PTX/GPU primitive is indicated for a connection/I/O path; no GPU benefit claimed. Frozen old variant10 provides comparison with existing mature sqlite3 implementation, not an invented parallel serving engine.
