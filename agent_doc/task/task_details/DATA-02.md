# [DATA-02] 实际运行必要的参考/边界、数值/单位/计时/异常与复现检查，失败或证据不足返回修复与重测；不得仅凭自填pass放行或承诺绝对无bug。

Task-ID: DATA-02
Date: 2026-10-07

## Plan

实际运行必要的参考/边界、数值/单位/计时/异常与复现检查，失败或证据不足返回修复与重测；不得仅凭自填pass放行或承诺绝对无bug。

### 实现方法

复用 agent_runtime/result_validation.py 与 scripts/validate_experiment_result.py 的结构/版本检查，由宿主实际可信 verifier 执行任务相关的代码逻辑、参考/边界、数值/单位/计时/异常及复现检查。保留检查范围与未测项；失败、崩溃、过期或证据不足均不得作为可用结果。

### 验收边界

以实际代码、输入/产物版本和独立检查记录为准；结构/哈希校验不证明所有代码无 bug，当前宿主未部署独立后台模型服务。

## Progress

### Preserved implementation and evidence

- [ ] [DATA-02] 实际运行必要的参考/边界、数值/单位/计时/异常与复现检查，失败或证据不足返回修复与重测；不得仅凭自填pass放行或承诺绝对无bug。

### Historical context

Original task: [line 366](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L366).
Shared methods, results and evidence: [source section, lines 363–367](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L363-L367).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.

### 本轮功能验收（2026-10-07）

相关实现与独立正反例通过；全仓 730 项中 729 通过、1 项真实 tmux/Unix socket 条件测试跳过，Reader 3/3。最后上游仅修改 TASK 记录，代码/依赖无变化，按原版本证据复用并补验文档 55/55、发布门禁 29/29。详见 docs/document_architecture_validation/，此处不将程序测试说成绝对无 bug 或生产部署证明。统一 Git 发布仍由 DOC-04 跟踪。
