# 通信优化研究筛选 · 2026-10-09

本轮沿真实链路 `trusted host → Mailbox.publish → inbox → consume_handoff/prepare_context → host verification → acknowledge` 检查。角色注册表保留科研、旅行、代码阅读与 Claude marketplace，未新增角色或依赖。

| 来源与阅读范围 | 机制与本轮决定 |
|---|---|
| [CPP v1](https://arxiv.org/html/2609.33974v1)，2026-09-27，§3、§4消融 | 依据辩论中间结果作条件化边选择，强化学习奖励考虑正确性变化；训练和中间状态不可省略。候选保留，当前无固定模型/正确答案/训练预算，不能声称复现或安全剪掉科研证据。 |
| [MUTE v1](https://arxiv.org/html/2607.03473v1)，2026-07，§4.2–4.3、附录B | 以屏蔽消息后的联合价值差估计通信贡献，需要已训练MARL策略、critic及数据。采用“任务价值约束下优化成本”的评测思想；本地Python邮件箱不具备其数学对象，不实现该学习器。 |
| [AgentPrune官方仓库](https://github.com/yanweiyue/AgentPrune)，代码固定 c544dd6a1858c02c6d5d371d23c6e6ff55e0be21 | 实读 `AgentPrune/graph/graph.py` 的 trainable spatial/temporal logits、构图采样及run；README要求模型API与MMLU/HumanEval/GSM8K。不是无需训练的通用邮箱优化；不复制代码（根LICENSE未发现），不安装或运行其模型实验。 |
| [GitHub工程博客](https://github.blog/ai-and-ml/generative-ai/multi-agent-workflows-often-fail-heres-how-to-engineer-ones-that-dont/)，2026-02-24，接口/状态/重试段落 | 明确结构、动作和边界验证；保留本库固定envelope、幂等ID、独立消费者验收。性能优化不能省略这些检查。 |
| [Google ADK官方博客](https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/)，2025-12-04，§1、§3 | 持久完整状态与按次工作视图分离。现有上下文选择已经实现此方向；本轮把“持久历史/活动视图分离”落实到待处理投递索引，属于工程迁移，不声称论文创新。 |
| [SQLite官方部分索引](https://www.sqlite.org/partialindex.html)，查询日期2026-10-09 | `WHERE receipt IS NULL` 索引只保留待处理项，可在不删除历史记录的情况下缩小查询候选；ACK自动更新索引。直接实施候选，需测新建成本、写放大、跨run选择性。 |

## 候选、基线与边界

- 起点：bb5bf5b8edaebd8910f9a7af28830c668113d339 的真实Mailbox，默认max_events=1000，允许显式扩大。历史上下文token实验与本次SQL测量不匹配，不能拿它作收益。
- 强可用基线：相同SQLite/事务/持久性/完整API与相同数据，无新增索引。比较索引本身及必要时等价ORDER BY；不使用关闭fsync、内存数据库或略过校验的弱基线。
- 本轮预算：预声明最多两种等价候选，不达门禁保留负结果，继续下一研究批次；不得反复改阈值直到通过。
- 复杂度：旧查询可能扫描历史投递并排序；新索引可按recipient遍历pending seq。索引跨run，其他run待处理也可能被访问；不承诺O(limit)、多机或全负载固定加速。全pending时索引不缩小集合。
- Skill：沿用 research-implement-optimize，实际Python标准库/SQLite工具足够；不引入外部框架。`math.rank-nullity-quotient` 知识卡不适用非线性自然语言剪枝，本轮不用它给消息删除作保证。
- 研究状态：CPP/MUTE按预印本处理，仅阅读列明章节，不宣称完整复现或找到全领域最新最强方法；LatCom本次原文打开失败，沿用历史候选记录，不计本轮精读。

## 下一研究问题

真实模型通信A/B仍待可用host：固定科研/旅行/代码阅读任务与模型/权限/预算，对照全量、消费者闭包和任务价值剪枝；同时记录最终正确率、漏掉的关键反例、返工、端到端耗时和实际token。没有质量对照前不启用语义剪枝。本轮只验收SQLite轮询开销。
