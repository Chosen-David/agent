# [NEURO-03] 必要回归与插件同步通过，发布前 fetch/整合、非强制发布、独立读回远端，更新本机技能并完成自有 tmux 督导收尾。

Task-ID: NEURO-03
Date: 2026-10-07

## Plan

必要回归与插件同步通过，发布前 fetch/整合、非强制发布、独立读回远端，更新本机技能并完成自有 tmux 督导收尾。

## Progress

### Preserved implementation and evidence

- [x] [NEURO-03] 必要回归与插件同步通过，发布前 fetch/整合、非强制发布、独立读回远端，更新本机技能并完成自有 tmux 督导收尾。

产物：`knowledge/entries/neuroscience/`、`docs/knowledge_learning/2026-10-07-neuroscience/`、`evals/knowledge/neuroscience-queries.json`；私有运行 `.agent-runs/neuroscience/`。运行中保持本 TASK 稳定，历史报告及源快照不可追改。

NEURO验收：10张跨物种研究卡（9篇正式论文、1份已读预印本）及4篇作者/机构博客，语料56条；来源窗口2021–2026，所选最新论文2026-09-29。全仓548项（537通过/11跳过）、Reader3/3；新卡双后端Top1与40项决策检查通过；旧原始排名退化完整保留，有界候选5恢复上下文门槛。功能发布 `effbab2480a770c70aaba075860c42464fe5a70d` 已独立核验完整树，本机15技能/294文件已同步，安装后真实CLI再次通过10查询/40决策。督导v1因来源哈希修订撤销并保留记录；v2使用剩余预算重验，83项要求全部reportable、remaining=[]，done且monitor stopped/live=false。既有WSL每3600秒维护仍live，下次11:22:56 +08:00。此处勾选为督导结束后的审计修订，旧证据绑定原TASK，不追改历史。详见本轮report.md、validation.json、publication.json和checks/runtime-readback.json。

### Historical context

Original task: [line 9](../legacy/TASK.b537d62002c8478825021eef769c6482faa0d2926d604df95467c45595e80384.md#L9).
Shared methods, results and evidence: [source section, lines 3–14](../legacy/TASK.b537d62002c8478825021eef769c6482faa0d2926d604df95467c45595e80384.md#L3-L14).
Source SHA256: b537d62002c8478825021eef769c6482faa0d2926d604df95467c45595e80384
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
