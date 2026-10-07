# [DOC-04] 完成独立正反例、实际架构链和全量回归，合并本轮AIK/VEX后刷新main统一发布与远端核验。

Task-ID: DOC-04
Date: 2026-10-07

## Plan

完成独立正反例、实际架构链和全量回归，合并本轮AIK/VEX后刷新main统一发布与远端核验。

### 实现方法

独立冻结正反例并回放实际迁移；执行临时 Git/安装器/运行时与完整仓库回归。整合之前未发布的 AIK/VEX 与当前 main，绑定最终文件、任务和验收，再以非强制更新统一发布并独立读回；此前失败保留，不发布未验收版本。

### 验收边界

以实际代码、输入/产物版本和独立检查记录为准；结构/哈希校验不证明所有代码无 bug，当前宿主未部署独立后台模型服务。

## Progress

### Preserved implementation and evidence

- [ ] [DOC-04] 完成独立正反例、实际架构链和全量回归，合并本轮AIK/VEX后刷新main统一发布与远端核验。

用户2026-10-07明确要求完整架构和实现细节服务新doc结构，并在全部完成后一起推送main。doc/guide只由人工发布，AI不创建或编辑其中的文件；advice是待评估意见，不自行覆盖guide或授予新权限。

### Historical context

Original task: [line 359](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L359).
Shared methods, results and evidence: [source section, lines 354–362](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L354-L362).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.

### 当前进展（2026-10-07）

已实际迁移 93 项唯一任务，生成 93 份详情；旧 TASK 全文 SHA256 为 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021，归档逐字节一致，原根文件仅作跳转。guide 目录为空，未写入任何指南文件。独立检查发现的边界漏洞正在逐项修复复验；最终全量验收与 main 发布未完成。

### 并发整合补充（2026-10-07）

保留原 93 项迁移和新增 REUSE 三项后，整合 main 18e0904 的 10 项新任务，当前 canonical 索引共 106 项。既有 96 份详情字节不变；另保存上游原 TASK 全文归档 SHA256 b537d62002c8478825021eef769c6482faa0d2926d604df95467c45595e80384 及新 10 份详情，不把上游勾选当成本轮独立科学验收。

### 907 上游合并与发布候选 v2（2026-10-07）

最新 main 9078908 的124路径并发增量已保留；6项新任务经隔离迁移加入，canonical共115项。迁移时原109份详情逐字节不变；本次仅DOC-04/AIK-03/VEX-03追加Progress，109份稳定Plan不变。文档55、发布29、插件1、Markdown14项通过。原全仓730/Reader3按未变化实现范围复用，改变语料另作独立差异验证；索引测试修正候选/已发布计数并保留首次4失败。
当前报告：docs/document_architecture_validation/release-summary.json；独立v2验收和精确Git对象/ref发布、远端读回仍待完成。保持任务未勾选，不把本地验收称远端已发布。

### fd9012 最新并发补充（2026-10-07）

随后main新增60路径元数据/证据和蝾螈candidate，已无损整合；追加3项任务后共118项。全部既有published字节与运行时不变，最终77published+2candidate；限定候选排除/索引补验后复用907检索与已有实现验收。最新上游未完成的EK-122522-03保持未完成。发布与远端读回仍待同一合并候选完成。

### f9898df 上游去重与 v3 合并候选（2026-10-07）

最新main已独立发布AIK两卡并完成收尾，按其真实回执保留，不再称AIK未发布。本轮整合矩阵知识和上游文档/测试变更，120任务、78published+2candidate；118稳定Plan不变。128项针对性检查通过，旧全量/Reader仅限定未变范围复用，当前检索/未验证范围见release-summary与upstream-v3报告。DOC/DATA/REUSE/VEX合并发布仍待权限、实际Git发布和独立远端读回；本任务保持未完成。

### 013cfa1 并发收束与 v4 候选（2026-10-07）

只整合已发布上游46路径和MATH-19..22，124任务、80published+2candidate。120稳定Plan及142实现/测试/工作流依赖不变；95项针对性检查通过，旧全量与Reader限定复用。AIK已发布状态和原回执不变；独立副本SEM候选不纳入。当前范围与raw8行/上游叙述21题的差异见v4报告。实际Git发布及独立远端读回仍待完成，保持本任务未勾选。

### 21cb987 候选增量与 v5 收束（2026-10-07）

仅整合上游候选/证据与3项任务，127任务、80published+3candidate。124稳定Plan、142实现依赖和全部原published文件不变；10项索引与6组代表排名检查通过，旧索引过期拒绝及0更新刷新可复核，既有分数按范围复用而不重测。五个二进制对象已上传，精确tree/commit/ref与远端读回尚待发布方完成。本任务保持未勾选；不扩展科学或SEM范围。

### a52e95e 最终 v6 差异收束（2026-10-07）

仅保存28项最新上游增量与3项已完成历史任务；当前130任务、127稳定Plan不变、81published+3candidate。10项索引/文档与插件检查通过；实现与历史验收范围不变。紧凑证据引用原tree/回执，不复制整份库存；无新设计/科学/SEM工作。五个二进制对象可复用，最终commit/ref发布与远端读回仍待发布方完成。
