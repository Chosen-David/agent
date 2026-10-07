# 最新74→76条知识整合补验

本轮只补验新合并基线的知识检索与引用，不改知识卡、旧74文件证据或运行时，不重做已接受的来源/数学审查，也不重复父任务全仓测试。统一发布仍须最终独立验收和父任务汇总完成。

## 基线与范围

- 实际已发布基线：`18e0904c9e2b9343cf7163bd2cb38cb14c362ec6`，74条。
- 当前候选：76条；原148个条目文件逐字节保留，仅新增原先已接受的两卡四文件，其哈希未变。
- 基线快照：`aa155523ba0ccc3560d3569f6d07bd5d7acb15a07de6147fd90fa56840b3e952`。
- 当前快照：`71ddbb92417e50b326d50ccd85607fffa95f6eed7531f7c043d010c0e120b8d0`。
- 检索/知识源码、运行前后哈希及catalog身份见 [source-corpus-checks.json](source-corpus-checks.json)。`knowledge_index.py` 只有写路径保护导入及 `_connect` 写连接前置检查，排名与查询函数未变；本报告不代替写保护全部路径验收。

先实际查询当前 `doc/results/`，找到原AIK历史记录，保留原记录SHA和unchecked状态：[prior-result-search.json](prior-result-search.json)。选择 `verify_delta`：已审数学卡内容相同可保留旧来源身份，但74→76语料与41/48条历史语料不同，旧检索结果不能充当当前验收。

读取保留策略后，先检查条目JSON来源元数据，没有与四个保留目标的DOI/URL重合，再加载允许的知识语料。没有查阅保留目标论文、答案或外部新来源。

## 原有四套查询：零新增退化

原始查询、gold、Top-3和8条/20,000字符预算不变。四套共36题×两后端，即72个逐题比较，Recall@3、context recall、MRR及无命中判断均无新增退化。[完整比较](legacy-comparison.json)

新基线自身的缺口原样保留，不归因于这两张卡，也不说旧评测全部通过：

| 原有集合 | 文件Recall@3/context | SQLite Recall@3/context |
|---|---|---|
| original | 17/21；6/7 | 17/21；6/7 |
| round2 | 0.75；0.75 | 0.75；0.875 |
| morphology | 0；0 | 0.5；0.75 |
| engineering | 1；1 | 1；1 |

这些是既有评测的平均指标；每题和MRR也逐项比较，不能以平均值相等替代逐题验收。

## 12条冻结开发题：当前结果

冻结题SHA256仍为 `f9af50f1e1381f33f41348e00f4ea78059a15d05c4b92c71ca8d598bc4496061`。此次复跑是开发/回归，不是未见任务。默认8条/20,000序列化字符，完整前提与强依赖不截断。

| 模式 | 文件Top-3 | 文件context | SQLite Top-3 | SQLite context |
|---|---:|---:|---:|---:|
| 默认全库 | 9/12 | 11/12 | 7/12 | 10/12 |
| 明确领域筛选 | 11/12 | 12/12 | 11/12 | 11/12 |

因此当前默认context是21/24、领域筛选23/24。历史48条默认22/24、41条领域24/24仍保留为当时事实，不可描述当前76条库。[默认结果](default-current.json)、[领域结果](domain-current.json)

默认文件A12在新增代数卡等种子/依赖之后，成本卡完整包超预算；SQLite默认仍缺A03、A12，领域筛选仍缺A12。所有失败和跳过原因保留，没有提高预算、削弱gold或修改上游RL/代数知识。

## 明确人工相关性选择后的可用恢复

对已知三个默认缺口，实际调用原有search/related/context，并核对show全文与完整refs：

- 文件A12：同一查询已返回正确性卡；明确排除无关种子后，从其关系读取成本卡。
- SQLite A03：同一查询已有相关经验案例；明确选择它，再通过正常关联读取两张推导卡。
- SQLite A12：先以相同查询限定 `ai-algorithms`，再明确选择已召回的正确性卡，排除不相关RL训练条目，读取关联成本卡。

三种聚焦包全部恢复，最多14,118/20,000字符，全文未改且依赖闭包校验通过。[恢复证据](manual-recovery.json)、[复算脚本](verify_manual_recovery.py)

这需要明确的相关性判断，不是自动检索已修好，更不将已知题恢复当盲测。脚本记录这些固定操作，是复核证据，不是新生产检索策略。

## 验收状态与复现

本生产检查已完成，交由独立整体验收者确认范围与原始数据；父任务负责全局回归、最终同步及全部完成后统一发布。没有fetch、sync、commit或push，没有设备性能/形式化证明/默认全成功声明。

复现旧集比较：把固定 `18e0904...` 的 `knowledge/` 用只读 `git archive` 解到新的隔离目录，再执行既有 `docs/knowledge_learning/2026-10-07-ai-algorithms/compare_retrieval.py`，传 `--baseline 隔离目录/knowledge --candidate knowledge --repo "$PWD" --out 新输出目录`。

复现新题仍使用该历史目录中的 `check_domain_recovery.py`、`evaluation/frozen_tasks.json`；分别增加/省略 `--unscoped`。两个默认退出1均由保留的context缺口产生，不能改报为执行错误或成功。明确选择恢复用本目录 `verify_manual_recovery.py --repo "$PWD" --corpus knowledge --cases docs/knowledge_learning/2026-10-07-ai-algorithms/evaluation/frozen_tasks.json --output 新结果.json`。

公开副本仅替换私有路径前缀；数值、查询、gold与失败状态未改。[转换记录](publication-transformations.json)、[结构化摘要](summary.json)及文件清单保留可核验哈希。原始输出在独立工作目录保存，不覆盖旧轮次。
