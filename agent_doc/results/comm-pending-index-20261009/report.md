# 通信待处理索引：独立实测与范围

历史快照：此报告对应usage账本整合前的索引单因素试验。最终发布版本见 [整合补验](../comm-pending-index-integration-20261009/report.md)；不要直接在新main执行以下旧命令并混用数字。重放本历史试验须在隔离checkout中以 `candidate-before-integration.py` 的精确字节恢复通信模块，再核对manifest代码哈希。

日期：2026-10-09。任务：COMM-PERF-01。基线：`bb5bf5b8edaebd8910f9a7af28830c668113d339`。

本轮采用仅3行DDL的部分索引：`communication_deliveries(recipient,seq) WHERE receipt IS NULL`。持久事件/回执历史保留，查询SQL、路由、幂等键、引用与预算校验均不改变。已有数据库由Mailbox构造器自动创建索引，重复打开幂等；没有引入框架、服务或模型训练。

这是持久历史与活动工作集合分离的工程应用，不声称新的通信学习算法。CPP、MUTE、AgentPrune等研究的机制、实读范围和暂缓原因见 [research.md](research.md)。

## 配对测量

使用真实文件SQLite和完整 `Mailbox.inbox` 调用（连接、SQL和JSON解码均计时），合成事件由基线公开publish/ACK接口生成，再backup为两臂相同数据。5次预热、31次交错配对；p95为nearest-rank样本统计，不是生产SLA。VM指令计数单独运行，不污染计时。独立上下文在本任务全仓回归结束后重跑全部6场景，精确结果/顺序/状态/usage与基线一致。

| 场景（总事件/接收者） | 基线中位数 ms | 索引中位数 ms | 加速比 | 基线→索引 VM指令 |
|---|---:|---:|---:|---:|
| 100/2，全待处理 | 0.541 | 0.525 | 1.03× | 1828 → 1416 |
| 1000/8，95%已回执 | 1.364 | 0.430 | 3.17× | 11450 → 816 |
| 10000/8，99%已回执 | 8.576 | 0.485 | 17.70× | 110700 → 1416 |
| 10000/8，全部已回执 | 6.970 | 0.345 | 20.20× | 110100 → 116 |
| 10000/8，4个交错运行，目标99%已回执 | 3.039 | 2.374 | 1.28× | 27826 → 53016 |
| 10000/8，4个交错运行，目标已清空 | 3.117 | 2.551 | 1.22× | 27601 → 52616 |

三个预定积压门槛均达到：VM减少>80%，中位数加速≥2×。小队列差异接近噪声，不宣称收益。初轮与部分回归重叠的计时保留于 `raw/index-only.json`，只作探索；上表来自 `raw/independent-quiet.json`，全部样本、p95和实际PRAGMA均保存。硬件/版本见environment.json。

## 额外成本与局限

| 场景 | publish中位数：旧→新 ms | ACK中位数：旧→新 ms | 候选首次完整打开 ms | DB文件增长 bytes |
|---|---:|---:|---:|---:|
| small | 0.595 → 0.698 | 0.391 → 0.414 | 0.733 | 4096 |
| default_backlog | 0.907 → 0.773 | 0.617 → 0.467 | 1.728 | 12288 |
| large_backlog | 0.937 → 0.984 | 0.423 → 0.474 | 6.541 | 20480 |
| drained | 0.992 → 1.007 | 0.368 → 0.442 | 5.827 | 0 |
| multi_run | 0.642 → 0.628 | 0.385 → 0.357 | 20.755 | 1130496 |
| other_run_pending | 0.639 → 0.711 | 0.396 → 0.427 | 18.847 | 1126400 |

- 索引按接收者、未回执状态组织，不含run_id；多运行场景还会访问其他运行的待办，VM工作量约增至1.9倍，且文件增长约1.13MB。实际墙钟略改善不能掩盖这一退化，不承诺跨运行扩展性或O(limit)。若宿主按run分库存放，更符合本轮主要获益条件；本API允许共享数据库，不假定所有宿主已经分库。
- 全部待处理时集合没有缩小；写入与ACK需要维护索引。上表首次打开包括完整构造器而非纯建索引，文件增长为物理文件大小差，0不等于索引不占页。保留原样本中的噪声和退化，不挑最好一次。
- 测量使用本地合成事件、当前Python/SQLite/CPU和系统缓存；没有真实模型任务成功率、token费用、网络通信、GPU或应用端到端收益。没有后台模型host/tmux部署声明。

## 验证与使用

- 通信专项16项通过，新增旧库迁移/完整历史保留及非连续ACK、多运行、重启用例。既有并发重试、路径/摘要、引用变更、不可变回执和预算等继续通过。
- 全仓854项：845通过、8可选项跳过、1既有失败。失败为 `test_generated_plugin_references_are_current` 的 `code-reading_execution.md` 不同步，在干净基线worktree复现相同失败；相关文件本轮未修改。原始日志保留。
- 独立审阅：plan_review.md保留首次返修；plan_review_v2.md批准冻结计划；code_review.md、result_review.md和verification.json给出实际审查/结果适用范围。manifest.json固定代码、输入、配置、环境和原始数据哈希。人工Work独立调用不冒充自动ReviewSession服务。

复现（仓库根；输出路径必须不存在）：

```bash
python scripts/benchmark_communication_inbox.py \
  --baseline bb5bf5b8edaebd8910f9a7af28830c668113d339 \
  --plan agent_doc/results/comm-pending-index-20261009/plan.json \
  --out /tmp/comm-inbox-reproduction.json
python -m unittest discover -s tests -p test_communication.py -v
```

首次脚本的精确字节保存在benchmark-v1.py；当前脚本只补了真实PRAGMA和测量窗口时间，方法/工作负载没有变化。无需第二个排序候选：索引单因素已满足预定门槛，避免无收益扩展。

## 持续任务检查点

已读回现有“agent库通信优化”任务启用、每小时一次；未新建、未更改其他任务。配置读回不证明云端已实际执行。下一轮先同步main并复用本轮基线与结果，优先考察跨run待办选择性或真实host的通信质量/成本A/B；没有实测提升则保留负结果、继续查新，不为轮次制造修改。main发布不代表用户现有安装已同步。
