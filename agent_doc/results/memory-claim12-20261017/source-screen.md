# 候选依据

实际入口：Mailbox.prepare_context → basis_context → check_handoff_basis → claim_graph；直接claim_graph为本次完整函数计时口径，不冒称完整Mailbox/请求延迟。
claim_graph当前每代重扫pending并重建depends_on集合。链上每代移除一个节点，图检查段累计扫描n(n+1)/2节点；schema校验仍有独立线性成本。仅静态复杂度，不是已测瓶颈或生产负载分布。

成熟实现：Python官方graphlib.TopologicalSorter文档，2026-10-17核查，https://docs.python.org/3/library/graphlib.html 。输入为节点到前驱映射；unknown前驱会自动加入图，prepare可在任何消费前抛CycleError；static_order的顺序取决于插入顺序。直接替换会改变本库未知父、混合cycle/unsupported的诊断时序，需guard/fallback或明确契约变更；本候选不授权变更。比较标准库和小型Kahn，不以底层自写优先。

真实知识检索命令：python -m agent_runtime.knowledge --root knowledge search 'dependency graph topological validation'。
snapshot 767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18；返回maxflow、RL奖励、FlashInfer词法候选，均与当前依赖遍历算法前提不符，不作为本次方法保证，无采用knowledge_refs。早先rg knowledge/index*路径不存在错误不视作全库无知识。

本次不重算已有论文数量：父任务12篇阅读矩阵和后续独立来源笔记保留，最近ReCache筛选不适用于未接入KV的证据打包；本候选由真实循环和通用拓扑算法提出，不虚称新论文创新/模型效果。
