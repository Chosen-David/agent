# [ALG-05] 同步知识与插件索引、更新覆盖/状态，完成统一回归；每次发布前同步并保留并发改动，直接main提交与独立远端核对。

Task-ID: ALG-05
Date: 2026-10-07

## Plan

同步知识与插件索引、更新覆盖/状态，完成统一回归；每次发布前同步并保留并发改动，直接main提交与独立远端核对。

## Progress

### Preserved implementation and evidence

- [x] [ALG-05] 同步知识与插件索引、更新覆盖/状态，完成统一回归；每次发布前同步并保留并发改动，直接main提交与独立远端核对。

MATH-15/16纳入本完整课程轮次，不因单条Krylov完成而结束。主AI单一写入者；不改SGLang，不扩大为无限期数学百科，也不以条目数冒充能力。

本轮高等代数证据：docs/knowledge_learning/2026-10-07-algebra/report.md 与 curriculum.md。18主题来源/推导核查、76项有限检查及现有files/SQLite结构检索完成；自然问句与宽泛旧查询的遗漏完整保留。ALG-04 的知识/结构层验收完成，独立未见测试与模型A/B仍未完成；不能将其标为效果提升。ALG-05 保持待远端验证。indexer文档是随后独立任务，产物不写入SGLang。

ALG/MATH发布闭环：实现commit 11ace692d3b0e6249b203e1e8813eb9c342346ec、tree e0ec3f98ffd2ea8c5d40784ee0034038b70e1054 已非强制推送main，API/pull与独立ls-remote均读回remote_verified。548程序（540通过/8跳过）、reader3、76有限检查、结构检索/成本证据保留；自然问句遗漏及未见模型验收未完成。下一任务为用户指定 indexer 子空间设计文档，不修改SGLang或启动新定时任务。

### Historical context

Original task: [line 363](../legacy/TASK.b537d62002c8478825021eef769c6482faa0d2926d604df95467c45595e80384.md#L363).
Shared methods, results and evidence: [source section, lines 357–369](../legacy/TASK.b537d62002c8478825021eef769c6482faa0d2926d604df95467c45595e80384.md#L357-L369).
Source SHA256: b537d62002c8478825021eef769c6482faa0d2926d604df95467c45595e80384
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.

### 上游发布状态更正（2026-10-07）

上游 e7a908aaa2198d740dd4fcfc835b8e2931db16e5 将原共享叙述由待发布更正为已远端核验，原任务行及勾选状态不变。最新完整原文保存在 [上游 TASK 快照](../legacy/TASK.d9d62758a6294a346955315378ee6849aa5c1e6f072e8b23ff3ef7bebcadd650.md)，保留旧快照不覆写；未复制该批次另行交付的私人文档。
