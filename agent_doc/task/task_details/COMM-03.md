# [COMM-03] 接入主 AI和科研入口，扩展现有每3小时任务的通信研究方向，发布 main 并读回。

Task-ID: COMM-03
Date: 2026-10-06

## Plan

接入主 AI和科研入口，扩展现有每3小时任务的通信研究方向，发布 main 并读回。

## Progress

### Preserved implementation and evidence

- [x] [COMM-03] 接入主 AI和科研入口，扩展现有每3小时任务的通信研究方向，发布 main 并读回。

授权：本会话要求探索通信研究并升级仓库；沿用直接 main、先 pull 后 push、不改 SGLang。复用现有角色/Engine/交接校验，未引入外部服务或更换架构。证据索引：`docs/communication_research.md`。
本次不冒充原持续优化任务的十篇精读/全角色真实模型批次，不重置其状态或在研工作。当前宿主无 tmux/持久模型 adapter，不声明后台模型监督启动；会话内继续工程工作。真实模型通信质量/成本 A/B 列为待测。

COMM-02证据：专项14/14，全仓403项（395通过/8跳过）、reader3/3；独立上下文实际使用合成科研交接，4事件/7投递、真实子进程中断恢复、补方差复算和旧结果拒收通过。保留首次脚本断言错误及恢复，主AI另目录重放通过。索引 `docs/communication_validation/verification.json`。COMM-03的入口和原每3小时任务更新已完成并回读，待本候选发布核对。

COMM-03发布阻塞：自动审批拒绝直接main推送，理由为本轮指令未明确授权更新默认分支；已保留本地提交，不更换接口绕过。随后同步并整合远端 `11af8dff2b1f599aca8098a1979e59e73ced36c1`，保留知识库升级，解决TASK追加冲突；整合后412项检查404通过/8跳过，插件同步通过。等待用户明确批准本次发布，再刷新远端、普通push及读回。

COMM-03授权更新（2026-10-06 22:26，Asia/Shanghai）：用户明确要求“直接推送到main分支，我给你权限”，并要求持续定时跟进通信方向。已同步远端 `3dedbb9b0a7f83b6d9a1e015aeb8598a117e4408`、保留知识库发布记录并解决TASK追加冲突；此次远端差异仅文档，沿用412项整合回归证据，通信专项14/14和插件同步再次通过。原每3小时任务已增加本次授权及通信方向接续要求，保持启用。

COMM-03已完成：main `b9325c5dc609e9a32ae3186e041485a4efa9de9a`、tree `34250047a9be45ac628ad741a023d191ee3c7c5a` 经GitHub读回和Git拉取核对，与本地验收内容完全一致。非强制、expected_sha保护更新；原每3小时任务保持启用且Prompt回读一致。先前审批阻塞为历史记录，已由用户明确授权解除并实际发布。持续通信方向评测未因本次工程交付而结束。

### Historical context

Original task: [line 137](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L137).
Shared methods, results and evidence: [source section, lines 133–149](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L133-L149).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
