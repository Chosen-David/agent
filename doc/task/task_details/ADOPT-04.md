# [ADOPT-04] 更新接入/迭代文档，必要回归通过后刷新 main、发布并读回；核验自有监督收尾及原维护活性。

Task-ID: ADOPT-04
Date: 2026-10-07

## Plan

更新接入/迭代文档，必要回归通过后刷新 main、发布并读回；核验自有监督收尾及原维护活性。

## Progress

### Preserved implementation and evidence

- [x] [ADOPT-04] 更新接入/迭代文档，必要回归通过后刷新 main、发布并读回；核验自有监督收尾及原维护活性。

产物：`scripts/setup_codex.py`、`templates/codex_global_instructions.md`、`tests/test_codex_setup.py`、`docs/codex_adoption/`；私有部署与模型记录 `.agent-runs/codex-adoption/`。本轮先完成实际安装和安全同步，不重复创建已有云端每小时任务。

本轮验收：15 技能/259 文件已安装；新原生 Codex 实际发现并调用知识工具，39 条记录校验通过；523 项测试中 512 通过、11 跳过，论文阅读器 3/3。实现提交 `aea33c3ddfa9cce875f7e75f5147eae8a40a2ee2` 已独立读回 SHA/完整树；宿主技能同步实际成功，原 WSL/tmux 周一三五 08:00 维护存活且启用发布后同步。自有 v2 督导已独立验收并收尾；历史 ID 只保留原证据，不重标历史实验。公开记录：`docs/codex_adoption/validation.json`、`docs/codex_adoption/deployment.json`。

此文件固定在仓库根目录，由主 AI 统一维护。本轮任务来自 2026-10-06 用户指令。
其他项目使用自己的根 TASK.md，不复用本仓库任务或另建多个活跃总清单。
高频进度与运行日志放 `.agent-runs/<run_id>/`，本文件保留目标、验收和结果索引。

### Historical context

Original task: [line 34](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L34).
Shared methods, results and evidence: [source section, lines 27–67](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L27-L67).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
