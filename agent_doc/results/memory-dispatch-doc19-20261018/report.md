# MEM-DISPATCH-DOC-19：在启动工作前拒绝失效任务文档

基线main `b58836816ff178abce4028348b7d3de3f21a31c7`。
`agent_runtime/task_manifest.py:290–301`在最后文档检查之后调用宿主`context.current()`；回调之后仅重新校验记忆和知识。因此回调期间修改或删除已绑定任务文档时，handler仍会先执行，随后post-action检查才返回blocked。最终状态正确不能证明没有过时任务产生作用。

在最后pre-dispatch try中复用`check_task_documents`，放在记忆/知识检查之后。保留`current=False`优先级、全部已有验证路径及合法Progress追加。错误原因前缀扩展为document/memory/knowledge。没有更改任务目标、参考快照或授权接口。

## 复现与候选验证

`tests/test_dispatch_freshness.py`新增8个测试方法，用实际临时文件和snapshot_project_docs绑定，断言handler调用次数为零。基线15项中5项失败：旧布局任务修改/删除、canonical索引/Plan改变、缓存历史检索后的重复派发。修后普通及`-O`各15项通过；合法Progress、旧/canonical未变文档complete+verify保持通过。

首版测试将legacy/canonical控制放在同一临时根，触发双活跃TASK错误；改为各自独立fixture，再在未改生产代码的基线重跑。before.log保留该测试自身错误，before-v2.log才是有效修前证据。不把该fixture错误算成生产缺陷。

命令：`python [-O] -m unittest discover -s tests -p test_dispatch_freshness.py -v`。
独立新上下文核对源码及原始输出，从git基线加载真实模块，15项正式回归加6项独立边界共21项：基线8失败、0错误；候选普通/-O各21通过。另覆盖已采纳建议变更、任务详情删除、非法UTF-8及兼容控制。详见independent-review.md/json。最终串行全库运行1264项、8跳过、0失败/错误；Reader 3项通过。final-regression.json记录运行前后相同的源码/测试hash。119.507秒仅为测试日志时长，不是性能基准。full.log公开原始最后20行及完整日志SHA，完整原始日志保留于私有检查点。

## 边界与代价

这是现有文档依赖契约的可靠性修复；新增文件读取/哈希成本未测速，无token、KV、QA、TTFT或吞吐提升主张。检查与外部动作不是原子事务：其他线程仍可能在最后检查之后变更文件。该补丁只堵住可同步复现的宿主current回调间隙，不能宣称解决所有TOCTOU或回滚已执行作用。
历史数据不改；对依赖文档恰在current回调期间变更的历史任务需按实际动作审查，不自动判定所有实验受污染。仅当前库修改，不操作SGLang/TwoLevel资源。
研究方法及保留的取舍见[research.md](research.md)。父任务MEM-STORAGE-01继续开放。

公开独立复现：`python [-O] agent_doc/results/memory-dispatch-doc19-20261018/independent-runner.py`；加`--baseline`应有8个失败。需要基线git对象。原版脚本保留，公开版仅将根目录定位parents[2]改为parents[3]。

## 发布文档核验

全库测试之后的project_docs validate发现基线TOKEN-TOTAL-18详情缺少Task-ID/Date，导致当前仓库文档快照入口报错。按唯一索引补齐两项身份元数据，未改原计划/进度含义。原始失败保留docs-validation.log，复验见docs-validation-after.log。此修复改变该详情的稳定快照哈希，已有绑定的计划需正常reconcile；不能冒称旧绑定继续有效。
