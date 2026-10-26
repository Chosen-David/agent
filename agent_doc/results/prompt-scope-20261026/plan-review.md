# Independent plan review — PROMPT-SCOPE-01

Decision: **approve the bounded candidate plan**, before production edits or test execution. Reviewer: `/root/prompt_scope_review_2225`, 2026-10-26. Project/workflow root: `/workspace/scratch/6416f20dc59b/agent-run-1303`. This is source/plan review, not result acceptance. Only this review file was authored; no tests, benchmark, model task trial, production, TASK, guide, Git or foreign archive mutation was performed.

The current stable SYSTEM-99 is Version39; Version40/phaseX is a proposal, not an already-published task revision. Main must reconcile that narrow phase before execution, preserving all existing pending/failed/cancelled gates. Unique TASK index and both human-only guide files were inspected read-only (GUIDE is empty). The scoped local-regression exception does not remove the already-requested independent result review. No new permission or inference budget follows from this approval.

## Source and oracle assessment

The counterexample is concrete: `Prose` + a nonphysical separator + literal backticks occupies one Markdown physical line. Python splitlines nevertheless starts a synthetic line at those backticks, allowing an otherwise nonexistent first text fence. A later line-start decision marker is then treated as canonical global scope. The inverse fixture puts fake closing backticks after prose inside a genuine text fence; splitlines closes the real fence before its marker. Existing physical_lines preserves those suffixes within their real line while retaining character offsets. Import plus fence-loop substitution addresses both mechanisms without changing marker search or block endpoints.

The eight literal separator fixtures exercise all extra splitlines boundaries beyond CR/LF. Canonical rejection, exact retention of an unknown research source, all four additional shared markers, and genuine canonical acceptance after fake closers have independent literal expectations. Expectations do not invoke physical_lines or _span. The direct additional-marker test intentionally isolates the shared-section helper; existing composer cases cover its integration. Full source bytes are checked in the CLI fixture, and each modified in-process source is checked where applicable. Original tests retain exact/differing policy, first-full/later-reference, ambiguity, quote/comment/outer-fence, symlink, cache absence, selection and cap checks.

The proposed loop-only repair preserves per-invocation emitted sets, exact text equality, selection order, trusted source hashes and standalone source bytes. Ambiguous canonical scope still rejects; unverified noncanonical scope remains complete. Marker matching and the parser's existing conservative scope heuristic are deliberately unchanged. This is not a general CommonMark correctness claim, nor additional CR-only-marker coverage.

configure_utf8_output is the existing shared stdout/stderr reconfiguration helper. Calling it before argparse makes raw and ensure_ascii=False JSON output actually UTF-8 under the forced cp936 child environment. The new CLI expectations inspect UTF-8 bytes, successful exit, empty stderr, disposition and literal source inclusion; they cannot pass solely from API output. Preserve CLI arguments and failure behavior. max_chars continues to bound the complete composed prompt, not JSON metadata or the terminal newline; applying the neighboring wire-budget policy here would change the established contract.

run_checks.py fixes the intended baseline/fixed module selections, captures raw combined output and return code including timeout, and records before/after file hashes. Outer120s and nested15s bounds are explicit. Root must retain original-source failure evidence before repair, then run the three accepted modules and obtain independent result execution/review against actual changed bytes. The runner does not itself establish independent identity or acceptance. Existing portable installation matrix is Ubuntu/Windows × Python3.10/3.12; adding the prompt module there and reading all four real jobs remains future evidence, not a current pass. Do not repeat old fullsuite/PID/ALIAS/role/Codex/wire gates or reset their budgets.

## Reading audit and limits

Independently inspected the local text main §§1–6 including Tables1–4/captions1–5, C.1, D.1–D.2, E.1/Table6 and E.2 overview, H.1–H.3. HTML was hash-checked, not visually read; no PDF pixels, B/Table5, Table7, F/Table9, G table or other appendix prose were independently read. Root's broader declared appendix reading is a root record, not reviewer coverage. Main prose/table and requested methodological claims match the inspected body; no separate lengthy paper summary is added.

审计要点：任务筛选运行与新NoMem基线明确分开；Rescue/Harm由每任务3×3跨条件配对计算，不能当九个独立样本，bootstrap按任务；历史记忆构建tokens不在求解成本内；失败轨迹归因为人工且类别可重叠，不是因果消融；构建流水线未做系统对照。论文不能证明本仓库模型任务质量提高。

Pinned prior reading index hash matches and records 11 retained distinct same-batch readings; this review did not reread that historical corpus and does not certify a new twelve-paper independent body count. GACC is downloaded-only and uncounted. Reading.md keeps future evaluation advice separate from implementation. Source inspection of decide_run, check_handoff_basis and check_task_memory supports its repository interpretation: explicit conditions/current independent scoped acceptance, declared reference checks, and no scientific applicability certification.

Limits: original failures, repaired passes, native CI, actual host/model behavior, complete provider token/cost accounting and overall SYSTEM-99 acceptance remain unverified here. Current root/reviewer inference usage is unknown, not zero. No model-quality, performance, cost or whole-round completion conclusion is accepted.

## Frozen SHA-256 bindings

- `AGENTS.md`: `97f35fc8fb91097a34380c12a9581936f8a78c6f9c10a05183c84511645738ed`
- `workflows/project_document_workflow.md`: `6ee07eca5091187b27e02056c3ae83f66183cfc07dc4c7af5c80742ffacdaaf4`
- `workflows/result_validation_workflow.md`: `349cebab1a78baa63b5c7d422f239c2d802f9f77a1ad180ceb4871ebea372888`
- `agent_doc/results/prompt-scope-20261026/plan.md`: `8d89347af21095968e14743f61f9fe03c26b81511d190d76b23c9e6d2baec130`
- `agent_doc/results/prompt-scope-20261026/reading.md`: `f52d66a8534f783be923c2300767c451b4fe0c2d8be2643e908b1a2878358931`
- `agent_doc/results/prompt-scope-20261026/inputs.json`: `430ad9a3ba1ce4a28c05225356437f4f2ba457190aca612fce1b647c4bab9b76`
- `agent_doc/results/prompt-scope-20261026/run_checks.py`: `9750d07e2f4a3e575b26ace1a96c18dd028922fce2c35edf1d52d0903190c12f`
- `tests/test_prompt_context.py`: `67727190d01e959d539397a319a883a92f078b17d3717e233ff0e0f1d2cef663`
- `agent_runtime/prompt_context.py`: `af06ab2860ccb9be2698b2d7422e3dc43cafd0872c6d9f2ef20bcc275a361306`
- `scripts/prompt_context.py`: `758a1148c53bea34bb92f8a24855929428618391b6d95228501345fb228aaaa4`
- `agent_runtime/project_docs.py`: `456bbe40a5ca731e7ab311a4435838252627c9447d66e88b51ee082cd361e92c`
- `agent_runtime/context_serialization.py`: `2606666cf723af13cb2b8a4a0934848f233ffb16c50728fc4a43da01ff26453d`
- `agent_doc/task/TASK.md`: `cac11b59a920f4dc1dd398568ba6b2d0d0593ae5ac25d59858c53a2b739c706f`
- `agent_doc/task/task_details/SYSTEM-99.md`: `ece04290a24449e425effbfdc08029b260311c3e05d21cb9320ad795599ae702`
- `agent_doc/guide/GUIDE.md`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `agent_doc/guide/README.md`: `f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261`
- `.agent-runs/history-quality-2225/2610.27524v1.txt`: `13d734246a18197eca837036e8bbb67d19632c80e98a8ee5447b51a3099297ad`
- `.agent-runs/history-quality-2225/2610.27524v1.html`: `54373363bcead2751133bb807e5cd2223078e560c683c4df596b3c411e44fc00`
- `agent_doc/results/workflow-transfer-reading-20261026/inputs.json`: `f748b204d55d1057bf2a0e2cef16413401ef30260a9b33bd4ac38e3db2f91578`
