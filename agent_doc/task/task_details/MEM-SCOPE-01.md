# MEM-SCOPE-01

## Plan

同SYSTEM-99，基线7e5c76835ef9a32194017316759318143f6a487f。reconcile newer_sibling_in_scope仅读scope[0]，漏计其他共享scope的新条目。改遍历全部scope，按id去重；保持只读候选提示，不自动失效或更正，不改变known correction权威、字段/预算/原contradictions提示。普通低风险诊断修复按轻量回归，独立SQLite并发快照问题暂不重构。

验收：真实SQLite固定时间的旧条目first/shared、新shared、新first/shared及无关条目；逆序scope输出计数均2、跨scope不重复，过滤shared结果同一，并确认条目不变。先保留失败，再跑记忆/交接相关3.9/3.12及-O；不主张吞吐/模型质量或整批完成。发布前fetch并保留并发提交，普通发布、远端回读。

## Progress

- 首版夹具遗漏evidence=verified，默认candidate而非active，原双failure保留但不算生产复现。修正后同新增1项测试仅scope第一项不同出现1failure：旧实现计数1，全部共享范围预期2；反向scope计2，证明顺序依赖。

- 修后3.12/3.9各58项通过5.514/5.440s、-O专项1通过；条目及过滤语义检查通过。见[证据](../../advice/MEM-SCOPE-01.md)。只读诊断轻量回归，不主张独立模型/质量/性能或整批完成；并发快照仍待单独设计，发布回读另核。
