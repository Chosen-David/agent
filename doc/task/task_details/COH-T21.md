# [COH-T21] 根据完整证据选择最小修复，冻结候选，完成针对性检查、全部当前角色真实任务、实际交接和必要非退化验收，刷新main后按最终候选发布并读回。

Task-ID: COH-T21
Date: 2026-10-06

## Plan

根据完整证据选择最小修复，冻结候选，完成针对性检查、全部当前角色真实任务、实际交接和必要非退化验收，刷新main后按最终候选发布并读回。

## Progress

### Preserved implementation and evidence

- [x] [COH-T21] 根据完整证据选择最小修复，冻结候选，完成针对性检查、全部当前角色真实任务、实际交接和必要非退化验收，刷新main后按最终候选发布并读回。

目的：避免正确的Agent产物被错误评分事实误判。w1仅保存基线；w2增加未发布的等待/调度实现和工作流修补，仍无发布候选；CO-016回滚遗漏保留待测。数据与接续入口：`docs/continuous_optimization/rounds/2026-10-06-eval-coherence/checkpoint.json`、`round.md`。这只是本工具仓库的优化清单，不替代其他项目TASK。

### Historical context

Original task: [line 174](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L174).
Shared methods, results and evidence: [source section, lines 170–177](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L170-L177).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
