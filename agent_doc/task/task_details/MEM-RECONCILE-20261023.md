# MEM-RECONCILE-20261023: 记忆自动对齐与过时记忆清理

## Plan

1. 分析当前记忆管理机制的两层架构与清理空白
2. 添加记忆新鲜度评分（staleness signal）
3. 实现 `reconcile` 子命令：自动识别潜在过时/矛盾记忆，给出 review 建议
4. 跨会话记忆 (.md) 与项目记忆账本的自动对齐
5. 独立测试 + 推 main
6. 纳入 1h 轮询迭代

## Progress

### 2026-10-23 19:00 分析完成

**两层架构**：
- 项目记忆账本 (SQLite)：immutable ledger, status: active/candidate/stale/superseded, 手动 correct 触发传播
- 跨会话记忆 (.md)：项目级事实的精炼摘要，手动维护

**空白**：
- 没有自动过时检测 — active 条目一直 active 直到有人手动 correct
- 没有压缩/对齐 — 账本只增不改，跨会话 md 没有与账本对齐
- cross-session .md 没有版本/过期标记

**设计约束**（明确遵循）：
- NEVER delete entries from the immutable audit ledger
- NEVER VACUUM or compact the ledger
- Reconcile = 只读分析 + 建议；不修改 ledger

### 2026-10-23 19:30 reconcile 子命令已实现

**新增 `MemoryLedger.reconcile(scope, detect_contradictions, max_chars)`**：
- **dependency_staleness**：active 条目传递依赖 superseded/stale 条目（_transitive_ ancestor 检测）
- **newer_sibling_in_scope**：同 scope 内存在更新的 active 条目（时态衰减信号）
- **multiple_confirmed_in_scope**：同 scope 多条 user_confirmed 共存（矛盾候选，可选开启）

**实测结果**（合成 ledger 验证）：
- 正确识别 `old-perf` 为 potentially_obsolete（同 scope `perf` 有 `new-perf`）
- 正确识别 `perf` scope 内双 confirmed 矛盾
- `_revise` 已传播的 staleness 不再重复标记（无冗余信号）

**实现细节**：
- 只读，不修改 ledger，不删除条目
- 使用缓存的依赖边构建 transitive ancestor map（避免多次 DB 查询）
- CLI: `python -m agent_runtime.project_memory --root <dir> reconcile [--scope S] [--detect-contradictions] [--max-chars N]`
- 纳入 `bounded_read` max_chars 溢出保护
