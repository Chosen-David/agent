# [AIK-01] 核对推测采样分布保持与成本边界的原论文/官方版本，形成带精确前提的知识候选与反例，保留新旧工作隔离。

Task-ID: AIK-01
Date: 2026-10-07

## Plan

核对推测采样分布保持与成本边界的原论文/官方版本，形成带精确前提的知识候选与反例，保留新旧工作隔离。

## Progress

### Preserved implementation and evidence

- [x] [AIK-01] 核对推测采样分布保持与成本边界的原论文/官方版本，形成带精确前提的知识候选与反例，保留新旧工作隔离。

### Historical context

Original task: [line 340](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L340).
Shared methods, results and evidence: [source section, lines 338–343](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L338-L343).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.

### 当前整合补验（2026-10-07）

新基线 664e09e 含 46 条，加入本轮两卡后 48 条；原 92 文件和两卡字节保持一致。旧 72 个查询/后端组合零新增退化；默认上下文 22/24，领域筛选 23/24，不能沿用旧 41 条库的 24/24。A12 明确选择关联卡并读取全文后，11,326/20,000 字符内完整恢复，这不是自动恢复。统一发布仍待本轮其他要求完成。

### 最新知识基线补验（2026-10-07）

最终整合改以 main 18e0904 的 74 条为基线，加本轮两卡为 76 条；原 148 文件不变，旧 72 查询/后端组合零新增退化。当前新题默认上下文 21/24，领域筛选 23/24；已知三处缺口需要明确相关性选择和全文读取，在 20,000 字符预算内恢复，不能宣称默认全命中。报告见 docs/document_architecture_validation/knowledge/report.md；前述 41/48 条结果仍仅属于各自旧快照。
