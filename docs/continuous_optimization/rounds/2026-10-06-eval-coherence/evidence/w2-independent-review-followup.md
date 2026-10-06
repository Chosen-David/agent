# W2 independent runtime follow-up review

日期：2026-10-06。独立审查者：`review_wait_runtime`。

结论：**原 R1、R2 在当前审查版本均已修复；本次复查范围内未发现剩余可复现问题。** 第一份 `w2-independent-review.md` 保持原样。本文件只追加修复复查证据，不替换先前失败记录。

## 独立检查

重新读取当前四个目标文件相对 HEAD 的实现/测试差异，没有用主 AI 的修复描述替代代码检查。当前实现：

- `Store.cancel` 对转为 cancelled 的节点清除 diagnosis_required；`Engine.reconcile` 在合法完成时清除此标记。
- `review` 对 done/cancelled 节点以及整链 cancelled 屏蔽诊断标记；只在 todo/doing 或 wait_budget 原因下覆盖下一步。因此旧快照中残留的标记也不会覆盖这些终态指示，其他 blocker 的下一步不会被等待提示覆盖。
- `tick` 在派发扫描前，对 todo/doing/blocked 且已有 pending_since 的节点根据当前时间更新诊断阈值，不依赖再次调用 handler。

未改实现、测试或原报告；未进行 Git 提交、发布、网络或付费调用。本次唯一仓库写入是本文件。

## 原最小案例重放

重新执行首报告中三个临时 SQLite / prepare / ReportingHandler / review 路径，使用相同的 max_polls、max_seconds、diagnose_after_seconds 和受控时钟。额外断言重开 SQLite 后诊断状态仍一致；所有断言通过。

| 案例 | runtime status | diagnosis_required | next_step | handler 调用次数 | all_reportable |
| --- | --- | --- | --- | --- | --- |
| 一次 pending 耗尽 poll 预算后明确 cancel | cancelled | false | respect cancellation | 1 | false |
| 一次 pending 耗尽 poll 预算后通过合法证据 reconcile | done | false | verified result available | 1 | true |
| t=1000 pending，next_at=1060，t=1020 新 tick 到达诊断阈值 | active | true | main AI inspects owned job progress, external waits and resource evidence; validate any authorized acceleration against the same inputs and acceptance | 1 | false |

R1：取消与证据确认完成的状态/下一步现已一致。R2：阈值 tick 更新诊断，但仍不额外调用 handler，保留 next_at 的派发限制。

## 实际执行回归

- `python -m unittest discover -s tests -p 'test_task_waiting.py' -v`：12/12 通过。
- `python -m unittest discover -s tests -p 'test_task_manifest.py' -v`：18/18 通过。
- `python -m unittest discover -s tests -p 'test_task_runtime*.py' -v`：33/33 通过。

合计63个程序测试通过，包含新增的阈值提前唤醒、取消诊断、reconcile 诊断回归，以及原有预算、取消、持久化、并发 claim、lease fencing 与 scheduler 回归。独立最小重放在上述计数之外，不冒充新增正式测试。

## 证据身份与边界

HEAD：`e8ee3dca5dc8cd076fc031dd4510dabde214e046`。复查结束时 SHA256：

| 文件 | SHA256 |
| --- | --- |
| agent_runtime/core.py | 47dd90f76e42679e4c06c69706c0d2a032cb8df14d7e1b0c2bedb26f96e78827 |
| agent_runtime/task_manifest.py | fc3d285cb87e25674b0adc28802bd9db5db74e8f5210e0a92ba338b663a7b3b1 |
| tests/test_task_waiting.py | 3552dc89029001957d2a5d8f7c82163e89ca939bc0655bf335e302482f106836 |
| tests/test_task_manifest.py | 81775c64a4f524d2359fa72a7296ac42b198cbe9bf53ef05d63c8928d4a34791 |

诊断状态在有效 tick 更新；没有新 tick 的只读 snapshot 不承诺实时计算 elapsed。此复查不主张 scheduler 保证在阈值精确唤醒，也不证明实际服务器、tmux/SSH、真实模型执行或长期运行收益。仍不是各角色真实模型任务发布门禁。
