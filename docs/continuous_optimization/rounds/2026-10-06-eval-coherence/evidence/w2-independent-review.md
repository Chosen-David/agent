# W2 independent runtime code review

日期：2026-10-06。审查者：独立子 Agent `review_wait_runtime`。

结论：发现两项可复现报告/诊断问题，第一项应在验收前修正。未发现本差异直接绕过取消执行门禁、授权、持久化预算或轮转公平性的证据。这是本地程序审查，**不是各角色真实模型任务发布门禁，也不是模型效果或服务器集成验证**。

## 范围与身份

已读 AGENTS.md、prompts/decision_review.md 和根 TASK.md；按 EXECUTE 进行授权的只读审查与本地临时复现。只审查相对 HEAD 的 `agent_runtime/core.py`、`agent_runtime/task_manifest.py`、`tests/test_task_waiting.py`、`tests/test_task_manifest.py` 及必要的 scheduler/supervisor 调用者。未读取 continuous_optimization 的评审结论；未改实现、测试、checkpoint 或 Git。唯一写入仓库的文件为本报告。

HEAD：`e8ee3dca5dc8cd076fc031dd4510dabde214e046`。工作区存在并发修改；复现后读取到的 SHA256：

| 文件 | SHA256 |
| --- | --- |
| agent_runtime/core.py | 319147b6090f1074a5383735cdf6a98ef21938a9fd0d2828d7bcef79e6e3a3c1 |
| agent_runtime/task_manifest.py | 66b51351778ee2e335fa773a69da79dcc3c6a6fe2b4e48f81a3e71206b316eac |
| tests/test_task_waiting.py | 37c4265f48fee1ab8f568a857837b81ed7f9fca0ce903d6cf7af0dacbfd33603 |
| tests/test_task_manifest.py | 5f7ad9ceef8cd3e7e244c4675d5eba75b6289bb16aae9c9e92cef2ea0a461357 |

## Finding R1 — P2：诊断提示覆盖取消或已完成任务的下一步

位置：`task_manifest.py:214–216` 的无状态条件覆盖；必要调用者 `Store.cancel`、`Engine.reconcile`。新逻辑只在常规 tick 的 done 分支清除 `diagnosis_required`，取消和 reconciliation 路径保留旧值。

最小触发：一个配置 `max_polls=1` 的任务返回一次 pending，得到 blocked + diagnosis_required=true；随后明确 cancel，或提供真实通过 handler.verify 的证据调用 reconcile。两种路径均可在真实 SQLite 中复现。

实测：

| 后续操作 | runtime/node status | diagnosis_required | next_step | all_reportable |
| --- | --- | --- | --- | --- |
| 明确取消 | cancelled / cancelled | true | main AI inspects owned job progress, external waits and resource evidence; validate any authorized acceleration against the same inputs and acceptance | false |
| 合法证据 reconciliation | done / done | true | 同上 | true |

影响：cancelled 的 `respect cancellation` 和 done 的 `verified result available` 被诊断/加速指令替换；最终报告可能同时显示完成和需要继续诊断。引擎取消状态仍阻止实际重派发，因此这里没有声称直接执行越权。消费者依赖 next_step 时会收到与终态不一致的行动指示。

最小修复方向：终态的 next_step 优先于诊断覆盖；取消/reconcile 完成时清除当前诊断标记，历史等待计数可保留。加入“先触发诊断，再取消 / reconcile”的报告回归测试。现有取消测试只验证调用次数，不覆盖报告。

## Finding R2 — P2：到达诊断阈值的有效 tick 仍可能不报告诊断

位置：`core.py:337–343` 只检查 max_seconds，`core.py` pending outcome 分支才计算 diagnose_after_seconds。诊断标记不是在每次 tick 随 elapsed 更新。

最小触发：supervision min=max=60，wait_policy max_seconds=100、diagnose_after_seconds=20、max_polls=10。t=1000 第一次 pending，next_at=1060；t=1020 触发一个不同 event_id 的有效 tick。结果仍为 todo、diagnosis_required=false、next_step 为 dispatch；没有再次调用 handler。必须等到下一次成功 pending（或最终耗尽预算）才更新诊断值。

影响：诊断阈值短于 backoff/next_at 时，主 AI 维护报告错过已达到的阈值；若下一次观察只返回 retry/blocked，诊断值还会继续陈旧。调度器自身不保证在阈值精确唤醒，这不是本 finding 所要求；本问题是**已经唤醒**仍未更新。可在每次 tick 对等待节点刷新 elapsed 诊断标记而不额外调用 handler，并明确只读 snapshot 是否表示截至上次 tick 的状态。

## 可复现程序

以下在仓库根目录执行，仅用临时目录、SQLite、受控时钟和合成 handler；没有网络/模型调用：

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from agent_runtime.core import Engine, Store, Outcome
from agent_runtime.task_manifest import prepare, review, atomic_json, ReportingHandler, result_report

class H:
    idempotent = True
    required_capabilities = frozenset()
    def run(self, task, context): return Outcome('pending')
    def verify(self, task, evidence): return evidence == ['proof']

for mode in ['cancel', 'reconcile', 'threshold']:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        (root / 'TASK.md').write_text('- [ ] [T1] Work\n')
        plan = prepare(root / 'TASK.md', 'r', 'auto', 'authorized')
        task = plan['tasks'][0]
        task['action'] = 'observe'
        task['wait_policy'] = {'max_polls': 10 if mode == 'threshold' else 1,
                               'max_seconds': 100, 'diagnose_after_seconds': 20}
        plan['supervision'] = {'min_seconds': 60, 'max_seconds': 60, 'rationale': 'bounded'}
        store = Store(root / 'state.db')
        store.create(plan)
        clock = [1000.]
        engine = Engine(store, {'observe': ReportingHandler(H(), root)},
                        authorize=lambda *_: True, clock=lambda: clock[0])
        engine.tick('r', 'first')
        if mode == 'cancel':
            store.cancel('r', 'explicit stop', now=clock[0])
        elif mode == 'reconcile':
            atomic_json(root / task['report_path'], {'task_id': 'T1', 'summary': 'verified',
                'data': [{'kind': 'synthetic', 'description': 'fixture'}]})
            _, proof = result_report(root, task)
            engine.reconcile('r', 'T1', ['proof', {'task_report': proof}], 'host verified')
        else:
            clock[0] += 20
            engine.tick('r', 'threshold')
        report = review(store.snapshot('r'), root)
        node = report['requirements'][0]['nodes'][0]
        print(mode, report['runtime_status'], node['execution']['diagnosis_required'], node['next_step'])
```

## 已执行验证与未发现问题的范围

- `python -m unittest discover -s tests -p 'test_task_waiting.py' -v`：11/11 通过。
- `python -m unittest discover -s tests -p 'test_task_manifest.py' -v`：16/16 通过。
- `python -m unittest discover -s tests -p 'test_task_runtime*.py' -v`：33/33 通过。
- 总计60个已执行程序测试通过；上面独立复现发现的问题不在这些测试的覆盖中。
- 等待预算：仅 opt-in pending 成功返回退还一次 attempts；retry、异常与过期 lease 仍消耗尝试预算；poll/elapsed 耗尽进入 blocked，未观察到错误标为成功。
- 持久化/公平：游标、计数及 claim 在同一 SQLite transaction 内存储；重启测试和既有并发 claim 测试通过。轮转仍逐项检查依赖、next_at、授权和 handler；未发现新增绕过。
- 兼容：无 wait_policy 继续旧 pending 计费语义；已有计划在新 runtime 可读。新版计划的降级执行安全、旧 runtime 对 wait_policy 的支持不在此次验证范围。
- 取消：实际 dispatch 门禁与 lease fencing 的既有测试通过；R1 是新增报告指令不一致。
- 不据此主张真实 tmux/SSH、真实模型行为或长期生产效果已验证。
