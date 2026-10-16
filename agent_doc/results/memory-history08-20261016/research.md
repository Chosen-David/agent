# 新阅读与采用边界

2026-10-16：[TallyMem / Beyond Retrieval](https://arxiv.org/html/2610.19474v1)，2610.19474v1，2026-10-14。实际阅读§3–6的来源跨度、按序视图、typed query、执行边界，§7实验与选读Appendix K/L/M成本、代码控制及仓库适配。未逐图或全附录通读。

Keep original events and explicit source identities; deterministic execution is exact only given correct ledger and event specification. The paper separates access from aggregation, and warns that model-specified filters remain fallible. Full AMA gains are modest; held-out repository evaluation uses a benchmark-specific adaptation, not zero-adaptation transfer. Annotated construction and online compilation add model costs. Here we retain the existing full history packet and ordering and test a physical SQLite event index; this is engineering support for source access, not a reproduction of its query language, routing, or quality gains. We do not infer model KV, QA or token gains.

APDMem 2610.02472v1 HTML本次返回Internal Error，只有既有摘要线索，不计精读或采用。此前12篇矩阵保留历史身份，本轮不重复计数。

SQLite官方[Query Planning](https://www.sqlite.org/queryplanner.html)§1.3、2.1、3核对：普通索引保留rowid用于同键排序；events.sequence是INTEGER PRIMARY KEY别名。SELECT *仍需table lookup，不称覆盖索引；保留显式ORDER BY sequence并实测EQP。

真实入口：CLI main(history)→MemoryLedger.history→_get与events查询→完整packet。没有发现agent_runtime内部history消费者，本轮只允许审计历史接口延迟主张。来源不可变、事件顺序不压缩；不新增自然语言聚合或伪造底层KV消费者。

## 后续路线候选：CogMem

2026-10-16定向阅读 [CogMem](https://arxiv.org/html/2610.11314v1)，2610.11314v1，2026-10-08。已读§3方法/式1–7/Algorithm1、§4主表与设置/消融、§6限制，选读Appendix E成本与G错误分析；未逐图/全附录通读，不混淆另一同名CogMem。

Its typed schema distinguishes attributed Claims from operational Event/Fact records; Fact does not certify truth. Consolidation adds provenance links instead of deleting episodes. Routing uses model intent and sufficiency judgments despite deterministic operators. The English-benchmark evidence and synthetic attribution probe do not establish deployed or multilingual reliability. Iterative QA adds online token cost, and storing provenance links does not ensure the agent actually follows them. We defer a new ingestion, consolidation or ReAct pipeline until real model access and task quality evaluation exist. Current ledger already distinguishes kind/evidence/source/status; introducing PEC²F node types blindly would change semantics without a consumer. This paper is a separate future-design lead, not evidence for the physical event index or any claimed quality improvement.

作者[CogMem README](https://github.com/Silent-Rain02/CogMem)本次只读网页，未锁commit/克隆/安装/运行。README自述仍为pre-release、非archival branch；要求Python≥3.12、chat与embedding endpoint，数据需另下，切embedding维度需重建workspace。故只留未来适配线索，不把README结果当本库复现或默认服务已可用。
