# MEM-INDEX-96 independent plan review

- Reviewer: `/root/memory_index_verifier`, independent native agent context; producer/planner: `/root`.
- Project root: `C:/Users/WI/Desktop/home_work/AI_LLM/agent`.
- Reviewed: Plan v1 in `agent_doc/task/task_details/MEM-INDEX-96.md`; whole-file SHA256 at review `85ebff856ba4a772fdc85e74a375a0fe652d6baaf3de26a1f56f0633b93ade42` (includes then-current Progress).
- Baseline HEAD: `50c1ca1e74df1026ba05b4cfd53903605315b234`.
- Decision: **approve** for the bounded manual-host CLI extension and subsequent independent verification. This is a plan review, not data acceptance or a runtime ReviewSession receipt.

## Review findings

1. Intent and guide: the proposed content-free navigation and read-only storage accounting address the stated memory/file/cache investigation without changing trust or persistence architecture. `agent_doc/guide/GUIDE.md` exists and is zero bytes; no additional guide requirements can be inferred. No guide writes are permitted.
2. Assumptions and implementation boundary: inspected the existing ledger implementation, including `_connect`, `_get`/`_read_entry`, `list`, `check`/`_walk`, `history`, and CLI dispatch. Explicit opt-in index/storage commands can preserve default behavior. Current full entries remain authoritative, and active status does not itself certify scientific truth. Index results must carry no stronger validity claim.
3. Historical evidence: actually read `prior-search.json` and the `memory-storage-20261015/report.md` source. The former is lexical and partial, with missing historical records; the latter concerns hydration latency in a different environment and lacks this index/storage feature. Reuse its method and correction constraints only; reject transferring latency numbers or claiming that this search exhausted all history. The saved search reports **250**, whereas Plan v1 says 249; this minor factual discrepancy should be reconciled in a versioned factual correction or explicit Progress note before final reporting. It does not change implementation scope or acceptance.
4. Knowledge: read the producer's actual `knowledge-read.json`. Its A100/OPT/LLaMA KV-cache workload does not establish any SQLite pagination guarantee. No literature-derived numeric or algorithmic guarantee is needed for this plan; correctness will come from implementation inspection and independently derived properties. The saved knowledge display contains replacement characters in Chinese fields; do not present that display as an intact quoted source.
5. Acceptance: no loss, duplication or reordering; deterministic ties; exact scope; complete metadata/source/dependency preservation; no content in index; correction/acceptance/status and snapshot rejection; complete-item hard output limit; legacy schema and invalid argument handling; read-only storage; exact body recovery and UTF-8 output-byte reduction are concrete and testable. Token counts, model quality, latency, cash savings and deployment remain outside acceptance.
6. Risks: snapshot identity must cover full selected entry contents and metadata, filter, and project identity within a consistent read transaction. Page packing must count the complete serialized envelope, including cursor/snapshot fields and Unicode. Empty pages and oversized first entries need explicit behavior. Storage must neither initialize/migrate a ledger nor VACUUM/delete data; inspect DB/WAL/SHM effects where applicable. Malformed metadata and old schemas must fail explicitly or retain documented compatibility.
7. Resources and ownership: local CPU/temporary synthetic ledgers and at most two bounded repair rounds fit the plan. No paid inference, GPU, background job, schedule or service is needed. Root owns implementation/TASK; reviewer owns only this run's `independent*` files. Preserve the preexisting dirty `.gitattributes`, progress and json_context work and all failures.

## Prerequisites before data production/consumption

- Freeze the six-criterion `experiment-validation-plan/v1`, execution/input configuration and result contract before running the producer's measurement. Specify exact serialization and byte metric; no timing acceptance is implied.
- Keep producer data pending until this reviewer receives completed implementation and frozen manifest/raw artifacts, then independently inspects real code, exercises independent properties/boundaries, reruns the measurement and checks hashes.
- Code, inputs, config or relevant environment changes after freezing require explicit revalidation; preserve old failed/raw evidence and use a new result identity for a repair round.
- This review ran no test or experiment and changed no implementation. It is an independent manual host workflow, not an installed or authenticated runtime orchestration backend.

## Sources read

`AGENTS.md`, `prompts/decision_review.md`, the task detail and canonical TASK entry; installed code-reading skill and its workflow/execution/project-document/result-reuse/knowledge-access references; `workflows/result_validation_workflow.md`; `workflows/project_memory_workflow.md`; existing `agent_runtime/project_memory.py`; this run's prior-search and knowledge-read; historical memory-storage report.

Source workflow SHA256 at review: memory workflow `c6b15db78c97d8ee412e6f0613a2376f0cd02a4aabdd9721289f33196dc98d3d`; result-validation workflow `b1f2f14d1554697ce9b44ea476d1182210f4d8c8c31def3e0c74b1e701d72a4b`. These hashes identify inputs and do not prove their semantic correctness or provenance.
