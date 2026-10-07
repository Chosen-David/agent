# [MATH-14] 更新按学科/结构检索、学习状态与插件快照，执行必要验收及回归；重新同步main后直接发布并读回，保存下一主题及未见测试缺口。

Task-ID: MATH-14
Date: 2026-10-07

## Plan

更新按学科/结构检索、学习状态与插件快照，执行必要验收及回归；重新同步main后直接发布并读回，保存下一主题及未见测试缺口。

## Progress

### Preserved implementation and evidence

- [x] [MATH-14] 更新按学科/结构检索、学习状态与插件快照，执行必要验收及回归；重新同步main后直接发布并读回，保存下一主题及未见测试缺口。

主AI单一写入者；证据 `docs/knowledge_learning/2026-10-07-conditioning/`，私有接续 `.agent-runs/math-conditioning/`。沿用知识Skill、现有索引/记忆与发布门禁；不修改SGLang，不将自然语言残差类比为线性求解证书。当前宿主tmux/持续模型动作不可用，当前会话继续授权工作，不声称已启动后台监督。

MATH-13/14本地验收：经典后向误差和条件性、2026-09-10 arXiv2609.12266v1筛选、排名与接地电路迁移已完成；65项有限检查，4道新结构查询两后端命中。单条cl100k_base JSON上下文3,522tokens，不是账单/模型收益。旧Recall@3保持20/21、上下文召回1；SQLite倒数排名略降已记录。保留并发返修交接提交并合并TASK至6e667289，复验全仓542项（534通过/8跳过）、reader2项、插件快照/实际引用哈希通过；待实际main发布读回，未运行Lean或模型A/B，不采用MSM生产替换。

MATH-14发布读回：实现提交 `e6157805e2743e109e614f9f8dba44c91b26cb3b`、tree `1e91d03fa72695f411c0bb84725ada5da203509f` 已按expected_sha非强制直接发布main，与本地验收树一致；API、pull及PublicationLedger独立ls-remote确认remote_verified。来源/65项结构计算/两后端检索/542项程序回归证据保留，公开记录 `docs/knowledge_learning/2026-10-07-conditioning/publication.json`；本轮只采用知识，不宣称模型质量或收费改善。闭环仅TASK及发布元数据，下一主题与真实A/B缺口已保存。

### Historical context

Original task: [line 330](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L330).
Shared methods, results and evidence: [source section, lines 327–337](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L327-L337).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
