# Memory table transport accounting

Status: **deployment v2 usable-with-scope** on d9fdf9b3 plus the bound candidate. [Current contract](deployment-v2/contract.json), [manifest](deployment-v2/manifest.json), [independent review](independent/deployment-v2/review-v2.json) and [explicit host acceptance](deployment-v2/accepted.json) bind the actual evidence. The v1 live-source binding is historical after the concurrent update; v2 preserves it and the two old sources. The catalog `memory-pack-deployment-20261021-v2/record.json` indexes these versioned files as references without claiming their bytes were moved. Stored acceptance never authorizes future reuse without a fresh host gate.

Plan and research boundaries: [TOK-MEM-20261021](../../task/task_details/TOK-MEM-20261021.md). Manual validation DAGs describe producer → independent verifier → publication, not a deployed scheduler. The reviewer verified that only dispatch/default-write-scope and its test changed, then checked all current bindings and the exact bridge for unchanged v1 sources/config/tokenizer/corpus. Fresh v2 dispatch5/strict24 and independent12 tests passed; the v1 native52/250-property observations are explicitly reused, not relabeled as new runs.

Complete payload o200k token counts (deterministic cases):

| Case | Ordinary JSON | Claims table | Basis tables |
| --- | ---: | ---: | ---: |
| Empty | 33 | 67 | 97 |
| Singleton | 142 | 156 | 164 |
| Short, 32 entries | 3679 | 3135 | 2523 |
| Unique metadata, 32 | 3711 | 3167 | 2555 |
| Long prose, 8 | 7141 | 7029 | 6897 |
| Unicode, 8 | 1101 | 989 | 857 |

The short-32 packet saves 612 tokens (19.5%) against the prior claims table, or 1156 (31.4%) against ordinary JSON; UTF-8 bytes are 12765/10186/7262 respectively. The actual Mailbox two-format pair is 2013 → 1979 tokens, 6184 → 5996 bytes. Empty/singleton packets grow. These are per-case transport observations, with no aggregate or universal gain claim. The independent verifier recounted 40 v2/reproduced payloads with complete BPE token sequences and reproduced all six deterministic cases byte-for-byte.

The six deterministic fixtures compare ordinary JSON, `claims-table/v1` and `basis-tables/v1`. The actual Mailbox fixture compares ordinary JSON with `basis-tables/v1`, retaining full memory dependency closure. Measurement counts the complete compact sorted JSON payload, including table headers and version marker, with tiktoken 0.12.0/o200k_base. It excludes tool wrappers, request/history, provider input/output, reasoning and this development session. There are no model calls, total-token/cash/QA/latency or disk-space claims. Restoring an ordinary object before sending it to a model would require counting that expanded input instead.

Reproduction on Windows requires the optional pinned tokenizer (isolated here at `.agent-runs/memory-index96-deps`) and o200k tokenizer cache (`.agent-runs/memory-index96-token-cache`). Set `PYTHONPATH` and `TIKTOKEN_CACHE_DIR` to those directories, plus `PYTHONUTF8=1`/`PYTHONIOENCODING=utf-8`; then run `python -X utf8 agent_doc/results/memory-pack-20261021/measure.py --output YOUR_NEW_RUNTIME_DIRECTORY`. Preserve the frozen results rather than overwriting them. The deterministic cases must reproduce exactly; actual Mailbox timestamps may vary and each new pair must independently restore and recount exactly.

`targeted-tests.txt` contains the final native 52-test UTF-8 regression. `strict-boundaries-ext4.txt` contains the Linux-only 24-test regression from a temporary ext4 snapshot whose every extracted file is checked against `strict-source-snapshot.json`; that snapshot's synthetic Git revision is not a publication revision. `run_checks.py` documents the initial native + mounted-WSL commands; `run_strict_ext4.py` documents the targeted Linux retry. No unrelated full-suite pass is claimed.

Failure history is retained: `attempt-1-native-powershell.txt` is the unmodified UTF-16 PowerShell capture (GBK Unicode subprocess failure and missing native `fcntl`); `strict-boundaries-wsl.txt` has two three-second mounted-filesystem CLI timeouts. UTF-8 child policy and a verified ext4 snapshot resolved these checks without changing product code or relaxing test timeouts. Historical failed runs are not accepted measurements.

The repository has no local memory ledger to compact in this run. These are public synthetic transport fixtures; no private or inaccessible cloud memory was read, summarized or deleted. The new format is opt-in, leaves ordinary JSON/old table encoding compatible, and does not replace source/freshness/authority checks. Full content and old evidence remain recoverable.

Published implementation: [c513427c](https://github.com/Chosen-David/agent/commit/c513427c1600003ea47c025686cce6b2091ea1b2). Native Git and GitHub read back that SHA; tree matched the locally staged candidate. Post-publication scoped validation and `setup_codex.py`/`--check` passed. [Publication receipt](publication.json) records that verified snapshot; subsequent documentation closure does not change the measured code.
