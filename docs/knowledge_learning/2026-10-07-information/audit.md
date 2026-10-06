# 实际入口与消费者审计

读取prompts/orchestrator.md“基础知识按需建模”、config/role_registry.json中的model-with-knowledge，以及agent_runtime/knowledge.py的context、agent_runtime/project_memory.py的_check和项目记忆工作流。链路仍是主AI→现有Skill→摘要检索→show/context→knowledge_refs；本轮只同步知识快照，不写新Skill。

context以完整条目/前置包选择，超预算显式skipped/partial，applicability=unchecked；预算单位是序列化字符，不是token。它没有验证任务后验相等，不能称信息论无损。MemoryLedger复查引用active及依赖，工作流要求压缩保留有效纠错/来源/约束；这些身份门禁不验证自然语言摘要充分性。未声明引用的旧任务也不能自动保证。

|理论前提|当前消费者证据|判断|
|---|---|---|
|明确X/Y/T及分布|有任务文本、条目及身份，无总体目标联合分布|不足以认证MI或Bayes风险|
|同一核或Markov结构|外部来源、查询与工具可增加信息|必须条件化或扩展输入|
|后验一致/充分性|context仅预算选择，记忆门禁仅状态身份|没有充分性证明|
|同模型同工具预算对照|本轮没有模型运行|不宣称Agent收益|

合成迁移：X=(U,V)，Y=两条件异或（或双传感器恰有一个故障）；同1bit输出预算比较任务摘要与只留U。此映射只保留给定逻辑/概率，不代表真实授权/物理故障服从独立公平bit。不能直接改主AI摘要或放行。
