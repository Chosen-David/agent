# 持久任务链：验证记录

Run `supervisor-upgrade-2026-10-03`，Python 3.12.14，Linux，标准库 SQLite。起点 `e72e0cfc0d9223f5d5b0dc273f3a5d41a12c5e3b`。

基线实际运行：仓库120项测试、paper-reader 3项测试通过。旧监督测试明确为文档/合成规则示例，不具有生产状态持久化、租约或调度能力。候选新增真实可运行核心；不拿不存在的旧runtime作速度对照。

整合远端 `25c1512` 后实际完成：**163项仓库测试 + 3项paper-reader测试全部通过**，其中新增运行时测试33项（独立测试26项、独立review回归7项）。最终[仓库日志](supervisor_research/evidence/final-tests.log)、[reader日志](supervisor_research/evidence/final-reader.log)、[演示receipt/状态/停止readback](supervisor_research/evidence/demo.json)均已保存。plugin引用同步检查、Python编译检查与diff空白检查通过。

并发远端新增了10项其他能力测试，因此不能将163−120全部计为本功能测试。保留两处追加冲突双方内容：科研SKILL的论文范例学习入口与监督入口，以及sync脚本的两个工作流映射。未覆盖代码组织、paper gate或既有监督续跑。

独立review复现5项首版问题并逐项修复复核：祖先证据失效未传递、重试退避被claim重置、权限依赖阻塞不退避、FIFO阻塞验收、旧drain覆盖wake。后两项加入普通文件/有界读取与调度代次CAS。详见[审阅记录](supervisor_research/review.md)，未隐藏负结果。

| 场景 | 实际验证 | 边界 |
|---|---|---|
| 重启/崩溃 | 真SQLite重开；真正terminate worker后从持久状态恢复 | 租约到期通过合成clock推进，不等待真实长超时 |
| 重复/并发 | 重复event不重复调用；两个spawn进程竞争同一DB；过期token拒绝提交 | handler为确定性合成实现，不证明外部API exactly-once |
| 完成/依赖 | 真实artifact hash核查及变更导致传递失效；坏证据拒绝 | 不评估LLM科研质量或规划质量 |
| 权限/失败 | 默认拒绝、不消耗执行次数、独立支线推进、预算耗尽failed、reconcile验收 | 宿主回调负责真实授权/钱和计算预算 |
| 取消 | 进行中取消拒绝迟到结果；预约与tick间取消竞态；只停止自有monitor | 不强制杀死任意外部工具 |
| 调度 | 真实subprocess serve→CLI arm ID/readback→文件达标→monitor stopped；服务退出readback不live | 本地前台服务仅在宿主/进程存活期间工作 |
| 故障加固 | 真实FIFO、超限文件；old/new drain/wake交错；授权回调异常；旧schema迁移 | 交错与文件增长测试部分使用明确mock，见测试注释 |

合成对照是固定契约/独立期望值下的故障前后行为与原始缺陷复现，不是线上用户任务成功率对比。旧版本没有生产runtime，故未捏造与旧runtime的性能比；本轮不声称速度、token或模型成功率改善。可复现命令：

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
python scripts/sync_plugin_references.py --check
python scripts/demo_task_supervisor.py
```

实验边界：确定性handler和可控clock属于synthetic workload，SQLite事务/真实多进程争抢/worker terminate与subprocess serve属于实际本地执行。没有运行线上LLM、付费任务、云scheduler、用户机器daemon或第三方框架基准；没有修改SGLang、平台内部监督或Heartbeats。原始论文实验不是本仓库实测。

## 2026-11-26：审查回调的执行所有权

`LocalScheduler.drain_once` 的到期预留只能延迟重投；回调超过预留时间时，旧实现允许另一个调度器同时进入 `on_due`。现在复用跨平台文件锁接口，在同一 SQLite 路径旁持有稳定的 `.drain.lock`，覆盖审查、tick 和回写；竞争调用返回 False，不修改到期时间、版本或任务预算。锁文件不删除或替换，进程退出由操作系统释放锁；原 due、wake 和版本 CAS 继续负责重启后的重试与事件合并。范围是同一本地账本的参与进程，不是跨数据库、远程文件系统或外部 AI 的全机互斥。

验收使用真实 SQLite、真实子进程和受控时钟：预留过期仍拒绝竞争回调；进程被杀后可重新 drain 且锁 inode 保留；tick 异常释放锁；wake 不被旧回写覆盖；重定向锁拒绝。移除 flock 的变异由“回调进入两次”的需求断言拒绝，而非检查器崩溃。相关 88 项检查运行，87 通过、1 项跳过；本次为同一主 agent 自检，不是独立审查或 Windows 实机验证。进程崩溃前已投递的外部作用仍可能重投，锁不提供 exactly-once，也不证明截图现场 owner 已消费队列。
