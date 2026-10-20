# SYSTEM-99 阶段C：完成证据复核

基线 `68e883e986c97ffbfc96602e96baafef46880e4d`；Python3.12.14，Linux6.18.55/x86_64/glibc2.39。本地临时文件、SQLite与CPU；未启动外部模型、服务或未知作业。

## CHAIN-TERMINAL

`agent_runtime/core.py:403`原done快返跳过当前证据检查。全部完成后修改真实ArtifactHandler文件、返回False、删除handler或抛异常，新的可信tick仍返回done。修前新增6项回归全部失败，含8个失败子例；既有active链回归不能覆盖此入口。

按独立审核的SYSTEM-99 Version4，仅整体done的新事件进入`_check_done`，沿用现有依赖闭包计算；本次失效的原done节点转blocked并需显式reconcile。事件与状态同事务持久化，立即返回，不领取任务。旧evidence/attempts保留；恢复原文件不自动恢复验收，依赖须按序显式核对。活跃链原failed语义、cancelled、重复event、managed worker与scheduler均不改变。

```text
terminal-before-v3.log: Ran 6 tests in 0.385s; FAILED (failures=8)
terminal-focused.log: Ran 74 tests in 5.855s; OK
terminal-full.log: Ran 1372 tests in 96.927s; OK (skipped=8)
terminal-reader.log: Ran 3 tests in 1.588s; OK
sync_plugin_references.py --check: exit 0
```

专项含真实CLI init/tick/status、文件替换、Store/Engine重开、逆拓扑菱形和同闭包多节点失效、无关支线、非幂等动作不重放、去重事件行数、取消与显式恢复。CLI用明确legacy临时fixture，不代表生产计划降级或真实独立宿主。全库1364项执行通过，8项跳过不算通过。

[独立验收](independent-stage-c.md)已接受usable-with-scope：独立83项（82通过/1真实tmux跳过）、Reader3及同步通过，另补当前有效保护fixture、审计异常事务回滚和真正双独立根闭包。固定旧Engine的5个API方法仍有7预期失败；未把加载失败当修前证据。源/测试/修前/全库日志哈希在回执保留，未将独立专项称为独立全库重跑。

## 尚未完成

本修复只覆盖**当前审核有效且实际收到新可信tick**的portable终态。`status`回读不认证，已停止monitor不会自行重arm。顶层计划审核撤销后的终态恢复尚待单独核验；managed原完成复核另有路径，不能冒称本补丁修了所有宿主。

历史结果登记覆盖、双生产者查询漂移、通信/更正到真实消费者报告失效与恢复、真实模型质量/总成本和跨机宿主仍open。同批正文十篇阅读已记录，不把论文成绩、字节量或本地测试通过当模型收益；无性能主张。本次是阶段检查点，SYSTEM-99未完成。
