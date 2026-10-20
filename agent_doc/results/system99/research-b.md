# SYSTEM-99 正文阅读 B

读取日期：2026-10-20。范围：四篇原始论文的新阅读，不以摘要、搜索结果或旧笔记抵数。
本记录仅提供机制、评估设计与迁移假设；未运行论文模型、付费服务或GPU实验，论文分数不是本库收益。

## 来源、去重与覆盖

开始先以四个标题/ID检索 `agent_doc/results/`、`docs/` 的Markdown，均无命中；另读
`artifact-read76/research.md`、`memory-storage-20261015/research.md`，其中旧论文不重复计入。
四篇均实际获取指定版本原始PDF；前三篇先逐节阅读arXiv原始HTML，随后核对关键PDF原页。
未声称逐页视觉审读，也未把渲染成功算作阅读。PDF/辅助文本/渲染位于私有运行目录
`.agent-runs/system99/papers-b/`，下列hash绑定实际下载字节。

| 论文与锁定版本 | 日期；PDF身份 | 实际覆盖；未读范围 |
| --- | --- | --- |
| [EvoMemBench: Benchmarking Agent Memory from a Self-Evolving Perspective](https://arxiv.org/html/2605.18421v1)，2605.18421v1 | 2026-05-18；30物理页；SHA-256 `4f3a9a28742ad89fba7d5010431ce5c597bbd819ce0c1e473cdd6d8ff1f163d6` | HTML §1–6，含§3定义、§4构建、§5全部实验与表3–6、预算/迁移对照；补读B.2接口/截断/检索配置；视觉核对PDF p6–7表3/4和图2。未完整读A/B.1/C、未核查图3/4及附录热图原图。正文无独立limitations节，限制判断见下文。 |
| [DolphinBench: Mapping the Pareto Frontier of Agent Memory](https://arxiv.org/html/2609.24971v1)，2609.24971v1 | 2026-09-21；8物理页；SHA-256 `618586c12870bb61f7880b199a70b01970c03fb4836ca3268acca0f94eb0fe87` | HTML §1–6，含全部构建、验证、评分、表2与§5五类限制；视觉核对PDF p5结果表/指标。无附录；未逐页看其余PDF图像，图1/2只读正文说明与图注。未下载运行配置和trace，不能独立复算结果。 |
| [MemSyco-Bench: Benchmarking Sycophancy in Agent Memory](https://arxiv.org/html/2607.01071v2)，2607.01071v2 | 2026-07-02（提交15:40:30 UTC）；43物理页；SHA-256 `6a4c25d6c2ecdcf833740f42b29a54448ac741381d553c50e738180ec77c8d59` | HTML §1–5完整正文；补读B.4验证、D指标、E.3效率/E.4干预、F.1–F.3设置；视觉核对PDF p6构建与p9图6/表2。未完整读A/B.1–3/C/E.1–2/G、各系统JSON及图7–18原图。当前摘要页另有v3(2026-10-15)，本记录没有混用v3正文。正文无独立limitations节。 |
| [The Compliance Trap: Diagnosing How AI Agents Consume Conflicting Memory](https://arxiv.org/pdf/2607.10608v1)，2607.10608v1 | 2026-07-12；25物理页；SHA-256 `adf8426ba1a9120f62eb2310628803df7a0534da77444e31b7c460ba48f55e05` | PDF p1–9 §1–6全部正文；补读E.2入口×grounding消融、G重试与无记忆重试消融（p20–21、23–24相关段落）；视觉核对p7图4/表2和p9表6/7、限制。未完整读A–D/E.1/E其余/F/G末表及其余图像，不宣称全部附录核验。 |

获取失败保留：Compliance的`/html/2607.10608v1`、`/html/2607.10608`、`/abs/2607.10608v1`和搜索工具打开`/pdf/2607.10608v1`均返回Internal Error。
未凭其搜索摘要计数；随后普通HTTP下载同一原始PDF成功（447831 bytes），才开始正文阅读并纳入四篇。
Dolphin PDF转文本报告字体嵌入警告；表2采用原页视觉核对，不依赖警告后的纯文本列序。

## 1. EvoMemBench

以“单回合/跨回合×知识/执行”拆解记忆，统一utilize/update接口。15种记忆方法用DeepSeek-V3.2骨干，另设三种无记忆模型；预算16K–128K且记忆也占窗口，溢出先截早期历史。表4中ReasoningBank在16K为43.0%、骨干28.5%，但128K多法退化；§5迁移亦有负结果。采用分层评估及保留精确执行状态，不采用固定记忆形态或默认压缩。限制是改造BFCL、单一记忆骨干和按该骨干成绩划难度；预算变化并非独立证明摘要失真为唯一原因。本库仍需真实恢复/更正任务验证。

## 2. DolphinBench

把记忆测量落到动作而非提示检索的QA：三个人设各约50万用户消息token、200任务。每题用GPT-5.6-Luna做两次oracle历史成功/两次无历史失败检查；确定性与GPT-5.6-Sol语义判分须在同一动作满足全部条件。表2同时报告摄取+测试总费用与任务中位延迟，配置排名随模型/harness变化。采用“有证据/撤证据”对照与质量/总成本联合验收，拒绝以召回率或便宜CPU等同任务能力。限制：合成历史、模拟应用、仅1–4个评分动作，摄取/测试分离；没有独立组件消融或生产服务中断证据。

## 3. MemSyco-Bench

五类任务区分事实、作用域、证据冲突、更新选择和有效个性化。七个记忆系统统一bge-m3，建记忆用DeepSeek-V4-Flash，生成骨干与温度按任务固定。§4.2显示61–62%错误发生在已检索相关记忆之后；图6中泛化caution改善部分冲突却损害个性化，“Are you sure”亦会退化。采用“相关≠有决定权”的scope/时间/来源检查及五类正负对照；拒绝一律忽略记忆或加一句警告便宣布解决。限制：合成任务、rubric/LLM判分、原生配置差异与未复算trace；正文/附录部分百分比和增量叙述不一致，不能照搬精确平均收益。

## 4. Compliance Trap

固定记忆文本、改变early/persistent/late暴露，按Entry–Propagation–Recovery分解轨迹；WebArena 684题预检与结果筛选77题机制集分开，另造231题MemTrapBench。RCR区分服从概率，DPC在同一服从子集配对损害；表2的63–72%服从并非本库风险率。E.2正交变入口/grounding，G用无记忆重试控制采样；警告减少伤害也损失帮助。采用首次受影响动作、传播/纠偏及恢复后的最终验收观测；不直接采用retry-on-fail控制器。限制：web代理、合成trap、77题有选择偏差、已知成功/失败信号及额外重试成本；作者亦称仅诊断证据，不是部署方案。

## 本库迁移与未验证边界

这些来源支撑SYSTEM-99后续检查的设计：区分静态协议通过与实际任务成功；在相同任务下比较有效/过期/跨scope记忆、原始证据可用/撤去；记录首次受影响动作、最终恢复与全部装配/判分/重试成本。
它们不证明当前TASK解析修复的收益，也不授权改记忆策略。阶段A应由真实checkout回归证明；真实模型任务质量、费用和长流程恢复仍需主控后续验收，不能用本四篇的分数填补。

知识接入：实际执行`python -m agent_runtime.knowledge --root knowledge search 'agent memory retrieval preference conflict trajectory evaluation' --limit 3`，snapshot `767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18`；命中QLoRA/HNSW/FlashAttention，仅词面memory相似，与行为消费/恢复不匹配，拒用，`knowledge_refs=[]`。事实依据是上列原始论文与当前项目契约，不把检索命中当理论保证。
