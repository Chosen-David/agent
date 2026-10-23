# MEM-SNAPSHOT-01：记忆诊断共用读取快照

基线 `6e32ef824603bc891f36e15787d7e5d4bc64b309`。reconcile先通过list另开连接读取active，再从原连接读取失效状态和依赖；读取间correct提交会混合两个时间点。真实SQLite WAL回归中，更正前为2 active/0 flagged，更正后1/0，旧代码却报告2/1。

机械提取list连接内正文为_list_on，原生list绑定到当前对象时，reconcile在同一已有读事务中收集数据。原正文与新helper AST完全一致，保留过滤、解码、排序、异常及预算语义。自定义子类/实例list和绑定其他账本的方法仍调用一次；既有scope说明明确其快照一致性未核验，不新增字段、不自动更正或失效。

## 证据与复现

新增tests/test_memory_reconcile_snapshot.py：真实临时SQLite启用WAL，在_get水合过程中由另一连接correct并提交，不使用sleep。检查本次旧快照2/0、后续新快照1/0，以及superseded/stale持久化结果；覆盖继承、子类/实例覆盖及绑定其他账本。修前1failure原样保留，修后专项4项通过，-O专项4项通过。

```text
PYTHONPATH=tests python -m unittest tests.test_memory_* [实际展开为各模块] tests.test_project_memory tests.test_handoff_basis
Python3.12.14: 138 tests, 11.923s, OK
Python3.9.25: 138 tests, 12.106s, FAILED(errors=1)
```

唯一3.9错误为既有test_replaced_global_row_factory_keeps_same_connection_ddl_behavior：自定义行工厂执行DDL遇database table is locked。在隔离、未改的6e32基线运行schema模块9项同1error，未把该缺口隐藏或归因本补丁。首次命令未设PYTHONPATH导致fixture导入失败，修正入口后的结果如上；原日志均保留。命令中的通配仅概述，精确模块集合可由sorted(Path('tests').glob('test_memory_*.py'))转换点号模块再追加两模块复现。

[SQLite隔离文档](https://www.sqlite.org/isolation.html)说明WAL读事务保持开始时快照；本修复采用已有事务，不改变账本写入协议。独立Plan v2及最终候选复核接受有限范围：3.12相关49通过、3.9排除旧schema模块40通过，两解释器-O专项各4通过；额外验证首次SELECT前更正返回完整新快照、原生路径仅一连接、普通/矛盾/预算拒绝均不写账本。较广138项由主AI运行，未冒称独审重复。返回的是同一时点快照，可能早于返回时刻。日志reconcile-snapshot-{before,py312-correct-entry,py39-correct-entry,py39-schema-baseline,optimized}-2159.log保留于私有检查点。

一致性保证限原生list读取；自定义读取策略、并发文件替换和宿主行为不在验收内。无速度、token或真实模型质量收益主张，无新增论文阅读计数。SYSTEM-99仍未完成：既有3.9行工厂边界、目录alias、决策协议冲突、真实宿主/输入暴露/全部actor usage与任务质量继续open。
