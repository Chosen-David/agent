# Research mapping — 2026-10-19

既有12篇方法矩阵：`agent_doc/results/memory-storage-20261015/research.md`，本轮复核其范围/局限，不计为新精读12篇。上一轮RIME记录与缓存负结果保留原路径，不迁移或覆写。

新增原文阅读：[Beyond Retrieval: Evidence Access and Event Aggregation in Agent Memory](https://arxiv.org/html/2610.19474v1)，v1 2026-10-14；覆盖正文§3–8及附录A/C/I/J/K/M的机制、对照、成本与边界。TM保留原始轨迹，按问题选择来源可定位的证据；TallyMem额外让模型指定事件条件，由确定性执行器聚合。其正确性以ledger和事件定义正确为前提，文字引用匹配不证明事件语义。AMA总体提升小于诊断子集，MINTEval需专门适配；不同部署/开发子集不能混算，构建与在线编译均有成本。

采用：将来源保留、选择、物化分别检查，固定本地输入与完整输出，记录失败和被排除条件。暂缓：LLM事件编译/自动记忆改写，缺真实任务与成本验收。本候选只是常规延迟物化的工程应用，不是TallyMem算法实现，也不拿论文结果作本库性能数字。

Python [3.12 copy文档](https://docs.python.org/3.12/library/copy.html)核对嵌套对象共享与深复制边界：本候选内部元数据只读；最终返回仍走原JSON深拷贝，并由独立污染测试检查。LazyMem HTML访问失败，未计入已读。

技能选择：沿用已安装research-implement-optimize与仓库标准库基准/独立审核，不安装新依赖。无原生监督适配/tmux不妨碍本次有界本地实验，但不能声称已部署常驻监督。
