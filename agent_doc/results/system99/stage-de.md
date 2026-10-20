# SYSTEM-99 阶段D/E：历史发现与审核恢复

基线 `9ab9becde217b74c50464155ab675dee9f422a60`；沿用同一未结束批次，按[Version5独立方案审核](independent-plan.md)实施。Python3.12.14、Linux6.18.55/x86_64/glibc2.39；仅本地CPU、SQLite和临时文件，无模型或外部宿主运行。

## D / RESULT-CATALOG

[调查与边界](catalog-plan.md)确认252个结果目录中82个缺少record，并不代表82份坏结果。只为`result-fd95`调用现有`ResultStore.register_history`，新增record，保留14份原文件及其哈希，与`50c1ca1e74df1026ba05b4cfd53903605315b234`逐字节相同；未补造缺失的私有全库日志。

同一正式查询`RESULT-FD-95`与`result-fd95`（limit20/max_scan5000）修前各扫描252、无命中、82个缺记录错误；修后各命中目标一次、81个错误、partial=false。record SHA256为`74f8c5b361d8d95662bf61fdf5da7c9cf964b12597a8e472932ce8387f15e828`。`catalog_probe.py --after`普通与`-O`输出一致，逐项检查14引用；`decide_run`继续返回`verify_delta/unknown`、proof=null、禁止自动跳过，即使提供返回True的verifier也不调用。登记时间不冒充测量时间，旧pass不升级为当前验收。

这里只恢复一个真实结果的发现能力；其余81个目录待分型处理。登记会改变旧`prior_result_search`响应，不能替旧保护计划静默刷新审核；多生产者查询漂移仍open。没有上下文token、模型质量或速度收益主张。

## E / CHAIN-REVIEW-RECOVERY

`agent_runtime/core.py:385–401`原顶层审核拒绝只阻塞整链与未执行节点，保留已完成节点的done；审核恢复后旧完成状态可重新生效，无显式恢复围栏。新5项回归修前4失败、1通过；取消负控原本就通过。早期v2日志的两个fixture路径冲突已修正，不能当生产缺陷证据。

拒绝审核时将done节点持久化为`blocked/plan_review_after_effect/requires_reconciliation`，沿用既有恢复契约。保留完成证据、attempts、dispatches和重试时刻；认证恢复、后续wake与Store/Engine重开不解除围栏。当前有效审核、授权、依赖和证据核对后的显式reconcile才可恢复；动作不重放。混合DAG的已完成前缀阻塞后继，独立且尚未执行的支线可在认证恢复后运行；取消保持取消。未改managed、doing lease或事件去重顺序。

```text
review-restore-before-v3.log: Ran 5 tests in 0.578s; FAILED (failures=4)
de-focused.log: Ran 79 tests in 6.765s; OK
de-opt.log: Ran 5 tests in 0.807s; OK
de-full.log: Ran 1377 tests in 100.097s; OK (skipped=8)
de-reader.log: Ran 4 tests in 0.504s; OK
sync_plugin_references.py --check: exit 0
```

全库1369项执行通过，8项跳过不算通过。[独立结果验收](independent-stage-de.md)接受usable-with-scope：109项中108通过、1真实tmux跳过，另验证原围栏逐字段保留、审计异常事务回滚、旧core固定4失败/取消正控、重复登记拒绝且15文件哈希不变、临时坏引用负控。独立没有重跑全库。本修复要求收到可信tick；纯status读取不认证，不声称已停止的monitor会自行恢复。

[新增正文阅读](research-c.md)固定Chubby原PDF版本、章节、运行数据与局限；同批累计11篇，不计新一轮。历史登记覆盖、查询漂移、通信/记忆更正到真实消费者的完整恢复、真实模型质量与总成本、Claude加载和tmux/SSH宿主仍有关键验证缺口。阶段提交仅供恢复，SYSTEM-99未完成。
