# Retention / selection reading

2610.00366v1, Juli Huang, submitted2026-09-30T06:38:14UTC. Primary HTML: https://arxiv.org/html/2610.00366v1

Read: main1–7, Tables1–8, Figure1 caption; references incidental, no PDF-image audit, author-code/raw replication or appendix claim.

Method: query-independent retention crossed with query-time selection; shared300 seeded episodes/two queries, episode-bootstrap2000 resamples. Five retention/five selection rules, informative/uninformative queries, budget/delay/distractor controls; MPNet768-d cached embeddings; FLAN-T5-large greedy answering; SQuAD300-question transfer.

Evidence: matched-access selection and history-access gains differ. Synthetic selection saturates retained evidence; natural-text dense retrieval improves over lexical. Type-oracle uses privileged labels; marked distractors and latent topic structure create artificial retrieval gains. Recall is not answering accuracy.

Unresolved: Table2 random retention remains53% at capacity10/20, contradicting the ensuing universal convergence statement. Table7 accuracy/conditional-accuracy and §§4.4–4.5 absent/present-wrong counts do not reconcile; retain unknown, no silent numeric repair.

Limits: ten-item single-turn streams, bounded-item capacity rather than tokens, no correction/multi-session/multi-hop evaluation; one answering model/prompt. General ceiling does not establish realistic saturation or deployed cost/quality gains.

## Relation to this repository

采用/调整：未来比较既有任务包、活跃只读导航与全量读取时，先固定可访问证据全集，再单独记录保留范围、选择范围和最终回答/动作；导航未载入与持久证据被删除分别归类。该原则是待落实的评价方向，不是新实验的批准或验收。

现有basis_context保留所选/必需及candidate/rejected声明与祖先，MemoryLedger闭包沿声明依赖水合；已知上下文提示要求可信宿主当前实际保有，引用合法不证明模型注意/理解。检查了memory检查/修订/闭包、prepare_context及现有缓存/更正测试源码；未运行测试，不将同名read/check当跨存储事务或最新状态到动作的保证。

暂缓：自动删记忆、查询选择器、embedding策略、拓展持久缓存及目录架构迁移；需要本库真实任务、完整模型输入和全角色用量/质量证据。保留唯一TASK、人类guide只读及既有MemoryLedger/定向交接。未增加旧实现副本、未重启任何耗尽门禁，无生产/模型/性能结果；SYSTEM99仍未完成。新正文记录仅此ID，公开与独立核对完成前不增加可恢复计数。
