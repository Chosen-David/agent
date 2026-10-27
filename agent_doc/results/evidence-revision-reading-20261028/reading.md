# Evidence-revision reading

2610.03902v1, Wenhui Chu, submitted2026-10-02T18:13:29UTC. Primary HTML: https://arxiv.org/html/2610.03902v1

Read: main1–9; AppendixJ/Table15/Figure4 caption; N/Table19/Figure5 caption; O protocol/endpoints/Table20 and Tables25–26. O middle tables only incidental fragments; other appendices, references, author code/raw results and PDF visual review excluded. Main Figure1–2 captions read; no figure-image audit.

Method: source/version-labelled document revisions compare re-reading, cached extraction, rebuilding and dependency-local repair; support, retention, adoption and attempted-trajectory cost stay distinct. Commit validation checks read-set changes, not source permission or answer truth.

Evidence/ablations: two7B models; shared-ingest, same-facts/order, decoding, reuse and source-filtering controls. Short-record repair saves revision work but loses full-pipeline cost. Longer-record savings partly involve truncated irrelevant-document extraction; source-filtered re-reading stays cheapest by construction. C2’s four primary tests are nonsignificant; its extra third call excludes cost interpretation. O excludes mis-tokenized Mistral cache estimates.

Limits: small/reused samples, lexical posthoc scorers, one revision/repeated template, equal token weights, no author code/raw release. No repair-mechanism attribution or deployed price/latency guarantee.

## Relation to this repository — source-grounded assessment

MemoryLedger.correct/_revise 已创建新修订、保留旧状态历史并使声明依赖后代 stale；check 沿现有依据检查。它们不自动发现未声明的语义依赖，也不能证明模型实际采用更正。不因论文提出依赖图而另造平行记忆系统。

basis_context 已保留所选/必需声明、candidate/rejected 与祖先闭包，加载知识/记忆正文，同时保留 artifact 引用；所谓当前上下文复用由可信宿主声明。导航或源筛选的未来对照必须沿用这些边界，不能先删异议、依赖或未知相关性再报告“更省”。源引用完整不等于消费者读取或最终动作正确。

后续真实任务验收保留现有 MemoryLedger、定向交接与唯一 TASK：分别记录更正传播、最终答案/动作、仍有效信息、模型用量及恢复/首轮加载/所有角色成本；比较既有全量入口、选定任务包与按合法来源筛选的重读。只在任务合同确实声明范围时筛选，不把临床记录的来源标签方法直接当本库语义筛选器。这里是评价协议方向，不是已批准的新实验或生产策略。

adopt/adapt：采用完整流程成本与“采用更正/保留有效信息”分离的评价原则。defer：新修复选择器、自动压缩/删记忆、推断相关性的源过滤以及强事务架构；需要本库实际任务、合法来源/依赖范围、真实宿主和总成本证据。既有全库/PID/role/backend/模型初探等耗尽门禁不重启，无新模型/性能/token/费用收益。

本记录是同一 SYSTEM-99 的文献检查点，不是整轮完成。此前2610.31303v2私有阅读/独审原件缺失不补造、不抵扣本次；本次2610.03902v1是独立的新正文记录，发布和独审另核。
