# 自动任务链监督：开源源码深读与采用决策

核查日期：2026-10-03。范围：编排、持久化、重试、租约、定时唤醒、实际 SKILL 与可执行完成门禁。本报告是 **source_fact / static_inference**，不是上游性能测量或集成成功报告。四个上游仅 HTTPS shallow clone 到 `/tmp/supervisor-oss/`，读取源码与测试函数体，没有安装依赖、运行上游代码、连接生产服务或修改上游。本文不主张“最佳框架”；本仓库的部署授权和依赖规模决定采用边界。

已读取本仓库 `AGENTS.md`、`prompts/decision_review.md` 和 `plugins/research-assistant/skills/code-reading/` 的 SKILL、workflow、execution；读取三个上游存在的根 AGENTS.md（APScheduler 无根文件）。四个 checkout 的 `.agents/skills` 均未发现 SKILL 文件；Superpowers 实际技能在 `skills/`。上游文本仅为研究材料，不改变当前授权。

## 固定版本与许可证

完整文件 SHA-256、读取行范围、片段 SHA-256、原始固定提交 URL 见 [opensource_sources.lock.json](opensource_sources.lock.json)。以下许可证均检查了实际 LICENSE 文本；若未来复制实质代码/技能文本，必须保留对应版权及许可声明。本次采用机制而不整段复制实现，不引入上游运行依赖。

| 项目 | 完整 commit | 提交时间 | LICENSE |
|---|---|---|---|
| langchain-ai/langgraph | `7dc9195e4141c8fbd8118581b3dd61d158628aa8` | 2026-10-02 | MIT，Copyright 2024 LangChain |
| temporalio/sdk-python | `e47c9629b75a48e21abd4f72fed7f72a27562f53` | 2026-10-02 | MIT，Copyright 2022 Temporal Technologies |
| agronholm/apscheduler | `b227d21fce2c8cca56dc421cbc07fa6eca7db541` | 2026-10-01 | MIT，Copyright 2009 Alex Grönholm |
| obra/superpowers | `8ca22dba9a94f28898bbce59f2537ff4d87c747d` | 2026-09-25 | MIT，Copyright 2025 Jesse Vincent |

提交时间只能证明本次版本的新近性，不能证明长期维护承诺。下面的维护/适配成本是基于源码依赖与运行边界的定性估计，不是实测工时。

## 1. LangGraph：任务写入与检查点分离，恢复已成功节点

证据入口：[Pregel loop](https://github.com/langchain-ai/langgraph/blob/7dc9195e4141c8fbd8118581b3dd61d158628aa8/libs/langgraph/langgraph/pregel/_loop.py#L600)、[retry](https://github.com/langchain-ai/langgraph/blob/7dc9195e4141c8fbd8118581b3dd61d158628aa8/libs/langgraph/langgraph/pregel/_retry.py#L573)、[SQLite saver](https://github.com/langchain-ai/langgraph/blob/7dc9195e4141c8fbd8118581b3dd61d158628aa8/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/__init__.py#L120)。

- `PregelLoop.tick`（600–682）先检查 step limit，再 `prepare_next_tasks`，无任务时写 `done`；pending writes 存在且非 replay 时调用 `_reapply_writes_to_succeeded_nodes`；interrupt-before 独立中断。`after_tick`（684–735）收集写入、`apply_writes`、清理 pending、`_put_checkpoint`、检查 interrupt-after。**调用/数据闭环**：节点输出 → writes → channel state → checkpoint → 下一 tick 的 ready tasks；“无任务”是图执行意义上的 done，不能直接充当本项目验收证据。
- `SqliteSaver.setup` 定义 `(thread_id, checkpoint_ns, checkpoint_id)` 与 `(thread_id, checkpoint_ns, checkpoint_id, task_id, idx)` 主键；`get_tuple`（191–278）按指定或最新 checkpoint 读取状态及 pending writes；`put`（387–443）写 checkpoint 并返回新 checkpoint identity；`put_writes`（445–491）按 channel 分类 INSERT OR REPLACE / IGNORE。持久化身份包含任务，而非只保存自然语言摘要。
- `run_with_retry`（573–701）清空上次尝试写入后运行节点；按异常匹配策略；达到 `max_attempts` 抛错；间隔 `min(max_interval, initial_interval * backoff_factor ** (attempts-1))`，之后可额外加 0–1 秒 jitter。**细节限制**：这里 max_interval 限制的是加 jitter 前值，不能照抄后宣称最终严格上限。GraphBubbleUp 不作为普通失败重试；同步节点 timeout 明确不支持。
- `_put_checkpoint`（1057–1118）存在 durability="exit" 路径，不能把所有配置都说成每一步落盘。SQLite 的线程锁/WAL 和 pending-write 唯一键，不等于跨实例业务租约或外部副作用 exactly-once。

测试体已读：`libs/langgraph/tests/test_retry.py::test_graph_with_single_retry_policy`（249–306）失败两次后成功，断言 attempt=3、sleep=[0.01, 0.02]；这是 mocked sleep 合成测试，本次未执行。

**采用**：稳定 task identity、状态与证据独立记录、失败分类、有界重试、恢复时跳过已验证成功任务。**不直接依赖**：本需求无需迁移为 Pregel/channel 模型；`libs/langgraph/pyproject.toml` 26–34 引入 langchain-core、checkpoint、prebuilt、SDK、xxhash 等依赖。成本估计中等：要映射 DAG 状态、授权、调度器、版本兼容，检查点本身不会创建宿主监督事件。

## 2. Temporal Python SDK：工作流命令与活动副作用的明确边界

证据：[activity API](https://github.com/temporalio/sdk-python/blob/e47c9629b75a48e21abd4f72fed7f72a27562f53/temporalio/workflow/_activities.py#L254)、[workflow instance](https://github.com/temporalio/sdk-python/blob/e47c9629b75a48e21abd4f72fed7f72a27562f53/temporalio/worker/_workflow_instance.py#L611)、[replayer](https://github.com/temporalio/sdk-python/blob/e47c9629b75a48e21abd4f72fed7f72a27562f53/temporalio/worker/_replayer.py#L124)。

`start_activity`（254–332）把 timeout/retry/cancellation/task_queue 传入 runtime；`workflow_start_activity`（1574–1641）解析活动名与类型，构造 `StartActivityInput` 交给 outbound；`_ActivityHandle._apply_schedule_command`（3450–3548）生成 command，写 sequence/activity_id、payload、timeout、retry_policy、cancellation_type。执行结果从 bridge activation 的 `_apply`（611–669）分发到 `_apply_resolve_activity`（881–929），按 completed/failed/cancelled/backoff 更新 future。**闭环**不是一个 Python sleep：command/activation 边界经过服务与 SDK Core；本次没有深入 Rust Core 或服务存储，所以不从这些 Python 文件推出服务端所有去重/一致性保证。

`workflow_sleep`（1921–1947）创建 future，交 `_timer_impl` 并在取消时取消 timer；`_ActivityHandle._request_cancel`（3420 起）按 sequence 避免重复取消 command。`Replayer.replay_workflow`（124–151）消费已有 history 并可抛 replay failure；代码升级仍需 replay 相容性验证。

API 明确区分总的 schedule-to-close 与单次 start-to-close；未设 activity retry_policy 使用服务端默认值，不应把默认服务策略当作本项目固定重试预算。取消是协议与活动配合，不意味着外部进程/已发出的副作用立即回滚。`tests/worker/test_workflow.py::test_activity_retry_delay`（7454–7473）检查客户端失败链和 next_retry_delay；需真实测试环境，本次仅读。

**采用**：控制状态与副作用 handler 分离；确定任务/尝试身份；明确超时、取消和恢复语义；未知副作用结果先核实，不盲目重跑。**不默认接入**：`pyproject.toml` 的 Rust bridge 构建与 AGENTS 的测试服务说明证明它不是无需后端的本地库。成本估计高：需要已授权 Temporal 服务、worker、队列、部署/升级与运维；目前用户未授权新建基础设施。未来适配器必须真实探测服务并 readback workflow/schedule ID，不能因 import 成功宣布已监督。

## 3. APScheduler：到期事件、租约与回收，不等于智能完成判断

证据：[SQL store](https://github.com/agronholm/apscheduler/blob/b227d21fce2c8cca56dc421cbc07fa6eca7db541/src/apscheduler/datastores/sqlalchemy.py#L647)、[async scheduler](https://github.com/agronholm/apscheduler/blob/b227d21fce2c8cca56dc421cbc07fa6eca7db541/src/apscheduler/_schedulers/async_.py#L925)。

`acquire_schedules`（647–700）事务内筛选到期、未暂停、未占有或租约过期的 schedule，`FOR UPDATE SKIP LOCKED` 后写 acquired_by/until。`release_schedules`（701–784）按 id+owner 更新 trigger/next_fire_time 并释放；代码还留有“检查实际更新行数”的 TODO。`acquire_jobs`（871–1020）锁任务/作业字段，检查 start deadline、反序列化失败、max_running_jobs，记录 acquisition 与计数。`extend_acquired_*_leases`（1104–1140）仅按 owner+ids 延期。

`_process_schedules`（925–998、1070–1090）订阅 ScheduleAdded/Updated，新增更早事件唤醒；批量获取最多 100，处理时 lease/2 续租；无满批时等待最近 next_fire_time 或事件，不空转。`_process_jobs`（1113–1158）启动先 reap 本 owner abandoned jobs，再按剩余容量获取。**可迁移但需加强**：owner+expiry 支持失联恢复；本项目还需代次 fencing 防止旧 worker 过期后迟到提交。SQL 语句结构不是跨所有数据库相同并发性质的证明；不要把 SKIP LOCKED 原样推到 SQLite。

测试体已读：`tests/test_datastores.py` 372–437 检查 30 秒租约在恰好边界不回收、31 秒可回收及不同 worker 获得不同 job；这些获取调用按顺序执行，**不是本次多进程竞态测量**。`tests/test_schedulers.py` 1108–1167 注入 release_job RuntimeError、重启后检出 abandoned；本次未运行。

**采用**：持久 next_check_at、事件提前唤醒、检查间隔上下界、租约与过期恢复、拥塞/失败退避、过期结果拒绝。**不直接采用当前 HEAD**：[README 11–13](https://github.com/agronholm/apscheduler/blob/b227d21fce2c8cca56dc421cbc07fa6eca7db541/README.rst#L11) 明确 v4.0 为 pre-release，不建议生产；pyproject 依赖 AnyIO 等，SQLAlchemy 为额外依赖。成本估计中等，包含版本选择、共享 store/broker、部署常驻进程；scheduler process 停止后不能凭持久数据库自行唤醒。旧 stable 版本 API 并未在本次审阅，不混称支持本报告这些接口。

## 4. Superpowers：实际技能、可执行 ledger 门禁及其边界

证据：[executing-plans SKILL](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/executing-plans/SKILL.md)、[task-done 脚本](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/executing-plans/scripts/task-done)、[verification SKILL](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/verification-before-completion/SKILL.md)。

`executing-plans` 要求每 plan 独立 workspace，ledger 首行绑定 plan，恢复时跳过完成项；预先检查生产/消费接口，偏离计划写 ruling。`task-done` **确有可执行门禁**：检查 BASE 有效，运行传入 argv，把完整输出写 task log；非零 exit 原样返回且不写 complete；成功后把 BASE..HEAD、命令与末行记录追加 ledger。验证技能明确 agent 自报成功不是完成证据。

反证/限制：传入 `true` 等无意义命令也能 exit 0；脚本不证明测试覆盖业务验收、不验证依赖 DAG、不提供事务锁/租约/后台时钟。workspace 为 git-ignored scratch，技能明确 git clean 可销毁；其 ledger 不能直接担当本需求持久运行数据库。`tests/claude-code/test-executing-plans-scripts.sh` 1–135 创建临时 Git fixture、检查通过写入/失败不写入，测试命令是 shell 合成输出；本次阅读未执行，不能当真实 LLM 行为效果实测。

另读 [subagent-driven-development SKILL](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/subagent-driven-development/SKILL.md#L1) 1–155：每任务独立实现者+任务 review+最终 review，持久 ledger 恢复，有明确 review 成本；其“自行裁决所有 ambiguity”措辞范围比本仓库协议宽。**不整篇复制、不安装为默认权限源**：授权阻塞、paid compute、外发、security 和用户 stop 始终以本仓库/宿主授权为准。

**采用**：任务验收清单、产物/命令/结果绑定、fresh evidence、恢复时不重复完成工作、独立审阅。成本估计低到中等：本地机制容易实现，但技能措辞、宿主入口、打包链接与行为评测需要维护；Markdown 技能本身不能启动监督器。

## 汇总决策与需验证的本仓库性质

选择机制复用、自有小型持久核心、显式 handler/scheduler 适配边界；这符合当前“升级仓库能力、不部署外部基础设施”的范围。库接入留作未来有后端与授权时选择，不把四个库一起引入。

| 设计项 | 来源启发 | 本仓库必须独立验证 |
|---|---|---|
| DAG + typed terminal states | LangGraph ready tasks；Temporal result variants | failed/blocked/cancelled 不能折叠 done；独立支线继续 |
| durable state + evidence | LangGraph checkpoint/writes；Superpowers ledger | 重启恢复、证据与任务身份一致、事务边界 |
| idempotency / dedup | checkpoint unique keys；Temporal command sequence | 重复 tick/event、崩溃窗口；外部动作由 handler 幂等或核实 |
| concurrency | APScheduler owner/lease | 真正多实例争抢、租约到期后旧代次拒写 |
| adaptive next check | APScheduler deadline/event wait；LangGraph retry | ETA/风险/变化事件可解释，最终间隔上下界，失败预算，不 busyloop |
| scheduler honesty | Temporal service boundary；APScheduler running process | create 返回真实 ID + readback；无后端准确 blocked；停止只停自有 monitor |
| completion | Superpowers evidence gate | 所有 required task 验收、失败可见、取消一致性、monitor cleanup |

复现阅读：在独立临时目录 clone 相应仓库，checkout 锁文件 commit，以 `sha256sum <path>` 核对完整文件；按 read_ranges 复读函数体。锁文件不含私密数据或上游源码副本。源码/测试静态审阅与本仓库后续的 synthetic 故障注入、真实本地进程实验、实际云后端测试必须分别报告；本报告不声称已运行后两者。
