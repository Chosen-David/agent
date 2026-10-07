# [SYNC-03] 通过相关回归，刷新远端并非强制发布、读回完整树、同步本机技能；核验本轮督导收尾和既有 tmux 维护活性。

Task-ID: SYNC-03
Date: 2026-10-07

## Plan

通过相关回归，刷新远端并非强制发布、读回完整树、同步本机技能；核验本轮督导收尾和既有 tmux 维护活性。

## Progress

### Preserved implementation and evidence

- [x] [SYNC-03] 通过相关回归，刷新远端并非强制发布、读回完整树、同步本机技能；核验本轮督导收尾和既有 tmux 维护活性。

实现：`scripts/setup_codex.py`；回归：`tests/test_codex_setup.py`；公开证据：`docs/codex_adoption/round2/`；私有运行：`.agent-runs/codex-sync-preflight/`。最终勾选属于收尾修订，运行中保持本文件稳定；旧督导报告保留其源快照和哈希。

SYNC 验收：合入并发通信改动后全仓 542 项（531 通过、11 跳过）、reader 3/3；13 项安装器回归全部通过。实现提交 `43195db3c60a87b7b2007b1676eb2d1e149fb44e` 已独立读回 SHA/完整树，本机同步和 --check 成功；v3 督导全部要求可报告、monitor stopped/live false，原知识维护 live true。勾选为督导退出后的收尾修订，报告绑定保留的旧 TASK 源快照，不宣称字节相同。并发 EFF 任务/状态由原负责人维护，本轮只核对其已发布祖先与不可变证据。证据：`docs/codex_adoption/round2/publication.json`。

### Historical context

Original task: [line 21](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L21).
Shared methods, results and evidence: [source section, lines 15–26](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L15-L26).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
