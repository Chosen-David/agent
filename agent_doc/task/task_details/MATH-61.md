# [MATH-61] 离散二次稳定性证书与非正规瞬态

Task-ID: MATH-61
Date: 2026-10-09

## Plan

### 目标与验收
持续数学知识建设和直接main授权；补充math.discrete-lyapunov@1。固定有限维实A、Q正定、P正定；证明Schur稳定等价离散方程与P范数收缩，区分原范数瞬态。公开8个精确CPU结构算例全部通过、3个无定理名问题在file/SQLite各Top3命中、完整目标及Jordan/Hermitian强依赖context≤12000字符、53相关回归、5既有candidate字节不变。无模型/GPU/e2e/token实测，不宣称性能收益或形式化证明。

### 实现方法
EXECUTE，1800秒/最多2审核周期/2结果attempt，不部署监控。经典Boyd EE363 Winter2008-09 lecture13 slides21–25；近期Wei/Zhao/Liu arXiv2508.01410v2(2026-03-13)§III–IV原文，连续时变证书不等于离散网格证书；另筛选2603.08191v2(2026-06-13)，仅元数据/摘要，不采用未核验混沌主张。
8个fixture：正定方程/下降恒等式、非正规欧氏增长、Jordan幂、稳定边界、Q半正定不足、P半正定不足、稳定矩阵切换积发散、固定线性误差递推迁移。Fraction精确计算，不用样例证明一般定理。检索问题是公开开发结构检查，非模型未见评测；手工拒绝非LLM实测。迁移固定线性迭代可给条件式证书，逐层Jacobian/LLM反馈不直接认证。root唯一TASK作者，审核仅写独立证据。结果检索partial/scanned55，三类凸输出历史命中均不复用数据。
独立fresh plan review→produce→不同fresh verify_experiment_result→publish；相同冻结合同贯穿三个节点。绑定指南/任务/角色/知识/状态/prior。保留旧状态快照，闭环再更新live状态/镜像。只写新卡、README/coverage/state及knowledge镜像、当前结果目录、MATH-61详情/总索引。不修改生产/SGLang/guide/holdout，不新建Skill。无部署ReviewSession/远程监督，仅本地独立授权工作。发布前fresh fetch/CAS无force，远端SHA/tree核对。全局已知无关code-reading快照stale记录而不扩大修复。

## Progress

已同步clean main 582373461f692f9fa49525b1d54c26e659c25464。待独立计划审核。

独立计划approve；独立结果usable-with-scope（不同fresh上下文）。8精确公开case/6检索/9991字符完整依赖/53回归/231稳定镜像对/5candidate字节检查通过。原始记录与279artifact绑定已native登记；无模型/GPU/token/e2e/Lean/未见测试。待实际main发布后闭环。

知识/证据main提交d2d06cbf053bc90422b3f6dfcc0074df8a9af1fc，fresh fetch及ls-remote SHA/tree一致；全局无关镜像stale保留。原计划/原状态保留，现授权收尾更新live状态和总索引，未改冻结结果/验证绑定；闭环提交随后发布。

下一步：保留原post-RoPE/GPU评分包络及其他学科轮换游标。真实模型/GPU与未用测试仍缺；本卡只支持固定线性或另有域/统一度量证明的映射。生产收益未成立，不改生产行为。
