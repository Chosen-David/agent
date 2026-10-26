# SYSTEM-99：受控记忆对照与原文保真

2026-10-26；基线 `c64fb6ea8cda5deffd32b3499a7d2994f01de1d0`。
正文精读与静态源码续接；没有执行新测试或模型评测，没有生产修改或收益验收。

## MemDelta

Kuan Wang，[MemDelta: Controlled Baselines and Hidden Confounds in Agent Memory
Evaluation](https://arxiv.org/html/2606.29914v1)，`2606.29914v1`，2026-06-29。
实际阅读 HTML 正文 §§1–5、Tables 1–10、Appendix A–C 与图注；未逐页检查 PDF/图像像素。

方法（§3）：固定管线，分别改变检索、embedder、答题模型和写路径；LongMemEval-S。
结果/消融（§4）：仅换 embedder，500题47.2%→53.4%；模型家族排序不同。
Mem0对照只含有效88例、两个题型，12个API失败排除；embedding只是近似匹配。
成本只由5例pilot估计，不能当全部样本实测。p=1与宽区间不证明等价；
不同模型采用题型排序后的不同前n子集，不能假装全题型随机样本。
§4.2将188/300称为错误中的63%，分母实际是300例；不复用为错误条件率。
局限（§5）：合成对话、有限题型、单一judge、因素交互，非完整因果分解。
作者原始代码/数据未复验，本文数字不作为本库收益。

决定：采用变量隔离、匹配实例与失败分母审计，暂缓任何“某架构等价/无用”的推广。
本库任务包/全量比较需固定问题、当前更正及可用原文，再分开测试选择、编码、消费者。
统计未显著不能替代预先声明的非退化门槛；失败、跳过与成本样本必须单列。

## Fidelity Before Structure

Tao An，[Fidelity Before Structure: Verbatim Chunks Beat Lossy Artifact Extraction
in Long-Conversation LLM Memory](https://arxiv.org/html/2601.00821v4)，`2601.00821v4`，
2026-07-22。检索中的旧标题 CogCanvas 不当作本版结论。
实际阅读 HTML 正文 §§1–7、主文 Tables 1–3、Appendix D 与 L；其余附录未精读，
相关主文引用不冒充已核查附录原数据。没有 PDF 视觉审读。

方法（§3）：固定 retrieval/rerank/answer/judge，交换原文块和抽取artifact，另控graph。
主文报告（§4）：LoCoMo Cat1–3原文43.9%、artifact28.0%；LongMemEval-S为67.4%/45.4%。
控制含无graph、零重叠、匹配预算、dense-only、session抽取与句级原文；原文与artifact并存
不等于替换。局限/反例（§6）：拒答较弱，合成多跳反而利于artifact；主要为单管线、
stateless/免训练范围，端点跨批漂移。Appendix D区分存储丢失与查询未命中；
L中GraphRAG调用未计量、本地GPU边际费用记零，不能当完整系统成本证据。
未在本库复现实验，不把两篇论文不同judge/样本的绝对值互作性能比较。

决定：保留可追溯原文及有效更正，但不删除结构化MemoryLedger，也不新建共享聊天池。
账本是来源/依赖与失效审计，不是论文里取代原文的LLM抽取器；两者不可直接类比。
强制压缩时还须验证否定、量词、日期、未决异议和拒答，不能只测答案命中率。

## 现有消费路径及后续边界

只读 `record_context.record_view`：按固定源SHA返回选中及global行的原始记录，
显式声明partial；host仍须枚举全部必需记录。`task_context.task_view`保留所选TASK行和
所有非任务行，返回source_lines及遗漏数，并要求另读详情/依赖。源码未把选择称作语义完备。
因此本次未确认这两条路径需修复的生产缺陷；实际宿主选择是否齐全、消费者是否正确理解仍未知。

同一批次本次新增2篇正文，清理后已发布/本候选可恢复的新记录共5篇；旧55篇私有记录未恢复，
十篇门槛尚未重认。接下来继续正文及真实消费验证，固定可执行验收后才提出原地修复。
PID/ALIAS/role/Codex旧门禁与预算不重置，系统级未决项不结案。
本次有主控/独审AI推理，所有actor的精确provider tokens/cache/输出/费用未知，不记零；
没有另行启动被评测Agent、模型benchmark或后端任务。
