# Actual role evaluation evidence

Latest applicable candidate: `263958510f78789e33dd29676d510a672900ce26`.

The automatically generated matrix selects passing evidence for **15/15 roles**:13 without explicit repair feedback and2 feedback-assisted recoveries. Five targeted main/knowledge-handoff checks also pass. Prior execution reuse is identified by original candidate and exact dependency hashes; this does not claim every role reran on v5. Root independently verified the selected artifacts and dependency equality.

| Historical run | Raw case passes / preregistered denominator | Actual cases | Criteria |
|---|---:|---:|---|
| v2 |16/19|19|57pass,1fail,2ungradable|
| v3 |8/12|10|29pass,2fail;2superseded cases unexecuted|
| v4 |6/7 raw;5/7 after budget adjudication|7|21rawpass,2ungradable; budget grading correction separate|
| v5 |3/3|3|11pass|
| Code-organization feedback repair |1/1|1|4pass|
| Assistant feedback repair |1/1|1|3pass|

V2 material defect (unsupported CNY), missing reading-page evidence, repeated code-organization rollback failure, v4 consumer original-process evidence gaps, and inconsistent assistant-budget grading remain preserved. The original unprotected v1 attempt is excluded. These repeated/grouped cases are not independent statistical trials; no model/token/cost or generalized improvement claim is made.

The actual review→repair mailbox used5events/9deliveries. Seven receipts are recorded; **two repair-recipient final ACKs remain pending after deadline enforcement**. Document semantics passed, but full receipt-protocol completion is not claimed. See communication-summary.json/md for schema failure, real correction, timing negatives and separate program probes.

Original evidence archive: w4-v2-evidence.tar.gz with archive.json. Incremental v3/v4/v5/repair evidence: w4-incremental-evidence.tar.gz with incremental-archive.json. Extract both into the same fresh directory, run `python -B w4-role-controller/replay.py` and `python -B w4-role-controller/replay_incremental.py` for record/hash/material-review replay. This is not a new model execution. Scripts/artifacts retain original observed paths; archived files are not rewritten to imply portability of worker workloads.

final-matrix.json/.md contains exact role provenance and historical denominators. communication-summary.json/.md separates content acceptance, transport validation, ACK state and budget compliance.
