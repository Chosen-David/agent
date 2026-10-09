# [MATH-58] 突发服务包络与任务队列边界

Task-ID: MATH-58
Date: 2026-10-09

## Plan

用户持续基础知识建设授权；PROJECT_ROOT 为 agent，禁止修改 SGLang、人类 guide、生产运行时或新增 Skill。本轮文档限定候选 candidate.burst-service-envelope@1，经典来源为 Le Boudec/Thiran 作者教材 §§1.3–1.4，近期筛选 arXiv:2609.03335v1。给出累计工作量、到达/服务曲线、积压与虚拟延迟证明，映射受保留服务的任务队列，拒绝把均值吞吐和预测当保证。不新增 published 卡，不生成实验数据；解析算例、无定理名问题、跨领域与前提反例都是公开开发材料，未见模型/GPU测试延期。独立新上下文计划审核和不同上下文文档审核后提交 main；不冒充 ReviewSession/实验认证。预算 900 秒，最多 2 个审核周期；先前查询 incomplete 不当完整历史无命中。next_topic 保留。


精确模型与验收：连续流体 A,D≥0 非递减，A(0)=D(0)=0、D≤A、同一工作单位、无丢弃；所有区间 A(t)−A(s)≤α(t−s)，α(0)=0、α(h)=σ+ρh(h>0)；所有 t 的 D(t)≥inf_{0≤s≤t}{A(s)+R(t−s−T)_+}。σ,T≥0、R>0、0≤ρ≤R 时独立推导垂直差与虚拟延迟（等价水平差）界 B≤σ+ρT、W≤T+σ/R；初始积压另计，FIFO 才转成逐任务完成保证。文档审核必须逐项检查量词、卷积证明、单位算例、边界、删除前提的反例与来源/自己的推导分离；近期研究可判不适用或未验证，不预设收益。

## Progress

- 从最新 main 3efd311 恢复 clean checkout，读取 TASK、角色、索引、状态和现有 Skill/治理；未找到同主题 active 登记。历史查询 scanned=52 有缺失记录，知识检索命中调度卡但非服务曲线定理。结果目录保存真实输出。无部署监控、GPU、模型测量，token 未计量。

- 独立计划审核 cycle1 revise 后 cycle2 approve；完整反馈存结果目录。git diff --check 无输出。项目级 project_docs validate 失败于既有详情稳定节格式（WRITE-EVIDENCE-20261009-01 无 Plan；KERNEL-FEEDBACK-01、ORCH-PAR-01 多处 Plan），本轮未改这些文件；MATH-58 自身一个 Plan/Progress。不是数学或运行时回归通过。

- 不同 fresh-context 文档审核 approve-with-document-scope，advice hash 3f572db6cadc33d0ee8ac7f4b99d496b3c83cc4ac5b23ae0165ed57345a75b5e；实际 FINAL 已观察，非运行时实验回执。准备直接 main 发布，远端确认后另记收尾。

- 文档提交 d5b0bdd177b9375a95be2b7e1316a63fbc7a1b4a，远端 fetch/ls-remote SHA 及树 3e4af000e62bacbcc5928f71685356da57fe972e 与本地候选一致。原生 HTTPS push 缺凭据；既有 GitHub connector CAS main 发布成功。收尾更新覆盖、限制与状态，稳定 Plan 未改。下一步需单位/服务保证证据和真实 trace；原 next_topic 保留。
