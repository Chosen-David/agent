# [BASIS-03] 跨层失效和成本验收、全仓回归、插件引用同步；刷新 main 后直接发布并核对远端。无同模型 A/B 时不声称质量或 token 收益。

Task-ID: BASIS-03
Date: 2026-10-07

## Plan

跨层失效和成本验收、全仓回归、插件引用同步；刷新 main 后直接发布并核对远端。无同模型 A/B 时不声称质量或 token 收益。

## Progress

### Preserved implementation and evidence

- [x] [BASIS-03] 跨层失效和成本验收、全仓回归、插件引用同步；刷新 main 后直接发布并核对远端。无同模型 A/B 时不声称质量或 token 收益。

授权：用户认可09:15分析建议，并要求注意 token 消耗；单一写入者主 AI。新证据放 `docs/communication_basis_validation/`，运行状态放私有 `.agent-runs/basis-upgrade/`。当前宿主 tmux 不可用，未启动后台监督或模型调用；保留原持续任务及无关状态。

BASIS-01/02 验收：统一知识/项目记忆依据门禁、显式结论依赖、已校验消费者影响定位及完整上下文预算已接入 Mailbox 与主入口。19项专项/CLI测试通过；并发工程知识合并后全仓513项（505通过/8跳过）、reader3/3。重复正文4497→1007字符，原引用/前提保留；实际token/同模型质量A/B未测，旧ACK与原数据保留。证据 `docs/communication_basis_validation/report.md`。BASIS-03待实际main发布和远端读回；不声称宿主部署。

BASIS-03 发布读回：实现 main `6248c5415fa866cc70cd87842e19ed73d858b544`、tree `b66eef559c32a04714bfe1aa864c66a4aad91b94` 与本地验收树一致；非强制 expected_sha 更新，GitHub API、git pull 及两次独立 ls-remote 核对。PublicationLedger 实际记录 tested→committed→pushed→remote_verified，原检查点保留。当前收尾仅更新 TASK/发布记录，不新增代码或性能声明。

### Historical context

Original task: [line 274](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L274).
Shared methods, results and evidence: [source section, lines 270–282](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L270-L282).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
