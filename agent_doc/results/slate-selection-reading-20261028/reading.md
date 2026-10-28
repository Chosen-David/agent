# Slate-selection reading

2610.34673v1, Xinyu Zhang and Weiwei Sun, submitted2026-10-26T01:05:20UTC. Primary: https://arxiv.org/html/2610.34673v1

Read: main1–8, appendicesA–E, Tables1–8/Figure1–3 captions. References, images, author-code/raw replication excluded. Continues uncredited1000 methods checkpoint; one unique body.

Method: BM25/dense fusion, learned ten-feature ranking and budget fill; optional write-time records. Factorization is an expectation identity. Item-wise optimality assumes independent relevance, invariant conditional reward and additive costs; fill needs monotonic reward.

Experiments: 152development/348test questions shared across LongMemEval-S/M; main answerable multi-session stratum209; four perturbed budgets, question bootstrap10000; LoCoMo conversation holdout. Ablations retrain features and vary pools, ranking, budgets and date tags.

Limits: shared training sessions disclosed; all500 comparison includes development and copied protocols; hard filler harms; date tags can regress; DeepSeek-M gain becomes parity under another judge. Nonsignificance does not prove monotonicity or equivalence. Shared headers violate additive-cost idealization. Cost3.2x covers selection saturation on A100 with different concurrency; shared-pool inclusion changes ratios, excludes complete answering/judging/build lifecycle. No repository performance transfer.

## Repository applicability

采用/调整：未来评价须把候选池完整性、排序后依赖闭包完整性、最终回答质量分开；同时保留全部角色、首次构建、分页/补读、重试和验收的实际成本。相关性排序不得替代必需依赖、更正、异议或指南约束；同一任务包与全量读取的比较还需完整实际模型输入及质量判据。本次只是评价依据，不是新实验批准。

只读源码关系：MemoryLedger索引是导航，check/closure检查当前声明依赖；basis_context保留candidate/rejected与祖先，预算不足拒绝整包；communication ACK独立于语义验收。检索阶段完整性不是授权或科学正确性的证明，时间新旧也不是自动采纳规则。上述为本库既有边界的源码核对，无实测收益结论。

暂缓：新增学习排序、默认填满预算、自动删旧记忆、共享聊天池或agent_doc迁移。恢复条件是本库独立、固定真实任务上的依赖/更正/异议保留、最终质量和完整费用验收。保持唯一TASK、人类guide只读、原实现原地维护；旧门禁不重置。独立复核/公开回读后同批可恢复正文24→25，未完成部分此前未抵数；SYSTEM99仍未完成。历史索引unknown，不伪称受信运行时验证。
