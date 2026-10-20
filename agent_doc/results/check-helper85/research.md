# 研究与本轮取舍（2026-10-20）

新核验原文：[Beyond Downstream QA: Rethinking How We Evaluate Agent Memory](https://arxiv.org/html/2610.22209v1)，2026-10-15 提交。阅读主体方法、指标、实验、限制及附录 A 的状态演化例子；未声称逐页阅读全部附录。

其 FEB-30 以30条合成轨迹逐步检查记忆内部状态，辅以下游问答；内部诊断与最终答案应互补。嵌入匹配与 LLM judge 有噪声，小规模合成事实演化不能代表所有 agent 任务。本轮 adapt：在读取器调用及 schema 转移处直接设断言，而不是仅检查最终输出或退出码；不引入其模型服务、分数阈值或未经验证的记忆算法，不把论文结果当成本库收益。

本修复是已有优化的兼容性补全，不宣称算法创新。既有十篇精读记录位于 `agent_doc/results/read-boundary56/research_a.md`、`research_b.md`，另有 `memory-storage-20261015/research.md`；本轮没有新读十篇。历史研究只作导航，不能替代当前代码验证。
