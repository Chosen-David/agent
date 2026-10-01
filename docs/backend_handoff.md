# 外部 Backend 交接契约

外部项目只提供它擅长的能力，不直接成为本仓库的“项目真相”。主 AI 把外部结果归一化后再交给对应 workflow 验收。

## 最小交接记录

```json
{
  "backend_id": "paperqa2",
  "backend_version": "release-or-commit-if-known",
  "task_id": "run-id/task-id",
  "request_scope": "本次让外部能力完成什么",
  "input_refs": ["公开 URL、文件 hash 或项目内路径"],
  "started_at": null,
  "completed_at": null,
  "status": "completed|partial|failed|not_run",
  "evidence": [
    {
      "claim": "外部工具返回的候选事实",
      "source": "URL / paper / page / artifact",
      "backend_confidence": null,
      "local_verification": "verified|unverified|conflict"
    }
  ],
  "artifacts": [],
  "limitations": [],
  "next_owner": "research-explore"
}
```

## 规则

- 外部 backend 的“完成”只表示它完成了分配的子任务，不等于整个 Agent 目标完成。
- 引用、数值、benchmark、路线、营业时间等进入最终交付前，按当前 workflow 的证据标准复核。
- 外部输出如果与用户材料或当前权威来源冲突，保留冲突，不自动覆盖。
- 私密论文、数据、代码不能因为 registry 推荐某项目就自动上传到第三方服务。
- repo coding backend 提交的 patch 必须经过本项目要求的测试/正确性/性能验收。
- autonomous research backend 的代码执行必须满足 registry 中的 requirements。
- 失败时记录限制并回到当前 workflow 的 bounded fallback，不递归切换多个 backend 直到失控。
