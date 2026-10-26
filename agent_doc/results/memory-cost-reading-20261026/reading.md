# SYSTEM-99：记忆成本与公平输入

2026-10-26，基线 `31a5b9c1607219db0947b4b5a2120f65395a07b3`。
同一未完成批次的文献及源码阅读；没有新实验、性能或模型质量验收。

## 正文记录

Zedong Peng，*MemoryTax: The Bitter Lesson of Agent Memory*，
[arXiv:2610.29823v1](https://arxiv.org/html/2610.29823v1)，2026-10-21。
实际阅读 HTML 正文 §§1–6、Tables 1–4、Figures 1–4 说明与 Appendix A–C；
没有逐页 PDF 视觉审查。精确输入哈希见 inputs.json。

方法（§2）：LoCoMo 单会话419 turns/152问题，七方法×三模型，每格一次；
全上下文、BM25、Mem0、Zep与三种工具 Agent 对照。
作者报告（§§3–5）：Opus 下 Pi 99%/$6.95，全上下文95%/$17.84。
写者/读者交叉（§4/Table3）测试抽取信息损失；caption 分组（§5/Table4）
揭示输入不等价，无图片证据88题只差一答。
成本（§2/Table2）含构建、LLM/embedding调用和缓存价格，排除judge；token统计不含embedding。
关键协议（Appendix B）：失败/空答重试，只计接受试验，因此表中金额不能当全部尝试总账。
局限（§6）：单会话/单次、弱模型judge及错答案、caption不等价、历史均能装进上下文、
默认配置与价格/cache依赖。上述为作者报告，未在本库复现。

## 本库源码核对与决定

续接上一份 AgentMemGate 记录，不增加竞争记忆层。只读检查：

- `handoff_encoding.MEMORY_COLUMNS` 明列 kind、content、source、scope、evidence、status、
  created_at、document_refs、deps、id；`encode_basis_tables` 拒绝缺失/未知字段。
- `choose_basis_payload` 比较完整编码；不兼容表格 schema 时尝试完整 JSON，
  每个候选须可解码且满足调用者提供的 token/字符预算。
- `basis_context` 的 usage 明确仅精确序列化 payload，不含工具 envelope、模型输出。
  known_memory_ids 是可信宿主对当前上下文已有内容的声明；代码核查新鲜性，不能认证真实持有。
- 现有 `test_memory_tables` 有实际 Mailbox 闭包/往返、纠错后拒绝复用源码；
  `test_handoff_basis` 有 leaf cache 不省略缺失父项的源码。本次未重跑，不能据此授信当前实测。

没有发现“表格直接删除 kind/evidence/status”的已确认缺陷。保留现有正式实现，
不为阅读结果造新模块、常驻旧版或机械增加提示。自然语言消费者是否正确区分 active intention
与已发生 observation，及 cache 声明是否符合实际宿主输入，继续未知。

采用的研究判断：后续全量/任务包/活跃视图比较必须先固定相同可用原始证据，
并检查更正、异议、依赖及中间状态；不能让一组多看到附件，再把准确率差归因于检索机制。
成本需含构建、检索、选格式、工具、所有actor与失败/重试，分开冷启动/复用与缓存价格；
无法观察的provider字段写 unknown。独立评判/审稿也单列成本，不因论文排除judge而漏账。
以上是后续实验的必要口径，不是已批准/已执行实验，也不改变稳定 Plan 或旧预算。

## 第二篇正文：检索与查询裁剪

Yuqian Wu 等，*Back to Basics: Let Conversational Agents Remember with Just Retrieval
and Generation*，[arXiv:2604.11628v1](https://arxiv.org/html/2604.11628v1)，2026-04-13。
实际阅读 HTML 正文 §§1–6、主文 Tables 1–4、Appendix A.1–A.3/B.1–B.3/C/D/E、
Table 5–7 和图注；没有读取图内像素，HTML 中空白表格引用不当成已见数值。

方法（§3）：TIR 用最相关 turn 的相似度给 session 打分；QDP 用额外模型按问题抽取原文片段。
实验（§4/A）：四个对话基准，默认 Contriever、gpt-4o-mini-2024-07-18、top3。
消融（Table4/7）：LoCoMo F1 15.76→19.62→22.66；生成阶段平均 tokens 2348→2685→1403，
不是完整调用总账。并非所有指标胜出：LongMemEval-s 的4o-J为57.20，MemGAS为60.20。
局限（§6/D）：在线裁剪串行延迟，隐私/可解释性；Full History 只保留最近128k，
不是百万token基准的完整上下文。零答案词重合不能证明一个turn没有语义作用。
均为论文报告，本库未复现。

本库适用判断：借用“细粒度定位后取必要上下文”的检索假设，暂缓将QDP引入正式交接。
本库 `basis_context` 已显式保留未选中的 candidate/rejected claims 及其依赖闭包；
查询相关性裁剪不能覆盖这些语义必需项。即使片段不含答案词，也可能记录否定、
更正、授权边界或依赖，不能用原文词保真冒充完整事实保真。应先在现有任务包与全量输入
的等证据对照中检查这些反例，而非直接机械删文档/注释或另造共享聊天池。

## 检查点与下一步

本次新增2篇正文；连同上次已发布记录，目前清理后可恢复的新正文记录共3篇，
旧55篇私有原件仍未恢复，不据此重认十篇门槛。继续相关正文及真实消费者审查，
固定可执行验收前不宣称创新已落地、任务质量或性能提升。PID/ALIAS/role/Codex旧门禁与
系统级未决项保持；未做测试、模型调用、预算重置或生产修改。
