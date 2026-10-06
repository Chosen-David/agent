# 记忆与上下文：本轮四篇新增全文阅读

阅读日期：2026-10-06。已先按 arXiv ID 对全局 papers.json 去重，四篇均未登记；同篇不同版本不重复计数。固定 v1，全文实际取自 arXiv PDF；MemoryBank HTML/网页 PDF 读取报错，改为直接下载原始 PDF 成功。只保存笔记和哈希，不提交原论文副本。没有运行论文模型或安装其 runtime，以下数字都是论文报告。

## 机制对照

| 论文/固定原文 | 问题与机制 | 实验条件与原文证据 | 成本/失败与不迁移边界 | 本库对照和决定 |
|---|---|---|---|---|
| [MemoryBank](https://arxiv.org/pdf/2305.10250v1), 2023-05-17 | 时间戳对话→日/全局事件与用户画像→dense retrieval；回忆强化、随时间指数衰减 | §§2.1–2.3、§4.2/Table2；15虚拟用户、10天、194中英人工探针，人评分开检索与回答 | 摘要/嵌入维护成本；v1没有忘记机制独立消融，没有意图纠错/依赖失效测试 | 待测分层检索视图；拒绝以时间衰减删除科学证据、约束或更正 |
| [Mem0](https://arxiv.org/html/2504.19413v1), 2025-04-28 | summary+recent→候选事实，近邻比较后ADD/UPDATE/DELETE/NOOP；graph variant将冲突边置无效 | §§2–4/Tables1–2；GPT-4o-mini，m=s=10；LOCOMO十长对话、约26K tokens，去掉adversarial类；judge十次 | Table2 full-context J72.90高于base66.88和graph68.44；graph多跳低于base；构建/摘要成本另算，宽松judge不等价严格事实验证 | 待测紧凑检索与更新分类；拒绝自动覆盖删除审计历史；无本库质量收益证明 |
| [RULER](https://arxiv.org/html/2404.06654v1), 2024-04-09 | 不只single needle：多key/value/query、变量链、聚合、加噪QA；可控长度/难度 | §§3–6，Table3/Figs2–4，AppendixB–F；13任务每长度500例，4K–128K；8A100、greedy，GPT-4 API型号附录A | 有效长度阈值为Llama2 chat4K的85.6，非普适标准；recall判定可能放过额外错误项；合成不等价研究任务 | 待测参数化长链/遗漏/聚合保留任务，扩展现有pipeline，拒绝照搬阈值或把NIAH通过当任务完成 |
| [Lost in the Middle](https://arxiv.org/html/2307.03172v1), 2023-07-06 | 控制信息位置和长度；比较检索召回与reader使用能力 | §§3–6/Figs5–14，AppendixA–D；NQ 2.7K例/10、20、30文档，UUID500例/75、140、300对，greedy，0613/Claude1.3等 | query前后重复修复UUID却对QA位置趋势帮助小；更多文档召回增加但reader饱和；旧模型、答案字符串包含评分 | 待测按需加载/位置扰动；拒绝无条件重复提示或假定2026模型同样曲线 |

## MemoryBank：证据与取舍

§2.1保存原始带日期对话、日摘要、全局摘要及生成画像；§2.2 MiniLM/Text2vec+FAISS近邻；§2.3 R=exp(-t/S)，首次S=1、召回S加1/t重置，并明说这是高度简化探索模型。§3开放模型LoRA rank128、3 epochs、A100、38K心理对话；此训练不能归因给记忆系统。§4.2 Table2分开检索准确率与回答正确性：英文ChatGPT检索0.763/正确0.716，ChatGLM检索0.809/正确0.438，表明找到不等于正确使用。没有成本延迟实测与forgetting独立消融，不能据此承诺科研效果。

候选 CXT-MB-01（待测）：在 `workflows/project_memory_workflow.md` 所述原文按需取回之上，增加带ID/来源/摘要版本的scope视图；源账本不可变，摘要只能candidate。收益是假设性上下文减负；成本是摘要失真和失效传播维护。最小实验：同一冻结用户更正链，比较原文/摘要+回取，记更正召回、来源命中、旧结论泄漏、上下文长度。拒绝遗忘删除：科学原始观测及不常用的stop约束不能因召回频率低丢弃；本库 `agent_runtime/project_memory.py` 已有显式revision/cascade，保持其硬门禁。

## Mem0：证据与取舍

§2.1从新消息对结合全局摘要与10近期消息抽事实，查10近邻再由模型选择操作；AppendixB伪码UPDATE复用ID、DELETE移除旧事实，和本库固定版本依赖不兼容。§2.2 graph冲突边标invalid、支持时间视图，较适合保留历史，但不是科学因果依赖级联。Table1 graph并非全面胜：多跳J47.19低于base51.15。Table2响应p95 base1.440s/full17.117s伴随质量差距；§3部署token指标主要为回答时取回context，§4.5构建开销另述。不能将此写成全流程成本降低或本库端到端延迟提升。§3.1排除不可答类别、AppendixA宽松judge允许同主题长回答，均不足检验旧错误意图回流；§4.5对Zep异步延迟观察仅限作者当时配置。

候选 CXT-M0-01（待测）：`project_memory.py` 的active/scope筛选先执行，再做可审计有限条数检索/按需read，不能先top-k全部历史再过滤使active被挤掉。最小实验混入旧意图/stale候选/相似无关scope，报告有效命中、泄漏、遗漏与查库耗时，不默认安装embeddings服务。
候选 CXT-M0-02（待测）：主AI的更新建议只能输出候选、引用旧ID和更正原文，由现有串行correct/accept应用；以“目标改变 vs 纠正误解”双时态holdout检验，拒绝只按最新日期或LLM冲突判断直接删证据。成本是提案复核和声明依赖；不同目标历史同时有效需保留。

## RULER：证据与取舍

§3多条目检索刻意测完整性；VT加hop/chain，聚合增难度，§5/Figs2–3显示干扰、遗漏、重复、错链、抄例子以及以参数知识代替上下文。Table3 GPT-4从4K96.6降至128K81.2；这只是其固定旧型号的13任务平均。AppendixB四hop一chain、四value/query，C任务相关性去冗余，D模型模板/answer prefix，E单needle大多满分对比F聚合与QA较低。论文文句声称所有模型vLLM/8卡，GPT-4实际上API型号在A，不能误写闭源本地运行。recall-based presence无法直接作为本库严格安全/来源评分。

候选 CXT-RU-01（待测）：`evals/agent_model_tasks.json` 与 `scripts/agent_eval_pipeline.py` 复用参数化fixture，轮换scope数、依赖深度、revision位置、同名干扰、待办多项聚合；独立验收既查应含集合，也查不应含stale/额外结果。预期发现长任务恢复遗漏，成本为模型调用预算与fixture生成维护；最小判别旧新同输入/预算的位置×噪声holdout；单元测试仅证程序门禁，不能代替模型任务。

## Lost in the Middle：证据与取舍

§3.1 exactly-one gold与Contriever distractors，文档约100tokens，控制10/20/30数量和gold位置；§3.2 greedy，0613版本，GPT-4全文评测估>6000美元故只子集。§4 UUID隔离语义；§5 encoder-decoder在训练长度内较稳、超出亦U型；前后query在UUID很好，QA稍差/最小改善。§6读者饱和早于retriever：>20篇边际收益约1–1.5个百分点，不应全量灌入skills。AppendixA时间不一致/歧义控制、B随机distractor、C500例GPT-4、Doracle/closed-book提供反混淆证据。评价是答案字符串出现而非来源或唯一正确结论，不能迁移到高准确科研声明。

候选 CXT-LM-01（待测）：按 `workflows/project_memory_workflow.md` 把当前有效意图版本、硬约束、未决项放紧凑hand-off，详细历史/source按需取回；在 `scripts/agent_eval_pipeline.py` 保留全量skill快照审计但仅向执行者提供相关任务入口，明确“审计保存”与“上下文加载”不同。收益是假设性低成本/少遗漏，风险漏依赖和压缩过度；最小实验同一内容换首/中/末位置，加多跳事实、单位、stop约束与旧更正，旧新版同预算，评分查实际产物/来源，并记上下文预算未知项。不能凭Token下降就采纳，正确性非退化为硬门禁。

## 综合候选

四篇支持一个连贯方向：保持显式来源与revision账本作为真相，给检索视图做scope/status前置筛选和有界装载，再用多条目/错链/位置扰动验证。MemoryBank强化频繁记忆可能与纠错优先相冲突；Mem0语义UPDATE/DELETE可能破坏固定依赖；Lost query重复不是通用解；RULER recall分数不是发布门禁。此文件只提出候选，不表示改动已采用或模型性能已提高。
