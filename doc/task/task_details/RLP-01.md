# [RLP-01] 将既有维护改为 3600 秒固定周期，迁移旧周历状态、保持重启恢复与单轮互斥，真实部署并读回活性和下次到期。

Task-ID: RLP-01
Date: 2026-10-07

## Plan

将既有维护改为 3600 秒固定周期，迁移旧周历状态、保持重启恢复与单轮互斥，真实部署并读回活性和下次到期。

## Progress

### Preserved implementation and evidence

- [x] [RLP-01] 将既有维护改为 3600 秒固定周期，迁移旧周历状态、保持重启恢复与单轮互斥，真实部署并读回活性和下次到期。

### Historical context

Original task: [line 7](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L7).
Shared methods, results and evidence: [source section, lines 3–14](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L3-L14).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
