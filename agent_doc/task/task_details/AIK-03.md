# [AIK-03] 同步知识插件、整合最新main、测试后直接发布并核对远端；不捎带旧会话未发布的大批runtime修改。

Task-ID: AIK-03
Date: 2026-10-07

## Plan

同步知识插件、整合最新main、测试后直接发布并核对远端；不捎带旧会话未发布的大批runtime修改。

## Progress

### Preserved implementation and evidence

- [ ] [AIK-03] 同步知识插件、整合最新main、测试后直接发布并核对远端；不捎带旧会话未发布的大批runtime修改。

### Historical context

Original task: [line 342](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L342).
Shared methods, results and evidence: [source section, lines 338–343](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L338-L343).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.

### 当前整合补验（2026-10-07）

新基线 664e09e 含 46 条，加入本轮两卡后 48 条；原 92 文件和两卡字节保持一致。旧 72 个查询/后端组合零新增退化；默认上下文 22/24，领域筛选 23/24，不能沿用旧 41 条库的 24/24。A12 明确选择关联卡并读取全文后，11,326/20,000 字符内完整恢复，这不是自动恢复。统一发布仍待本轮其他要求完成。

### 最新知识基线补验（2026-10-07）

最终整合改以 main 18e0904 的 74 条为基线，加本轮两卡为 76 条；原 148 文件不变，旧 72 查询/后端组合零新增退化。当前新题默认上下文 21/24，领域筛选 23/24；已知三处缺口需要明确相关性选择和全文读取，在 20,000 字符预算内恢复，不能宣称默认全命中。报告见 docs/document_architecture_validation/knowledge/report.md；前述 41/48 条结果仍仅属于各自旧快照。

### 907 上游合并与发布候选 v2（2026-10-07）

最新基线75张published+1candidate，本轮两张AIK合并后77+1；候选头足类不进入默认检索。116默认与42有界上下文查询/后端组合零新增退化；AIK默认21/24、领域筛选23/24，3处缺口经明确相关性选择读全文恢复，不能称默认全命中。继承的round2有界检索缺口仍保留；无新增科学推广/GPU或模型A/B。
当前报告：docs/document_architecture_validation/release-summary.json；独立v2验收和精确Git对象/ref发布、远端读回仍待完成。保持任务未勾选，不把本地验收称远端已发布。

### fd9012 最新并发补充（2026-10-07）

随后main新增60路径元数据/证据和蝾螈candidate，已无损整合；追加3项任务后共118项。全部既有published字节与运行时不变，最终77published+2candidate；限定候选排除/索引补验后复用907检索与已有实现验收。最新上游未完成的EK-122522-03保持未完成。发布与远端读回仍待同一合并候选完成。

### 已验证上游发布收尾（2026-10-07）

最新main f9898df已包含本任务独立发布与收尾。实现提交 `017debae0e490f350ae1364a822ea0d4b2df82cc`，远端回执 `docs/knowledge_learning/2026-10-07-ai-algorithms/publication.json` 按上游字节保留；canonical状态与实际已完成发布同步。原始上下文另存 `doc/task/legacy/TASK.efc0ca3024bd28a2d50a420270c94cf6938d2dccd1a561cff51baa748ea8c613.md`。此前本地合并候选中的pending描述仅是旧阶段记录，不再作为当前AIK/本任务未发布主张。DOC/DATA/REUSE/VEX合并发布仍独立待完成，不覆盖上游成功证据。
