> 发布说明：并发main已采用等价索引，本轮保留该实现，只合入独立证据；本页数字对应归档候选，参见 [并发协调](publication_reconciliation.md)。

# 通信索引：新main整合后的最终验收

日期2026-10-09，COMM-PERF-01。发布前main并发合入 `0498816` 的事务usage账本，保留完整账本和本轮3行部分索引。原始bb5bf5b单因素证据仍保留，不能当作整合后的倍率。

新基线：`0498816bbe0a9d5eeee78284d2cba94817c4eb7c`；候选通信模块SHA-256：`c02b577228f9625e7bcb641e7be1448c2733b8de480c574efcc11617b327ebad`。对新基线的生产代码差异仅为 pending-recipient/seq 部分索引；原inbox查询不变。

## 同数据独立复测

沿用先前冻结的6场景、5次预热、31次交错配对、完整Mailbox.inbox计时、独立VM计数及精确输出比对。基线和候选均启用新usage账本。

| 场景 | 基线中位数 ms | 索引中位数 ms | 加速 | VM指令：旧→新 |
|---|---:|---:|---:|---:|
| small | 0.420 | 0.424 | 0.99× | 1856 → 1444 |
| default_backlog | 1.073 | 0.468 | 2.29× | 11478 → 844 |
| large_backlog | 9.743 | 0.679 | 14.36× | 110728 → 1444 |
| drained | 7.293 | 0.388 | 18.78× | 110128 → 144 |
| multi_run | 3.091 | 2.450 | 1.26× | 27854 → 53044 |
| other_run_pending | 3.002 | 2.459 | 1.22× | 27629 → 52644 |

small=100事件/2接收者全待处理；default_backlog=1000/8、95%回执；large_backlog=10000/8、99%回执；drained=10000/8、全回执。后两例10000事件交错分属4个run，只有目标run按99%/100%回执，其他run全待处理。默认轮询limit20。

## 全部成本与限制

| 场景 | publish中位数旧→新 ms | ACK中位数旧→新 ms | 候选首次完整打开 ms | 文件增长 bytes |
|---|---:|---:|---:|---:|
| small | 0.728 → 0.781 | 0.571 → 0.490 | 0.804 | 4096 |
| default_backlog | 1.307 → 1.166 | 0.849 → 0.866 | 4.099 | 12288 |
| large_backlog | 0.724 → 0.802 | 0.542 → 0.544 | 7.782 | 20480 |
| drained | 0.659 → 0.694 | 0.420 → 0.426 | 5.326 | 0 |
| multi_run | 0.649 → 0.761 | 0.440 → 0.443 | 21.621 | 1130496 |
| other_run_pending | 0.721 → 0.861 | 0.501 → 0.579 | 20.034 | 1126400 |

- 不丢消息、不删历史、不改ACK/预算/引用验证；25项通信与账本回归、1项插件同步检查通过。旧完整回归854项的1项插件失败已由上游修复并在整合版复验；没有把旧日志改写成全绿，也未重复宣称新版全仓854项重跑。
- 三个预定积压门槛均满足>80% VM减少及≥2×中位数加速。small约0.99×，不宣称提升。跨run两个场景虽然延迟略改善，但VM工作量仍约1.9×，文件增长约1.13MB；共享数据库扩展性仍是下一轮候选，不能声称O(limit)或普遍收益。
- 同一台共享CPU、合成真实SQLite文件测量；未锁频、未保证独占，保留所有样本与p95。首次打开包括完整构造器；文件增长0并非零索引页。没有模型质量、tokens、网络、GPU或应用端到端性能结论。
- [计划审核](plan_review.md)、[独立结果复核](result_review.md)、[冻结清单](manifest.json)及[原始数据](raw/independent-quiet.json)支持精确范围。原始研究与初次返修见 [研究筛选](../comm-pending-index-20261009/research.md)。CPP/MUTE/AgentPrune为学习式候选，本轮采用持久历史与活动视图分离的工程方法，不声称复现其算法或创新论文。

## 复现与续接

```bash
python scripts/benchmark_communication_inbox.py \
  --baseline 0498816bbe0a9d5eeee78284d2cba94817c4eb7c \
  --plan agent_doc/results/comm-pending-index-integration-20261009/plan.json \
  --out /tmp/communication-integration-new.json
python -m unittest discover -s tests -p "test_communication*.py" -v
```

须先核对候选模块/脚本哈希与manifest；未来main改变后使用当前归档快照或重新做版本补验。既有每小时通信优化任务已启用，未重建或更改其他任务；配置读回不等于云端批次已执行。下一轮优先跨run待办选择性，或具备固定模型/质量rubric后做真正通信质量与成本A/B。没有可靠收益则继续查新并保留负结果，不强行提交。
