# SYSTEM-99 阶段F：无关登记不改写已审任务

问题ID：`CHAIN-SEARCH-DRIFT`。基线 `789697f2b3e2e190a6954248d4b18cbbe0b44a4d`；按[Version6独立方案审核](search-review.md)实施。Python3.12.14、Linux6.18.55/x86_64、glibc2.39，仅本地CPU/SQLite/临时文件，未调用模型或部署宿主。

## 触发、修复与测得变化

保护计划A→独立验收A→B→独立验收B中，A正常登记中央结果后，B的无命中完整查询仅`scanned:0→1`，旧`ReportingHandler.run`仍因整个响应不等而阻塞B。这是可用性误阻塞，不是安全绕过。修前8方法有2断言失败、6通过；A实际运行且验收完成，B实际调用0次。首次fixture未中央存储的errors、随后负控共用blocked状态的问题均另存失败日志，不作生产红证。

`agent_runtime/task_manifest.py:66–102,322–331`仅分类完整已知v1词法响应：无partial/errors，默认扫描范围及字段/类型合法，除scanned外规范JSON完全相同才接受计数变化。完整相同响应保留既有兼容路径，同时使用原结构相等和JSON相等，防止bool/int、tuple/list或对象键编码造成宽相等。候选新增/消失/hash/排序/分数变化及查询、schema、未知字段、缺口变化仍拒绝。

原计划SHA、审核回执、传给handler的整个task保持不变；实际新查询照常完整写journal，计数例外另记`prior_result_scan_only`。分类日志失败时B不执行，恢复日志后也不自动重放。没有修改搜索器、缓存、认证、结果gate或自动复用规则。

新14方法中，实际双生产者链修后四节点完成，A/B各执行一次，两个独立算术gate均done；重启不产生第二次计划审核。显式复现/new_claim仍实际执行，不替换为旧结果复用。原始输入为`n=[0,1,2,7,19]`、3次重复、seed0、无量纲整数平方和；既有验证器以闭式公式独立复算、核对样本ID、边界及原文件。此处“独立”是CPU测试adapter契约，不是模型身份认证或真实科学任务验收。

## 复现与证据

```text
python -m unittest tests.test_prior_search_drift -v
drift-before-v3.log: Ran 8 tests in 3.890s; FAILED (failures=2)
drift-after-v5.log: Ran 14 tests in 4.141s; OK
focused-f-v3.log: Ran 106 tests in 14.725s; OK
optimized-f-v3.log: Ran 14 tests in 7.388s; OK
full-f-v3.log: Ran 1391 tests in 105.909s; OK (skipped=8)
reader-f-v2.log: Ran 4 tests in 0.491s; OK
reader-app-f-v3.log: Ran 3 tests in 1.585s; OK
python scripts/sync_plugin_references.py --check: exit 0
```

最终全库v3中1383项执行通过、8项跳过；根Reader/Memory的4项也包含在该全库中，与另跑Reader应用3项分列。`after-v2`的1个error是新断言从tick返回状态取plan导致KeyError，已改为Store.snapshot；旧日志未覆盖。v4后补双侧相同畸形字段/仅count变的负控，证明白名单不只依赖字段不相等拒绝；同时对齐空白query校验，最终以v5源码/测试与全库v3为准。先前13项及两次全库旧候选日志保留，不混作最终通过。

| 固定对象 | SHA-256 |
| --- | --- |
| 基线task_manifest.py | `b9ec8f8881e26265fec368570bfb2b9fde2aed01ae6643ee0dab7f4543cd0e41` |
| 最终task_manifest.py | `b9bef1029d9aa1b5b0d83c793c0f676b05ccdacc20a21be948f1cccaefcf1729` |
| 新回归test_prior_search_drift.py | `4778fc87b0c0e279f729b866ef2c34a33befc8de39c207089da0b906d69bed7b` |
| 既有算术fixture/验证器test_result_validation.py | `79e3840fe6b39432526e4c75fcf98f9c6bf2a3aa410e58d2d281550902482377` |
| 修前最终8方法日志 | `f0654e4be7dad59c387cea9a5aeb0b0a343eda24dbb9b69cf35b00eb6e6c1d4d` |
| 修后最终14方法日志 | `3ee7fbe917092795425df5e7cf52c7a7bd1bd1e04d4a536a4b96cc271ed8b279` |
| 最终全库v3日志 | `c69d89ea4bdbb713a25f0be8e5a35bda16dd36baa5fa1ae05652195a1514cb29` |

[最终独立验收](independent-stage-f-final.md)接受`usable-with-scope`、无阻断；
另实际运行最终14项、Reader应用3项及同步检查，逐行核算全库1383通过/8跳过。
此前[分版本独审与暂停记录](independent-stage-f.md)保留，不将其旧候选“最终”
称谓代替当前冻结SHA验收。

## 未完成边界

不是性能优化：未测wall/模型token/质量/成本，不报告提速。仅完整无错查询的纯统计变化获益；本库现有81个缺登记目录、默认有界查询截断和真实候选变化不在例外中，仍可能要求版本化重审。此补丁不让不完整搜索自动等价，也不提供查询快照隔离或check/effect原子性。

[新增正文阅读D](research-d.md)记录固定`2609.03340v2`正文/附录、消融、局限与adapt/reject；同一未结束批次累计12篇，不重计旧批次。实现Skill要求的基线、实际硬件边界及负结果保留；论文成绩不作本库收益。通信/记忆更正到真实消费者的恢复、历史登记覆盖、Claude新会话加载、模型质量/总成本和tmux/SSH宿主验收仍open。阶段提交只是可恢复检查点，SYSTEM-99未完成。
