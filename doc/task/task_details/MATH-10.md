# [MATH-10] 同步按需知识/插件快照、执行相关回归，刷新main发布并远端读回；保留子空间扰动接续，不修改生产停止。

Task-ID: MATH-10
Date: 2026-10-07

## Plan

同步按需知识/插件快照、执行相关回归，刷新main发布并远端读回；保留子空间扰动接续，不修改生产停止。

## Progress

### Preserved implementation and evidence

- [x] [MATH-10] 同步按需知识/插件快照、执行相关回归，刷新main发布并远端读回；保留子空间扰动接续，不修改生产停止。

MATH-10发布读回：main 16600b0ba605c1356e75c446fe497ec43fe164d1，tree 2316231f5a5424fe79c99c1393d99bc553123f3c 与本地验收树一致；非强制expected_sha保护更新。82项有限断言（含轨迹重复检查）、知识38/38、全仓472项（464通过/8跳过）、reader3/3；保留动量更慢负结果，无模型A/B或生产停止改进。子空间扰动接续已保存。

### Historical context

Original task: [line 232](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L232).
Shared methods, results and evidence: [source section, lines 229–235](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L229-L235).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
