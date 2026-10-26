# SYSTEM-99：历史流程的适用性与任务质量

2026-10-26；基线90228b44bb6ec4439af2a1987a442b630d5e84e8。
同一批次的阅读/静态审查，不是新轮次、实证复用或生产修复。

## New body reading

Wang, Mao, Fried, Neubig. [Agent Workflow Memory, 2409.07429v1](https://arxiv.org/html/2409.07429v1), 2024-09-11.
Read: main §§1–7, Tables1–9/figure captions; Appendices A.3/B/C, Tables10–11. A.1/A.2 and image pixels were not reviewed.
Method: infer reusable subroutines from trajectories, abstract instance values, and add them to website-specific context. Offline uses training examples; online gates induction with a model success evaluator.
Experiments: WebArena and Mind2Web; fixed GPT-4-0613 for WebArena. Table1 reports 35.5% versus accessibility-tree-only 15.0%; this differs from the headline comparator.
Ablations: rule/LM induction is comparable on WebArena; text/code and observation formats vary. More context is not uniformly better.
Negative evidence: Table4 cross-domain offline step success improves while task success falls. Table11 combined memory has cross-task task success below both separate variants, despite “between” prose. Table9 and its prose also disagree.
Limits: evaluator errors, distribution/order dependence, and rigid actions missing intermediate observations; trajectory steps omit total induction/evaluation cost. No local reproduction.

## 源码对应与决定

静态读取MemoryLedger的连接/遍历/更正/check/_context_closure/reconcile、check_task_memory，
以及check_handoff_basis、basis_context、basis_impact、knowledge task/handoff检查。
内置有依赖记忆闭包在同一SQLite读事务装载root和祖先；普通check仍只返回所需root。
无依赖root沿用先前检查得到的快照，不因后续外部更正就能断言该快照内部不一致。
自定义ledger保持逐层调用；跨知识库/文件/账本到最终模型动作的原子一致性未被证明。
本次没有确认可独立复现的新生产缺陷；不能用再加一次check冒称消除了所有竞争窗口。

现有procedure kind、candidate隔离、correct的superseded/stale后代传播、定向handoff和唯一TASK继续作为权威。
采用“单步、整任务、适用前提分别验收”的后续判别视角；不新建workflow记忆库或竞争任务清单。
不将模型判定的成功直接提升为已验证procedure，也不保存论文式私密thought字段。
复用已有Skill时仍需当前目标/更正/依赖核对；历史成功、当前哈希和ACK均不能单独认证适用性。
下一步真实消费对照须覆盖旧流程适用/任务已更正/出现新中间状态，观察最终操作与恢复结果及全部调用成本。
此为待验证方向，未执行模型/benchmark/测试；不重试旧受阻或已耗尽预算的分支。

同批保留正文记录由10篇增至11篇，本次仅新增上述一篇，旧55篇遗失原件及独审重读不计。
所有actor实际推理用量/费用未知，不记零；本次没有新性能、token或模型任务质量收益主张。
先前CONTEXT-WIRE-01四组原生CI已通过，但不代表全库、原生PID前提或SYSTEM-99整体已验收。
