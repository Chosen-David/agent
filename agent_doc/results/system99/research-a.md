# SYSTEM99 正文阅读 A：记忆与失败诊断

阅读日期：2026-10-20 UTC。本记录是文献证据与迁移取舍，不是本库实验、正式投稿审稿或运行时实现。4/4 篇取得原始 arXiv HTML 并分段覆盖正文；不是摘要计数。论文数字均为作者报告，未在本库复现，未调用付费模型/GPU。

## 查重、来源与范围

- 在当前检出 `dcc10b10537a3b410a25f6ef3f2c842a3c1777b4`，实际执行 `rg -n '2602\.16313|2603\.25001|2605\.14865|2607\.07989|MemoryArena|MP-Bench|AgentLocate|Holistic Evaluation' docs agent_doc .agent-runs`，阅读前无命中；因此本轮四篇可计新读。主控已同步最新远端并持有仓库锁，本角色只写此文件。
- 结果库 CLI 查询 `MemoryArena MP-Bench AgentLocate Holistic Evaluation`：扫描199、`partial=true`、65个缺失record等错误；5个返回项是 combined-corpus 两项及 math-convex-projection / math-convex-support / math-discrete-lyapunov 历史，未返回这四篇的正文记录，不复用作新阅读证据。此检索不证明历史穷尽。
- 知识 CLI 查询 `agent memory failure attribution multi-session`：snapshot `767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18`；返回 QLoRA/HNSW/FlashAttention 内存卡，语义不匹配，不采用，`knowledge_refs=[]`。本轮依据是下列原始正文与已读本库契约，不把词法命中当适用。
- 已自行读取 research-review 的 SKILL 与相关完整工作流，采用其版本、主张—证据、反证和适用性核验纪律；按委派范围不扩大成 venue 打分、工具安装或实现任务。
- 四篇 HTML 全部可达，无 `abstract_only` 或失效论文来源；一次工具长输出截断后已重开相邻区段补齐。未下载/逐页视觉审读PDF，所有图仅阅读图题及正文解释，不能宣称已核验图内曲线/标注。下列行号为本次 arXiv HTML 阅读器定位，章节为稳定主定位。

## A1 MemoryArena

原题：[Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks](https://arxiv.org/html/2602.16313v1)，`2602.16313v1`，2026-02-18。

已读：§1–5及Impact Statement（HTML L81–353）；§3.1四类数据构建、§3.2 Retrieve/Update环、§4.1–4.6设置/指标/结果/深度/延迟/POMDP讨论；表1–4正文数据。未读：附录A–C、附录图表与具体prompts；图1–3未做视觉核验。无专门组件消融，§4比较不同记忆范式，不能当作同系统受控消融。

机制是每个子任务结束更新记忆、后续动作按需检索，任务强制依赖早期状态。766组购物、旅行、搜索、推理任务中，表3固定GPT-5.1-mini比较记忆方案；外部记忆并非普遍优于原始长上下文，精确槽位/引理复用尤其怕过度摘要，§4.4随依赖深度退化。限制是人工构造依赖、模型/接口条件有限，不能把失败全归因于记忆。**adapt**：给记忆/交接验收增加“旧事实必须影响后续动作、纠错后旧状态不得复活”的跨会话用例；**reject**：以已检索、已压缩或召回率代替端到端正确性，也不据此默认引入更复杂记忆服务。

## A2 MP-Bench

原题：[Rethinking Failure Attribution in Multi-Agent Systems: A Multi-Perspective Benchmark and Evaluation](https://arxiv.org/html/2603.25001v1)，`2603.25001v1`，2026-03-26。

已读：§1–8（HTML L65–309）；§3形式化、§4标注/合并/分歧、§5排序与解释评估、§6设置/主结果/温度/采样数/跨模型比较、§8限制；表1–5正文数据。未读：附录A–C及图6/8完整prompts；图1–4未做视觉核验。

机制保留多个“失败步骤—理由—理想动作”，以三名专家共识排序而非唯一根因。289条GAIA/AssistantBench、MagenticOne/CaptainAgent日志，默认三次采样、温度1；表2以nDCG和LLM解释评分评估，表3–5分析温度、次数和模型组合。限制是小规模助手域、解释经模型合并/评判，排名一致不证明实际修复有效；表3–4也不支持每个配置严格单调增益。**adapt**：错误归因保留候选、各自证据与反例，区分上游来源和下游显现；**reject**：把共识票数当严重度/客观因果，或由多个同意直接授予验收通过。

## A3 Holistic Evaluation

原题：[Holistic Evaluation and Failure Diagnosis of AI Agents](https://arxiv.org/html/2605.14865v1)，`2605.14865v1`，2026-05-14。

已读：§1–6（HTML L67–241）；§3.1叶span指标/聚合、§3.2全局覆盖/计划、§3.3互补案例、§4设置与比较、§5局限；表1–4正文数据；附录B.2/B.3/C（L611–804）。未读：附录A/B.1；图1–6均未做视觉核验。表3是单案例检测对照，并非完整受控消融。

机制把叶span的工具/推理错误与全局目标覆盖、重复调用分开检查，再沿层级汇总。TRAIL的148条GAIA/SWE-bench轨迹、841项span标注，GPT-5.4作judge并额外映射分类；表4显示局部定位改善，但“定位准确率”分母是预测错误项，不是完整召回。作者§5及附录C承认任一局部错向上传播会把无害格式问题等同全局失败，且标注/分类边界不稳。**adapt**：验收同时检查局部契约与全局目标；**reject**：直接套用默认existential聚合、把span关联路径称作已证因果，或用judge分数替代独立数据核验。

## A4 AgentLocate

原题：[Who Broke the System? Failure Localization in LLM-Based Multi-Agent Systems](https://arxiv.org/html/2607.07989v1)，`2607.07989v1`，2026-07-08。

已读：§1–6及Ethics（HTML L51–215）；§3三阶段算法、§4设置/结果、§5消融与误定位；算法1、附录A/B/E–K文字和表1–15（L268–531）。附录C/D在所取HTML只有标题，没有完整prompt内容，故不计已读；图1–5只读图题/讨论，未核图内数据；未读代码（作者称接收后发布）。

机制先猜agent-step，再用同基模三种提示的Evaluator自报置信加权，最后LoRA训练Judge。Who&When按50/10/40划分，Aegis训练8933/测600；表13比较直接猜、仅投票、直接标签微调，完整法在算法集Qwen all-at-once步骤准确率38.10%，但手工集16.67%与两变体持平。§3.1明确未运行理想动作反事实，附录B还要求单步可修复集合非空；长轨迹与显现点偏差仍在。**adapt**：归因先列可反驳假设及所缺验证；**reject**：把自信投票称为独立因果验证、强制唯一根因或在无授权条件下引入模型微调。

## 本库入口映射与交接

已核对 `prompts/orchestrator.md` 的事实/假设区分、`workflows/project_memory_workflow.md` 的candidate与纠错依赖、`workflows/agent_communication_workflow.md` 的消费者依据门禁、`workflows/result_validation_workflow.md` 的可信独立verifier。上述文献支持强化现有边界与验收用例，不证明必须新增服务或改关键schema。

建议主控后续最小验证（尚未执行）：跨会话消费已更正记忆、候选根因与已证事实分离、上游错误/下游显现错配、局部格式错但全局正确四类固定案例。应分别保留错误候选、过程契约与最终验收结果；不把任一论文榜单数字登记成本库收益。本角色没有修改源码、TASK或人类指南。
