# COMM-ORDER-01 accepted scoped results — 2026-10-09

Inbox now orders on delivery.seq rather than equal joined event.seq. Existing pending index yields ordered rows and avoids a temporary sort before LIMIT. This established SQLite mechanism is applied without schema/storage/API changes; scientific novelty is not claimed. See research.md for fresh paper screening and choices.

Baseline ffe7f9d and candidate share exact fixtures. Twelve cases, 3 warmups and21 alternating pairs each; full public inbox connection and JSON decode included. Raw observations/outliers preserved. Producer summary retains its pre-review pending label as frozen data; actual acceptance is validation.json plus authenticated independent controller registration in record.json.

| Pending events | Layout | Baseline ms | Candidate ms | Speedup | VM reduction |
|---:|---|---:|---:|---:|---:|
| 100 | single | 0.392 | 0.360 | 1.09x | 3.98x |
| 100 | interleaved | 0.414 | 0.380 | 1.09x | 1.37x |
| 100 | last | 0.476 | 0.429 | 1.11x | 1.03x |
| 100 | absent | 0.318 | 0.338 | 0.94x | 1.00x |
| 1000 | single | 0.589 | 0.373 | 1.58x | 33.73x |
| 1000 | interleaved | 0.504 | 0.370 | 1.36x | 10.85x |
| 1000 | last | 0.525 | 0.522 | 1.01x | 1.00x |
| 1000 | absent | 0.483 | 0.480 | 1.01x | 1.00x |
| 20000 | single | 5.771 | 0.781 | 7.39x | 661.83x |
| 20000 | interleaved | 5.092 | 0.652 | 7.81x | 211.04x |
| 20000 | last | 3.559 | 3.304 | 1.08x | 1.00x |
| 20000 | absent | 3.819 | 3.652 | 1.05x | 1.00x |

Independent five-repeat replay confirms 8.56x/8.15x latency improvement on20k single/interleaved cases and exact deterministic VM reductions. Independent reviewer checked all retained aggregates/hashes, 1208 public properties and16 communication tests. Target-last/absent rows still require scanning; no universal O(limit), worst-case or concurrent traffic guarantee. Tested publish/ACK overhead passes frozen guard; no new maintenance cost mechanism.

Root regression: 881 tests,873 passed/8 skipped; reader3 passed. Unchanged schema and exact usage ledger/restart/order/ACK/run-isolation behavior verified. Scope: local synthetic SQLite sharedCPU/warmcache fixtures, abbreviated seeded event bodies. No model quality, token, network or end-to-end performance evidence. Research sources/limitations, environment, raw JSON, independent scripts and validation are retained beside this report.

Publication gate: integrate newly arrived main commits without overwriting others, rerun final-tree tests and non-force expected-head update/readback.

Final integration: preserved main cd90e35 (TOK-002). All reviewed artifact hashes unchanged. Final-tree full regression885 tests,877 passed/8 skipped,109.270s; reader3 passed. See final_tree_tests.log and final_tree_reader.log.
