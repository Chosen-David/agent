# [MATH-04] 同步插件快照、回归并重新同步main发布，核对远端；保留接续主题与未执行测试。

Task-ID: MATH-04
Date: 2026-10-07

## Plan

同步插件快照、回归并重新同步main发布，核对远端；保留接续主题与未执行测试。

## Progress

### Preserved implementation and evidence

- [x] [MATH-04] 同步插件快照、回归并重新同步main发布，核对远端；保留接续主题与未执行测试。
  - 不把已有固定角色样本当成独立抽样；只更新可复用知识，不接入生产停止/推送决策。

MATH-04发布读回：main 6aabcdf3db1375856fd63ff9a58c7d527149088d，tree eb901c288170d18010257ae21dad67ab1d346f92 与本地验收树一致，非强制expected_sha保护更新，GitHub远端HEAD已核对。知识专项38/38；全仓472项（464通过/8跳过）、reader3/3。首次3处扩库断言失败及修复保留，无生产模型收益声明。下一主题为数值迭代的收敛/残差证书，近期方差自适应候选仍待测。

### Historical context

Original task: [line 210](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L210).
Shared methods, results and evidence: [source section, lines 206–214](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L206-L214).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
