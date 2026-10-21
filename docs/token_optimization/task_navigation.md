# 摘要优先导航与文档变更增量

2026-10-21 落地两项针对“主 AI 续跑/派发重复读取”的机制，均为吸收 npu_kernel_agent 的
「`capabilities` 只读最小视图 vs 完整冻结」分层加载与「receipt / remember-vs-recompute」模式：

## task_navigation（摘要优先导航）

主 AI 续跑/导航不必每次重读所有 `task_details/*.md` 全文。`agent_runtime.project_docs.task_navigation(root)`
返回一份有界摘要：总索引行 + 每个 detail 的派生 `Status`/`Owner`、`### 摘要` 与有界的 `## Progress` 末尾，
用于判断“该看哪个、下一步由谁继续”；只有真正推进某个任务时才打开那份 detail 全文。

- 命令行：`python -m agent_runtime.project_docs --root ABSOLUTE_PROJECT_ROOT nav`
  （`--max-chars` 默认 12000，`--progress-tail-chars` 默认 400；超预算直接失败，不截断）。
- `Status`/`Owner`/`摘要` 是派生态，仅作导航摘要，不替代受管 SQLite 账本节点状态与独立验收；
  缺失时返回 `None`，重复时 fail-closed。
- 身份/日期与索引不一致、非 canonical 索引、越界预算均报错。

## document_delta（文档变更增量）

`agent_runtime.project_docs.document_delta(current, refs)` 对两份 `project-documents/v1` 快照做对称的
SHA 级差异：`task_details`/`guides`/`advice`/`adopted_advice` 各自给出 added/removed/changed 键，
外加 `layout`/`task_index` 变化与顶层 `any_changed`。主 AI 恢复时用 `snapshot_project_docs(root)` 取当前快照、
与上一次 `document_refs` 求增量，只重读变化的指南/建议/详情，未变化条目无需重读。
`check_document_refs` 的既有行为不变（它仍做计划绑定校验并抛错），此函数是纯差异，不校验计划绑定。

## 范围与未声明项

- 本轮未跑付费 A/B 短对照（无可用后端/额度），因此**不计任何 token 节省成功数**，也不据此推断长文收益；
  机制级收益待后续真实短对照后再按既有口径验收（见 [README](README.md) 的计数规则）。
- 这只是减少重复读取的工具与说明，不改变人类指南优先级、Plan/Progress 边界、取消/授权或结果验收。
