# 人类优先的任务命令行

`python -m agent_runtime.collaborative_flow` 串行连接讨论、任务规划、环境 Skill、实现和任务验收。默认 `<人类-AI模式>`，显示问题后等待约 10 分钟；未回复则关闭当前输入提示并进入 `<双AI模式>`。时间粒度不是验收重点，恢复后不重新开始整个等待期。

```bash
.venv/bin/python -m agent_runtime.collaborative_flow \
  --project-root /absolute/project --workflow-root /absolute/agent \
  --project project_name --task-id TASK-01 --prompt '用户任务原文' \
  --adapter /absolute/trusted_host.py --output /tmp/task-01-evidence
```

也可用 `--prompt-file /absolute/project/TASK.md` 读取项目内已有任务文件，后续核对其内容版本；已保护的旧任务仍按原账本恢复，不另开入口降级。

单题支持数字选项或自由文本；多题支持 `{"question-id":"answer"}`，`/cancel` 取消。`--status` 读取持久状态；`--answer '{"question-id":"new detail"}'` 可恢复并提交人类反馈；`--cancel` 记录取消。此进程运行时负责等待，并在双 AI 模式于检查点调用审查者；退出后不声称有后台监督器。已有 tmux/任务监督器可管理这个前台命令，必须另核验真实进程。输入断开不会冒充人类答复，恢复读取原截止时间。

## 宿主接口

沿用显式可信 Python adapter 的接入方式，不从 prompt、计划 JSON 或模型输出导入代码。adapter 提供 `build(root, task_id)`，返回具备以下方法的对象：

| 方法 | 输入与结果 |
| --- | --- |
| `discuss(state)` | 读取项目真实上下文，返回 `summary` 和可选 `questions`；可以先写任务验收脚本。每题包含 id/question/options、allow_free_text 和 kind（implementation/business/permission/budget） |
| `plan(state)` | 返回可审阅 `summary` 和 `steps`；每步 id/depends_on，依赖只能指向前面的步骤。应交代要求、选择依据、风险、验收和错误假设，不要求模型内部完整推理 |
| `implement(payload)` | 主 AI 唯一代码写入者；输入含 prompt/answers/plan/step、实际 environment、已加载 Skill 正文及哈希、project_root 和 test_binding。返回可 JSON 序列化结果 |
| `planner_identity(payload)` | 可信宿主确认主模型实际调用身份：invocation_id/context_id/host_source/provider_id/model_id |
| `review(request)` | 独立上下文、不同实际模型返回 `{review, proof}`；review 使用既有完整 full_review/verdict 协议、原七项检查加 spec_compliance/code_quality；讨论答案放 verdict.answers |
| `authenticate(request, review, proof)` | 独立核验实际调用记录，返回既有 ReviewSession 所需的精确请求/响应哈希、两个身份、fresh_context 和 budget_valid |

控制器约束受支持入口的执行顺序，不是操作系统沙箱；讨论/规划阶段的写入应由宿主限制在任务测试与受管计划，审查者只读正式代码。

宿主还要提供规范 `reviewer_model_id`。模型身份取自实际调用记录，不接受模型自报；别名由宿主解析。缺后端、认证失败、同模型或预算耗尽均 blocked，不伪造审查上线。仓库的自动测试使用明确标注的合成宿主，未安装生产模型后端。

审查 AI 在讨论、验收设计、每个多步骤任务的完成点、最终验收参与；程序保存状态和控制执行。审查 AI 不直接拥有代码写权限，不通过“同意”赋予主 AI 新权限。宿主负责真实工作树隔离、工具授权、请求费用和实际调用期限；此 Python 接口不能中断任意宿主函数。

## 验收与环境路由

实现前，宿主必须在 `WORKFLOW_ROOT/agent_doc/<project>/test/<task-id>/` 准备非空 `suite.json` 和实际脚本。沿用统一检查格式，origin 绑定目标项目；规格与错误假设写进任务详情。实现前后校验整个任务测试目录的内容指纹，测试变化必须重新规划。

程序探测 Python/解释器、平台、CPU、GPU/驱动及 nvcc；驱动输出和 toolkit 分开记录，工具缺失为 unknown。加载现有 `research-implement-optimize`；实际发现 GPU 时额外加载 `gpu-experiment-dispatch`，将正文和环境一并传给实现宿主。H20 等型号是环境输入，不凭名称捏造专用 Skill，也不因加载 Skill 就宣称已安装 CUDA 或代码高性能。真实加速需任务自己的基线、性能脚本及非退化标准。

验收直接调用：

```bash
.venv/bin/python scripts/project_test.py --workflow-root /absolute/agent \
  --project project_name --target /absolute/project --task TASK-01 \
  --output /tmp/task-01-checks
```

`--task` 只运行指定目录的清单；不传则保留原项目级检查。报告仍绑定目标版本、内容、脚本和原始日志，拒绝零 unittest、跳过、超时及变化的输入。轻量来自缩小到当前任务的必要检查，不意味着这些检查覆盖整个仓库。

失败进入 repair，命令行最多自动返修两次；单次审查响应限两分钟（宿主负责实际中断），双 AI 整个任务最多六次审查调用，恢复和返修不重置计数。长任务超出预算需要显式重新规划。关键业务、预算或权限问题即使超时也保留人类决定，不让 reviewer 自动批准。

## 可见规划与恢复边界

任务详情写在目标项目 `agent_doc/task/task_details/<task-id>.md`，唯一索引仍为 `agent_doc/task/TASK.md`。不会覆盖其他作者的既有详情或改人类 guide；已有受保护任务继续使用原审核/恢复账本，不能经本入口降级。详情保存可审阅决策摘要和进度，不是内部 CoT。

状态在目标 `.agent-runs/collaboration/`，写入检查版本并串行加锁。保存外部动作开始标记；动作异常或结果不明时不自动重放。已确认实现结果可恢复，环境/Skill/测试变化要求重新规划。晚到的人类反馈使旧计划失效；若宿主动作仍在进行，先记录反馈并 blocked，待宿主核对副作用，不声称旧进程已取消。取消也不能杀掉未接入控制的外部进程。

`done` 表示本次任务测试通过，双 AI 模式还要求当前审查通过；不是人类批准、一般正确性证明或未实测的性能收益。测试结果属于对应快照，写入收尾进度不追溯改变原始报告。
