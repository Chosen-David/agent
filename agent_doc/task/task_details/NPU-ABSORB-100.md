# NPU-ABSORB-100 吸收 npu_kernel_agent 剩余可移植设计

Task-ID: NPU-ABSORB-100
Date: 2026-10-21
Status: blocked
Owner: main-ai

## Plan

### 摘要

- 把 npu_kernel_agent 剩余的 4 项可移植设计落到本库：后台任务进程身份判定、统一 artifact 索引、
  结构化 intake、确定性结果 next 尾注。每项独立实现 + 测试 + 推送 + 远端读回核对。

### 目标与验收

- 阶段A（进程身份）：task_supervisor 的 live.json 记录 starttime，status 用 /proc/PID/stat 校验，
  防 PID 复用误判；专项测试通过。
- 阶段B（统一 artifact 索引）：新模块一趟扫描 run/项目树，按 role/category/status/required/mutable
  分类，给"缺什么/变了什么"单一视图。
- 阶段C（结构化 intake）：NEEDS_CONFIRMATION 补问 schema（≤5 选项）+ 答案重注入 + 完整性重检。
- 阶段D（next 尾注）：确定性结果补单一可执行下一步，让 resume 零重推。
- 无可用模型后端：不虚构 token 节省成功数或"已让 AI 常驻"，机制级收益待真实短对照后另核。

### 沙箱 / 写入范围

- 唯一作者 main-ai；写 agent_runtime/*.py、tests/*.py、agent_doc/task/TASK.md 与 task_details/、
  docs/token_optimization/ 说明。
- 禁止写 agent_doc/guide/（人类只读）；SGLang 不在范围。

### 实现方法

- 逐项先写实现与测试，独立复核后推送，读回远端 SHA。

## Progress

### 进度与证据

- 阶段A（进程身份）：task_supervisor.read_process_starttime + live.json starttime + status 校验；
  专项 test_status_verifies_worker_process_identity_against_pid_reuse 及全部 managed_supervisor 11 项通过。
- 阶段B（统一 artifact 索引）：新增 agent_runtime/artifact_index.py（build_artifact_index + diff_artifact_index），
  确定性分类 + required 缺失/匹配 + 哈希级对称 diff；tests/test_artifact_index.py 9 项通过。
- 阶段C（结构化 intake）：新增 agent_runtime/intake.py（build_intake + apply_intake），
  ≤5 选项补问 schema + 答案重注入 + 完整性重检；tests/test_intake.py 7 项通过。
- 阶段D（next 尾注）：新增 agent_runtime/next_step.py（attach_next + validate_next），
  校验 action/command/reason 三元 footer，不覆盖已有 next；tests/test_next_step.py 5 项通过。

### 阻塞与下一步

- 四阶段代码均已实现 + 单元测试 + 推送 + 远端 SHA 读回核对；独立结果验收待可信宿主后端，
  无后端则如实 blocked，不伪称"已让 AI 常驻"或已完成独立验证。
