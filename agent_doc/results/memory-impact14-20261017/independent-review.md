# MEM-IMPACT-14 独立代码与数据验收

Verdict: **usable-with-scope，候选代码/合成 CPU 配对验收通过**。仍须完成全库/Reader/最终暂存独立审核与发布回读；本文不提前宣布发布。父 MEM-STORAGE-01 未完成，不支持模型 KV、QA、token、网络或完整推理 TTFT 结论。

绑定：plan-v2 SHA256 `f0d5b4b1affd249860801f704c60e22cbb24b930e92bfe75565c4e5aca215b11`；validation-plan.json SHA256 `608015991bc27dc4c6ce95d57a795cd379f01baef2cac8e998cd245beeecaa08`；候选 handoff_basis.py `b2355dab0b097b54ad9c4818ce955b3e46a3f4b11c3175f169d717f2166ac50b`；check.py `69df85701b900d402463bba6f718209e16e7fca52190176c4ed75d39d3a80ae5`；永久测试 `b7130d2681f0036c4a6e16c506b10655272cce42da04ac494066bfd8fa0f05df`。六标准/数值门槛在 producer 前已冻结于 v2；schema projection 写于 producer 后、独立验收前，已明确披露，不冒称全部文件均预先生成。

## 执行与六项标准

实际串行命令 `PYTHONHASHSEED=14 python .agent-runs/memory-impact14-20261017-1256/check.py --out .agent-runs/memory-impact14-20261017-1256/independent`，exit0。producer 完成后才独立重放；没有同时测试/其他 benchmark。后续独立额外检查不计时；已通知主执行者计时结束才可开最终回归。

| 标准 | 结果与依据 |
|---|---|
| implementation | pass。审读完整 diff、baseline、harness、fixture、永久3测试与真实 Mailbox 入口。唯一生产改动抽出闭包，前两轮原算法保持，深/大/稀疏 exact 内置类型才建 reverse adjacency；种子已含两轮扩展，BFS 去重恢复同闭包。claim_graph/根因校验/每项 hash/共享 manifest override/ACK 不动，无跨调用缓存。 |
| reference_boundary | pass。每 actor 250 seeded DAG 与独立祖先 oracle，10 个完整入口场景每对返回全对象相等。本人另设计 34 个定向 case：尺寸0/1/8/63/64/65/128、tuple与反序、空/中间种子、独立组件多根、density511/512/513分派、4种特殊类型原操作轨迹、真实 module导入身份、公共非法记录诊断。候选输入图/种子均不改。 |
| data_integrity | pass。baseline.py 逐字节等于 git main01c60f5 的真实 handoff_basis.py；复算 producer/independent 的源码、baseline/harness/fixture/plan/input hashes。两 actor10×21对全部存在、未丢离群值；corruption后到测量/分配后 DB全表逻辑及 result/manifest bytes 不变。两 actor deterministic 输入/工件 hash 相同；DB根路径不同不要求跨actor数据库hash相同。 |
| numerical_sanity | pass。全部840个 timed ns 值正整数；两个 actor每场景21对的中位数、reduction与gate逐项独立复算相等。内存单位 bytes，timing外单次 tracemalloc，不混称 RSS/VRAM。raw对保留全部最小/最大样本，可直接复算范围；harness没有另外导出min/max字段。 |
| measurement_validity | pass for frozen synthetic scope。10 场景均为完整 impact；构造/consume/腐败/绑定/oracle在外，3 warmup对、21交错对，无缓存返回。源码动态导入确实因 sys.modules 切换调用实际相应模块，finally恢复。两个 actor两个主门槛及各控制均通过。共享CPU未绑核/锁频，不能保证逐调用收益或真实任务分布。 |
| reproducibility | pass for candidate data。独立同21对重放，附加34 case成功，源码/harness核验前后未变。主执行者永久3项普通/-O日志已查看，最终全库与Reader属后续release门禁，不由本项代替。 |

真实导入核查额外用 sys.setprofile（仅 untimed probe）捕获 `basis_impact` code object：baseline/candidate 各恰一次且等于目标模块对应真实 code object，未 stub 生产函数，完成后 sys.modules 恢复 candidate。内部 helper 接收的是 claim_graph 已构成的普通 dict及合法父ID；直接对未校验图/外层自定义graph mapping的行为不承诺。公共输入仍先走原校验，额外非法已存record诊断保持相同。

## 独立完整入口结果

| 场景 | baseline median ms | candidate median ms | 耗时下降 |
|---|---:|---:|---:|
| no-consumption | 0.199005 | 0.214748 | -7.9109% |
| healthy-chain512 | 4.175149 | 3.979539 | 4.6851% |
| artifact-chain128 | 6.114444 | 3.421282 | 44.0459% |
| artifact-chain512 | 54.973371 | 12.865672 | **76.5965%** |
| artifact-star512 | 12.259503 | 12.276098 | -0.1354% |
| manifest-chain512 | 4.132473 | 4.080106 | 1.2672% |
| artifact-small8 | 0.703514 | 0.749873 | **-6.5896%** |
| artifact-shared256 | 11.419567 | 8.009096 | **29.8652%** |
| artifact-dense128 | 56.099300 | 55.916059 | 0.3266% |
| artifact-mixed512 | 29.641200 | 11.794974 | 60.2075% |

producer 主门槛 chain512 下降75.526%、shared256下降29.9003%，独立对应76.5965%/29.8652%，均满足≥25%/≥15%；其他各自退化≤15%。no-consumption未进入闭包代码，其7.91%波动仍如实计为控制回归，不因解释为噪声删除。small8独立退化6.59%、producer约6.13%必须披露，不能宣称所有输入都快。

独立 tracemalloc chain512 baseline1573677 / candidate1573645 bytes，shared256 1364590 /1364558 bytes，均只差32 bytes；producer同样极接近。JSON/完整入口峰值掩盖了局部邻接构造，**没有证明峰值内存改善，也未隔离新增邻接辅助内存**。静态上快路线增加 O(V+E) 临时字典/列表/集合，时间收益是以额外局部结构换取，不能写“零内存代价”。

## 补充检查自身失败保留

independent-extra-v1.py 与 independent-extra.log保留首次补充检查失败：错误oracle假定 `memory_refs=[None]` 必须对外raise。原 `basis_impact` 把 ValueError纳入 stale reasons，此例 baseline/candidate 都返回而不是抛出；不是生产候选回归。修正独立oracle为完整return或exception结果一致且包含memory_refs错误原因，保留 malformed evidence_claims 必须失败的判定。未改生产/正式harness/原测量，不重跑挑样。修正版 independent-extra.py、independent-extra-v2.log、independent-extra.json 的 **34 case** 通过；四类自定义容器/字串调用轨迹完全匹配原循环。

## 验收边界

这是经典图遍历在当前声明依赖上的局部工程应用，无新论文算法或质量主张。未变现有 claim_graph，两轮/64节点/4倍密度只是冻结实现选择，不是最优常数。无真实调用频率、多消费者/WAL写入、进程启动/publish/consume/setup、实际模型或GPU证据；不能把局部完整API改善推成整体Agent任务收益。r09历史SQL失败及impact13仅发现性数据继续保留、不复用为本次性能样本。下一步只有最终串行回归/暂存归档通过才允许原授权内发布。
