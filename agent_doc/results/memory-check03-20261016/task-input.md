# MEM-CHECK-03 bounded manual plan

Project: Chosen-David/agent, main 9b6cc775a900f2c0d26d97f88de5622129eec014.
Current user scope: ongoing Agent memory/KV reliability and efficiency, implement
and publish only measured improvements; no TwoLevel edits in this task.
GUIDE is empty and human-only. Existing MEM-STORAGE-01 remains incomplete.

Hypothesis: MemoryLedger.check() validates and hydrates every requested root,
then redundantly hydrates those same roots again in the same read transaction.
Retain only requested root objects from validated traversal, in requested order.
Do NOT retain all dependency objects, cache across calls/transactions, bypass
document hashing, change SQLite/schema/API, alter acceptance or delete history.
No graph/semantic/vector service, external models, paid calls or GPU.

Actual prior ResultStore query: MemoryLedger SQLite scope status retrieval,
limit5/max_scan200: memory-scope02 first, memory-storage second, partial=true,
61 unreadable records. Historical measurements concern list(), not check();
reuse research and measurement protocol only, new check() claims require new data.
Knowledge search found PagedAttention/QLoRA/HNSW; none proves SQLite gains.
Use SQLite official transaction isolation and existing 12-paper memory/KV matrix.

Manual chain: independent fresh-context plan review -> minimal code/tests and
baseline differential -> paired CPU measurement -> independent code/data
validation -> full regressions/docs -> fetch/publish main and byte readback.
This is NOT a managed DAG or ReviewSession; tmux/host adapters unavailable.
Repository AGENTS.md explicitly requires independent plan/result contexts.

Acceptance fixed before timing: exact complete packets/order, same error classes
and messages on measured invalid inputs, corrections/document changes rechecked
on next call, no persistent cache. Two large multi-root fixtures >=20% median
wall reduction; all small/dependency-heavy controls <=15% regression. 21 paired
randomized repetitions, full check() including connection/validation/hydration,
warm local SQLite, no setup or equality checks timed. Raw failures retained.
At most two implementation candidates, one host CPU, <=30 minutes total.
No claims for model KV tensors, LLM QA, tokens, TTFT, cold disk or GPU.

Freeze detail: config.json in this private run freezes all fixture dimensions,
payload lengths, graph shapes, refs, seed, repeats, hash and thresholds. No
document-bound roots in performance fixtures; real document hashing/changes are
correctness-only tests, no speed claim there. Reduction = 1-median(after)/median(before).
Invalid matrix: malformed refs, missing/stale/candidate/superseded roots/ancestors,
bad scope/document JSON, missing dependency schema, dangling/cyclic dependencies,
root/dependency overlaps, tuple refs, ordering, legacy no-document table, failed
checks and next-call corrections. Compare complete result or exception class/name
and message to frozen baseline (normalize module-local MemoryError identity by name).

Ownership: root writes implementation/tests/benchmark/task/report only; reviewer
writes assigned private plan verdict and later independent evidence files only.
No human guide writes; no unrelated task changes. Stop no unknown processes.
