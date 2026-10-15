# Agent 记忆与 KV 存储：方法核对及应用决策

日期：2026-10-15；代码基线 `408af9e8975eb2bc8db6c97a81db7743bc587ecd`。目标是原始证据可追溯、修正及时失效，以及实际任务成本降低。下面区分跨会话事实存储、上下文组织、引擎 KV 三层，避免缓存命中被误认为回答正确。

## 阅读范围

本轮直接访问以下 12 篇原文，针对方法、前提、实验设计与局限阅读；不是摘要凑数，也不声称所有页面、附录及图像都新近完整审读。LongMemEval/A-MEM/MemGPT/Zep 的既往深入笔记保留于 `docs/continuous_optimization/rounds/2026-10-06-memory/research/memory.md`，本轮复核相关正文，不重复计算为新论文。近期不可访问的 Tessera/KVSET 仅是线索，没有列入已读。表内“最小验证”是后续实验要求，除首阶段检索外均未执行。

| 原文及本轮覆盖 | 机制与实验边界 | 本库决定及最小验证 |
| --- | --- | --- |
| [LongMemEval, 2410.10813v1](https://arxiv.org/html/2410.10813v1)，§3–5，重点§5.2–5.4 | 分解提取、跨会话推理、更新、时间、拒答；索引/召回/阅读分别影响结果。扩展检索键可保留原文，摘要替代原文有信息损失；时间过滤依赖时间解释正确。 | adapt：保留原始记录和修正链，先减少无关加载。后续按五能力分组评估，而非仅 recall@k；加入错误旧事实与无答案题。 |
| [A-MEM, 2502.12110v1](https://arxiv.org/html/2502.12110v1)，§3–4及检索消融 | 原子笔记、链接与演化，检索再扩展关联内容；LLM 链接与更新有额外成本，实验类别收益不同，不能证明任意自动改写可靠。 | defer 自动演化；adapt 来源链接与按需展开。固定原文对照 link-only/LLM-update，记录事实矛盾率、漏召回、额外调用。 |
| [Mem0, 2504.19413v1](https://arxiv.org/html/2504.19413v1)，§2–4与结果表 | 提取与 ADD/UPDATE/DELETE/NOOP 决策；图版本引入关系。全文上下文仍有质量优势，图结构也并非所有指标占优；搜索和生成延迟需分开。 | defer 自动删除/覆盖既有 verified 记忆；候选抽取须通过现有 accept/correct。用固定 QA 比较完整历史、仅检索、候选摘要，联合计费与质量。 |
| [MemGPT, 2310.08560](https://arxiv.org/pdf/2310.08560)，本轮 pp.1–5 §2、§3.1；其余沿用旧笔记 | 有限主上下文、外部存储与分页检索，通过控制流换入。对话记忆实验支持分层思路，不能证明任意压缩保真。 | adapt 分层访问原则：原始历史仍落盘，命中才装配完整对象。新增本地全入口差分基准；未来验证多轮修正及分页遗漏。 |
| [Zep, 2501.13956v1](https://arxiv.org/html/2501.13956v1)，§2–4及分类结果 | episode/entity/community 图，区分事件有效时间与录入时间。部分类别退化，网络/服务对照存在环境差异。 | adapt 双时间及 provenance 设计，defer 重型图服务。测试迟到事实、回溯更正、同名实体；保留原始时间及来源，不能仅测总均分。 |
| [PagedAttention, 2309.06180v1](https://arxiv.org/html/2309.06180v1)，§3–6 | 逻辑/物理 KV 分页、共享及写时复制缓解碎片；收益受模型、并发、GPU 内存及调度影响。 | reuse 成熟引擎，不在纯 Python Agent 重做 GPU allocator。需真实引擎确认分页派发，测峰值内存、并发、TTFT 与引用释放。 |
| [SGLang, 2312.07104v1](https://arxiv.org/html/2312.07104v1)，§4–6 | RadixAttention 按 token prefix 复用，引用计数与调度协同。前端代码移动并非通用严格语义等价优化。 | defer 引擎接入；稳定前缀候选须先保证提示词和工具顺序语义。比较 exact prefix on/off；不可为命中率重排来源或共享跨租户状态。 |
| [CacheBlend, 2405.16444v1](https://arxiv.org/html/2405.16444v1)，§3–7 | 非 prefix KV 缺失跨文档注意依赖，通过选择性重算恢复质量并调度加载/计算；属于实测质量权衡，非逐位等价。 | defer 默认启用。禁止简单拼接独立文档 KV；日后测位置变化、文档顺序、QA 分数及重算比例，全重算作正确性参考。 |
| [KVFlow, 2507.07400v1](https://arxiv.org/html/2507.07400v1)，§3.1–3.3、§4 | Agent Step Graph 的后续使用距离指导驱逐/预取，固定 prefix 与变化 suffix 分开；GPU/CPU/loading/offloading 状态协同。真实 PEER 与长固定前缀的合成收益幅度不同。 | adapt 到后续缓存访问计划，暂不启动预取线程。必须有后端 ready/free、引用与取消协议，再比较单流、公平 IO 预算和误预取成本。 |
| [LMCache, 2510.09665v1](https://arxiv.org/html/2510.09665v1)，§2–8，重点§4–7 | connector 解耦引擎，批量搬运、层间流水、少复制；控制面 lookup/pin/move/clear。短上下文或网络慢时传输成本可抵消重算收益。 | 优先作为未来实际 adapter 候选。先 exact prefix CPU tier，对比 HBM-only 和无缓存；观察真实 token/byte 命中及 p50/p95，而不是模拟 key 命中。 |
| [RAGCache, 2404.12457v1](https://arxiv.org/html/2404.12457v1)，§4、§7及配置 | knowledge tree 按上下文位置组织前缀，PGDSF 结合频次、成本、大小；实验 workload、缓存容量和文档顺序会改变收益。 | adapt 后续“重算成本/字节”驱逐实验，defer 本轮实现；须与 LRU 强基线对照，计算建索引及迁移总成本，不改变检索文档顺序来刷收益。 |
| [ObjectCache, 2605.22850v1](https://arxiv.org/html/2605.22850v1)，§2–6 | prefix/hash 身份、层优先布局、批量服务聚合与远端数据路径；短输入的启动开销和长输入可隐藏传输是不同区间。 | defer 远端 object store：目前无对应部署与负载证据。后续验证内容/配置身份、损坏/部分写、恢复、每字节读写成本及端到端时延。 |

## 当前实现与应用边界

`python -m agent_runtime.project_memory list` → `MemoryLedger.list()` → `_get()` → SQLite 是本轮真实入口（实际参数见 `--help`）。现有 `add/accept/correct` 维护不可变原文和依赖状态。本轮把“分层访问、原文保留、先确定相关记录再装配”的原则用于 CO-017 已登记候选：只为请求状态加载内容、文档引用及依赖，仍以 Python 解码全部 scope/文档元数据保护已测错误行为；scope 精确成员过滤保持原位。它是常规延迟装配技术的适配，不是 MemGPT、KVFlow 或 LMCache 算法的完整复刻，也没有语义摘要、向量压缩或 GPU KV 新功能。

针对 runtime/scripts 的 `KVCache|past_key_values|prompt_cache|prefix_cache|cache_control` 检索和当前模型/任务接口追踪，未找到实际 KV tensor 存取消费者。纯 Python 字典保存 token hash 不能省去模型 prefill；因此本轮不增加无人消费的“KV cache”假接入。

## 后续可执行路线

1. **事实层**：保留 raw 内容、source、scope、created_at、接受与修正身份。召回索引是可重建副本；候选摘要不能成为覆盖原文的唯一来源。增加 LongMemEval 风格的更新/时间/拒答真实任务，测试恢复和依赖失效。
2. **上下文层**：先测现有装配器的来源/依赖身份及稳定 token 前缀。缓存身份至少绑定项目/租户、精确 token 前缀、模型权重版本、tokenizer/chat template、adapter/LoRA、位置/RoPE、KV dtype/layout、引擎/格式版本；具体可共享字段由实际后端决定。缺字段 fail closed，不能仅凭文本 hash 跨模型复用。修正失效的是依赖上下文，原始实验不删除。
3. **引擎层**：确认已授权可用服务及原生 connector。首先使用 vLLM/SGLang + LMCache 的精确 prefix 能力；引擎拥有 tensor 生命周期，Agent 只提交上下文身份/访问计划和接收实测遥测。缓存不可用时正常重算；部分写不可发布；取消时引用释放，异步搬运须 ready/free 保护，不把磁盘读取未完成视为 hit。
4. **验收层**：同模型、输入 token/hash、预算、输出约束、并发和内存额度下，比较无缓存、原生 HBM prefix、CPU offload 三组；冷启动/warm/JIT 分开。记录实际命中 token/byte、读写/重算量、TTFT p50/p95、完整任务时延/质量、峰值 HBM/RAM/磁盘、失败/取消和隔离。不支持字段记 unknown，不记 0。只有传输成本低于重算且质量门槛通过才启用；非 prefix blending/量化压缩单独试验。

## 官方实现与近期经验核对

- [LMCache 官方仓库](https://github.com/LMCache/LMCache)，2026-10-15 访问 README：已提供分层存储、引擎适配和观测能力，优先复用而非另建 tensor 存储器；当前仓库说明不等同本项目已安装。
- [2026-05-12 官方多轮 Agent 基准](https://blog.lmcache.ai/en/2026/05/12/benchmarking-lmcache-for-multi-turn-agentic-workloads-on-amd-mi300x/)：方法与负结果显示，工作集能留在 HBM 时 CPU tier 可能增加开销，压力区间及真实 trace 很关键。该栈的 hash 配置教训不能无版本地推广为全部后端配置。本文未复现其 GPU 数字，也不采用博客中的未经本项目验证的质量结论。
- [官方 Benchmarking](https://docs.lmcache.ai/getting_started/benchmarking.html)：同一配置重放作为后续对照要求；本轮只检索到文档说明，未运行其工具。旧 storage_backend URL 不可访问，未按已验证接口使用。
