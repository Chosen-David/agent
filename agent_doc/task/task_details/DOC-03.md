# [DOC-03] 适配主AI、全部角色、监督恢复、任务/发布/记忆校验、安装器与模板；不把目录改名当运行时升级。

Task-ID: DOC-03
Date: 2026-10-07

## Plan

适配主AI、全部角色、监督恢复、任务/发布/记忆校验、安装器与模板；不把目录改名当运行时升级。

### 实现方法

主 AI、角色、任务清单、ReportingHandler、监督恢复、发布和项目记忆复用同一文档解析/依赖接口。安装器创建 canonical 空清单和空目录，但不代写 guide 文件；独立技能通过同步脚本分发按需协议，验证包内引用闭合和隔离 CLI。

### 验收边界

以实际代码、输入/产物版本和独立检查记录为准；结构/哈希校验不证明所有代码无 bug，当前宿主未部署独立后台模型服务。

## Progress

### Preserved implementation and evidence

- [ ] [DOC-03] 适配主AI、全部角色、监督恢复、任务/发布/记忆校验、安装器与模板；不把目录改名当运行时升级。

### Historical context

Original task: [line 358](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L358).
Shared methods, results and evidence: [source section, lines 354–362](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L354-L362).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.

### 当前进展（2026-10-07）

已实际迁移 93 项唯一任务，生成 93 份详情；旧 TASK 全文 SHA256 为 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021，归档逐字节一致，原根文件仅作跳转。guide 目录为空，未写入任何指南文件。独立检查发现的边界漏洞正在逐项修复复验；最终全量验收与 main 发布未完成。

### 本轮功能验收（2026-10-07）

相关实现与独立正反例通过；全仓 730 项中 729 通过、1 项真实 tmux/Unix socket 条件测试跳过，Reader 3/3。最后上游仅修改 TASK 记录，代码/依赖无变化，按原版本证据复用并补验文档 55/55、发布门禁 29/29。详见 docs/document_architecture_validation/，此处不将程序测试说成绝对无 bug 或生产部署证明。统一 Git 发布仍由 DOC-04 跟踪。
