# RESULT-TIME-97 固定计划

日期2026-10-20，基线50c1ca1e74df1026ba05b4cfd53903605315b234。
目标：结果记录时间UTC越界不得中断整个search；正常日期、排序、原文件及信任语义不变。
已观察_timestamp对0001-01-01T00:00:00+01:00和9999-12-31T23:59:59-01:00抛OverflowError。
这里只是只读诊断；正式API/CLI修前测试在计划审查后执行。

## 方法与范围

仅在_timestamp的astimezone调用处将OverflowError转换为ResultStoreError并保留cause。
拒绝给search加泛OverflowError捕获：自定义show/其他逻辑的异常必须继续传播。
不裁剪日期、不替换时区、不新增依赖、不改JSON/排名/配额或其他仓库。
源码、tests、本文及TASK归主控；独立审查只写本目录independent*。
有界任务依赖：独立计划审核→修前测试→局部修复/回归→独立结果验收→主控发布。
无tmux/ManagedEngine宿主适配器，不创建监控，不声称受管DAG已经部署。

## 历史与研究

实际结果CLI查询'result search context metadata malformed validation'，limit3/max_scan200：
scanned199/partial=true，候选advice-context-20261009、combined-corpus-v4-20261007、
advice-link-20261010；均不对应日期边界，不复用测量。SEARCH-DEPTH-93窄来源隔离仅作设计参考。
知识CLI 'validation finite numeric input'命中Fano/有限菜单/高斯投影，不适用于datetime拒绝，不采用。
已有十篇原文阅读记录read-boundary56/research_a.md及research_b.md本轮重读，非十篇新阅读。
沿用AgentChaos真实触发+正常对照原则，Python3.12官方datetime文档为直接API依据。

## 六项验收与预算

implementation：检查_timestamp与show/search/register_history/CLI真实调用；仅转换来源明确的UTC溢出。
reference_boundary：上下极值及相邻可表示日期；两时间字段；正常邻居、全坏、no-hit；自定义show异常传播。
data_integrity：真实临时文件、固定输入/代码hash、修前失败日志；记录字段和文件字节保持。
numerical_sanity：非法UTC不接受；合法转换与标准库一致，拒绝/隔离计数准确。
measurement_validity：指标仅故障隔离及正常对照通过数；不声称速度/模型提升，计时N/A。
reproducibility：普通/-O专项、独立基线配对；必要全库及Reader回归。
本机CPU合成文件，最多1轮实现和1次修订；不使用模型API/GPU/远端服务。
通过独立检查后显式暂存本任务文件，发布前fetch，普通main推送或连接GitHub原子CAS；远端回读树和代码。
