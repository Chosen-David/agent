# MATH-76：不精确凝聚的残差核验

2026-10-10；既有 `candidate.singular-boundary-condensation@2` 的不可覆盖补充，与@1共同读取。新增的是原系统残差、边界误差及固定线性消费者的可复核推导，未增加生产求解器或多机调度性能。

- 近似内部求解时，边界块残差r_K与精确凝聚残差相差BᵀA⁻¹r_I。完整残差必须按原H/h/坐标核对；零reduced残差可能交付错误解。
- 指定线性目标可用对偶身份认证；近似对偶必须计其自身缺陷。一个目标正确不等于全解正确。逆范数需要有效上界，小残差、预处理缩放或因子误差不能代替前提。
- 严格迁移到接地电路线性电压观测，核对S/V/A/Ω单位；浮动gauge、非线性功率目标、跨worker内部耦合等拒用。

完整推导及六个公开手算情境：[补充说明](../../advice/MATH-76-condensation-residual_by_gpt.md)。全部是开发/教学材料，不是CPU、模型成功率、形式化证明或未见测试。没有matched模型/GPU/多机/同预算Agent A/B，没有值得直接采用的性能改进。

实际历史搜索scanned123、partial=true、41条缺记录错误（含@1报告目录没有record）。初稿误沿用上轮122，普通Plan初审revise后已修正并保存原反馈/两版Plan；未冒充检索完整或复用独立科学数据。@1报告仅作为已读解析背景。真实知识查询和两张必要条目全文/完整knowledge_refs保存在本目录；candidate导航只在navigation.json，未接入canonical搜索。

经典Netlib LAPACK1999两节来源核查区分后向/前向误差及估计器。近期Carrica等arXiv2601.08082v3，2026-05-29；检索2026-10-10，选择性读取HTML方法和结果/限制，未核实正式发表。作者单卡评价与大动态范围导致Schur补失去正定的案例用于研究筛选，不移用速度数字；原文的因子误差指标不是本项目每个rhs的目标误差证书。来源/阅读范围见sources.json。

审核为普通独立文档审核，非可信ReviewSession或result_verifier。初审原文见plan_review.md；最终综合审核状态以document_review.md为准。没有恢复MATH65、提高旧预算或覆盖其失败。guide、SGLang、Skill/runtime、canonical条目/计数/游标及@1原字节保持；本轮TASK/coverage/history仅追加。

下一步defer真实求解器迁移：先固定原矩阵/h/partition/单位/观测c及认证浮点残差界，可信宿主审核允许后，同硬件比较完整solve与condense/recover，核对目标误差是否包含参考解差值，并把构建、对偶solve、通信与认证成本计入总耗时。缺证据则保持候选。普通手算例不构成性能或模型能力收益。

按既有授权普通main提交，无PR；同步后核对远端SHA/父/树和全部变更字节，具体已核验commit以最终回复及远端读回为准。成本见cost.json；token与收费未知，不用字符量代替token。
