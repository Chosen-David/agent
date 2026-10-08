# 有限支持条件化与near/far质量诊断_by_gpt

日期：2026-10-08。新增 `math.support-conditioning` v1，沿用现有model-with-knowledge，学科与结构索引及离线快照同步。只报告知识/结构检查，没有模型性能提升结论。

## 真正增加的能力

为删token或过滤样本的问题补充三个判断工具：固定支持的逆向KL最优分布及正向KL无限边界；条件化可能放大误差的定量TV界；候选内归一化不能识别全局质量的严格构造。现有截断TV/输出界复用，不重复计为新知识。

near/far最小迁移：完整logit为(20,0)，候选只留下第二token。候选far占比=1，全局far质量≈2.0611536×10⁻⁹。仅候选占比不能判断全局“near已经足够”或校准层预算；需完整合法集合分母、额外全局质量估计或认证界。传感器接收率/接收内告警率给出跨领域同结构例。此数学映射保留集合与概率的关系，没有验证具体SGLang生产路径。

## 来源与近期研究

[MOIRA v1](https://arxiv.org/abs/2610.04313v1)，2026-10-03；[MassAlloc v1](https://arxiv.org/abs/2609.32712v1)，2026-09-26，均为2026-10-08核查的原始预印本。MOIRA估计覆盖与MassAlloc完整QK/归一化器分析的适用边界见 [research_by_gpt.md](research_by_gpt.md)；不复用论文实验数字为本机结果。经典讲义准确定位、推导与反例见知识卡。

## 实际验证

| 层级 | 实际证据 | 结论范围 |
|---|---|---|
| 有限数学/CPU | 1731条公开开发记录，包括1113条精确TV、99条KL分解、462条零事件拒用 | 零精确算术违例；最大float绝对误差2.22e-16；不代替一般证明 |
| 独立复核 | 全部记录重新执行；独立重叠质量TV表达、Decimal80参考及4294条额外有理数病例 | v2 usable-with-scope，见independent_review_v2.md；非Lean |
| 双检索后端 | 3个不提示定理名的问题×2后端，含传感器迁移与hard-mask拒用 | 6/6在top3、5/6在top1；显式学科过滤。仅词法/结构检查，未实测主AI应用或拒用能力 |
| 按需加载 | 仅加载新卡；正文7359 UTF8 bytes；ceil(bytes/4)=1840 | 粗略token估计，非模型计费/省token实测；元数据额外成本另计 |
| 回归 | 相关70项knowledge/index/handoff/reuse/result检查与快照一致性 | 最终记录regression_final.json；有限回归非绝对无bug保证 |

CPU生产循环0.044131秒，单次perf_counter元数据，不做速度比较。各检索命令耗时保存在retrieval_commands.json。实际knowledge_refs存published_knowledge_refs.json并check-refs通过。既有未见模型测试未使用；以上问题已公开/用于开发，不当作未来未见测试。

## 失败与协议边界

初次计划缺共享合同和固定阈值被独立审查退回，v1及review保留。初次实验manifest空seeds不符合当前结果协议，保存为v1 invalid；revision3显式采用未使用的确定性枚举标记0，重新生成v2并独立复验。初次回归插件快照缺新卡，已用现有sync脚本修复并复测，旧失败保留。

独立审查由宿主新上下文执行，未部署Engine/ReviewSession/tmux服务。无trusted runtime verifier时CLI的pending如实保存在runtime_inspection_without_provider.json；人工宿主scope验收不能冒充已认证Engine回执。原始JSON的完整记录以gzip无损归档，不把摘要冒充全量数据。

## 未成立的迁移、限制和续接

不能由逆向KL最优推出value输出/e2e最优；不能由估计页面覆盖推出逐query头的认证下界；不能由本轮CPU例推出逐层α/β/γ优于统一参数。没有真实trace、GPU、模型A/B或省token证据，故不修改生产策略，更不修改SGLang。

下一步保留已有频率支持/残差外包及其他学科游标：在冻结真实trace上分别记录候选条件占比、全局mass估计偏差和遗漏质量，再以同模型、实际读写量及完整系统成本对齐比较层预算策略。按既有授权验证后直接main发布；发布前重新同步、非强推及远端读回，提交状态在最终回报与任务进度记录。
