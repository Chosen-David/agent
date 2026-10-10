# [MATH-76] 分块消元的完整残差与目标量误差

Task-ID: MATH-76
Date: 2026-10-10

## Plan

EXECUTE用户持续学习要求2/4/5/6/7/8/9/10。复用research-explore与知识入口，主AI唯一作者；1200秒文档研究边界，两次普通独立审核调用上限，非受管DAG或可信ReviewSession。缺可信实验验收后端，不产生CPU科学数据、模型/GPU/Lean或未见测试，不重置MATH65预算/失败/暂停。

补既有candidate.singular-boundary-condensation@1的数值条件缺口，写不可覆盖的@2补充（仅可逆实对称SPD子范围）：完整两块残差与精确凝聚残差关系、局部逆近似带来的内部残差、已认证逆范数下误差、线性目标的对偶残差身份、奇异gauge/浮点/缩放拒用。区分项目自推代数与经典后向误差，不能据数值残差或因子误差声称解精度。

先查实际历史结果及知识工具；历史搜索scanned123且partial/缺记录，命中不对应本轮科学数据，不复用。读取math.linear-solve-backward-error与math.schur-complement-block-elimination全文并记录真实版本hash。经典Netlib LAPACK1999 §§4.4误差解释；近期限定筛选Carrica等arXiv2601.08082v3（2026-05-29）作者HTML相关方法/结果/限制章节，核对版本/发表状态，不移用速度数字或把单GPU当多机证据。

普通独立审核共最多两次调用：第一次Plan初审；若初审返修，第二次同时复核修正后的完整Plan和完成文档，不另开第三次调用。当前初审revise计一次，不退款；第二次未通过则保存候选并停止发布。普通独立Plan及文档复核；公开无定理名解析例包括病态小残差、局部近似的边界零残差、目标量正确但全解错误、浮动gauge反例和接地电路。只报告知识/结构审查，不称模型实测；公开例不能算未见。没有可靠生产收益时defer runtime。

advice完整补充、results来源/检索/使用/审核/成本与双索引；TASK、coverage缺口和learning history仅追加，canonical计数/游标、旧候选及证据、guide/Skill/runtime/SGLang不变。同步main处理并发后按授权直接main，无PR，核对远端提交/父/树及全部变更字节。下一步是带认证残差/矩阵/单位/目标的真实求解器同条件对照，须可信宿主门禁及已授权预算，不能以本轮换ID恢复MATH65。

## Progress

- 同步main261090f，工作树clean；当前治理/角色/索引/持续状态已读，GUIDE空文件且README有人类边界解释。未发现同主题在执行任务；保留旧候选与所有暂停分支。真实查询输出已保存，待普通Plan审核。

- 普通Plan初审revise：实际目录扫描123（本轮目录创建增加扫描项），不是122；已保留原稿并修正。审核总调用上限仍2，第二次综合核对最终Plan与文档，初始revise不改写为通过。无第三次调用、无预算重置。

- 第2/2普通综合审核approve，最终Plan修正与全部残差/对偶身份、6手算例、量纲、来源/候选范围通过。完整反馈与候选hash保存；非阻断标题解释在审核处置中说明，候选原字节不变。TASK/三学科缺口/history仅追加，下一步真实迁移仍defer。

- 元数据/路径/hash检查通过：557保护路径未变、已审核候选和稳定Plan hash一致、TASK旧字节与coverage/history前缀保留。JSON有效、git diff --check通过；无程序修改无需功能回归。发布前fetch仍261090f，无并发变化，准备普通main提交。
