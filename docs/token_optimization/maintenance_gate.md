# 已确认事件的维护门禁

`agent_runtime.maintenance_gate.MaintenanceGate` 是显式宿主包装器，保持现有 `build()['maintain']` 接口。默认监督器/适配器不改变；安装技能不自动接管 Claude/Codex 会话，也不部署新定时器。

```python
from agent_runtime.maintenance_gate import MaintenanceGate, MaintenanceOutcome

def build(root, store, run_id):
    def observe():
        # Read current project/guide/task/code/config/evidence/advice versions,
        # owned-job notifications, user events and due review/diagnosis flags.
        return {"project_root": str(root), "run_id": run_id,
                "events": collect_current_wake_sources(root, store, run_id)}

    def maintain(report):
        outcome = process_current_events(report)
        # Only after actual handling. A submitted asynchronous job is pending.
        return MaintenanceOutcome("handled" if outcome.finished else "pending")

    return {"handlers": handlers, "authorize": authorize,
            "maintain": MaintenanceGate(maintain, observe,
                project_root=root, run_id=run_id, max_quiet_seconds=300)}
```

示例中的 collect/process/handlers/authorize 是项目宿主实现，不能从不可信任务文本加载。root 必须先解析为当前项目的绝对规范路径；观察器返回完全匹配的 root/run。现有 result/plan verifier 仍按原契约注入，示例不取消任何独立验收。

首次调用仍执行维护。仅当上次返回类型明确的 `MaintenanceOutcome('handled')`、处理前后观察一致，且同一观察未到 quiet 上限时，重复调用才返回 `unchanged`。原回调返回None、pending、错误、观察读取失败、处理期间事件变化或时钟回退均不确认；失败还使旧确认失效。重启不恢复确认，先重新维护。已有异步作业的查询必须由低成本观察器覆盖，或维持pending返回，让维护继续查询。

指纹保留报告所有字段与外部事件，只忽略 `publish()` 顶层展示用 `updated_at`；嵌套时间、deadline、证据和错误状态保留。严格JSON预检限制32层、8192节点和字符数量，最终编码≤64KiB；大检查点或无效输入报错，不截断/不伪造空事件。这些是应用级预算，不是OS沙箱或实时延迟保证。

外部事件完整性由可信宿主负责。advice变更CLI可提供一个来源，但空advice列表不等于无任务：用户指令、指南、任务/代码/配置/证据、作业通知、到期复审和诊断都须覆盖。时间推进不会自动改变哈希，观察器须明确到期标志；quiet上限只是有界补查，不允许超过项目lease/等待诊断期限。observer/clock异常使本次维护失败并由现有worker记录supervisor_error，恢复后重新处理。

门禁只控制维护回调，没有缓存审查者证明、跳过结果验收、改写任务状态或扩大授权。CPU测试覆盖状态变化/失败/边界；真实模型成本仍需固定短trace并独立验收后才报告。[监督器成本分析](supervision_cost.md)保留其他潜在热点。
