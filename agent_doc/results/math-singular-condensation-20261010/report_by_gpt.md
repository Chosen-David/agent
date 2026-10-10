# MATH-75：奇异块消元与边界压缩

2026-10-10；文档候选 `candidate.singular-boundary-condensation@1`。本轮增加的是可复核的前提与拒用推导；尚未增加实际主AI控制器、模型或多机任务编排性能。

- 奇异块不能只把逆替换成伪逆。固定边界y时须核对 `f−By∈range(A)`；对所有y可用须核对内部源与耦合矩阵的像空间条件。否则能量可无下界或线性系统不相容。
- 电路/固定线性科学求解能精确保留边界响应；内部注入必须带上仿射偏置，浮动电位必须检查gauge与总注入平衡。电导二次型为耗散功率，不是储能。
- 消元可把星形图变成完全图。变量数减少不意味着数据或通信减少。多worker局部凝聚只有在内部块真独立时才能直接相加；边界D只装配一次，跨内部边不能省略。
- 同partition的全矩阵谱能量夹逼能继承到精确边界能量，不能用几个向量测试、entrywise误差或不同rhs冒充该前提。

## 证据与实际验证

[候选推导与8个公开手算情境](../../advice/MATH-75-singular-condensation_by_gpt.md)；[普通独立Plan审核与一次纠错](plan_review.md)；[不同上下文文档复核](document_review.md)。初稿误写历史扫描121，实际122；已修正并保留原/新版Plan快照，未把原Plan追记为通过。

独立文档复核approve，核对一般证明、8个公开解析例、物理单位、源项与图/分块反例、Higham原作者Theorem1、PMLR正式书目。整体系统向量记u=(x,y)的非阻断记号澄清写在review记录；候选保持已审核原hash。

实际知识工具检索并读取两张必要卡，见knowledge_search.json、两张entry快照及knowledge_use.json；真实历史结果检索扫描122，partial=true且缺记录，3个命中是corpus release，不复用科学数据；不声称查遍或模型能自动选卡。候选双索引见navigation.json；这只是按需文档导航，没有晋升canonical检索语料或新增Skill。

经典：Higham，作者网页2023-06-01/显示更新06-06，Generalized Schur Complement/Theorem1。近期：Wang等ICML2025/PMLR267正式论文记录，62172–62221，检索2026-10-10；只读官方摘要，两个PDF入口获取失败。论文批量边界矩阵/GPU运算是作者方案筛选，不复现或移用其速度数字。完整来源/查询/读取范围见sources.json。

本轮没有CPU数值稳定性实验、Lean、模型检索/拒用实测、GPU、实际通信/字节计量或同预算Agent A/B；没有读取未见测试。普通独立文档审核不是可信ReviewSession/result_verifier。结构/哈希检查结果见preservation_check.json；它们不证明算法性能或模型可靠性。

## 状态与下一步

TASK登记MATH-75文档scope，学科缺口追加到linear-algebra/numerical-analysis/physics，持续history追加；canonical110已发布/5candidate计数、原完成/尝试/GPU游标以及MATH65失败、预算耗尽和blocked状态保持不变。未修改SGLang、guide、runtime或Skill。

生产采用defer。真正科研求解迁移须先固定matrix、partition、source/gauge、误差口径与完整原文，经过可信Plan/独立结果门禁，再同硬件比较完整solve与凝聚：边界响应、内部恢复、构建与多rhs重用成本、通信字节、峰值内存及总时间。共享子空间或attention不能只靠near/far类比迁移。本轮没有值得直接采用的性能改进。

按既有授权直接main，无PR；发布前重新同步并检查并发，发布后核对远端SHA、父提交与树。发布成功的准确commit以本轮最终回复及远端readback为准，不把未提交/未核对状态写成已完成。成本见cost.json，token/收费未知。
