# read-boundary56 原文研究 A

访问日期：2026-10-19。主控授权：只写本文件；生产代码、guide、唯一任务索引由其他所有者处理。已读 AGENTS.md、prompts/decision_review.md、project_document_workflow.md；采用 explain-research-concepts 的原始来源核验规范。决策 EXECUTE：调查既定文件 I/O 预算竞态，训练/模型架构替换不在本次授权内。主控确认已新克隆并同步 origin/main `ffd9abf` 后写入。

真实完成：**5 篇原文方法/实验/消融或消融缺口/限制定向精读**；另 1 篇仅摘要及作者 README，未计入。没有逐页视觉审读，不称完整复现；未运行模型 benchmark、训练或论文代码，不声明本机 LLM 质量提升。以下数值均为论文报告。网页有单源摘要长度限制，故只保留最关键证据与精确章节锚点。

## 历史证据与当前问题

实际检索 `rg`：在 `agent_doc/results` 和 `agent_doc/task` 查询 `read-boundary56|knowledge.*budget|IO.*budget|read budget|AgentChaos|AgentFold|ACON|AgentFly`，取前 60 行，非穷尽。命中 token-fifty 系列快照明确说 AgentFold 当时只查摘要，不能复用为本轮精读；context-metadata35/review.md 是旧审阅线索，未做当前独立有效性认证，不复用其测量。

只读核验 `agent_runtime/knowledge.py:115` 的 `_read`：先 `stat().st_size <= MAX_BYTES`，再 `read_text`。因此读取前检查与实际读取之间可以变化；这是代码层观察，尚不是本文件执行的失败实验。以下迁移建议也不是已实现结论。

## A1 AgentChaos

- 原文：[2608.06790v1](https://arxiv.org/html/2608.06790v1)，2026-08-07；题名 AgentChaos: Chaos Engineering for Agent Systems via Programmatic Fault Injection。
- 实读覆盖：§3 分类、§4.1–4.4 wrapper/任务隔离/触发核验；§5.1–5.4、表3–9；§6.1–6.2限制。表格由 HTML 核对，未读图片像素。
- 机制：HTTP 层按字段、位置、频率注入，保存原始/修改响应与实际触发事件；未触发样本不进入受故障成功率。
- 证据：表4 AutoGen 故障下工具调用为对照的6.55倍；表7持续故障比单次更具破坏性。这里是配置敏感性分析，不是修复组件消融。
- 限制：系统在 ADK 重实现、每架构仅一个实例、每配置样本少；§4.3部分 error/timeout 是响应内容替换，不能当成真实传输失败覆盖。该论文没有证明文件系统预算安全。
- 决策 **adapt**：保留“故障真实触发+原始计数+正常对照”的评测原则；不移植 HTTP monkey patch。文件读取注入须由本项目独立设计。
- 来源回执：`turn1187view0`、`turn1189view0`、`turn1192view2`、`turn1193view0`、`turn1196view2`、`turn1199view3`。

## A2 ACON

- 原文：[2510.00615](https://arxiv.org/html/2510.00615)，页面实际标记 **v3，2026-06-01**；题名 Acon: Optimizing Context Compression for Long-horizon LLM Agents。带 v3 URL失败，未混称已读取另一版。
- 实读覆盖：§3.1–3.4公式与优化过程；§4.1–4.5表1–4/阈值分析的文字；附录A限制。未穷尽附录C/D全部案例。
- 机制：阈值触发历史/观测压缩；比较原文成功而压缩失败的轨迹，先优化效用再优化压缩，可蒸馏小压缩器。
- 证据：AppWorld表1完整上下文56.0、两阶段历史压缩56.5；OfficeBench却76.84→72.63。表3去掉对比反馈51.2→50.6；表4本地中位延迟73.24秒→87.68秒（历史压缩）。不能把节省token写成普遍加速。
- 限制：主要GPT、受控环境；自然语言优化无收敛保证，历史重写可能破坏KV缓存，压缩可漏关键细节。
- 决策 **defer**：当前是字节读取边界，不是语义压缩；需另设同模型质量/成本试验才考虑接入。
- 来源回执：`turn1185view2`、`turn1190view5`、`turn1192view5`、`turn1201view1`、`turn1201view2`、`turn1196view5`、`turn1198view3`。

## A3 AgentFold

- 原文：[2510.24699v1](https://arxiv.org/html/2510.24699v1)，2025-10-28；题名 AgentFold: Long-Horizon Web Agents with Proactive Context Management。
- 实读覆盖：§3.2–3.5状态/折叠/训练；§4实现、表1、图3–5说明与案例；§5。检索全文 `ablation` 无命中，未发现移除单个折叠组件的受控消融；不伪造消融结论。
- 机制：最近交互保留完整记录，较早历史为连续区间摘要；学习单步压缩与多步合并；生成并过滤训练轨迹后SFT。
- 证据：Qwen3-30B-A3B训练模型BrowseComp 36.2；200轨迹中到100轮上下文约7k，仍有超过20%任务因调用上限失败。图中均值基于存活轨迹，不能解释成全体固定队列成本。
- 限制：提示本身不能稳定生成规定格式；结果含训练因素，缺组件消融，较小上下文不保证任务完成。
- 决策 **defer**：不得因压缩降低上下文就扩大已授权调用预算；本次不训练折叠模型，也不以其成绩背书I/O修复。
- 来源回执：`turn1189view1`、`turn1190view3`、`turn1192view3`、`turn1193view1`、`turn1196view3`、`turn1197view1`、`turn1197view6`。

## A4 AgentFly

- 原文：[2508.16153v1](https://arxiv.org/html/2508.16153v1)，2025-08-22；题名 AgentFly: Fine-tuning LLM Agents without Fine-tuning LLMs。
- 实读覆盖：§3公式1–11与算法1；§4.1–4.2；§5.1–5.5表1–5、组件/K/连续学习/OOD；§6.1–6.3成本与规划器分析。未重新推导附录A全部证明。
- 机制：冻结LLM，案例记忆辅助planner；非参数相似度或用soft Q-learning学习检索，executor经MCP行动。
- 证据：表3 DeepResearcher平均F1随K从0到4为59.9→64.5，K=32为63.9；表5无CBR59.9/72.2、完整66.6/80.4（F1/PM）。无CBR也随迭代上升，不能把全部迭代收益归因记忆。
- 限制：有限约3k训练数据快速饱和；高难度输入token明显增长；跨模型总榜不能隔离记忆贡献。文中污染解释不是本研究独立确认。
- 决策 **defer**：受控检索数量可作候选，但学习检索不修复读取竞态；新reward/记忆训练需单独评估。
- 来源回执：`turn1189view2`、`turn1190view4`、`turn1192view4`、`turn1196view4`、`turn1197view2`、`turn1198view1`、`turn1198view2`、`turn1199view4`。

## A5 Reflexion（经主控授权补足）

- 原文：[2303.11366v4](https://arxiv.org/html/2303.11366v4)，2023-10-10；题名 Reflexion: Language Agents with Verbal Reinforcement Learning。
- 实读覆盖：§3角色/反馈/记忆/算法；§4.1–4.3 ALFWorld、HotpotQA、编程及表1–3消融；§5限制、附录B.1 WebShop负结果。
- 机制：actor执行、evaluator反馈、reflection把错误经验写进有界记忆，后续尝试引用；不更新LLM权重。
- 证据：HumanEval Rust最难50题的表3为baseline60%、无测试仅反思52%、有测试无反思60%、完整68%。MBPP Python反而80.1→77.1；生成测试的假阳性会使错误代码提前结束。
- 限制：并发/API/非确定性行为难靠普通输入输出测试描述；WebShop100环境试到4轮无改善，反思会困在局部最优。
- 决策 **adapt/defer**：采纳“先获得可信失败证据，再记录修复教训”的组织原则；自动反思循环暂缓，不能把自评或重复尝试视作独立验收。
- 来源回执：`turn1204view0`、`turn1205view0`、`turn1205view1`。另PDF入口可访问，但未逐页视觉审读。

## 未完成来源：When Agentic Executions Fail

[2608.14680](https://arxiv.org/abs/2608.14680)，原文版本与提交日期未由可访问原页核验，**不计精读**。arXiv html（无版本/v1/v2/v3）、abs、pdf（含v1）、export PDF 均失败；搜索摘要可得；[作者仓库](https://github.com/kevinzck8k/agentic-fault-diagnosis) README可读；Academus仅摘要，明确无法生成正文。搜索日期与其他索引显示不同日期，不自行选一个冒充原文日期。

作者README支持：同输入故障轨迹与无故障参考配对、标签隔离。可作后续查阅线索；论文方法细节、消融和限制仍未核验，采用决定 **defer**。来源：`turn1193academia19`、`turn1198view4`、`turn1201view0`；失败：`turn1190view0`、`turn1190view1`、`turn1196view0`、`turn1196view1`、`turn1199view0`至`turn1199view2`；仅摘要：`turn1202view0`。

## 对 read-boundary56 的独立工程建议

以下是结合当前 `_read` 代码的推导，不是论文原有实现，也未在本文件内执行：

1. 故障矩阵至少覆盖：检查后文件增长、检查后路径替换、边界内/等于/超过预算、无效UTF-8、正常文件。若兼容承诺涉及特殊文件，单独验证非普通文件不会无限阻塞；不要由一次测试推广到全部文件系统攻击。
2. 使用确定性的事件/barrier把变化放在检查与读取之间，保存注入成功证据；未触发不能算防御成功。正常对照须与故障输入绑定。
3. 宿主应限制真正的读取请求并记录总返回字节；“无限read后切片”不能证明I/O有界。若用额外1字节判断溢出，必须把`预算+1探测`明确写入契约，不能声称零超读。
4. 分开检查正常语义/哈希、明确拒绝、资源读取量与终止状态。拒绝超限是安全结果，但不是业务任务成功；省token、少内存、正确回答也不是同一个指标。
5. 失败诊断与重试仍消费预算。上限由宿主强制；反思文本和历史案例不得重新授权预算。只有主控冻结修复代码/输入/日志并独立复核后才能形成当前补丁有效性结论。

交接主控：5篇定向精读已完成；原指定2608.14680保留未读记录；建议验证故障触发、有限读取和正常兼容三个独立断言。本文没有增加生产能力或替代后续实验验收。
