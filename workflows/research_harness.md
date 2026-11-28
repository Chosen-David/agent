# Budget-Aware Adaptive Research Harness

新任务策略版本 adaptive/v1。默认仅主 Agent 执行。single 模式只使用主 Agent；adaptive 按需派遣；manual 遵守用户指定上限和分工。历史账本恢复继续遵循任务创建时绑定的审核、授权及恢复合同。策略迁移需要记录用户授权、原版本、目标版本和理由。

默认跨项目总上限为两个活跃 Agent（含主 Agent），每 Cycle 至多四次新派遣。仅当独立交付物、未重复的研究价值、上下文范围、预算预留与资源隔离均明确时，由主 Agent 派遣一个 Worker。Worker 不再派遣。预算或资源占用无法核实时继续单 Agent。确定性训练监督由程序执行。

并行时两个生产者分别绑定任务、worktree、输出目录与恢复计划。首选宿主已有的 Agent 启动/恢复接口。每个生产者可规划、修改实现、运行测试及通过已有 training_claim 认领获准实验。只读科研模型回调仅为可选反馈。仅有一个执行者时按就绪任务继续并记录降级。分支与 worktree 隔离代码，不提供系统权限隔离。

1. 从当前项目 TASK、任务详情、实验注册表和运行日志恢复。记录 owner、工作树与提交、工件路径、资源与真实依赖。
2. 运行 research_workers 验证已分配工作树/分支及输出目录互不覆盖。复用 core.Store/Engine 的任务 DAG，以及 training_claim、training_workspace 和恢复检查。相同任务或训练认领按原标识对账。
3. 稳定正确性条件由程序判定。失败只阻塞依赖该结果的任务。中间意见进入有证据的修复队列。既有契约的策略变更需要用户授权并保留历史账本。
4. 使用结构化观测连接任务状态、rank 进程、日志更新、checkpoint 和磁盘。失联期间保持训练认领，重连后核验实际进度；存在不确定副作用时不得重复派单。
5. 完成阶段后统一验收；在预算允许且有独立价值时交叉复算。记录初始差异、修复与复验，并由用户对完整目标验收。维护计划、结果索引、失败原因及应用边界。未经生命周期批准不清理资产。

原生 CLI 开发 Worker 由可信宿主传入 required_capabilities（file_read、file_write、shell_exec、test_exec、git_worktree）。能力更窄、需要网络或 GPU 的任务不进入此开发入口。先用同目录的 App Server command/exec 验证 shell 与工作树读写；已知挂载拒绝按环境短期熔断。成功探测仅覆盖 Shell 基础能力，任务本身仍需通过产物验证。宿主不可用时主 Agent 继续合法任务；不要把 externalSandbox 当作降级开关。
