# 项目任务

此模板用于当前项目的 `agent_doc/task/TASK.md`，不是仓库根的第二份活跃清单。
尚未填写已授权任务；主 AI 根据用户目标建立稳定 ID 和详情，按日期简洁登记。

下列为格式示例，不是待执行要求：

```markdown
## 2026-10-07

- [ ] [T1] 用户指定的目标 ([详情](task_details/T1.md))
```

日期是任务来源/组织日期，不自动表示完成日期。索引行只放一条简洁目标（[ID] 后一句）；每项方法、验收、进度、证据和恢复条件写对应 `task_details/<ID>.md` 的「摘要 / 沙箱 / 目标与验收 / 实现方法 / 进度」，不在索引堆日志。detail 开头用 `Status`/`Owner` 标注派生状态与唯一作者（枚举见 `agent_doc/task/README.md`）。
人类指南位于 `agent_doc/guide/GUIDE.md`，AI 只读；提案与取舍记录位于 `agent_doc/advice/`。
