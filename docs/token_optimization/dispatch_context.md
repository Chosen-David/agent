# 独立子任务的完整上下文

已明确给出全部依赖的子任务可以由宿主创建新线程，避免再次输入父任务的历史。协调者保留人类对话；依赖未知、仍需历史、或无法完整重建父线程设置时继续分叉。这个入口不自动接管平台的 Agent 调度。

```powershell
python WORKFLOW_ROOT/scripts/dispatch_context.py --root ABSOLUTE_PROJECT_ROOT --request agent_doc/task/dispatch-request.json --max-chars 12000
```

请求是宿主明确填写的 `dispatch-context/v1` 对象，字段包括 `project_root`、`task_id`、`parent`、`settings_complete`、`needs_complete`、`history_required`、`guide_verified_human`、`required_refs`、`context_refs` 和 `instruction`。`parent` 必须包含原生 `thread_id`、已完成的 `last_turn_id`、`cwd`、`model`、`reasoning_effort`、`approval_policy`、`sandbox` 和已解析的 `config`。

只有两个完整性标志都为 true 且 `history_required=false` 时选择 `thread/start`。完整设置须核查父创建请求、实际生效配置、模型、推理强度、权限、工作区和指令；无法表达的自定义父指令不应被宣称完整。否则输出 `thread/fork`；设置未知时不覆盖父配置。`--force-inherit` 可生成相同完整任务输入的继承对照。

每份依赖都是当前项目内 `{path, sha256}` 文件，正文完整放入一次任务输入。必需依赖必须全部提供；新上下文强制包含该项目的 `agent_doc/guide/GUIDE.md`，非空指南须核实人类来源。宿主还要按任务核实所需记忆、证据、任务状态及版本，不能仅提供指南就声称依赖完整。工具不创建或修改指南。不跨项目继承、不静默截断；文件变更、重复引用、缺少必需依赖或超预算均拒绝。

输出的 `method`/`params` 直接传原生宿主 RPC，`input_text` 只作为本次任务输入，不再把机器配置重复塞入模型消息。需满足后端协议的实验功能要求；本次核验使用 Codex0.160.1 App Server 的 `experimentalApi=true`。`excludeTurns=true` 仅减少分叉响应的历史加载，不裁剪模型上下文，不能据此报 token 节省。原始接口说明见 [App Server](https://learn.chatgpt.com/docs/app-server)。

独立验收的 [短测证据](../../agent_doc/results/token-008-dispatch-20261010/README.md)：同模型/high、权限、配置、实际可见策略、工具、当前完整依赖和输出约束，一个已有短历史的父线程。继承输入18,733/输出80/总18,813；新上下文输入18,534/输出80/总18,614，少199，约1.06%。两边返回完全相同的 v8 取消状态及三个阻断条件。两次新调用共37,427 tokens；旧父调用不重计，缓存没有扣除。

六项边界测试、独立宿主原始账单与持久化历史核验通过，结果仅 usable-with-scope。服务最终内部提示词拼装不可见；一次短测不代表长文、整条协作链或现金成本效果。`current_turn_usage()` 读取最后一条原生 `tokenUsage.last`，包含本轮重新消费的历史输入；保留原有仅限新线程的严格记账函数。安装同步不等于运行中的宿主已采用本入口。
