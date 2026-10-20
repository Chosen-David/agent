# 研究与迁移边界（2026-10-20）

本轮是read74负结果的实现续作，不冒称本轮新增十篇精读。
已完成的十篇定向正文阅读与采用/暂缓判断保留于
[研究A](../read-boundary56/research_a.md)和[研究B](../read-boundary56/research_b.md)：
AgentChaos、ACON、AgentFold、AgentFly、Reflexion、MemGPT、Mem0、MemoryBank、A-Mem、MEM1。
沿用故障必须真实触发、正常语义与资源指标分开验证的原则；不采纳有损上下文压缩、
自动遗忘或自主记忆写回来替代无损文件读取优化。这不是新的记忆算法。

本轮当前检索 `site.arxiv.org agent context management memory efficiency 2026`，
返回ACM、MemForest、CoMem等候选；搜索摘要不算精读，不据此声称找到最新最优算法。
补读[Agentic Context Management v1](https://arxiv.org/html/2607.21503v1)
（2026-07-23）的§5、§6.1–6.3：异步摄取、预取与压缩有不同一致性/成本边界；
表2排除LoCoMo adversarial类别，原始逐次产物需申请取得；论文未报告生产时延。
因此不将其准确率或理论token成本曲线当本库CPU/内存收益。预取机制及压缩验证细节
未公开，暂缓采用。只完成本次指定段落补读，不将此前部分阅读假称本轮全文新读。

[Python 3.12 io文档](https://docs.python.org/3.12/library/io.html)明确区分
可seek与顺序流、二进制bytes与文本解码。故快速路径增加seekable检查，保留原二进制
内容和哈希流程。该文档不是CPython分配数值的证明，分配收益必须来自本机实测。
尝试GitHub的CPython v3.12.14 bufferedio.c网页未成功，因此不引用其源码行号。

知识查询 `file read allocation memory bound` 命中QLoRA、FlashAttention、HNSW；
语料snapshot 767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18。
三者不适用于本地有界文件读取语义，knowledge_refs=[]，不将相关词命中当理论依据。

旧read74取舍：size+1后拼接余段的小输入成功，但增长1byte→16MiB约33.6MB峰值，
故未合入；本轮只对小且可seek文件做探测，必要时释放探测结果后重新有界读取。
收益条件是正常小文件，代价是增长回退重复读取<=64KiB；大文件仍走原路径。
不宣称吞吐、冷盘时延、RSS、模型质量、token节省或请求端到端提速。
