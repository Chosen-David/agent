# CONTEXT-METADATA-35

Task-ID: CONTEXT-METADATA-35
Date: 2026-10-19

## Plan

基线24c892a721d0d511c0b38704ad5093fabfce5433。用户允许持续优化及验收后直推main。本轮以相同预算、顺序、完整返回和隔离为硬约束。人工GUIDE为空且只读。生产文件/mirror暂不改变；先作独立候选实验，不能把论文收益当本库收益。

候选将context的seed和related所需元数据读取与payload JSON深拷贝分开，仍运行ref、published门与完整依赖闭包；最终bundle仍用原get并深拷贝。无跨请求缓存，无摘要、压缩或预算放宽。自定义get方法（含实例hook/子类）回退原get，保留扩展行为。仅针对合法加载的JSON corpus与语义有效的records变更；任意注入不可序列化Python对象的损坏内部状态不在性能主张范围，但须独立列出行为差异，不能暗称全域等价。

历史result_store query knowledge context materialization：扫描234，partial且缺record；top5与本优化无匹配A/B。读取旧context-materialize31冻结计划、checkpoint及review，旧缓存66→65次get且未达10%，拒绝重跑同方案；本轮减少seed/related全文物化是不同候选。旧目录仅保留历史引用，不改写。知识query copy dependency graph closure返回maxflow/FlashInfer，前提不匹配，拒用。12篇既有论文矩阵复核见memory-storage-20261015/research.md，不算本轮新读12篇。新增TallyMem原文访问（2610.19474v1，2026-10-14）提示原文访问/选择/聚合各自验收，不采用其LLM编译器或宣称复现其算法。

DAG：主控冻结脚本/计划 → 独立新上下文计划审核 → 主控配对测量 → 独立代码数据检查与复跑 → 保留负结果或另立集成计划。主控唯一写TASK/脚本；reviewer只写results/context-metadata35/review.md和independent/。无tmux命令、native ReviewSession/常驻host adapter；本轮为已授权有界本地实验，不宣称受管监督服务已部署。

复用上一轮参数化计时结构：4查询matrix/量纲/attention量纲/zzqxnonexistent × limit5/20 × context/fresh=16场景，2warmup+11交错配对；每次完整输出相同，返回对象保留至stop、随后释放。context不含预建查询，fresh包括构造/校验/search/context，不清OS缓存；JSONL在配对外逐行flush。每轮timeout120s。目标matrix/5/context中位数下降至少10%；其余<=max(base*1.10,base+0.2ms)。独立tracemalloc每场景一次，candidate<=max(base*2,base+65536)。原始全部样本、绑定、输入hash、GC、CPU/affinity/clock保留，不挑样本。

最多1生产者和1独立复跑，0调参重试；计划审核最多2轮。独立六项检查implementation/reference_boundary/data_integrity/numerical_sanity/measurement_validity/reproducibility均必需。检查全部published IDs、空/重复/未知/未发布/过期snapshot、预算1/8/20及字符边界、deepcopy嵌套污染、records有效变更、custom get回退、related与context输出及异常。新主张需当前代码/数据绑定和独立验收；若阈值未过，保留原实现。不以CPU局部耗时替代LLM任务质量/成本/端到端token收益。若通过也仅可列为待集成候选，生产/mirror同步与完整回归另行冻结后发布。

## Progress

- 新独立clone，main未变；旧agent-audit-31文件保留，其git公共目录已被工作区清理，未修改历史证据。
- 候选主测与独立复跑各16场景通过冻结门槛；独立1505项语义/异常对照通过。目标6.590888→4.019058ms、10.648281→5.237379ms；共享宿主噪声明确保留，不外推。
- 第2轮独立计划审核批准integration-plan.md；只集成已测三方法，公共get不变，custom-get回退及最终深拷贝保留。新结构测试修前2失败，集成后专项8通过。
- 实际生产类对固定Git旧基线的唯一测量exit0，16场景全部过门槛；目标6.679570→3.608697ms，tracemalloc峰值116565→97034字节；fresh有负向场景，见report.md/summary.json。
- 全库1285项运行成功（8项既有环境skip），129.903s；独立集成1505项对照及243绑定通过。Reader/最终独立发布验收另见testing.log、review.md；main发布/回读完成前不把测试成功写成推送成功。
- 原计划/脚本已按字节冻结为results/context-metadata35/frozen-plan.md及frozen-benchmark.py；候选raw原路径按快照映射。大原始样本和完整日志本地保留，公开摘要不能独立复算全部样本。代码及现行脚本hash见report.md。
- 未完成：真实Agent任务质量、完整请求/模型token成本收益；无原生监督适配，不声称受管服务部署。持续任务不关闭。
- Reader3项通过；最终独立六项验收usable-with-scope，源实现与测量绑定不变。当前有界实现/测试工作完成；发布报告冻结时尚未更新远端ref，最终远端SHA/tree/关键内容由主控发布回读确认，不预填成功。
