# [COH-T22] 复现并在本地修补正常等待耗尽重试、公平调度与诊断状态边界；程序测试375项中367通过、8跳过，reader3/3。只代表程序验证，不代表部署、自主加速闭环或发布完成。

Task-ID: COH-T22
Date: 2026-10-06

## Plan

复现并在本地修补正常等待耗尽重试、公平调度与诊断状态边界；程序测试375项中367通过、8跳过，reader3/3。只代表程序验证，不代表部署、自主加速闭环或发布完成。

## Progress

### Preserved implementation and evidence

- [x] [COH-T22] 复现并在本地修补正常等待耗尽重试、公平调度与诊断状态边界；程序测试375项中367通过、8跳过，reader3/3。只代表程序验证，不代表部署、自主加速闭环或发布完成。

### Historical context

Original task: [line 180](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L180).
Shared methods, results and evidence: [source section, lines 178–205](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L178-L205).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
