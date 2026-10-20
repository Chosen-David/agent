# 本轮 Agent infra 精读与适用性

任务 MEM-INDEX-96；2026-10-20。完整原始来源通过网页正文读取，以下为定向精读范围，不宣称通读所有附录。历史12篇研究仍见 memory-storage-20261015/research.md，本轮不重复引用其收益数字。

| 原始来源 / 阅读范围 | 方法与实验核对 | 本库取舍 |
| --- | --- | --- |
| [MemGPT v2](https://arxiv.org/html/2310.08560v2)，§2.1–2.4、§3.1实现与DMR设置 | 主上下文与外部记忆分层；外部原始消息可重新载入，检索分页以限制上下文；DMR使用MSC前五会话生成第六会话问题，模型/评判器设置影响质量结论。 | adapt：显式目录分页、正文按需校验；不做递归有损摘要，也不把paper QA数字记成本库效果。 |
| [LongMemEval v2](https://arxiv.org/html/2410.10813v2)，§3.2–3.4、§4.1–4.2 | 区分索引、检索、阅读；更新和拒答是独立能力；证据会话由LLM生成并经人工筛选，商业系统实验限2024年8月、抽样97问题；摘要/事实抽取可能损失细节。 | adapt：保留完整原文/来源/依赖，index不授信，更新后旧cursor失效；目录字节实验不等于长期QA验证。 |
| [KVFlow v1](https://arxiv.org/html/2507.07400v1)，§2、§3.1–3.3、§4.1 | 固定prefix和动态suffix区别；Step Graph用于未来使用距离，prefetch还需loading/offloading状态；十agent合成实验有warmup且刻意制造显存压力，A10G与H100/PCIe配置不同。 | defer：本库当前没有本轮可用tensor cache adapter，不能用SQLite/文本哈希冒称prefill命中。只借鉴来源身份和ready状态需明确，不改任何SGLang代码/部署。 |

真实调用链：`project_memory.main(list)` → `MemoryLedger.list` → `_get/_read_entry` → SQLite完整条目，CLI默认pretty JSON。`Mailbox.prepare_context` → `basis_context` → `check_handoff_basis` / `MemoryLedger.check`，已存在current-context hints及完整依赖校验；磁盘曾读过不等于当前模型仍持有。新index只服务导航，继续由后者决定证据是否可用。

存储分层：`.agent-memory/memory.sqlite3` 为私有事实/更正账本；`.knowledge-cache`索引可重建；`agent_doc/results/<run_id>`是冻结原始验证材料。不能因为旧/大就删结果或记忆。本轮只读统计逻辑页与空闲页，不执行VACUUM、删cache或后台维护。按需分页不新增一份持久摘要，避免新的失效与归属问题。

知识复用实际入口：安装 `model-with-knowledge/scripts/knowledge.py` 的search与show；`infra.pagedattention-kv`正文及knowledge_refs保存在 knowledge-read.json。匹配：分层存储问题；不匹配：A100/OPT/LLaMA/服务队列/真实KV与本轮SQLite CLI。拒用GPU数值和性能保证。本轮为原创标准库CLI扩展，无抽取上游代码/API或新增依赖。

限制：目录不做语义排序，消费者需按scope/来源/依赖选正文；完整阅读可能完全没有输出收益。每页仍需完整list与快照重算，不主张数据库读取/CPU速度或大库可扩展性提升。无真实tokenizer/服务端用量时token、收费、LLM任务质量/TTFT均unknown，不增加success_count。
