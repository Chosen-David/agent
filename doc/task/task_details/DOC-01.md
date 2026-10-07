# [DOC-01] 实现 canonical doc/task/TASK.md 与按日期摘要、逐任务 task_details，保留旧任务ID及证据，迁移可恢复且重复执行不覆盖。

Task-ID: DOC-01
Date: 2026-10-07

## Plan

实现 canonical doc/task/TASK.md 与按日期摘要、逐任务 task_details，保留旧任务ID及证据，迁移可恢复且重复执行不覆盖。

### 实现方法

用 agent_runtime/project_docs.py 统一解析 canonical 索引与 legacy 指针；迁移生成按日期的短索引、逐任务详情及字节不变的原 TASK 归档。校验稳定任务 ID、详情路径、关联和重复执行；中断后只恢复与原快照一致的产物，不覆盖并发修改。

### 验收边界

以实际代码、输入/产物版本和独立检查记录为准；结构/哈希校验不证明所有代码无 bug，当前宿主未部署独立后台模型服务。

## Progress

### Preserved implementation and evidence

- [ ] [DOC-01] 实现 canonical doc/task/TASK.md 与按日期摘要、逐任务 task_details，保留旧任务ID及证据，迁移可恢复且重复执行不覆盖。

### Historical context

Original task: [line 356](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L356).
Shared methods, results and evidence: [source section, lines 354–362](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L354-L362).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.

### 当前进展（2026-10-07）

已实际迁移 93 项唯一任务，生成 93 份详情；旧 TASK 全文 SHA256 为 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021，归档逐字节一致，原根文件仅作跳转。guide 目录为空，未写入任何指南文件。独立检查发现的边界漏洞正在逐项修复复验；最终全量验收与 main 发布未完成。

### 并发整合补充（2026-10-07）

保留原 93 项迁移和新增 REUSE 三项后，整合 main 18e0904 的 10 项新任务，当前 canonical 索引共 106 项。既有 96 份详情字节不变；另保存上游原 TASK 全文归档 SHA256 b537d62002c8478825021eef769c6482faa0d2926d604df95467c45595e80384 及新 10 份详情，不把上游勾选当成本轮独立科学验收。

### 本轮功能验收（2026-10-07）

相关实现与独立正反例通过；全仓 730 项中 729 通过、1 项真实 tmux/Unix socket 条件测试跳过，Reader 3/3。最后上游仅修改 TASK 记录，代码/依赖无变化，按原版本证据复用并补验文档 55/55、发布门禁 29/29。详见 docs/document_architecture_validation/，此处不将程序测试说成绝对无 bug 或生产部署证明。统一 Git 发布仍由 DOC-04 跟踪。
