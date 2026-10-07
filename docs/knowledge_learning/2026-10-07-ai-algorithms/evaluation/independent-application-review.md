说明：这是初版/r2独立验收历史记录。文内 candidate_v1/、candidate_v2_fixedbase/、legacy_v2_fixedbase/ 等运行路径均相对 `../historical-evidence.tar.gz` 内的 validation/，不是要求存在于当前目录。当前最终结果见 [report.md](../report.md)。

# 独立 AI 算法数学与条件验收

## 结果

首版两条候选的数学与前提审阅通过。冻结12条新任务，逐题适用性/拒用/信息不足判断12/12通过；文件检索Top-3为12/12，SQLite为11/12，现有默认关联全文上下文均恢复到12/12。仍保留SQLite的1次原始漏召回，没有调整ranking、旧expected或冻结题，也没有把关联恢复说成Top-3修复。

候选仍为candidate，本验收不等于发布、真实模型质量/加速测试、自动适用性执法或形式化证明。验证者与候选作者分离；本验证者同时负责预先冻结任务与评审，未声称是额外独立模型试验。

## 冻结、范围与输入

- 先读取实际v1格式、文件/SQLite检索、show/context/refs接口，再于2026-10-07 01:03:52 UTC冻结新题；之后才收到并读取首版候选。
- 冻结任务SHA256：f9af50f1e1381f33f41348e00f4ea78059a15d05c4b92c71ca8d598bc4496061。
- 基线代码HEAD：c66b5ced2bbb15ef6d42a4c8530256b4152c94ed。
- 两候选原始JSON/MD哈希保存在candidate_v1/retrieval_results.json与application_review.json。
- 主库仅只读；脚本、副本、索引和报告均在独占validation目录。候选只在副本中将status改成published，其他元数据字段、完整正文不变。读取前后主库entries字节哈希一致。
- 未读研究作者题库或四项保留基准答案；未用GPU、未安装/运行上游、未改SGLang。

## CPU精确数学检查

check_math.py使用标准库Fraction，12个逻辑检查族首轮全部通过。循环配置是系统性边界覆盖，不作为独立统计样本累加：

- 28个三元六分母分布的784个有序目标/提议对，含504个提议有零概率的配置、28个全接受配置、36个完全不相交支撑配置；核对目标恢复、归一化、正部残差和TV恒等式。
- 729个二步条件目标/提议表对，每对检查块长1与2；额外一组非对称三token条件表完整枚举草稿、接受、拒绝校正、丢弃后缀、重启和bonus。结果与目标自回归联合分布逐项相等。
- 36种三接受事件联合分布检验一般尾和恒等式；相关/互斥反例显示边缘接受率不能替代到达前缀后的条件率。
- 独立反例覆盖实际proposal与校正q不一致、拒绝后错用目标原分布、greedy冒充随机目标、MTP仅边缘相等、树选择偏差，以及成本未知/验证成本升高/随机轮速度比/EOS或剩余预算截断。

候选特有的确定性候选消元与成本例子另用check_candidate_extras.py审查：4个补充检查族通过，其中448个分布/候选顺序配置、66个alpha/c设置各检查1–20的horizon。此部分在读候选后产生，明确不算冻结盲题。

## 关键数值边界

- p=(3/4,1/4)，报告q=(1/2,1/2)而实际top-1输出delta时，原实现输出(1,0)。换成真实proposal后校正可恢复p。
- p=(3/4,1/4)，q=(1/4,3/4)，拒绝后直接重抽p产生(5/8,3/8)，并非p。
- 三个接受事件全成/全败各1/2时，E[L]=5/2；从边缘1/2硬套几何式得到15/8，错误。
- 条件率(1/2,3/4,2/3)给E[L]=17/8；每草稿2ms、三个草稿、验证10ms、基线10ms/token的稳定成本模型给85/64倍。验证改20ms就变85/104倍，慢于基线。
- 全接受但请求只剩一个token，在仍支付16ms整轮成本时只发出一个有效token，相对10ms基线为5/8倍。EOS概率1/2、最多四token时实际期望长度15/8，不能计成4。

## 实际检索、全文与前提

使用原始冻结英文结构查询，不含定理名称；正例、错误前提、未知联合分布、greedy/tree/MTP外推和成本/停止都参与。负例允许召回相关知识，然后明确拒绝错误前提；不能把无召回作为唯一负例验收。

默认context预算8条/20000字符。两后端所有所需条目及强依赖都完整进入；部分包因其他候选超预算仍标partial，这不等于目标条目或其前提被截断。show全文、章节导航、完整requires引用闭包与check_refs均实际检查。API继续返回applicability=unchecked。

SQLite首次漏召回A12（EOS/剩余预算成本问题），Top-3含两条旧概率停止知识和残差条目，缺成本条目。既有关联导航从残差条目找到成本条目，在原预算内完整恢复。first_failure_and_recovery.json保存首次失败与恢复；没有代码或元数据修复，无须为单个冻结题过拟合。

## 来源核对与限制

独立核对了[Leviathan等ICML 2023](https://proceedings.mlr.press/v202/leviathan23a/leviathan23a.pdf)算法、接受/校正证明及成本假设，也核对[Chen等2023 v1](https://arxiv.org/pdf/2302.01318)的独立校正证明。两文p/q符号相反，本报告统一p=目标、q=提议。原文的iid与并行验证简化已与本轮一般条件尾和及实测成本要求分开。

近期论文和固定上游代码的来源真实性由另一路来源审查负责；本报告只审候选中的有限分布和成本逻辑，不认证被引用runtime。没有形式化工具证明、真实模型/GPU加速、生产吞吐或新自动停止策略。

## 复现与证据索引

- frozen_tasks.json / freeze_manifest.json：预先冻结任务与hash。
- check_math.py / math_results.json / math_first_run.log：12个精确检查族与首轮日志。
- check_candidate_extras.py / candidate_extra_results.json：读候选后的4个补充检查族。
- check_retrieval.py / candidate_v1/：两后端原始结果、完整context、show、refs和章节树。
- application_review.json：12题逐题应用/拒用/未知判断，绑定候选hash和章节。
- first_failure_and_recovery.json：原始漏召回与同一接口的上下文恢复。
- source_checks.json：原始文献的实际阅读范围。

复算数学：`python check_math.py --output replay_math.json`。副本检索运行参数见candidate_v1_run.log对应调用和check_retrieval.py帮助；需传只读repo、一个新work路径和两条候选JSON。

## 追加旧题非退化验收：首版未通过

按root要求，以同一18条published副本复跑原3套固定基线，原始查询、expected、ranking完全不变，并逐例对比16条基线。三次CLI均退出1，但判定依据是下列实际指标，非退出码：

- original，文件及SQLite：Recall@3均保持0.9523809524、context均保持1；MRR从1降到0.9285714286。physical-model的正确条目被新成本条目挤到第2名。
- round2，文件：Recall/context均保持1；MRR从0.8125降到0.7916666667。sensitivity正确条目由第2降第3。
- round2，SQLite：Recall@3从1降到0.875，MRR从0.7291666667降到0.6875；context仍1。sensitivity正确条目被新残差条目挤出Top-3。
- morphology完全不变：文件Recall/context/MRR仍为0，SQLite Recall/context仍1、MRR仍2/3。既有词干基线缺口没有算作新失败，也未隐藏。

初步原因是新alias中的宽泛“长度”和裸词residual占用了结构词通路。只报告诊断，不擅自修改候选。首版的数学/前提审查通过不等于旧题非退化门槛通过。逐题新旧结果在old_suite_comparison.json，命中字段/分路排序在old_regression_diagnosis.json。

## r2术语修订复验：旧题恢复，但新题退化

作者只修订aliases，正文与其他字段未变；r1原件保留。r2采用旧16条固定副本重建18条测试语料，有效结果位于candidate_v2_fixedbase/与legacy_v2_fixedbase/。先前candidate_v2/因主库并发新增同ID触发防覆盖检查而装配失败，其后legacy_v2/误接续输出无效，不能计验收；invalid_partial_v2_run.json记录完整原因与恢复。

r2旧3套逐题无新增退化，round2 SQLite MRR改善为0.75。但原12个新题（此时已属开发验收，不再称新盲测）文件Top-3降到9/12、context10/12；SQLite Top-3降到10/12、context11/12。A03两后端默认context均找不到新知识，A05文件后端完全无命中；A10文件Top-3未命中但关联恢复。r1_r2_new_task_comparison.json保存每题首轮/二轮对比。

因此r2不能因旧题恢复就声称全面通过。论文名称式alias删除了问题结构的检索入口；建议仅按准确、可解释的算法用途术语修订已定位的泛词冲突，仍须对所有新旧题复验，不修改runtime、原题或gold。
