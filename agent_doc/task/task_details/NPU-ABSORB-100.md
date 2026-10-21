# NPU-ABSORB-100 吸收 npu_kernel_agent 剩余可移植设计

Task-ID: NPU-ABSORB-100
Date: 2026-10-21
Status: doing
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

### 阻塞与下一步

- 继续阶段B（统一 artifact 索引），再阶段C、阶段D。
