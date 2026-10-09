# 通信优化调研与本轮取舍（2026-10-09）

这是有界筛选，未声称覆盖所有最新工作或复现模型结果。先核对现有库：不可变消费者路由、引用而非全文广播、预算、持久邮箱、消费验收、选择性上下文、返修恢复已存在。没有重造消息总线或新 Skill。

| 一手来源与阅读范围 | 可迁移内容 | 本轮决定 |
|---|---|---|
| [GOSC, arXiv:2609.39477v1, 2026-09-30](https://arxiv.org/html/2609.39477v1)，§IV-C/E、V-G/H；作者[代码](https://github.com/frezazadeh/gosc-agentic-teams/tree/387b49389385b51c275dc5a22ec1672087edda1d)，`gosc/realistic.py` 1–120 | 联合考虑消息内容、时机、传输成本；工程扩展明确计入包头和控制流量 | 借鉴“精确计成本、同时验证结果”的设计原则。现库只计 envelope UTF-8 字节×收件人数，本轮降低该计账成本；不把字节当 token，也不声称实现其无线调度算法。论文的信道、价值估计与本库不同，自动抑制消息暂缓。 |
| [When Upstream Messages Override Correct Answers, 2609.36855v1, 2026-09-29](https://arxiv.org/html/2609.36855v1)，§2–3.1 方法与原始摘要 | 固定接收方证据，比较展示/隐藏/反转上游结论；消息帮助与伤害应分别测量 | 保留消费者独立验收，不因吞吐优化删除纠错或审稿消息。后续语义筛选需要加入错误消息干预；本轮不声称模型正确率提升。 |
| [OpenMAS-GCom, 2609.21527v1, 2026-09-18](https://arxiv.org/abs/2609.21527v1)，摘要筛选；HTML正文获取失败 | 控制模型、提示词、预算和通信因素以隔离归因 | 仅采用受控对照原则，未声称全文精读或复现其29数据集。当前三臂共享输入和API语义，只改变预算统计实现。 |
| [RADAR 作者仓库](https://github.com/cszhangzhen/RADAR/tree/71d92b5e1517453f055a885c64cd6281d08521ab)，README、`model/denoising.py` 1–80 | 查询适应的图生成；实现依赖PyTorch/PyG及训练模块 | 候选而非依赖：当前缺任务质量训练/验证集，不采用训练后的拓扑替换固定权限路由。ICML2026为作者README声明，OpenReview遇验证页，未额外核实。没有复制代码。 |
| [SafeSieve, 2508.11733](https://arxiv.org/abs/2508.11733)；[DiffMAS, 2604.21794](https://arxiv.org/abs/2604.21794) | 分别为经验剪枝、可学习潜变量通信方向 | 本轮只做检索/摘要筛选，HTML获取失败；不作为已实现机制或实测依据。潜变量路线需要模型内部接口。 |
| [Anthropic 多Agent研究系统](https://www.anthropic.com/engineering/multi-agent-research-system)，2025-06-13，生产可靠性部分 | 长任务恢复、并发部署期间新旧执行者并存、异步一致性 | 用数据库触发器维护账本，使旧版Mailbox的append写入也被统计；保留旧数据、ACK含义与故障回滚。不是采用其私有系统实现。 |
| [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)，2025-09-29 | 用小引用按需读取，而非复制完整上下文 | 现有prepare_context已覆盖相关工程方向；不在本轮重复添加。 |
| SQLite [CREATE TRIGGER](https://www.sqlite.org/lang_createtrigger.html) 与 [Atomic Commit](https://www.sqlite.org/atomiccommit.html)，本日核查 | 触发器随语句执行，事务统一提交/回滚 | 独立实现INSERT维护的物化计数；迁移创建、回填和触发器同一IMMEDIATE事务，不改变durability PRAGMA。 |

GOSC论文脚注写非商业使用，当前仓库README显示MIT；有版本差异，因此本轮不复用其代码，避免混淆许可或将模拟器收益移植。固定GOSC源码blob `35691945c6ad9c70ec4e3b13c948dd5363774a2e`；RADAR源码blob `e9e15b6c9098bd04b4079535370dd62ae002ea03`。读取只覆盖上述指定范围，没有安装外部依赖。

## 候选比较与复杂度

记N为该run历史事件数、D为历史投递数、B为单条envelope字节、F为新消息fanout、R为run数。下述为计账额外工作，完整publish还包括路由扫描、文件校验、连接和持久化。

| 候选 | 历史统计开销 | 维护/语义 | 决策 |
|---|---|---|---|
| 原实现扫描COUNT与JOIN/SUM | 每次检查遍历历史；带字节预算累计工作可随N近似二次增长（定长/F固定时） | 无新状态，原语义 | 保留冻结基线 |
| covering index扫描 | 仍遍历历史，但可能减少表回查；增加索引空间和写成本 | 无近似 | 实测为第二基线，记录EXPLAIN QUERY PLAN及建索引成本 |
| 事务增量账本 | 一次run索引读取；每新事件/投递更新，约O(log R + F(log R + log N + B))，不含SQLite常数；额外状态O(R) | 一次迁移扫描已有数据；与事件事务一致；旧append进程兼容 | 本轮候选，必须通过冻结性能和正确性门禁 |
| 语义剪枝/价值调度 | 可能减少消息或token，但有评分成本 | 需要接收任务效用、遗漏风险及真实模型A/B | 暂缓，不能将拓扑变化混入无损底层测量 |

这是经典增量视图维护在本库通信预算中的工程应用，**不是新学术算法或论文方法复现**。若无收益，不以“用了论文idea”通过验收。

## 历史知识与结果使用

已查询 `agent_doc/results/`、任务索引及既有通信文档。历史selective-context测量是payload编码成本，不能复用为本次吞吐证据。旧模型交接trace显示大部分时间不在本地调用，故不宣称本轮能同比加速模型任务。`math.packetized-completion@1` 已按路径读取并拒绝直接应用：当前fanout/重试/多消费者不满足单FIFO无丢弃流条件。计数正确性使用事务不变量及独立扫描重算验证。

## 下一轮可证伪候选

只有当前批次通过后，再考虑消费者当前上下文的重复引用传输成本或待办扫描成本。语义路线先建立固定模型/预算、原始消息/隐藏消息/错误消息三臂评测，再评估是否值得改变路由；不得因节省消息降低科研验收或隐去负结果。已有每小时任务继续，不新建定时器。
