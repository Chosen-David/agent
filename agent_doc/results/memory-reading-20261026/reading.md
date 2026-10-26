# SYSTEM-99：计划与事实的记忆边界

2026-10-26；源码基线 `2bf58e97daf0920bae15466c3a07c6cdcd50d835`。
这是同一未完成批次的阅读检查点，不是实验结果、实现验收或新任务清单。

## 正文阅读

Chirag Sharma, Benjamin Fowlersmith, Karime Maamari，
*AgentMemGate: Addressing Speculation Contamination in Conversational Assistant Memory*，
[arXiv:2610.07707v1](https://arxiv.org/html/2610.07707v1)，2026-10-06。
实际读到 §§1–7、Algorithm 1、Tables 1–8、Figures 1–4 的 HTML 文本/表格说明、
Appendix A.1–A.7；不是逐页 PDF 视觉审查。HTML SHA256：
`631e5caa2842f7bd0c6e7b9708d4046f37166ec661dc268db377f9ed844725fd`。

方法（§3）：抽取→固定字段匹配→四类证据分类；未发生计划暂存，确认后提升、放弃后移除；
纠错与真实事件更新分开。实验（§§4–6）：literal/cautious × gate on/off，60/147/179
会话；核心 literal 待定污染 87.5%→0%，最终准确率 65%→95%。held-out 只测终态污染，
没有 pending window，不能混用两者。消融（§6.3/A.1）：去匹配 retry、无 gate 加 retry、
只读遮蔽计划；低污染可伴随未解决计划累积。局限（§7/A.5）：合成数据、小样本、单字段、
未测计划问答/保留策略；纠错仅5例且人工标签分歧。额外分类/逐回合检查调用不等于免费。
这些均为作者报告，本库没有复现实验。

## 与现有源码的关系及决定

当前 `agent_runtime/project_memory.py` 的 `_insert` 将 candidate 留在 candidate，
`_walk` 拒绝非 active 引用，`accept` 创建新 revision，`correct` 标记后代 stale。
`workflows/project_memory_workflow.md` 已要求推测默认 candidate、区分旧理解错误与目标改变。
`tests/test_project_memory.py::test_candidates_require_explicit_new_revision_acceptance`
已有对应账本回归；本次只读源码，没有重跑，也没有用旧通过标签授信。

论文的 profile current-value 和本库 active 不是相同概念：已获用户确认的 intention
可以 active，但这不表示计划中的外部事件已发生。不能把所有 intention 隐藏或自动降级，
否则可能丢掉有效用户目标。本次决定：采用“检查中间状态”的评测视角；暂缓新增分类器、
暂存表或竞争记忆层。尚未发现已确认需要修改的生产缺陷。

待验证假设：即使账本门禁正确，任务包/交接的语义投影仍可能把 active intention 当作
已发生 observation。先沿现有 `basis_context`、task memory refs 与定向交接检查消费者，
再决定是否需要实验。后续最小对照应覆盖计划未决、放弃、完成、纠错和仅改变未来目标，
同时核对中间与终态；比较全量和任务包时保留更正、异议和依赖。只有出现反例并固定验收后
才提出原地修复。模型任务质量、实际上下文 tokens、所有 actor 用量、调用/延迟总成本均未测。

初步源码检查：`_read_entry` 保留整行元数据，`handoff_basis.basis_context` 的 JSON 分支
携带完整 `memory_entries`，不是只提取 content。故不能将“kind 在该 JSON 分支被删除”
当作已知缺陷。表格编码、cache 省略后的实际当前上下文和自然语言使用仍未在本次核验。

## 阅读账与阻塞

本检查点新增并保留正文记录 **1篇**；先前报告的55篇私有全文记录仍未恢复，不能据此
重认当前保留记录已达到10篇。Mem0、MemoryTax 等搜索命中未在本次精读，不计数。
本次没有执行测试、PID/ALIAS/role capture/Codex 重试，也未重置其旧预算。
PID 原生身份视图前提、遗失候选及真实后端/端到端质量等 SYSTEM-99 未决项继续保留。
