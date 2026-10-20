# Independent CLI diagnostic

Scope: investigate the existing CLI-input checks failing on WSL Python 3.14.4 after the index extension. This is a diagnostic, not final result acceptance.

## Observations

Executed `independent-diagnostic-run.py`, which ran the same 34 existing tests in fresh subprocesses with (a) current memory module and (b) the memory module compiled directly from Git commit `50c1ca1e74df1026ba05b4cfd53903605315b234`, while keeping the same surrounding checkout and test source. The baseline substitution does not execute the new index tests or write an old module into the working tree. Both subprocesses exited 1. Raw commands and statuses are in `independent-diagnostic-checks.json`; unmodified subprocess logs are `independent-diagnostic-current.log` and `independent-diagnostic-baseline.log`.

The diagnostic result class exposes captured stderr at failing JSON assertions. Both old and current implementations emit the expected JSON error, preceded by Python 3.14 `ResourceWarning: unclosed database in <sqlite3.Connection ...>` warnings. Their exact triggering test/subcase depends on garbage collection/allocation timing. This is independently demonstrated baseline warning contamination, so these observed errors do not establish a regression in index/storage behavior.

Static source ownership check: `tests/test_memory_cli_input.py:25` opens a connection with `with sqlite3.connect(...) as db`; that context manager handles commit/rollback and does not close the connection. `rows()` is called repeatedly before/after stderr captures, leaving connection lifetime to GC. The final schema check uses the same ownership pattern. The production `_connect` closes its owned connection in `finally`; the new index code does not execute in the old CLI-input tests. New argparse allocations can move the warning's emission point without being the underlying leaked resource.

Recommended bounded fix: explicitly close the existing test-owned connections with `contextlib.closing`, preserving transaction semantics when needed. Do not suppress ResourceWarning or weaken the structured stderr assertion. Preserve both original failures and re-run affected checks. This reviewer changed no implementation or tests.

Limitations: the baseline comparison substitutes only the relevant memory module into the current surrounding checkout. It is not a complete historical checkout regression run. Diagnostic tests and traceback output are observations pending the final independent verification; no universal correctness conclusion follows.

## Optional tokenizer protocol

A separately versioned, pre-frozen local tokenizer protocol using `tiktoken==0.12.0` and `o200k_base` is reasonable within the existing local CPU/no paid inference boundary. Preserve byte-only v1 raw evidence and declare exact fixture strings, serialization/newlines, tokenization options, encoding data/version/hash, every complete index page, and every necessary body/dependency read. Count all compared payload tokens. Do not generalize to model API billing, total session tokens, task quality or a serving-model tokenizer that was not actually verified. If the frozen six workloads do not save tokens, retain and report that valid negative result. This is approval of a bounded measurement plan, not pre-acceptance of future data.
