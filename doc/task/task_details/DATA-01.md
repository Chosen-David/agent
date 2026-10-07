# [DATA-01] 在测试/实验产出数据后安排独立代码与数据校验节点，绑定输入、代码、配置、原始数据及产物版本，前置于结果消费和结论验收。

Task-ID: DATA-01
Date: 2026-10-07

## Plan

在测试/实验产出数据后安排独立代码与数据校验节点，绑定输入、代码、配置、原始数据及产物版本，前置于结果消费和结论验收。

### 实现方法

由可信任务规划/消费者指定 result_validation 要求，数据节点之后先进入独立校验，再允许下游结论和发布。绑定代码、输入、配置、原始数据、产物和运行标识；生产者省略字段或自填 pass 不能取消门禁。

### 验收边界

以实际代码、输入/产物版本和独立检查记录为准；结构/哈希校验不证明所有代码无 bug，当前宿主未部署独立后台模型服务。

## Progress

### Preserved implementation and evidence

- [ ] [DATA-01] 在测试/实验产出数据后安排独立代码与数据校验节点，绑定输入、代码、配置、原始数据及产物版本，前置于结果消费和结论验收。

### Historical context

Original task: [line 365](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L365).
Shared methods, results and evidence: [source section, lines 363–367](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L363-L367).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.

### 本轮功能验收（2026-10-07）

相关实现与独立正反例通过；全仓 730 项中 729 通过、1 项真实 tmux/Unix socket 条件测试跳过，Reader 3/3。最后上游仅修改 TASK 记录，代码/依赖无变化，按原版本证据复用并补验文档 55/55、发布门禁 29/29。详见 docs/document_architecture_validation/，此处不将程序测试说成绝对无 bug 或生产部署证明。统一 Git 发布仍由 DOC-04 跟踪。
