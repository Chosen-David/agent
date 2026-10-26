# Independent result review — PROMPT-SCOPE-01

Verdict: **usable-with-scope** for the reviewed local prompt scope/UTF-8 reliability repair. Reviewer `/root/prompt_scope_review_2225`, 2026-10-26. Independent execution: one fresh subprocess invocation of test_prompt_context.py, test_context_serialization.py and test_markdown_protocol_regressions.py; **35 methods passed, zero failures/errors/skips**, exit0, no timeout. Outer bound120s; nested prompt CLI bound15s. Full raw output is independent.log; invocation, environment, baseline comparisons and complete 381-file before/after bindings are independent.json. Every bound file remained unchanged during this run. Elapsed time is recorded only by unittest and is not a performance comparison.

## Code, baseline and reference checks

Actual production diff exactly matches the accepted imports/physical_lines loop and configure_utf8_output call; no marker, block endpoint, equality, selection, cache, source-read or prompt-budget logic changed. The CI diff adds only the existing prompt module to the four native matrix jobs. SYSTEM-99 now has Version40/phaseX and scoped progress; the unique TASK index and both guide files retain their approved bytes. No prompt source changes were observed.

Compared git055da9ed92e85e7a0997a0153ce54bdb44c51b67 bytes directly with baseline.json: both original production modules and shared project_docs hashes match exactly. Baseline before/after inputs are stable. The raw baseline records 23 methods, 52 failed subcases and 8 error subcases:32 additional-marker fake-opener failures,8 decision fake-opener failures,8 false canonical acceptances,4 actual CLI encoding failures, and8 fake-closer canonical rejections. These are repeated boundary cases, not60 independent defects. The CLI traceback specifically shows gbk rejecting U+2028; fake-closer errors originate at the canonical-scope rejection. Producer fixed.json binds the same frozen test source and current production bytes and matches its35-pass log. I did not rerun old source or retry any exhausted gate.

The final plan, reading, inputs, runner, test source, AGENTS and guide hashes match the pre-execution plan-review bindings. Literal source oracles remain independent of the repaired helper. My separate run verifies preservation of unknown source strings, fail-closed canonical ambiguity, genuine global scope after fake closers, all four shared markers, real cp936 raw/JSON UTF-8 output and unmodified temporary prompt sources. Existing exact/different policy, single-context dedup, real-entry, quote/comment/fence, selection/cap and symlink regressions pass. The complete composed-prompt character budget remains distinct from the JSON envelope/newline; the implementation did not import a new wire-budget contract.

## Acceptance limits and ownership

Accepted evidence supports this narrow reliability correction and these finite local cases. It does not prove universal CommonMark parsing, all platforms, actual model instruction following, task quality, cost or performance. Native Windows/Linux matrix execution and publication readback remain future work. Independent run environment is the recorded Python3.12.14 host; it is not native Windows coverage. Fullsuite/PID/lost-candidate/real-host and all other SYSTEM-99 gaps remain open; no old gate was retried or reset. Provider inference usage/cost remains unknown, not zero. Prior reading audit remains at its recorded actual scope; no duplicate paper summary or new independent reading count is claimed.

Only independent.log, independent.json and this review were written by the reviewer in this result phase. Production/tests/TASK/guide/producer evidence and the foreign staged archive were not mutated. This is scoped result acceptance, not whole-round completion, deployment or a universal bug-free certification.

## Selected frozen SHA-256 bindings

- `AGENTS.md`: `97f35fc8fb91097a34380c12a9581936f8a78c6f9c10a05183c84511645738ed`
- `agent_runtime/prompt_context.py`: `65772323070de699fd6719786fb4d21ab94c13c282658d6bb39f98557c0cdad3`
- `scripts/prompt_context.py`: `722d3728983997ae4fd0762669bab142f66b1fa82cbfefed18607f9e179fe5ed`
- `agent_runtime/project_docs.py`: `456bbe40a5ca731e7ab311a4435838252627c9447d66e88b51ee082cd361e92c`
- `agent_runtime/context_serialization.py`: `2606666cf723af13cb2b8a4a0934848f233ffb16c50728fc4a43da01ff26453d`
- `tests/test_prompt_context.py`: `67727190d01e959d539397a319a883a92f078b17d3717e233ff0e0f1d2cef663`
- `.github/workflows/portable-install.yml`: `e7a9e11bbac7e5a89f1a56a36d83690db86e30dba7c80857d74fcd61f3797778`
- `agent_doc/task/TASK.md`: `cac11b59a920f4dc1dd398568ba6b2d0d0593ae5ac25d59858c53a2b739c706f`
- `agent_doc/task/task_details/SYSTEM-99.md`: `7521d4ce548acc26486e2b742a04ea541f51a1a9e08d3b59941ec5c059ec6d0c`
- `agent_doc/guide/GUIDE.md`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `agent_doc/guide/README.md`: `f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261`
- `agent_doc/results/prompt-scope-20261026/plan.md`: `8d89347af21095968e14743f61f9fe03c26b81511d190d76b23c9e6d2baec130`
- `agent_doc/results/prompt-scope-20261026/reading.md`: `f52d66a8534f783be923c2300767c451b4fe0c2d8be2643e908b1a2878358931`
- `agent_doc/results/prompt-scope-20261026/inputs.json`: `430ad9a3ba1ce4a28c05225356437f4f2ba457190aca612fce1b647c4bab9b76`
- `agent_doc/results/prompt-scope-20261026/run_checks.py`: `9750d07e2f4a3e575b26ace1a96c18dd028922fce2c35edf1d52d0903190c12f`
- `agent_doc/results/prompt-scope-20261026/plan-review.md`: `2a198eeca17e88a3104a7f564e9439d351f1d65a5b684e9643d707e84593b98e`
- `agent_doc/results/prompt-scope-20261026/report.md`: `69c2cd8e8e85a02ae1a8070783fa4bf140060890c4248a1af7a5dd68c80a4ad0`
- `agent_doc/results/prompt-scope-20261026/baseline.json`: `7fca85bc1435338102e916e474435b7680e69362ef551992a2ff99cb6436e710`
- `agent_doc/results/prompt-scope-20261026/baseline.log`: `25db1df5189282b59ab5f008749bb6ba44aef0e3f48cd04a4252491d652635c1`
- `agent_doc/results/prompt-scope-20261026/fixed.json`: `ce26b6373e8efba4a8b4c165a78f023076b50024c06a6f91d10e1906859e2ea4`
- `agent_doc/results/prompt-scope-20261026/fixed.log`: `021c883572bbc13e7c362070c79601f8f870e09a174c108642a5e52fe7c9bcd2`
- `agent_doc/results/prompt-scope-20261026/independent.json`: `2ca4b497f4f348ddc3b836b4e78e70c5c5e8b76b5882f7be2d4181b677db2128`
- `agent_doc/results/prompt-scope-20261026/independent.log`: `fe4e32b2083219a6f9837f054880f338690a4d0365baab4704121aa09c0c3993`
