# 单主 Agent / 多 Skill 任务链 v1

一个主 agent 持有当前用户目标、唯一 TASK 与执行上下文。Skill 是主 agent 当前步骤的能力说明，不是另一个 agent、进程或独立审核者。本契约取代旧工作流中的自动委派、双主控和并行 agent 默认；专业方法、权限、许可证、失败证据和人类 guide 只读边界继续有效。

## 一次一步

1. 启动或恢复时先核对当前用户要求、当前项目指南、`agent_doc/task/TASK.md`、对应详情的 Plan/Progress、相关 memory 更正与 advice 差异。复用已有导航和 MemoryLedger；不另建总任务表或共享聊天池。
2. 从已有任务链选择一个依赖已满足、授权明确的步骤。记录当前 task ID、输入版本、验收、输出路径、预算与下一步；只加载这一步相关 Skill 和必要引用，不预读所有专业流程。
3. 主 agent 自己执行该步骤。不要 spawn/delegate 子 agent，不启动 planner-main/review-main，不借 tmux 同时跑多个 AI。外部工具作业允许在原授权内运行；等待期间只观察当前步骤、维护检查点，不开启下一执行步骤。
4. 核对实际输出、失败与证据，更新原任务详情，再进入下一步。未满足验收则修正或记录阻塞；未知副作用先核对，禁止盲目重放。取消、预算耗尽或证据过期不能当完成。
   当前步骤已返回明确失败/阻塞且无待核对作用时，可下一步选择不依赖它的已授权任务；依赖分支仍阻塞。pending、作业作用不明和等待预算耗尽不因此被越过。
5. 主 agent 可以下一步加载 review/测试 Skill 自检；这仍是同一作者，不能写成“独立复核通过”。已有合同需要独立验证时保留 pending，只接受真实外部检查证据或用户明确变更的合同，不伪造第二 owner。

## 能力与运行入口

能力来源是 `config/role_registry.json` 指向的现有 SKILL.md；role ID 保留作兼容的能力标识，不代表需启动角色模型。Claude 安装器仅安装 Skill 与主入口；旧指纹匹配的受管 agent 包装在升级时移除，用户修改或自建文件保留并提示冲突。Codex/marketplace 按需读取相同 Skill。

完整 checkout 可用 `python scripts/load_skill.py --project ABSOLUTE_PROJECT_ROOT --skill research-implement-optimize` 返回已核验安装的当前 Skill 正文与来源，供现有主 agent 读取；命令不调用模型。旧 `scripts/run_role.py` 保留离线诊断，不再用于执行角色。

运行时沿用已有 DAG/SQLite、依赖、授权、证据和恢复机制。每个 run 同时至多一个 doing，pending 步骤保留 active_step，重启不跳到下一 Skill；已存在多个活动作业必须先由主 agent 核对和收敛，不能仅靠升级代码宣称停止。此门禁不是跨数据库/跨项目的全机锁，也不能取消未接入的外部进程。

历史双主控批准、独立验收记录与失败数据原样保留，旧保护计划不自动改写或降级。若历史计划必须独立 agent 才可执行，它保持 blocked，须按新要求版本化协调；安装器不追溯批准历史任务。
