# Independent continuation plan review — PROMPT-SCOPE-01 v2

Decision: **approve the test-oracle correction as proposed**, before edits or execution. Reviewer `/root/prompt_scope_review_2225`, 2026-10-26; project `/workspace/scratch/6416f20dc59b/agent-run-1303`. Only this file was written. No test/fixture execution, production/test/TASK/guide modification, old-source run or CI retry was performed.

Both actual Windows excerpts show the same two raw-output failures, at the original source-in-decoded-stdout assertion; source LF is compared with Windows CRLF. JSON and all other prompt checks pass in those excerpts. Full decoded private log hashes and excerpt hashes match native-failure.json; each excerpt is an exact byte substring of its corresponding full log. Logs establish failure of run40342330469, not successful cross-platform acceptance. I inspected saved service-output evidence, not a fresh network job retrieval; Ubuntu success remains the producer's separately reported matrix observation.

The established CLI uses UTF-8 standard text print; configure_utf8_output changes encoding, not newline mode. With default newline handling, Windows translates every written LF to CRLF. An existing CR in a CRLF source is preserved, so raw CRLF source produces CRCRLF in that portion on Windows. That is the existing native print contract. JSON serialization escapes embedded CR/LF, so its parsed prompt must preserve the original LF/CRLF characters exactly; only the printed envelope's final newline undergoes native translation. This correction therefore belongs in the fixture, with production unchanged.

The proposed complete raw byte oracle is sound: known three fixture documents and wrappers, explicit general-policy reference substitution, two-LF joins, then print's one final LF, followed by native LF translation and UTF-8 encoding. It does not call compose_entries/_span/physical_lines or derive its expected body from received stdout. The exact whole-prompt JSON expectation also strengthens the old source-substring assertion. Both source endings × LS/PS × raw/JSON yield eight bounded CLI invocations; all existing scope, UTF-8 decoding, exit/stderr, retained disposition and source-byte invariants remain. The extra raw substring check is redundant but consistent. It neither deletes CR nor normalizes arbitrary output, so malformed newlines, lost separators, missing wrappers/constraints and unintended dedup remain detectable. Using ENTRIES for trusted paths/order is acceptable for this narrowly fixed oracle; this is not an independent test of the ENTRIES constants.

Current production modules, CI and original6772719 fixture equal git84fe6046 byte-for-byte. Prospective full fixture has only the reviewed method replacement, SHA53e0e26fe1cd9fd21a99ef1b50e66ae07688227792c84e30c9ac633bfac47fcc. Existing evidence stays immutable. Main must record the Version41 continuation, apply precisely these fixture bytes, execute the same three local modules once with distinct evidence names, and obtain independent result verification. Then an ordinary follow-up commit must receive all four successful native jobs including the prompt step. This approval does not turn failed CI green or prove Windows behavior from Linux. No CI removal/skip/rerun, old-source baseline/fullsuite/exhausted-gate retry or budget reset is approved. No new reading count, model-quality/performance or complete provider-cost claim follows; inference usage remains unknown, not zero.

The final continuation runner was additionally read: it uses the same three modules and120s subprocess bound, saves only new fixed-v2 evidence, and explicitly refuses either existing log or JSON before execution (including under -O). An initial JSON-only assert guard was corrected before this approval. Original runner/results remain untouched. Native raw translation is not byte-identical source materialization or proof of downstream host semantic fidelity; parsed JSON prompt equality remains exact.

## Frozen SHA-256 bindings

- `agent_doc/results/prompt-scope-native-20261026/native-failure.json`: `7138079d285e389980fe52fafede5025a64b2ceec47633c68767c11b234513d1`
- `agent_doc/results/prompt-scope-native-20261026/plan-v2.md`: `93c23583e710a2994d48604f0905ab2eede2141a72e04c4c66e68466729b435d`
- `agent_doc/results/prompt-scope-native-20261026/proposed-cli-method-v2.txt`: `b9d7f122b5b5b0e681434bc01443107901b4816835b3b736e9b4e6aa41e95d91`
- `agent_doc/results/prompt-scope-native-20261026/run_checks_v2.py`: `1606da84eae5a7fbba651da0ff8c5602ea17750d2b3a8f83893eab304a6166bd`
- `agent_doc/results/prompt-scope-native-20261026/windows310-failed-step.log`: `33b6b8910bf00a614f1179d9debb22c6f421dcc60f6a3723e0fd28b359a3dad5`
- `agent_doc/results/prompt-scope-native-20261026/windows312-failed-step.log`: `8e491f24b80b6eaff32fd9c69cdf5d64f91fee5ffef22c713fc5a640c2c1d188`
- `.agent-runs/history-quality-2225/native-ci/proposed_test_prompt_context_v2.py`: `53e0e26fe1cd9fd21a99ef1b50e66ae07688227792c84e30c9ac633bfac47fcc`
- `.agent-runs/history-quality-2225/native-ci/windows310.log`: `cd3198bb0294025dd0ee4c6ede1b7e6dc7aadbaf22b06badfa88782eea9ca958`
- `.agent-runs/history-quality-2225/native-ci/windows312.log`: `d9817558da3c43b4ee0466cf5212ad41b308e5ff1cd8501c970e3431d0a0c018`
- `tests/test_prompt_context.py`: `67727190d01e959d539397a319a883a92f078b17d3717e233ff0e0f1d2cef663`
- `agent_runtime/prompt_context.py`: `65772323070de699fd6719786fb4d21ab94c13c282658d6bb39f98557c0cdad3`
- `scripts/prompt_context.py`: `722d3728983997ae4fd0762669bab142f66b1fa82cbfefed18607f9e179fe5ed`
- `agent_runtime/project_docs.py`: `456bbe40a5ca731e7ab311a4435838252627c9447d66e88b51ee082cd361e92c`
- `agent_runtime/context_serialization.py`: `2606666cf723af13cb2b8a4a0934848f233ffb16c50728fc4a43da01ff26453d`
- `.github/workflows/portable-install.yml`: `e7a9e11bbac7e5a89f1a56a36d83690db86e30dba7c80857d74fcd61f3797778`
- `AGENTS.md`: `97f35fc8fb91097a34380c12a9581936f8a78c6f9c10a05183c84511645738ed`
- `agent_doc/task/TASK.md`: `cac11b59a920f4dc1dd398568ba6b2d0d0593ae5ac25d59858c53a2b739c706f`
- `agent_doc/task/task_details/SYSTEM-99.md`: `7521d4ce548acc26486e2b742a04ea541f51a1a9e08d3b59941ec5c059ec6d0c`
- `agent_doc/guide/GUIDE.md`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `agent_doc/guide/README.md`: `f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261`
- `agent_doc/results/prompt-scope-native-20261026/run_checks_v2.py`: `910addea895d99718d6a94da69f5059bcb5162cb86d329fd756350dbc0a03acb`
