# npu_kernel_agent 设计吸收记录

来源：内部仓库 `ssh://git@git.sankuai.com/~zhangchenxu06/npu_kernel_agent.git`（分支 `beta`，commit `84df115`）。
这是吸收其编排设计到本库的记录，不复制其 NPU 领域代码、skill 或交付物；SGLang 依旧不在范围内。

npu_kernel_agent 的核心分工：**LLM 子进程只负责“理解需求/设计/写码/提出假设”，确定性程序负责
doctor、schema 校验、编译、oracle 对比、计时、best-guard、STATE.json、打包与 verify**。状态以
`STATE.json` 为单一真相，阶段机按有序元组幂等重放，resume = 重读状态 + 跳过已完成阶段。

## 10 条可移植设计 → 本库对照

| # | npu 设计 | 本库现状 |
|---|---|---|
| 1 | 每个结果带 `next{action,command,reason}` 单一可执行下一步 | 缺（结果只有 `scope` 文本） |
| 2 | `STATE.json` 有序阶段机 + 幂等重放 | 等价：SQLite ledger + `task_supervisor`/`task_manifest` |
| 3 | 确定性 gate 主宰真相，agent 只提假设 | 等价：`result_validation`/`verify_experiment_result` |
| 4 | 不可变 prepare-review + 快照哈希 + 审批回执 | 等价：`plan_review` + `dual_main_workflow` |
| 5 | 结构化 intake（`NEEDS_CONFIRMATION` + ≤5 选项补问） | 缺 |
| 6 | verified handoff + 接收端复验 | 等价：`check_handoff_basis`/`validate_handoff` |
| 7 | 单飞后台任务 + 进程身份存活判定 | 部分：tmux supervisor 幂等启动，无 `/proc` 存活判定 |
| 8 | 统一 artifact 索引（role/category/status/required/mutable） | 缺（结果复用有 `result_store`，但无统一分类索引） |
| 9 | ledger 迭代协议 + 日志/行数一致性校验 | 等价：SQLite ledger + `done_when` 谓词 |
| 10 | 原子哈希「记住 vs 重算」记忆纪律 | 等价：`atomic_write` + `snapshot_project_docs` + receipt |

## 本轮已吸收（已推送）

- **分层加载**（#4 的只读侧）：`agent_runtime.project_docs.task_navigation` 摘要优先导航 +
  `workflows/project_document_workflow.md` 的续跑指引。见 [task_navigation](token_optimization/task_navigation.md)。
- **remember-vs-recompute / receipt**（#10 的增量侧）：`document_delta` 只重读变化文档。
- **后台任务进程身份**（#7）：`task_supervisor.read_process_starttime` + live.json 的 `starttime` 字段，
  `status` 用 `/proc/PID/stat` 校验心跳写者仍是同一进程，防 PID 复用误判。
- **统一 artifact 索引**（#8）：`agent_runtime.artifact_index.build_artifact_index` 一趟扫描、
  按确定性 category/mutable 分类、`required` 缺失/匹配，`diff_artifact_index` 哈希级对称增量。
- **结构化 intake**（#5）：`agent_runtime.intake.build_intake`/`apply_intake`，`NEEDS_CONFIRMATION`
  ≤5 选项补问 + 答案重注入 + 完整性重检，不猜不补。
- **`next{action,command,reason}` 尾注**（#1）：`agent_runtime.next_step.attach_next`/`validate_next`
  的校验三元 schema 原语，结果对象按需挂载，不覆盖既有 `next`。

## 剩余可移植项

10 条均已映射或吸收；#1/#5/#7/#8 本轮落为独立模块或监督器增强，#2/#3/#4/#6/#9/#10 与既有
SQLite ledger、`result_validation`、`plan_review`、`check_handoff_basis`、`atomic_write` 等机制等价，
不重复实现。独立结果验收仍待可信宿主后端。
