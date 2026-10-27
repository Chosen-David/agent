# TANGLE：冲突结构与动作选择

2608.13921v1 · Lu Yang et al. · [正文](https://arxiv.org/html/2608.13921v1) / [PDF](https://arxiv.org/pdf/2608.13921v1)。arXiv提交：2026-08-14 03:48:08 UTC；PDF页眉August17不当作新版。

实际阅读：HTML正文§§1–5、Table1、Figures1–6图注、附录A及人物表；HTML在B表头中断。补读PDF E–J（Tables10–11、Figure7图注、I案例）、K开头及K.4/Table12。未读B–D与K.1–K.3；未进行PDF逐页视觉审读、作者代码或原始输出复现。精确范围及缓存哈希见inputs.json；不把下载、摘要和目录计为阅读。

## 方法、实验与局限（论文主张）

TANGLE separates curated-memory reasoning from system-native extraction over matched synthetic personal histories. Its 541 conflicts cover contextual alternatives, oscillating behavior and disagreeing sources; five response models and four memory systems are evaluated. Five ordinal dimensions distinguish recognition, reasoning, calibration, clarification and faithfulness; risky commitment is separate. Two judges report independently; human exact agreement is 59.1%, versus 85.8% within one point. A balanced 60-instance paired ablation varies distractors from zero to six, with instance-cluster bootstrap intervals. CAAP separates decision and realization stages, selecting among six actions; three-backbone benefits vary. FULL/PARTIAL/NONE concerns observable conflict structure, not usefulness; NONE makes perception/diagnosis inapplicable rather than zero.

Limits: synthetic underspecified requests and rubric preferences differ from coding automation. Conditional FULL comparisons select different subsets and do not alone establish extraction causality. Faithfulness can rise without better diagnosis (Appendix I). Selected cases are illustrative. Two-stage CAAP lacks matched total-cost/latency evidence here; no repository benefit follows. Extractor configuration, runnable policy prompts and numerical figure-panel outcomes were not independently reproduced.

## 与本库的关系及决定

- `KnowledgeStore.get/context/check_refs`保留已声明requires闭包；`related`是有界一跳导航，不承担自动发现全部异议的保证。context未携带related的truncated，属于覆盖可见性候选，尚未复现为生产缺陷；不据此声称ready等于全集完整。
- `MemoryLedger.correct`更正明确旧ID并使声明后代stale；reconcile只给信号，不应因时间较新就自动消灭有效上下文分支。现有更正规则保留。
- `basis_context`已有消费者选择、必需依据和candidate/rejected保留；优先沿用其入口，避免另造任务池。声明完整性、实际模型收到的内容与动作仍需独立验收。
- **adapt**：将“完整冲突关系是否仍可观察”纳入未来全量/任务包对照，并把“动作遵守当前授权”与“引用真实”分别验收。用户明确当前指令优先，不将论文clarify策略强加到非交互执行。
- **defer**：不迁移agent_doc，不加自动最新优先/多数投票或额外CAAP调用。先固定真实任务及已声明更正/异议/依赖；对同输入比较关系覆盖、授权合规、任务质量、实际全角色token/费用，再决定改动。当前仅源码/文献检查，无测试、模型调用或性能结论。

SYSTEM-99/Plan51仍未完成；新增1篇实际正文记录，近期可恢复记录20→21。旧耗尽验证、后端和全链缺口不重启或结案。独审全文见review.md；它不是受信运行时认证。
