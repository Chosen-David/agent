# 范围与执行记录

用户将单次 Krylov 主题扩展为标准高等代数主线，随后要求完成后为 indexer 写子空间设计文档。主 AI 单写者；未启动另一轮重复写入，未新增定时任务。repo main 起点664e09ed97bcdb8d3896a7dd67d71bbc31d6b8dd；保留并发 RL/概率轮次及所有既有知识。private run math-krylov scope_version=2，发布前重新同步 main。

角色/Skill：沿用 repo model-with-knowledge、knowledge_access_workflow、task_supervision_workflow、project_memory_workflow；研究探索使用当前已安装 research-explore。无新 Skill/生产算法；只增加经核对的知识与有界验收。实际工具为原文网页/PDF、Poppler、Python Fraction/NumPy、既有 KnowledgeStore/files/SQLite 和可选 tiktoken；无 Lean、GPU/live model adapter、tmux监控或Agent A/B。

DAG：source/version check → 18-topic curriculum/entries → exact/numerical transfer and failure probes → retrieval/cost/regression → sync/publish/remote verify → indexer design document。高等代数范围见 curriculum.json，课程外领域明确列出。8篇研究只是有界筛选样本，不是数量型验收。

验收：每个主题正文前提/证明思路/正例/拒用条件；全部主题有限验证；不直接提示定理名的自然问题；结构查询、跨领域物理/矩阵方程/网络映射；公开失败与token成本；必须完整运行repo和reader回归。自然问句遗漏和未见模型测试作为限制保留，不能用更容易的结构关键词成功隐藏它们。没有模型实测，只能报告知识或结构检查。

新版复核：2607.07964由v1更新到v2（8月8日），2605.14489由v1更新到v2（10月5日）；采用新版相关章节后再写研究结论。已公开试题均不再算未见测试；独立封存推理任务与同模型A/B为后续未完成验收，不在本轮制造假结果。
