# 条件次高斯正态混合边界：本轮验收

稳定任务RP-T-20261008-1515，start_sha=b93e66c6f65cbc3a82c14472b9f657d8a38279d2；预算截至2026-10-08 15:57UTC。仅一项知识，零GPU/付费；未修改SGLang、人类guide、保留集答案或检索实现。科学/冻结任务验收已通过，最终独立全局评审与发布回执另见对应文件。

## 缺口与精确范围

新增math.normal-mixture-boundary v1。已有Freedman只给固定方差预算，betting卡给有界下注，alpha-spending给逐次预算；新卡给条件次高斯MGF假设下固定Gaussian mixture的闭式双侧时间一致边界，明确方差代理并非仅真实/经验方差。完整平方配方、Tonelli与有限截断停止证明自包含，requires=[]；旧卡仅related导航。无新定理/形式化/模型/GPU收益声明。

固定公开arXiv1810.08240v9，来源/独立阅读范围见sources.json和source-review.*。页面许可标签可读，独立license条款链接和PDF字节未获取；未复制原论文/代码/图，不声称新版或正式刊物字节一致。公开holdout元数据在选题前读过；四项保留范围均不涉及本条标量理论，未读取目标答案。

独立原证据审核发现首稿“蕴含条件零均值”可能被误读为无条件L1：随机有限代理不确保E|D|有限。已删除该非必要推断并明确本条非负指数证明的适用范围，candidate-initial与repair-history保留原字节。主定理/数值脚本没有变化，修订后获得derivation-reviewed，非formal。

## 实际验证

14项CPU开发检查：70位边界反演核对、数值Gaussian积分与闭式比较、合法可预测幅度树、256步首次越界精确整数路径计数、单位缩放及拒用/非法输入。256步公平随机游走结果0.018629229197864933≤.05；独立审核80位复核全部格点边界，最近整数距离约.0017285。有限路径计数不证明无限时间定理，后者由独立审读的解析推导支撑。

独立新用例在候选读取前冻结（cases SHA6120eb62238f9f66f42d25dd2e6ec8e5e8fbdbeee470c641fd80a681724f3613）。9个科学情形、9项机器检查和6条双语top5检索通过；原隔离run1、措辞修订run2、canonical run3均保留。支持root选择的脚本修订保留旧源码，未改冻结query/预期。新检索是独立编写的小型合成用例，不是LLM/真实模型效果。引用闭包、stale hash拒绝与自包含无强依赖已验收。

## 完整基线与候选回归

baseline及candidate均实际运行validate、sync、sync-check、持久index、原/round2 accept-context、morphology sqlite-required、全tests和Reader。两阶段全tests各852项：851通过、1真实tmux opt-in跳过；Reader各3/3。格式/同步/索引/diff为0。原/round2默认context3及补充context8、morphology共5个评估命令仍退出1；继承失败没有重标为通过，历史.95238不作为本轮实测值。

76个匹配suite/backend/query/context设置的比较，raw Recall@3、MRR、context recall和no-hit均无退化（含拒答）；它们是重叠回归组合，不是76个独立未见任务。所有逐query耗时/原始排名保留，均值不代替逐query门槛。默认context3：original两后端raw=.8095238095；round2两后端raw=.75；morphology files=0/sqlite=.75；全部与同步基线一致。旧english-alias/sqlite仍命中并排名1。

## 并发整合与保留

途中远端31e6b94完成MATH-51文档收尾，仅修改该任务、publication receipt与learning_state。已快进并把本轮追加记录重放在远端新状态之上；MATH-51完成标记、新open question、last_completed_round及其他领域队列均保留。本候选corpus snapshot仍d43e482d0207eb792941eb07c8b39203d6de93fcc049f8c36e74a26a2f97073f，源代码/eval/holdout未变。受影响的sync/validate/index/refs复核记录在postintegration.json；不把无关全套重跑当质量证明。

旧neuro的3/3审核lineage缺失阻塞未恢复、不重试；旧Freedman与首节别名v4不重做，失败all-sectionv3和既有绝对检索失败原样保留。数学T19–T23未改。正式库当前100published/3candidate，插件镜像同步。无运行时tmux/supervisor部署声明。实际提交、普通push、远端SHA/内容与CI可见性以publication回执和最终交付为准。
