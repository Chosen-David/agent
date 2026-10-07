# SagaLLM reading 4/10

Edward Y. Chang, Longling Geng. PVLDB18(12):4874–4886,2025.
DOI10.14778/3750601.3750611. Published PDF:
https://www.vldb.org/pvldb/vol18/p4874-chang.pdf
Read all main §§1–6, Algorithm1, Tables1–10; actually viewed PDF pages4877,
4882,4884 (architecture and disruptive schedules). Bibliography not systematically
verified; companion ALAS not read/countable here. No runtime installed.

Problem/mechanism: persistent application/operation/dependency state, external
validation, and reverse compensations (§§3–4). Algorithm1 generates workflow,
logging and compensation code, then refines until validated. Experiments (§5.1)
use four selected REALM planning problems, four models, March12–17,2025.
Tables6–9 illustrate temporal errors/replanning; Table10 is qualitative capability
comparison. No repeated aggregate success, component ablation or measured total
cost establishes general superiority in this experience paper. §6 defers formal
verification of generated compensation and broader experiments to future/companion
work. Its isolation/global guarantees need implementation verification; Gödel
references do not prove arbitrary LLM self-correction impossible (own inference).

Own candidate: preserve executed history and invalidate only dependent future
work in communication workflow/project memory; low adaptation cost, minimum
experiment is an interrupted repair with unrelated result retained, independently
rechecked against original finding. Pending real-model validation. Existing
Mailbox immutable receipts/project-memory dependencies already implement parts.
Reject full coordinator/runtime import: overlapping state ownership, unmeasured
maintenance benefit. Compensations are domain actions, not SQLite rollback or
proof of external exactly-once; generated cancellations cannot expand authorization.
