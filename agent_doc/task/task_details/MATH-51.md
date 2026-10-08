# [MATH-51] GPU 分数目标与误差证书迁移设计

Task-ID: MATH-51
Date: 2026-10-08

## Plan

持续基础学科学习授权；主题为实数点积包络到实际GPU kernel排序的条件迁移。仅来源与数学设计，不运行模型/GPU/数值实验；先搜索结果和已有知识，不重跑旧实验。已有浮点卡不变，不以公开cpu结果认证GPU。总900秒，计划最多2周期、生产1次，最多两篇近期论文，主作者唯一写TASK/详情、研究建议、学习状态镜像；独立reviewer只写本轮plan_review与independent_review。无SGLang、人类guide、生产代码、常驻Skill改变。

DAG: startup/prior_search -> independent_plan_review -> source/proof/design -> independent_document_review -> task/state/publication -> fresh fetch/nonforce main -> remote SHA/tree readback。是本地实际分离上下文审查，非Engine/tmux/server部署。内容验收：正式文档准确定位FMA/FTZ/mma未指定项；近期原始论文版本与实际读范围；条件式逐token外包加kernel偏差证明；量化前/存储实数/densekernel三个目标分开；正例/tie/非法换目标反例；未提示定理名一般、传感器跨域、似是而非拒用任务；公平GPU最小验证计划；明确无模型/速度/token/真实kernel认证。读取未见测试内容为零，不将公开设计例当未见模型验收。

缺GPU只阻塞真实kernel认证，不阻塞独立文档设计；原论文不可读时只能记录筛选线索，不冒称全文阅读。普通搜索有缺失record和partial，明确不穷尽；旧结果仅定位前提，不消费或重报旧数据。指南GUIDE为空，无新采纳建议。沿用model-with-knowledge；至少保留已有knowledge ID/version/hash；按需最多3条及强依赖；上下文字符不能称tokens。发布文档候选不宣称生产性能改进。

## Progress

独立新上下文计划approve，另一个实际上下文document review为usable-with-scope，仅非实验文档。已读2026-09-22原始预印本v1相关R1–R4及PTX9.4正式文档；明确s/g/c/t目标、逐项δ膨胀与η分离条件，保留顺序/FMA/FTZ手算反例和跨域单位检查。没有新知识条目、生产代码、数值/模型/GPU/回归测试或token收益。本轮仅来源/知识结构/条件推导检查；公开例与预期检索任务不算未见模型验收。建议agent_doc/advice/GPU分数目标与证书迁移_by_gpt.md；证据agent_doc/results/math-gpu-ranking-contract-20261008/，文档提交 b93e66c6f65cbc3a82c14472b9f657d8a38279d2 已经fetch/独立ls-remote和tree d98e3f5252060b143512a07bacd5f6e8bd6e1d65核对。下一步需实际kernel运算模型及GPU授权环境，保留原学科游标。
