# 组合入口的 token 优化

上下文 CLI 以完整 UTF8 JSON 和平台换行为单位检查显示预算，超限不截断：

| 入口 | 默认上限 | 显式提高上限 |
| --- | --- | --- |
| `task_context.py` / `log_context.py` / `record_context.py` / `reference_context.py` | 20000字符 | `--max-chars`，最多1000000 |
| `result_store.py search/show/decide/context` | 20000字符，默认紧凑 | 子命令后的 `--max-chars`，最多1000000 |
| `project_docs.py inspect/validate` | 20000字符，默认紧凑 | 子命令后的 `--max-chars`，最多1000000 |
| `project_memory` 的 list/history/impact/check/storage | 20000字符，默认紧凑 | 子命令后的 `--max-chars`，最多200000 |

结果库、文档快照和记忆的全局 `--pretty` 须放在子命令前，缩进也计入预算。
优先按任务、记录或scope收窄读取；需完整大响应时显式提高上限。写入命令不因
读取预算在成功后报错。显示字符不是token、数据库读取量或整次会话费用；现有
SHA/依赖/独立验收门禁继续有效。下面保留历史实验及其原适用范围。

2026-10-11按用户要求完成[五轮短对照升级](five_rounds.md)，各轮已独立验收并核对main，累计14项真实成功；随后启动[每小时优化器](hourly_optimizer.md)。五项短对照总tokens分别少18152、313、231、203、181；不推广为全会话净成本或长文收益。监督维护接入[事件门禁](maintenance_gate.md)与完整的显式项目文件/advice/外部事件观察器；先前99%额度停止记录仍保留，后续新命名空间已通过真实测试。

advice会议先由宿主检查[版本变更清单](advice_meetings.md)，按新增/修改内容与未决任务决定需要读取什么；归档也检测变更，不自动授信或关闭任务。此次有SGLang提交阅读和CPU边界检查，真实模型token收益尚待短对照，不增加成功计数。

已定位的 Python 函数可用 [精确符号上下文](source_context.md) 读取完整声明和静态本地依赖，保留原 SHA/行号；动态路径保留全文。真实短测总tokens少357，不据此推断全仓或长文效果。

主会话运行期见 Claude 的[监督循环报告](session_supervision_burn.md)及本库[实际调用链与建议评估](supervision_cost.md)。前者约75%的任务列表体积减少是来源自报，本轮没有其逐请求用量，不能作为本库总token验收；本地心跳与模型回调须分开计量。

独立子任务还可用 [完整上下文派发](dispatch_context.md)：宿主核实全部依赖和父生效设置后新建线程，否则继承历史。原生短测总token少199；不把空历史响应当上下文已裁剪。

主 AI 续跑/派发不必每次重读全部 task_details：先用 [摘要优先导航与文档变更增量](task_navigation.md) 取未勾选索引行 + 派生 Status/Owner/摘要/无时间承诺的有界进度首尾片段，只对真正推进的任务打开全文；恢复时用 `document_delta` 只重读变化的指南/建议/详情。本轮未跑付费短对照，不计 token 成功数。

固定子任务的新线程还可显式排除已确认无关的技能目录条目，保留必需/未知技能和全部项目、权限规则；机器配置直接给宿主。一次相同短测少927总tokens，需真实目录差异验收，见 [技能范围](skill_scope.md)。

两版文件的小改对比可用自包含完整行变更：完整旧版始终在同一输出内，新版能精确恢复且更短才用splice，不靠持久化“模型已读”提示。首个字符偏移候选实际总token增加246已拒绝；整行候选短测少148，边界见 [产物版本比较](artifact_comparison.md)。

同一接收者处理多个任务时，可信宿主可显式按已路由 task_id 读取局部 inbox，过滤在分页前，完整保留所选任务的全部 kind 和消息。其他任务仍待办，主协调仍查跨任务依赖及全范围收件箱。入口与短测边界见 [任务范围读取](inbox_task_scope.md)。

验收协调只需判断是否继续时，可选择完整结果外置、简短回执与按哈希恢复；保留所有状态、错误、范围和限制，显示和恢复均不授信。真实 CLI 接入与边界见 [验收上下文说明](validation_context.md)。

交接还可由兼容消费者显式选择 `claims-table/v1`，把重复 claim 字段名变成一次列头，保留全部值、否决和前提；默认 JSON 不变。调用路径、不可更改的消费绑定和短测边界见 [交接编码说明](handoff_encoding.md)。

外部工具目录也可按明确任务需求收窄：宿主确认需求完整且为空时，`scripts/codex_tool_scope.py --root ABSOLUTE_PROJECT_ROOT --contract task-scope.json` 输出新线程的配置覆盖；宿主将 `config_overrides` 传给 `thread/start.config`。契约示例：`{"schema_version":"codex-tool-scope/v1","requirements_complete":true,"external_tool_requirements":[]}`。有需求或不确定时保留默认；实际目录仍有未知工具则不派发此profile。全局配置、项目规则和权限不变。研究与限制见 [本轮说明](tool_scope_research.md)。这同样需要宿主显式调用，没有自动改变已运行会话。

只有在同一上下文确实需要同时载入决策、通用编排和科研编排入口时，调用受控组合器：

```powershell
python scripts/prompt_context.py --root C:/Users/WI/Desktop/home_work/AI_LLM/agent --entries decision general research --json
```

宿主把返回的 `prompt` 发送一次，保存 `documents` 和 `policy_sha256` 作为本次输入绑定。`--root` 是工作流源码根目录；项目的指南、任务和结果仍解析到用户选定的 PROJECT_ROOT。不需要协调的任务继续按需使用单个角色。

组合器只在本次调用中合并三个固定入口首个全局 `text` 指令块中逐字相同的共享决策协议。独特规则、冲突版本、外层示例和模糊范围保留；源文件不变，单独入口仍包含完整协议。超出上限直接失败。没有持久的“已经读取”缓存；修改文件、切换项目或上下文重置后须重新装入所需内容。

这需要宿主显式调用 CLI；安装仓库不会自动改写任意 Codex/Claude 会话。`scripts/token_probe.py` 是诊断性 CLI 对照，不保证两次启动的隐式工具目录一致，不能凭其差值计成功。服务端 input+output 是总 token，缓存 input 是其中子集。

首轮独立 CLI 对照因工具目录不同判失败，零计数。修订后同一 app-server 的两个独立线程保持实际非任务指令文本和工具目录相同，短任务总 token 从 20,946 降至 20,848，减少 98；input 减少 120，output 增加 22。两次同样保留三个阻断条件。验收仅接受这一短任务范围，不代表长文质量或全部交互成本。受控对照支出 41,794 tokens，失败对照支出 40,252；开发与本会话用量未纳入这两组数字。详见 [受控结果](../../agent_doc/results/token-001b-control-20261009/) 和 [失败结果](../../agent_doc/results/token-001-20261009/)。

研究依据限已阅读内容：[ACON，ICML 2026](https://proceedings.mlr.press/v306/kang26b.html) 的索引与摘要；未读完 PDF，不引用实验数字。[Beyond Token Savings，2026 预印本](https://arxiv.org/abs/2609.32961) 的摘要提醒更少 tokens 不一定更便宜、更快，相似总体分数可能掩盖任务差异。这里仅删除精确重复并检查逐任务 oracle，不移植论文收益。用量采集依据 [Codex 非交互文档](https://learn.chatgpt.com/docs/non-interactive-mode) 和本机 0.160.1 生成的实际 app-server schema；不假设未核实的输出 token 硬上限。

100 次成功须对应不同的真实升级：质量与独立验收通过、普通 main 发布及远端读回完成后才加一。失败、重跑、记录补充、估算和重复机制不加一。达到 100 后才进入每小时优化阶段；当前不宣称该后台阶段已启动。
