# [MATH-50] 保留分量预测与Schur残差

Task-ID: MATH-50
Date: 2026-10-08

## Plan

用户持续基础知识授权，补齐固定保留坐标a预测遗漏b的非中心二阶矩线性最优及残差矩；非线性条件期望、paired score与旋转前融合前提分开。总预算1200秒，作者/审查CPU各90秒；至多2计划周期/2生产尝试，不运行模型/GPU/新定时器、不写SGLang、人类guide或无关文件。原工作保留，main已同步bdb80ae，发布前重新fetch，直接非强制main并读回SHA/tree。

方法：有限二阶矩、Caa SPD，B=Cba Caa^-1，残差e=b−Ba，E[e a^T]=0，Cee=Cbb−Cba Caa^-1 Cab；任意T残差矩为Cee+(T−B)Caa(T−B)^T。自行完成证明；不将其等同于一般条件协方差。score=(qS+B^T qH)^T a+qH^T e，只有q独立于key才用trace二阶scoreMSE；真实paired校准须四阶目标。pre-RoPE预测B需要Rh(n)B=B Rs(n)，post-RoPE重学不宣称单频；预算公平比较固定索引维数/额外残差字节，无端到端结论。

验证：Fraction直接有限枚举矩阵预测/正交/Schur/任意T PSD差、零残差/非零均值/非线性/奇异拒用；paired q误差可使重建最优差于其他预测；2D有理旋转同频/异频；传感器单位和工况失配。三条不提示定理名的公开开发查询（一般、跨域、误用），文件/SQLite各top3，目标强依赖Schur和旋转，context≤14000字符，不冒充token。52项定向知识回归和插件同步；未读旧留出题内容，保存元数据hash，不算模型未见验收。

先独立新上下文plan-review批准后生产，再另一实际上下文核验六域冻结代码/递归全语料/输入/环境/原始数据/报告，只有usable-with-scope才发布。实际本地宿主分离审查，不宣称Engine/ReviewSession认证或tmux服务器部署。复用既有Skill/API/学习游标，近研读取AttSVD arXiv2610.06927v1（2026-10-03预印本）相关方法及Appendix B；博客Schur只作基础，自推公式独立标注。

root唯一作者：TASK/MATH-50详情、新卡及镜像、README/coverage/learning_state、本轮结果与自有运行状态；审查者仅本轮independent_*或plan_review文件。无同主题活动锁，旧结果只为取舍不复用测量；GUIDE空，无建议采纳。保留GPU残差证书和其他学科next_topic。

## Progress

独立计划v1/v2和最终六域结果审查完成，usable-with-scope。首次tuple/Fraction序列化失败，原代码/日志保留，修复后沿用原预算；最终25个精确案例、6次结构检索、53项定向测试及插件同步通过。闭包3条/11719字符，token未计量。NoPE/RoPE/混合预测边界、paired反例已入库；无生产行为、模型/GPU/Lean/e2e收益。科学提交 8c467f38c46e533423a95ae39c741a03db88fe42 已经native fetch与独立ls-remote核对，tree 35de2482556bc588bf854c789db4848d27bbf095。证据 agent_doc/results/math-linear-residual-20261008-v2/report_by_gpt.md；publication_receipt.json。下一步GPU残差证书与同预算模型实测；不将公开开发题当留出测试。
