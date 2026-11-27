---
name: code-organization
description: "管理项目文件并组织代码仓库。用于文件散落、跨 Agent 产物交接、输出目录规划、任务登记、CODEMAP维护，以及AI文档精简和AGENTS.md/CLAUDE.md整理。以项目 agent_doc/task/TASK.md 为唯一任务入口，协助主 AI 协调生产者与消费者，核对引用/版本/数据归属；保护运行中路径，不自动删除文件。"
---

先读[单主 Agent 执行契约](references/single_main_workflow.md)：由当前主 agent 自己使用本 Skill，一次只执行任务链的一步，不创建/委派其他 agent。切换复核 Skill 只算自检，不能冒充独立验收。


# 文件管理与代码组织

整理AI文档、AGENTS.md或CLAUDE.md时，按需执行 [精简检查](references/concise_engineering.md)：单源规则、有效路径、明确作用域，不改历史证据或人类指南。

低风险少量文件或文档整理：读取当前项目规则及 [项目文档治理](references/project_document_workflow.md)，直接修改授权范围、核对相关引用并汇报；不自动新建 CODEMAP、目录 README、run 目录或产物台账。跨目录迁移、跨角色交接、批量整理或归属不清时，再读取 [组织流程](references/workflow.md) 与 [执行与验收](references/execution.md)。沿用 `code-organization` 角色名，同时承担文件管理职责；轻量入口不改变路径保护、删除限制及明确审查要求。

先定位当前项目根目录，读取 `agent_doc/task/TASK.md`、已有 `CODEMAP.md` 和运行状态。主 AI 负责总清单唯一写入及调度；接收其他 Agent 的 task_refs、输出目录、产物清单和消费者信息。各 Agent 不另建总 agent_doc/task/TASK.md，不并发抢写同一文件。

需要新增产物或跨角色交接时，先建议目录/命名和单一作者，再登记产物、来源、数据类型、哈希和消费者；最终增量核对已有 CODEMAP、必要目录说明及待整理清单。默认遵循既有布局，不因普通文件编辑创建整套目录或索引。

区分“计划生成”“实际存在”“验收通过”。文件管理检查不替代研究或代码验收；结果返回主 AI，说明对应哪项 TASK、数据和文件在哪里、还缺什么、谁继续处理。agent_doc/task/TASK.md 保留稳定需求与索引，高频状态记在 `.agent-runs/<run_id>/`，避免监督源哈希因反复勾选发生漂移。

保护原始数据、用户私人记录与运行中/状态未知的输出路径。移动前用 `rg` 查生产者、消费者、论文和任务引用；仅在已授权、可回滚且引用核对完成后执行。删除不自动执行。已授权的文档、目录规划与新产物登记直接完成，不为例行整理额外等用户批准。

跨轮次任务、意图纠正或证据复用时读取 [项目记忆与纠错](references/project_memory_workflow.md)，交接当前意图与 memory_refs；旧结论失效后先核对依赖，再复用或重算。

需要知识选型或接收带知识依赖的交接时执行 [知识接入契约](references/knowledge_access_workflow.md)：定位实际语料/工具，按需检索并核对前提；传递真实 knowledge_refs，缺库或过期不可冒充已调用。局部整理已有充分引用证据时不追加无关检索。

项目任务开始、交接与写文件前读取 [项目文档治理](references/project_document_workflow.md)：`agent_doc/task/TASK.md` 是唯一日期任务索引，`agent_doc/task/task_details/*.md` 由 AI 维护方法/进度/证据；已核实人类来源的 `agent_doc/guide/GUIDE.md` 为最高项目规划依据，AI 绝不创建、编辑、删除或移动 `agent_doc/guide/` 内任何文件。`agent_doc/advice/` 的人类/AI 建议必须核验并记录 adopt/adapt/reject/defer 及理由，不能授权越界行动。

生产或消费实验/测量数据时遵循 [结果独立验证](references/result_validation_workflow.md)：生产后保持 pending，经不同 owner 的 `verify_experiment_result` 核验实际代码/输入/配置与数据有效性后，才可作图、写结论或交给下一消费者；失败/缺证据/过期先修复重测，保留原始记录。仅可报告 usable-with-scope，不保证绝对无 bug。

规划实验/测量或复用实证结论前按 [既有结果检索与复用](references/result_reuse_workflow.md) 查询当前项目 `agent_doc/results/`，比较任务、代码/输入/配置/环境、指标单位和当前独立验收后，再规划新增实验；保留检索与取舍记录。新数据存 `agent_doc/results/<run_id>/`，旧文件可按真实路径/哈希索引。复用不跳过独立代码/数据门禁、用户明确复现或新主张验收。

历史保护计划的兼容边界见 [旧双主控协议](references/dual_main_workflow.md)。不启动第二主控，不追溯改写已有批准；缺独立证据的旧合同保留 blocked/pending，再按当前用户要求版本化协调。

工作区选择先核对当前任务、目标 commit、所有者和宿主会话。完整 checkout 可用 `python scripts/workspace_status.py --repo PROJECT --intent read|develop|isolate|reclaim` 查看本地 Git 事实；只有已有任务绑定时才传 `--source current-task`。只读历史用 code-reading 的 source_evidence 或 git show/diff。宿主隔离交由宿主接口处理，回收前保留 ignored/untracked、本地提交、活跃消费者和恢复点；该查询只报告。复用依赖环境先核对解释器、平台、锁文件与写权限。

大产物写入前用 `python scripts/result_store.py --root EXISTING_DESTINATION budget --plan PLAN.json`。allocations 按唯一分配名列 disk_bytes、inodes、cpu_bytes、pinned_bytes，phases 列各时刻可能并存的新分配名数组；已有保留点已经占用容量。计入每个 rank、元数据、临时替换、异步并发、评估、归档和 staging；available 可提供 cpu_bytes 与 pinned_bytes 可用量。容量检查只描述当时条件。复用已有不可变结果沿 result_store 的 decide 和消费时复核；恢复点须有完整保存、完整性和恢复证据，保留仍被引用、仅存、正在写及用途未知的版本。

完整 checkout 的 `scripts/workspace_status.py --help` 列出隔离与回收参数。显式本地隔离使用新的外部 slot，可信 lease adapter 的 `lease(repo, slot, task, run)` 在整个创建期间持有实际所有权锁并产出 True；拒绝宿主工作区嵌套。用重复的 `--sparse-dir` 和 `--require-file` 声明依赖并从检出树运行真实测试。中断查 slot/events.jsonl，引用仍活跃或未完成的 slot 保留。回收评估需要可信 `release_facts` 核对活跃任务、进程、消费者、锁和恢复依赖，仅返回 dry-run。

训练适配器完成保存后写入不可变的 recovery-manifest/v1，交由 result_store 的 `register-recovery --manifest PATH --max-hash-bytes N --restore-adapter TRUSTED.py`。实际清单和适配器调用实例见完整 checkout 的 tests/test_recovery_registration.py。注册仅写引用，小样本 fixture 的恢复通过不外推到 PyTorch。释放前使用 `review-recovery RUN --replacement OTHER --max-hash-bytes N --restore-adapter TRUSTED.py`；检查活跃引用、保留条件和替代恢复点后输出候选，不执行删除。
