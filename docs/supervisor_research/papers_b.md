# 原始论文深读记录 B：协作、工具接口与技能反馈

核查日期：2026-10-03。以下读的是固定版本原文的方法、实验与限制，不是仅摘要或搜索标题。PDF 页码为 1-based；HTML 使用章节/表号定位，不伪造页码。浏览器成功读取三篇 PDF 全文及两篇 arXiv HTML 全文；执行环境直接下载 PDF 遇代理 `403 Forbidden`，因此没有本地 PDF，也不声称保存了 PDF。版本与定位的机器可读索引见 [papers_b_sources.json](papers_b_sources.json)。没有提交论文全文、用户材料或 PDF。数值是论文报告，未在本仓库重新运行模型实验。

## B1. AutoGen — 2308.08155v2

[Original PDF](https://arxiv.org/pdf/2308.08155v2), §§2.1–2.2 (pp.3–5), §3 A1 / Fig.4 (pp.6–7), ethics (p.10).

**Method/evidence.** Conversable agents expose send/receive/generate_reply; registered reply functions combine model, tool and human behavior. Conversation-driven control supports dynamic speakers, termination predicates and maximum auto-replies. A natural-language TERMINATE instruction is also demonstrated. In MATH, two built-in agents using GPT-4 score 52.5% on 120 sampled level-5 questions versus vanilla GPT-4's 30%; whole-test figures are 69.48% versus 55.18%. Several competitors were not evaluated on the full dataset, so these are different comparison scopes.

**Limits.** The authors identify risks from externally acting code/function calls and unresolved automation–human-control tradeoffs. A termination token expresses a model decision; it is not independent evidence of task success. These experiments do not establish durable scheduling, event deduplication or restart recovery.

**Transfer (our design inference).** Keep pluggable actor/tool interfaces and explicit bounded termination, but put the authoritative DAG and acceptance checks outside conversational history. An actor may propose completion; a verifier must attach evidence before committing it. Human-input configuration must not replace the repository's authorization gate.

## B2. MetaGPT — 2308.00352v7

[Original HTML](https://arxiv.org/html/2308.00352v7), §§3.1–3.3, §§4.1–4.4 / Tables 1–3, Appendix D.1.

**Method/evidence.** Five software roles exchange typed intermediate documents through a shared publish/subscribe pool. Actions activate after prerequisite dependencies arrive. Engineers execute tests, consult requirements/design/history, and revise until passing or reaching three retries. Benchmarks comprise HumanEval (164), MBPP (427), and author-created SoftwareDev (70). Reported pass@1 is 85.9%/87.7% for HumanEval/MBPP. Table 1 reports SoftwareDev executability 3.75 versus ChatDev 2.25, but token usage 31,255 versus 19,292. It records 541 seconds for feedback-enabled MetaGPT; the surrounding prose's 503 seconds corresponds to the no-feedback column, so we use the table.

**Limits.** Appendix D.1 explicitly describes interruption and choosing agent checkpoints as difficult. These benchmarks do not prove reliable cancellation/recovery. Author-created tasks and executability ratings do not imply arbitrary production completion.

**Transfer (our inference).** Use typed prerequisite artifacts and bounded execute–verify–repair; persist transitions independently of messages. Preserve failure after retry exhaustion. Do not import the paper's broad completion language as a state-machine definition.

## B3. AgentVerse — 2308.10848v3

[Original PDF](https://arxiv.org/pdf/2308.10848v3), §2 (pp.2–4), §3.1 / Table 1 (pp.4–5), §3.3 (p.6).

**Method/evidence.** Its loop recruits experts, collaboratively decides, executes, then evaluates goal–state differences. Evaluation can be human or model feedback and changes later recruitment. Vertical organization uses one solver with reviewers and bounded refinement; horizontal organization aggregates peers. Experiments use zero-shot GPT-3.5-Turbo-0613/GPT-4-0613. Table 1's GPT-3.5 MGSM score decreases from Solo 82.4 to Group 80.8; GPT-4 logical reasoning rises from Solo 64.0 to Group 66.5. Ten multi-tool tasks yield 9 successes for Group versus 3 for standalone ReAct; that small case set is not a general reliability estimate.

**Limits.** The paper attributes roughly 10% of MGSM errors to correct agents following incorrect feedback. Consensus can amplify mistakes. Model evaluation is not a durable, externally verified completion contract; no crash/restart experiment appears in these evaluated mechanisms.

**Transfer (our inference).** Diagnose observed gaps and revise only affected task branches. Reviewer agreement supplies diagnostic input, never automatic success or authority. Persist explicit failure reasons; independently ready branches remain runnable.

## B4. SWE-agent — 2405.15793v3

[Original PDF](https://arxiv.org/pdf/2405.15793v3), §§2–3 (pp.2–4), §§4–5 / Tables 1–3 (pp.4–6), Appendix E.3 (pp.117–118).

**Method/evidence.** The agent-computer interface provides compact search/view/edit actions, rejects lint-invalid edits, returns concise state feedback, and collapses older observations. Evaluation uses 2,294 SWE-bench issues from 12 Python repositories and 300 Lite issues. GPT-4 Turbo resolves 12.47% full / 18.00% Lite; the demonstrated shell-only Lite baseline is 11.00%. Removing editor linting reduces Lite to 15.0%. Resolution means evaluation tests pass after applying the patch. A $4 per-instance cap automatically submits existing edits on exhaustion.

**Limits.** Submission is not successful resolution. Most full-benchmark issues remain unresolved. Interface construction/case analysis was manual (Appendix E.3); results do not establish cross-domain or crash-safe operation. The abstract's 87.7% HumanEvalFix corresponds to Python; Table 2 also reports JS/Java, so avoid treating it as an undifferentiated aggregate.

**Transfer (our inference).** Standardize adapter results and diagnostic observations; store evidence references separately from condensed model context. Budget exhaustion becomes an explicit non-success state. Test-backed acceptance and persisted cancellation/recovery require their own implementation and tests.

## B5. Voyager — 2305.16291v2

[Original HTML](https://arxiv.org/html/2305.16291v2), §§2.1–2.3, §§3.1–3.3 / Table 1.

**Method/evidence.** A curriculum uses current environment state and completed/failed tasks; executable skills are indexed by description embeddings. Retrieval supplies five relevant skills. Interpreter errors, environmental observations and a separate GPT-4 critic guide refinement; after four unsuccessful code-generation rounds the curriculum selects another task. GPT-4-0314/GPT-3.5-0301 run through MineDojo/Mineflayer APIs. Evaluation reports 63 unique items in 160 prompting iterations. Across three trials, diamond tools are achieved in only 1/3 runs; without the skill library, 0/3. Baselines were adapted from NLP agents, not compared directly with pixel-input controllers.

**Limits.** Skill-library accumulation is not transactional task persistence. A critic may misjudge success. Switching objectives after failure is appropriate for exploration but does not satisfy a fixed user's unfinished goal. Three trials and privileged control APIs limit generalization.

**Transfer (our inference).** Record reusable procedures only with their validation context; reuse failures for diagnosis. Keep the user's original DAG obligation when exploratory subtasks change. Store checkpoint/effect evidence and explicit retry limits, rather than equating continuing exploration with eventual completion.

## 本仓库的工程决定（推导，不是上述论文已验证的结论）

- 完成定义分三层：actor 返回、独立验收证据、任务链全部必要节点成功；前一层不推出后一层。
- 论文支持结构化依赖、工具反馈、有限修复与角色分工作为设计来源；不能给 SQLite 事务、lease fencing、幂等、恢复或 scheduler SLA 背书。
- 定时间隔必须独立记录主 AI 估计、风险、进度变化和上下界；退避防止空转。上述论文没有实验确定适用于本系统的分钟数，因此默认值是工程参数。
- 对固定任务，达到重试上限只能 failed/blocked 并提供恢复条件；不借探索任务替换原始验收。授权阻塞不转成成功，监督器事件也不扩权。
- 用故障注入分别验证重复 tick、多实例争抢、crash/reopen、cancel、依赖阻塞与 terminal stop；清楚标注这些是确定性核心测试，而非真人任务成功率或 live LLM 性能证明。
