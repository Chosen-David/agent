# [MATH-56] 低秩逆更新与稳定性

## Plan

授权：持续基础知识建设/直接main发布；root唯一写TASK。SGLang、人类guide、生产行为、未用测试内容禁止改。

方法：A可逆，B=A+UV^T，S=I+V^TA^-1U；用块Schur证明B可逆当且仅当S可逆与Woodbury恒等式，不要求U/V满列秩。rank1 solve与SPD加/删除u，删除需u^TA^-1u<1；等号奇异，大于1可逆却非正定。在线ridge矩阵增量给严格数学迁移。自推并实测binary64标量A=1,b=1,u=2^54,v=1，SM最终相减得0而精确解非零；非小分母、A/B条件数均1，残差暴露错误。无普遍修复实现，近期MSM仅候选。

验收：非形式化完整恒等式与正定证明审核；10公开案例、3条无定理名/跨领域/前提失效查询×file/SQLite；53相关回归及镜像检查。没有LLM/GPU/e2e/token收益报告。复用Schur卡并固定强依赖；未用holdout仅元数据hash。

DAG：独立新上下文计划approve→produce→另一独立verify_experiment_result→consumer/publish；同一frozen合同贯穿。1200秒、最多2cycles/2attempts；仅本地工具真实调用，无远端GPU/监督服务，记录此限制。

先查历史原始输出与partial错误；原结果前提/数据不同，不复用为新实验。保持其他任务/next_topic。

## Progress

- main从647eea7 fast-forward到48bfa27，清洁工作树；同步最新指南/角色/知识索引/状态并检查无同主题活动。

- 完成：math.low-rank-inverse-update@1；SMW可逆等价不要求列满秩，SPD删除边界、真实binary64相消反例和在线ridge右端项更新。
- 10/10公开案例、6/6结构检索、53相关回归及镜像检查通过；独立计划approve与结果usable-with-scope已实际观察，508绑定完整。非Lean/未见模型/GPU/e2e/token收益。
- 近期阅读2609.12266v1（PDF2026-09-10），未确认最新版/正式发表；MSM未执行，保留候选。
- 科学提交e0e0c6e381f0572e6b903082037ceaae9d449dc9，树5b6e4f918db8895185a7dd9bfb6a740e0e68a2aa，fresh fetch/ls-remote一致；报告 [report_by_gpt.md](../../results/math-inverse-update-20261009/report_by_gpt.md)。
- 下一步：实际因子更新/直接分解/MSM残差与成本对照；保持既有next_topic与未见holdout，不改生产求解器或SGLang。
