# 串行协作任务命令行

`python -m agent_runtime.collaborative_flow` 串行连接讨论、任务规划、环境 Skill、实现和任务验收。新 CLI 任务默认 `dual-ai`，一位主模型提出代码修改，另一个不同模型只读审查。`--mode human` 进入人类讨论；显示问题后等待约 10 分钟，未回复则进入双 AI 讨论。业务、权限和预算问题仍等待人类决定。已有任务保持原模式和预算；Python API `Flow.create()` 保留 human 默认值。

## 内置 Codex 后端

先安装并登录支持 app-server 的官方 Codex CLI。本机验证版本为 0.169.0；旧版 0.114.0 无法读取当前 `service_tier=priority` 配置。可使用独立用户目录安装新版，避免改动现有全局客户端与账号配置。运行时仅使用已有登录，不保存账号令牌。

配置一次，指定**原生 Codex 可执行文件**（Windows 为包内 codex.exe，不能传 codex.ps1/cmd）及账号实际可用的不同模型：

```bash
python -m agent_runtime.codex_host --profile /absolute/user/runtime.json \
  --codex /absolute/codex --writer-model MODEL_A --reviewer-model MODEL_B
python -m agent_runtime.codex_host --profile /absolute/user/runtime.json --probe
python -m agent_runtime.collaborative_flow \
  --project-root /absolute/project --workflow-root /absolute/agent \
  --project project_name --task-id TASK-01 --prompt '用户任务原文' \
  --backend codex --runtime-profile /absolute/user/runtime.json \
  --write-path src/example.py --context-path README.md --trust-project-code \
  --output /tmp/task-01-evidence
```

Windows 同样使用 `python -m ...`，参数传绝对 Windows 路径；PowerShell 将示例写成一行或用反引号续行。原生文件可在安装目录用 `Get-ChildItem -Recurse -Filter codex.exe` 定位。本机使用现有 ChatGPT 登录，主模型 `gpt-6.1-sol`、审查模型 `gpt-6-astra`；他人使用自己的账号可用模型，不保证这些名称对所有账号开放。

`--probe` 实际调用两个模型并保存服务端身份和完成状态；单纯安装或写配置不等于已启用。默认 profile 为 `~/.codex/chosen-agent/runtime.json`。命令哈希固定，升级 executable 后必须显式协调 profile；已有任务的模型、权限路径和预算绑定不能静默替换。

两个模型均以只读 sandbox、禁用工具、独立上下文运行。主模型返回完整文件替换提案，由可信宿主校验路径和原文件哈希后写入。`--write-path` 可重复指定源文件；guide、测试、受管任务目录、Git 和运行状态禁止成为提案目的地。调用失败计入持久预算，异常工具、同模型、过期响应或签名不符均阻断。测试清单必须预先存在，内置后端不自动生成或修改验收。

宿主读取实际配置，在线程配置中逐一禁用继承的 MCP server/plugin，关闭 shell、多 agent、apps、web search 和本地图像工具；有生命周期 hook 的配置阻断，只读模型不继承其额外执行能力。配置字段参照[官方说明](https://learn.chatgpt.com/docs/config-file/config-reference)。

`--trust-project-code` 明确授权以当前 OS 用户执行**可信项目代码、测试及其导入**，并非 OS 沙箱；未声明时阻断。只读模型限制不隔离测试进程，不应将不可信项目代码交给此入口。账号、profile 和 HMAC 回执在项目之外；签名认证可信宿主的观察，不抵御已控制该用户或客户端的攻击者。回执不保存模型推理内容。

## 人类讨论与模式切换

```bash
.venv/bin/python -m agent_runtime.collaborative_flow \
  --project-root /absolute/project --workflow-root /absolute/agent \
  --project project_name --task-id TASK-01 --prompt '用户任务原文' \
  --mode human \
  --adapter /absolute/trusted_host.py --output /tmp/task-01-evidence
```

也可用 `--prompt-file /absolute/project/TASK.md` 读取项目内已有任务文件，后续核对其内容版本；已保护的旧任务仍按原账本恢复，不另开入口降级。

单题支持数字选项或自由文本；多题支持 `{"question-id":"answer"}`，`/cancel` 取消。`--status` 读取持久状态；`--answer '{"question-id":"new detail"}'` 可恢复并提交人类反馈；`--cancel` 记录取消。此进程运行时负责等待，并在双 AI 模式于检查点调用审查者；退出后不声称有后台监督器。已有 tmux/任务监督器可管理这个前台命令，必须另核验真实进程。输入断开不会冒充人类答复，恢复读取原截止时间。

显式切换同一任务：沿用原命令的项目与任务参数，加 `--switch-mode human --reason '需要人类讨论' --status`；恢复双模型用 `--switch-mode dual-ai --reason '恢复独立模型复核' --status`。切换增加 revision、归档旧计划并撤销旧批准，保留回答、问题、审查与返修预算；不会新建替代任务。进行中或结果不明的外部动作、已取消/完成任务和旧受保护账本不能借切换绕过。`--mode` 仍只声明初始模式，不能暗中更改已有任务。

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

宿主还要提供规范 `reviewer_model_id`。模型身份取自实际调用记录，不接受模型自报；别名由宿主解析。缺后端、认证失败、同模型或预算耗尽均 blocked。普通自动测试使用明确标注的合成宿主/故障服务；真实账号验证另外运行 `--probe` 和任务闭环。

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

若只是最终审查证据不完整，修复后用 `--retry-final-review --reason '说明'` 复核原报告与当前源码，完全一致才重试，避免再改已通过的代码。必要时显式 `--add-review-calls 2 --reason '说明'` 扩展原账本上限，每次至多追加六次，保留已用次数和变更理由；内置 host 的持久总调用上限仍独立生效。输入变化必须重新验收，进行中动作不能借扩预算重放。

最终重审还绑定原 revision、计划、有效回答、执行上下文、完整任务测试内容及已认证设计批准。重新规划会归档旧验收并撤销重审资格；外部 WORKFLOW_ROOT 的测试变化同样必须经过新设计批准和实际执行。

## 可见规划与恢复边界

任务详情写在目标项目 `agent_doc/task/task_details/<task-id>.md`，唯一索引仍为 `agent_doc/task/TASK.md`。不会覆盖其他作者的既有详情或改人类 guide；已有受保护任务继续使用原审核/恢复账本，不能经本入口降级。详情保存可审阅决策摘要和进度，不是内部 CoT。

状态在目标 `.agent-runs/collaboration/`，写入检查版本并串行加锁。保存外部动作开始标记；动作异常或结果不明时不自动重放。已确认实现结果可恢复，环境/Skill/测试变化要求重新规划。晚到的人类反馈使旧计划失效；若宿主动作仍在进行，先记录反馈并 blocked，待宿主核对副作用，不声称旧进程已取消。取消也不能杀掉未接入控制的外部进程。

测试报告为 blocked（包括超时）或缺报告时保留 acceptance 的 inflight 标记，不进入自动返修；测试子进程的后代可能仍运行，必须显式核对原动作。内置 host 在实际测试启动边界再次检查执行信任，API/已完成步骤的恢复也不能跳过；自定义可信 adapter 仍由其提供者负责执行授权。

Windows 与 POSIX 使用各自原生排他文件锁。Windows 输入轮询支持控制台、管道与 EOF，不对管道使用仅支持 socket 的 select。宿主在写入前再次核对任务版本与取消状态；多文件替换预检全部提案，每个文件原子写入，整批并非文件系统事务，写入中断仍按结果不明处理。确认未发生写入的提案预检拒绝进入 repair，计数不清零。

讨论包只包含当前决定、最后 verdict 与历史哈希引用，不反复嵌套完整审查记录。完整历史保留在原状态/回执中；任务 Markdown 仅记录计划、有效回答及最近事件摘要。模型输入超过 256KB 会要求明确缩小上下文，不静默截断要求。

验收快照明确区分生产输入与控制器进度：仅在文件字节仍匹配控制器上次记录的哈希时，排除本任务详情和唯一 TASK 索引的进度变化，报告记录这些路径/哈希。Guide、其他文档、源码和测试继续参与校验；外部改动控制器文档也要求协调。旧验收在返修讨论中标为历史，给出其是否匹配当前源码的结果；旧通过报告不能替代修复后的新验收。

每项实际执行的检查在报告中绑定原始 `.log` 的 SHA-256，最终审查包包含其完整 UTF-8 输出，并在审查完成后重新核对日志。缺失、修改或超过输入预算的证据阻断最终批准，不能只凭 exit code 放行；历史日志不可用会明确标记，允许继续规划新的验收。超大输出应改成范围明确、输出有界的检查，不静默截断日志。

`done` 表示本次任务测试通过，双 AI 模式还要求当前审查通过；不是人类批准、一般正确性证明或未实测的性能收益。测试结果属于对应快照，写入收尾进度不追溯改变原始报告。

GPT/Codex 新任务可显式传 `--mode dual-ai` 以便命令自身表达协作策略。缺真实不同模型宿主仍 blocked；设置模式、安装 Skill 或通过合成测试均不代表双模型已运行。此入口不改 ChatGPT/Codex 的账号级设置，当前聊天采用何种模式仍由宿主实际执行决定。
