# LEXICAL-EMPTY-23：无有效词查询的精确快路径

基线33ff30a0e068c4ad6e17cb6bf18a79b041fdef11；实际入口为knowledge CLI search/context
到KnowledgeStore.search，源码agent_runtime/knowledge.py:220–230，同步独立插件副本。
115条当前语料。标点、emoji或当前分词器不识别的文字可满足非空字符串校验却得到空词集。
旧实现仍对每条符合过滤条件的记录六个字段分词，交集恒空。新实现保留query和limit校验顺序及分词规则，
空词时返回原有信封和独立空列表；不缓存、不改变正常排序或过滤、不扩展语言支持。

修前新增3测试中6子场景失败（默认661次、include_unpublished=True时691次分词，而非1次），其余校验/NFKC检查通过；修后3项通过。
before.log/after.log保留原始输出。此前SQLite已有空词处理，本次只修文件路径。

## 主测（独立验收另见independent-review.md）

固定PYTHONHASHSEED=0，从git载入原模块，双方调用完整search；排除store加载。
一对warmup后7个交替AB/BA对，每个样本5次。输出完整JSON相等，样本不剔除。
主测期间有一次约0.16秒历史结果只读查询；无法排除外部调度竞争，正常查询波动不解释为收益。

| 查询 | 基线中位ms | 修改后中位ms |
|---|---:|---:|
| !!! | 60.327336 | 0.0031882 |
| 🙂 | 56.631497 | 0.0034588 |
| Ω | 54.8254904 | 0.0032952 |
| memory retrieval | 55.3984616 | 55.8371798 |
| low rank | 56.5662608 | 55.9615034 |
| 量纲 | 76.5144412 | 74.9035256 |
| topk | 88.1805328 | 81.8050568 |
| zzqxnonexistent | 74.1287432 | 71.8212536 |
| ＡＢＣ | 66.5610524 | 63.7556544 |

前三类通过预定50%下降门槛；其他通过max(1.15×baseline,baseline+0.5ms)非退化门槛。
主张仅限热store空词查询消除扫描，正常查询没有可靠提速主张。
不包含CLI初始化、端到端LLM请求、模型质量、token费用或GPU收益；峰值内存未测。

Python3.12.14/Clang22.1.3，Linux6.18.55 x86_64 CPU；无模型/API调用。
原始raw.jsonl包含全部63对、输出hash和环境；输入hash
12fcebdf5958212b900ee5938126b01e0889fb24e2654fcd0a8b27f1b4bd32b9；
两份生产文件SHA256均为2ac2a75bd06f3b420e937e9185b0f5ad70592205a91d7fd231fab4fdb2d89391。
历史实测不覆盖此次优化，保留原报告不改数值。复现：
`PYTHONHASHSEED=0 python scripts/benchmark_knowledge_empty_query.py`。

## 审核与边界

独立人工计划审核已批准TASK/详情/runner：初次缺TASK索引，补齐后回读通过。
任务详情初始SHA256为20c251c9f4fd26bcf88895a1d1d3968f5c40b9eafe28c2c5a572ab2391fa3d89，
runner为5364a4253b2a851bc65a6de809d2eb54fa2e42c78a97700e358349ea2e1eb8a5。
手工独立验收，不是原生ReviewSession或已安装tmux监督器。

独立六项验收usable-with-scope；144组边界差分通过。独立三个空词查询基线
59.50/65.22/63.32ms，候选0.00316/0.00367/0.00337ms，九查询均通过原阈值。
全库1276测试（8跳过），Reader3通过，文档validate通过。原始短日志见full.log/reader.log。
注册记录仅用于可检索的历史引用，不伪造原生验证证明；验收依据为独立人工报告。
