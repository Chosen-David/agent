# 独立运行时审阅

审阅日期：2026-10-03。范围：未提交的 `agent_runtime/core.py`、`scheduler.py`、`__main__.py`、`scripts/demo_task_supervisor.py`、`workflows/task_supervision_workflow.md`。已读根 `AGENTS.md`、决策门禁、主调度规则。没有修改核心、SGLang、外部服务或常驻进程。下述复现使用临时 SQLite、合成适配器、假时钟；FIFO 复现子进程由一秒超时强制回收。不是模型能力实验。

**初审结论：存在阻塞问题，不能把当前版本描述为已验证可靠的持久监督器。** 以下是已复现问题；修复后的状态须单独追加，不删除原始发现。

## R1 — P1：祖先完成证据失效后仍执行后续节点

位置：`core.py` `_check_done`（约193行）、`_summary`（约231行）、`tick` 依赖检查（约289行）。

最小复现：构造 `a → b → c`，handler 为幂等，run 返回 `Outcome('complete', evidence=['proof'])`，verify 按任务 ID 查询一个 invalid 集合；前两次 tick 完成 a、b，随后将 a 加入 invalid，第三次 tick。

实际输出：`calls=['a','b','c']`，状态 `a=failed,b=done,c=done`。a 失效会被发现，但 b 的本地证据有效，因此 b 仍 done；c 只检查 b 的状态后执行。若 c 是外发/部署等授权动作，将基于已经失效的前置条件执行。这里失效发生于链执行中，不属于文档所排除的“最终验收后产物改动”。

建议：在领取任何任务前按拓扑闭包验证所有必要祖先；对失效依赖传播不可用状态，包括已经 done 的中间节点。不要自动重放有副作用的历史完成节点。加入上述三层 DAG 回归，也检查 reconcile 的祖先证据新鲜性。

## R2 — P2：连续 retry/pending 没有指数退避

位置：`core.py` 304–307、334–341（初审行号）。

最小复现：单任务 ETA=20、low risk、监督范围1–60秒、max_attempts=6，handler 每次返回 retry；假时钟每次推进至 next_at。

实际连续五次延迟：`[10.0,10.0,10.0,10.0,10.0]`。claim 的 todo→doing 每次被视为 changed，idle_ticks 清零；返回 todo 只再加一，因此无法累计。预算最终使重试终止，所以不是无界 CPU busy loop，但与承诺的无进展指数退避不符，对轮询远端作业不必要地高频。

建议：分开持久进度与临时领取状态，按连续无进展结果维护计数。测试完整 Engine 路径，而不只是 interval 纯函数。

## R3 — P2：权限阻塞且带依赖时永久维持初始检查频率

位置：`core.py` 282–306 与 `_summary`。

最小复现：a→b，默认拒绝授权；连续六次不同事件 tick。

实际每次 `(idle_ticks,next_check_seconds)` 都为 `(0,5.0)`。每轮先把 a 从 permission blocked 重置为 todo，summary 暂时解除 b 的 dependency blocked；再拒绝 a 时，changed 在最终 summary 重阻塞 b 之前计算，误认为有进展。最终状态完全相同，但每次退避归零。

建议：以稳定调和后的状态或明确进度信号比较，权限探测不清除旧的持久状态；加入有依赖和逆序任务排列的集成回归。

## R4 — P1：内置验收器读取 FIFO 会永久阻塞监督器

位置：`core.py` `ArtifactHandler._evidence` 的 `stat().st_size` / `read_bytes()`（约367–369行）。

最小复现：在授权临时 root 内 `os.mkfifo(root/'proof')`，调用 `_evidence` 验收 proof。FIFO 的 st_size 为0，可通过16 MiB检查；read_bytes 等待写端，子进程一秒后仍未返回，被测试超时杀死。无需访问 root 外路径。

影响：内置 CLI 的 serve 同步执行 run，因此这一条计划可挂住本地整个监督服务；SIGTERM 只设置 stop flag，不能打断阻塞 read，max_seconds 也只在循环边界检查。若 FIFO 被已完成任务的 verify 读取，该读取还发生在 BEGIN IMMEDIATE 中，会锁住数据库，取消也可能超时。

建议：打开时使用非阻塞、拒绝非普通文件，针对打开的 fd 做 fstat 后限制读取字节数；避免 stat/read 间文件替换绕过大小限制。不能仅依据预读 stat 承诺有界验收。为内置验收器加入 FIFO/文件类型回归；适配器 verify 运行在写事务中这一限制应明确记录或调整架构。

## 已确认的边界与未夸大的能力

- 默认 authorize 拒绝；CLI 只注册只读 ArtifactHandler；计划内声明权限不会赋权。
- 事件 ID 在 SQLite 主键下去重；领取与状态更新用写事务；旧 token、租约过期和取消后结果提交有显式 fencing 检查。
- 外部副作用不能由 SQLite 强制撤销/去重，文档已明确要求合作式适配器；不能声称 exactly-once 或任意工具强制取消。
- arm 要求真实 ID、所属链、active/live readback；本地 heartbeat 只证明近期服务存活，文档披露最多30秒滞后。
- demo 是临时文件与合成任务，不是 LLM 的自主拆解、规划或长期完成率验证。未发现文档把它冒充真实 LLM 实验。
- `stop()` 与用户取消不同：只停止 monitor；对已领取动作应通过 Store.cancel 才能废弃提交。文档应维持此区分。
- 未评估真实云/消息后端、NFS、多机锁、恶意同权限进程；这些不在本轮实现承诺内。

## 建议补充的验证

除其他 agent 的主测试集外，应覆盖：上述四项复现；过期旧 drain 返回后的 due 写入与新 drain/wake 的交错；authorize 抛异常时 serve 的存活及错误归属；monitor stopped 后显式恢复语义。后两项为建议覆盖，并非本文已复现缺陷。

## R5 — P2：drain 收尾覆盖期间收到的 wake

位置：`scheduler.py` `drain_once` 最终无条件 UPDATE due。

已复现：假时钟100，drain预约下一次检查；engine.tick 期间调用 `wake('r','artifact changed during tick')`，读回 due=101；tick 返回 next_check_seconds=60，drain 收尾读回 due=160。可信变化事件的提前唤醒被旧 tick 结果覆盖，可延误一个 max_seconds 窗口。同处也缺少防止旧 drain 覆盖新 drain 的调度代次条件。

建议：为预约引入版本/token，wake 和并发领取更新版本；旧 drain 仅能更新自身预约，保留期间出现的更早唤醒。用控制交错测试，不依赖时间运气。此问题不造成已领取动作重复提交，但使“变化事件提前唤醒”承诺失真。

## 修复复核追加（第一轮）

主 agent 修改后的代码已用原始最小复现重跑：

- R1：通过；calls 只有 a,b，最终 a=failed,b=failed,c=blocked，没有执行 c。
- R2：通过；连续 next_check_seconds 为10、20、40、60、60。
- R3：通过；连续 idle_ticks 为1、2、3、4、5，间隔为10、20、40、60、60。
- R4、R5：此轮复核时尚待修复。

这是针对发现项的复核，不替代全量测试和实际后端验收。

## 最终修复复核（第二轮）

主 agent 修复 R4/R5 后，独立 reviewer 新增 `tests/test_task_runtime_review.py`，执行：

```text
python -m unittest discover -s tests -p test_task_runtime_review.py -v
Ran 7 tests in 1.053s — OK
```

- R4 已修复并复核：真实 POSIX FIFO 在有三秒防挂死保护的子进程内被拒绝；真实16 MiB+1普通文件被拒绝；模拟 fstat 后增长的文件仍被实际有界读取拒绝。
- R5 已修复并复核：tick 中的 wake 保持 due=101，不再被旧 drain 改为160；模拟旧/新 drain 交错，新 drain 的 due=111 保留，旧 drain 无法覆盖；旧四列 monitors 表迁移保留原始记录并补 version=0。
- 授权服务异常：真实一轮有界 serve 正常返回；授权回调抛 ConnectionError 后节点 blocked、attempts=0、动作调用数=0，monitor 保持 active。错误没有逃逸并终止服务循环。

**截至本次复核，R1–R5 均已修复并经独立最小复现/回归确认，没有已知未修复阻塞项。** 此结论仅针对此次审阅范围；不是生产可用性、真实 LLM 完成率或外部副作用 exactly-once 的认证。新测试没有修改核心或 SGLang，也没有部署外部服务/daemon。完整仓库测试由主 agent 统一执行。

保留限制：自定义 trusted verify 若自行阻塞，仍可能持有 SQLite 写事务；宿主必须满足短时只读验收契约。文件系统被同权限进程恶意替换、远程文件系统永久阻塞等情况不在已声明的本地可信宿主保证范围。上述边界不应在最终文档中扩大为任意工具强制超时/强制取消。

## 最新上游集成独立检查

集成基准为 `25c1512`，含 `7ec6418` 的10篇范文 gate 与 `0697224` 的 code-organization 更新。此次只复核合并与入口；主 agent 报告的163+3项全量结果不冒充 reviewer 重跑结果。

独立检查结果：

- 对 `research-assistant/SKILL.md` 与 `scripts/sync_plugin_references.py` 逐行验证：`25c1512` 的原文件全部行按原次序保留，新内容为追加，未删除并发上游内容。
- SKILL 的10篇范文入口和任务监督入口并存；同步映射保留6个范文学习引用并新增1个监督引用。
- 通用主AI、科研主AI、插件本地 orchestrator 三处监督入口都存在，并明确插件单独分发不含Python运行时，不假装后台服务已启动。
- `python scripts/sync_plugin_references.py --check` 与 `git diff --check` 均通过；检查范围未发现残留合并冲突标记。
- capability ready、monitor ID、active/live readback、独立验收、权限不由监督器授予、取消不撤销外部既成副作用等关键声明仍在，没有因合并引入新的已知阻塞。

文档收尾：本次检查时 `docs/task_supervisor_validation.md` 仍保留“最终核验后补入”的占位句，主 agent 应在交付前填入本次实际完整测试与演示结果；这是待完成记录，不能把占位当已验证证据。此次未修改运行时或上游规则。
