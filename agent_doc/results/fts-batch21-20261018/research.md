# FTS-BATCH-21：研究、候选和证据边界

2026-10-18；基线8cf78b709f49e4ecaa3030b57a341940c3f780a1。
沿用本项目已验证实现技能和Python/SQLite工具，不另装依赖。

本次复用并重读 [12篇方法细读矩阵](../memory-storage-20261015/research.md)。
它覆盖LongMemEval、A-MEM、Mem0、MemGPT、Zep、PagedAttention、SGLang、
CacheBlend、KVFlow、LMCache、RAGCache、ObjectCache的机制、条件、实验与取舍。
这不是本轮新读12篇的声明，也不证明本轮SQLite候选有收益。

本轮重新访问 [MemScope 2610.21170v1](https://arxiv.org/html/2610.21170v1)
（2026-10-15预印本），读取§3.3–4诊断/局部修改/配对实验及消融。
应用其“原始状态+当前实现定位、约束局部改动、保留失败”的评估原则：
只改索引删除，不换检索器，不覆盖原文；基线与候选从同一DB种子开始。
论文的任务准确率不移植到本库；我们没有部署它的Patch Agent或训练新模型。
注意论文的执行准确率与修补成本不是同一个指标。

另读取 [Persistent Memory in Multi-Agent LLM Inference 2610.07782v1](https://arxiv.org/html/2610.07782v1)
（2026-10-06预印本）§1–5前半的架构、独立条件、零结果与组件执行检测。
只作为评估补充，不计入本轮全文细读：索引构建局部收益不能冒充Agent质量、
模型推理速度、KV显存或token费用改善。其独立题目消融不足以检验跨会话记忆的
局限不适用于此处精确SQL差分，但提醒未来真实任务评测需要共享状态任务。

[SQLite FTS5官方文档§4.1](https://sqlite.org/fts5.html#the_unindexed_column_option)
确认UNINDEXED内容不进入FTS索引。代码的id为UNINDEXED，不能用正文MATCH代替
精确身份删除。扫描成本仍需本机实测，不以文档一句话替代profiling。

## 候选比较

| 候选 | 兼容性与成本 | 决定 |
| --- | --- | --- |
| 现有逐ID DELETE | 精确，事务已有；m个ID对N行重复筛选 | 固定强可运行基线，同SQLite |
| 最多128个ID IN批次 | 不改schema，绑定值，全部删除后按原顺序插入 | 本轮唯一实现候选 |
| rowid映射/外部content表 | 可少扫描，但需要schema迁移与额外维护 | 本轮不引入 |
| 全量重建 | 少扫描但改变rowid/更新成本及增量契约 | 不作为等价替换 |

这是常规集合化SQL的工程适配，不声称提出新算法。原型为批量成员筛选；
扫描次数结构上从m轮变为ceil(m/128)轮，实际SQLite执行细节和删除/分词/插入
总成本由同机完整build_index计时检查。额外ID列表为O(m)，单SQL占位符至多128；
没有新增线程池或GPU。候选不减少需要处理的原始文本、不扩大检索预算。

实际入口：agent_runtime/knowledge.py index命令调用build_index，
模型知识Skill的镜像CLI具有同一路由。schema/ENGINE_VERSION保持原值；
两份实现逐字节相同。脚本装载固定git对象作为基线，依赖文件须与该基线一致。

## 待检验与范围

冻结条件见task_details/FTS-BATCH-21.md；每场景完整计时包括连接、事务、
旧记录读取、删除、分词、插入及commit，不含双方等价的语料准备和DB复制。
无GPU、真实LLM调用、任务QA或计费测量。数据库字节不要求一致；逻辑表含rowid、
返回字段及检索JSON要求一致。不同物理FTS段布局不是检索语义改变。
只有所有门槛通过并独立验收后才允许性能发布；负结果必须保留。
