# DAG 成员检查优化候选 v1

基线 main6886c3ff3f4c5238d733d9da9ac349933f3020de。授权范围是Agent同接口可逆优化，排除SGLang、guide、外部宿主部署。上一full候选不复用、不重新测试。历史10篇核心精读+近期期文献包括ReliabilityBench、OrchestraBench、Recova：采用明确入口/冻结负例/成本分层；不将论文数据或阅读量当本库收益。AGENTS要求独立计划和数据复核，本次宿主review不冒充ManagedEngine接口部署。

候选 core.validate 当前逐条dependency在list ids做线性成员检查；构建已用于唯一性检查的set并复用于exact builtin str依赖。非exact str仍走原list membership，不扩大拒绝语义或改变非法依赖异常。保留全部字段检查顺序、重复ID/unknown/cycle错误、packed最终JSON验证。仅优化成员检查O(E*V)→exact str期望O(E)，cycle checking仍现有复杂度，不宣称整个validator线性。

工作负载：1节点小plan、512节点每节点依赖之前最多32节点的DAG、1000节点每节点依赖之前全部节点的DAG。数据公开合成；只测公开validate全部逻辑，不测Store/tick/LLM/e2e。2warmup+7交错配对，每样本小plan1000次、大plan1次。冻结门：两大plan中位耗时至少降10%；小plan不得退化超过10%；任一门失败拒绝不调阈值或重跑碰运气。总CPU有界120s，不绑定CPU、不占GPU，噪声如实记录。正确性：所有3节点有向图(512)、重复依赖/未知/非法类型、字段缺失、Unicode/空/重复id、self cycle、非拓扑顺序；比较exception type/message与input不变，普通/-O检查。若现有suite发现新的failure则保留，停止晋升。

生产者root → 独立代码/输入/原始结果验证 → publication可选。当前论文和性能数不能证明实际工作负载频次或收益；仅在合成入口CPU结论门通过时发布。代码变动后定向runtime和全库/Reader适用检查，fetch确认并发，再普通nonforce主分支发布及远端回读；无有效完整验收不推。只写本候选结果目录、core.py和必要边界测试，不写其他未提交研究目录。

先前检索 DAG validation dependency membership 有界250(实际199目录)缺record使partial，候选不是本次同workload验证，无可复用CPU收益。正式检索输出另保存。不宣称所有历史证据查全。
