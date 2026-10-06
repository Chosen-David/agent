# Agent 仓库任务总清单

此文件固定在仓库根目录，由主 AI 统一维护。本轮任务来自 2026-10-06 用户指令。
其他项目使用自己的根 TASK.md，不复用本仓库任务或另建多个活跃总清单。
高频进度与运行日志放 `.agent-runs/<run_id>/`，本文件保留目标、验收和结果索引。

- [x] [T1] 实现 tmux 托管监督与同盘恢复
  - 产物：`agent_runtime/task_supervisor.py`。
  - 验收：worker/guard 真实进程测试、SIGKILL 恢复、取消和自有监控清理；tmux 实际会话能力受当前容器限制，明确列于验证记录，未声称用户服务器已部署。
- [x] [T2] 自动/手动任务编排接入根 TASK.md，逐任务核对结果和剩余工作
  - 产物：`agent_runtime/task_manifest.py`、`templates/TASK.md`、`workflows/task_supervision_workflow.md`。
  - 验收：根清单、全量映射、版本变化、结果报告与独立证据要求；数据及剩余项进入 progress/final report。
- [x] [T3] 提供 Claude Code 快速 setup、主 AI、Skills 与子 Agent 接入
  - 产物：`setup.py`、`SETUP.md`、`CLAUDE.md`。
  - 验收：14 Skills 与 14 子 Agent、完整主调度、重复安装/检查/卸载和已有文件保护。当前环境没有 Claude CLI，模型行为未实测。
- [x] [T4] 扩展文件管理 Agent 并核对跨 Agent 交接
  - 产物：`workflows/code_organization_workflow.md`、`plugins/research-assistant/skills/code-organization/`。
  - 验收：任务前目录规划、逐项产物登记、生产者/消费者、单一根 TASK、活跃路径保护、独立合成项目使用记录。
- [x] [T5] 完成回归并推送 main
  - 验收：保留真实测试计数、跳过项与限制；同步插件引用；push 前再次 pull，远端 SHA 读回一致。

## 结果与边界

本轮结果索引：`docs/tmux_supervisor_validation.md`。
真实 tmux/SSH 断链测试、目标服务器部署和真实模型 host adapter 由主 AI 在目标服务器接入时完成；当前没有该服务器的连接信息，不记为已验证。代码实现的完成不等于服务器部署或线上 Agent 效果证明。

主 AI 每次启动/恢复、委派前、任务结束和最终汇报前先读本文件，再读最新运行状态。

本轮实现已发布并读回核对：`6f05166a4aad16e531f7717ab3cf07c02b3bc187`。测试与宿主限制详见上述验证记录；这条收尾记录不将未执行的目标服务器验证标为通过。
