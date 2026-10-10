# 普通独立Plan审核原始反馈

Reviewer: /root/condensation_residual_plan_review；fresh context；一次实际调用。decision=revise。非可信ReviewSession，不授权受管派发/实验。作者修改见plan_initial_snapshot与plan_final_snapshot；未把本次revise改写成approve，第二次总调用将综合复核最终Plan与文档。

实际读取：AGENTS.md、决策协议、项目文档工作流、双主工作流、review-main职责、MATH-76完整Plan、当前prior/knowledge搜索和knowledge_use、空GUIDE及README、MATH-75完整Plan/候选/report/document_review/authorization。没有运行实验、修改文件或读取未见测试。

| 检查 | 状态 | 理由 |
|---|---|---|
| intent | pass | 本轮围绕MATH75凝聚候选的残差、条件性和目标误差缺口开展文档学习；范围明确，不以本轮恢复MATH65。当前授权引用沿用持续学习要求；本审核不额外认证用户授权。 |
| guide | pass | GUIDE为0字节；README明确AI只读。Plan保留guide、Skill、runtime、SGLang及旧候选证据。未发现现有指南冲突。 |
| assumptions | pass | 明确限定固定原矩阵/rhs/partition及实对称SPD子范围，误差结论要求认证残差与逆范数；奇异gauge、浮点与缩放需拒用。补充应明确整体H≻0，从而A及精确S均SPD；不得仅有A≻0便逆S。 |
| prior_results | fail | 实际搜索scanned=123，Plan和knowledge_use仍写122。搜索partial且MATH75 record缺失；MATH75报告可以作已读文档背景，不能冒充当前独立数值数据验证。现有“不复用科学数据”处置正确。 |
| acceptance | pass | 普通独立文档复核、公开解析例、来源/读取范围、版本hash及保护路径检查足以支撑本轮限定文档交付。公开例不得记未见测试；近期论文尚待实际阅读，版本/日期/发表状态应在交付前核验。 |
| risk | pass | 不据残差、因子误差或来源速度数字推断精度/多机收益；没有生产收益则defer。新版补充须保存@1原字节，且目标准确不等于全解准确。 |
| resources | fail | 1200秒文档边界合理，但“两次普通独立审核调用上限”按字面包含当前初审。返修复审加文档复核将成为三次调用，不能默认为两次session或自行扩预算。 |

完整阻断问题：

1. target：MATH-76 Plan历史检索段；本轮knowledge_use.json prior_results。
feedback：实际扫描123，错误沿用了上轮122。
requested_change：统一改为123，保留partial/errors及不复用科学数据说明；明确MATH75只有人工读取的文档背景，不存在当前搜索成功取得其record或可信数据验收。
acceptance_check：新版完整Plan与实际prior_search字段一致，knowledge_use描述一致。

2. target：MATH-76 Plan首段审核资源。
feedback：两次总调用与当前返修后仍需完整文档复核的安排冲突。
requested_change：核对已有授权究竟约束调用还是session。若已有授权确实允许MATH75式“两session，Plan最多2 turns、document最多1 turn”，准确写明并保留实际调用账；否则遵守字面两次总调用，调整后续安排或记录预算阻塞。不得以换run_id、换任务或默改单位恢复额度。
acceptance_check：新版预算文字、实际已用次数和剩余审核安排一致，不超过1200秒及原授权。

非阻断执行提醒：在线性目标对偶残差部分定义残差符号后再写恒等式，并区分精确对偶和近似对偶的剩余项；接地电路例须保留西门子、伏特、安培以及半功率的单位说明。当前数学方向不需要扩大为实验项目。

作者处置：adapt两项，计数修正123并注明41错误；保持两次总调用，第二次同时核对最终Plan与文档，无额外Plan复审调用。近期来源已选择性读取并记录，而非未执行计划。旧初审完整保留。
