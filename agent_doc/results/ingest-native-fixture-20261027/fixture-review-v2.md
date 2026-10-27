# Native fixture capture follow-up review

Verdict: **approve for the exact maintenance delta and updated report wording**; revised native execution remains pending. No blocking finding. This source-only follow-up does not consume or reopen the publication-repair plan reviews, original local execution phases, or any diagnostic/backend budget.

I inspected the actual updated read-boundary/index diffs, complete updated changes.json/report/static-delta.json, and knowledge.main's stream configuration/output paths. Relative to the preceding fixture review, the only two additional source edits are `encoding='utf-8'` on the existing subprocess.run captures in `test_isolated_plugin_ingest_and_byte_identity` and `test_isolated_index_and_tree_cli`. Both retain text=True, capture_output=True, argv, cwd, timeout behavior and every assertion. Neither introduces errors='ignore'/'replace', exception suppression, a skip or a weaker expected value.

Knowledge.main explicitly reconfigures both stdout and stderr to UTF-8, prints rendered JSON, and emits non-ASCII error JSON. The fixtures invoke that CLI and parse its output as text/JSON. Strict UTF-8 decoding therefore aligns the parent capture with the existing child stream contract and still rejects malformed bytes. The two later Windows steps did not execute in workflow40480391048, so this is a source-supported portability precaution, not an observed second Windows CLI failure. The updated report makes this distinction explicitly.

Actual candidate hashes match updated changes.json:

| File | Current SHA-256 |
| --- | --- |
| tests/test_knowledge_ingest_scope.py (unchanged since first fixture review) | `bf8bb7f24c75ec617dcd8ef63e46558fe5f3a0ed622f2ab3497914d9e6b72a04` |
| tests/test_knowledge_read_boundary.py | `d6cbb60579dccc89fc6f326f41dbcd95df0164cd4b34e166d4d7d28e3f2272ce` |
| tests/test_knowledge_index.py | `4a4f5f8caf4eabe4fd1c376e82c06e946f3de3095e6a277266542f7c40258f61` |
| tests/test_knowledge_ingest_publication.py (unchanged since first fixture review) | `2cffc72c3deaa4dc7128189b5119e154933dbfebfb09aaacddfd891e6578cc4c` |

Production remains `5349e9c44f3be03d1a7dbc291562dfe98a71f1c532d302c49a8ffd5aa381e039`. Updated report SHA is `fadc6dde1679d931a998232999d9fa9c3446881703beafe132a22f54113c15a5`; changes.json is `414dbfd20d547ec0530f7919a15c8d3464a8cc3ed87038870fda525d05a4f0f1`; static-delta.json is `b0450228afefc35fb4bb1d64a2c7032cd10801752c2b112b7a38b890d2b73272`. The first fixture-review.md remains unchanged at `cd2c637411d47b101dea7469fac73cef26eac71494ed70511a018476b5442e5a`.

The updated AST projection statement covers corpus text I/O and subprocess capture encoding as one UTF-8 transformation category, plus fixture-path normalization as the other. My source inspection finds no additional behavioral or assertion delta. This is static evidence only, not a test execution result.

All earlier raw failures and limitations continue unchanged: the original integrated Windows alias/path mismatch cause is inferred without a captured old path pair; the corrected hook must reach its unchanged two-call assertion in the new native workflow. Original YAML zero-job and Windows failures remain failures, old local results stay tied to old fixture bytes, and SYSTEM-99 remains unfinished. Same four-file maintenance candidate and one corrective ordinary push/native check remain pending; no extra local replay, test, benchmark, CLI/model probe, rerun API or budget reset occurred in this review. This file is the sole new output.
