# [DATA-03] 验证伪造通过、代码/数据过期、错误实验和正确负结果场景，接通真实任务运行时/消费者并纳入本轮统一发布。

Task-ID: DATA-03
Date: 2026-10-07

## Plan

验证伪造通过、代码/数据过期、错误实验和正确负结果场景，接通真实任务运行时/消费者并纳入本轮统一发布。

### 实现方法

用正确负结果及故障注入对照验证新门禁：错数值、遗漏数据、刷新哈希仍错误、自评冒充审查、缺回调、回调中篡改、代码/配置/原始数据改变及路径越界。检查 ReportingHandler、后续消费、监督回调和报告证明的实际调用链，修复后重新验收而不抹掉原始数据。

### 验收边界

以实际代码、输入/产物版本和独立检查记录为准；结构/哈希校验不证明所有代码无 bug，当前宿主未部署独立后台模型服务。

## Progress

### Preserved implementation and evidence

- [ ] [DATA-03] 验证伪造通过、代码/数据过期、错误实验和正确负结果场景，接通真实任务运行时/消费者并纳入本轮统一发布。

### Historical context

Original task: [line 367](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L367).
Shared methods, results and evidence: [source section, lines 363–367](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L363-L367).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.

### 本轮功能验收（2026-10-07）

相关实现与独立正反例通过；全仓 730 项中 729 通过、1 项真实 tmux/Unix socket 条件测试跳过，Reader 3/3。最后上游仅修改 TASK 记录，代码/依赖无变化，按原版本证据复用并补验文档 55/55、发布门禁 29/29。详见 docs/document_architecture_validation/，此处不将程序测试说成绝对无 bug 或生产部署证明。统一 Git 发布仍由 DOC-04 跟踪。
