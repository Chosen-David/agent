# 记忆/KV研究增量与本轮应用边界

检索/原文核对：2026-10-16（Asia/Shanghai）。延续 MEM-STORAGE-01，已读
12篇的方法、实验、失败条件和采用矩阵保持在
[原始阅读记录](../memory-storage-20261015/research.md)，不重算为12篇新精读。
本次复查该矩阵，补读下列3篇近期预印本的方法与实验关键段；未逐页视觉审读
全部图、附录或独立复现其GPU数字。Tessera的HTML访问失败，只有检索摘要，
不列为精读完成。论文数量不能代替当前代码收益。

## 新增原始文献核对

- [EfficientAgent，2609.33762v1，2026-09-27](https://arxiv.org/html/2609.33762v1)：
  读§2–5尤其工作集、写准入、依赖保持重放与硬件负结果。仅加载比重算便宜
  不够，还要容量覆盖跨agent复用距离；固定拒写在大容量下反而增加重算。
  **adapt验收**：真实KV阶段需固定token重放、并发/容量矩阵、实际搬运与重算量；
  **defer实现**：本库尚无tensor消费者，不把SQLite延迟装配冒称该准入算法。

- [CacheScout，2608.14624v1](https://arxiv.org/html/2608.14624v1)：
  读§2–5的anchor、在线一阶转移、BFS生存分数、预热门和对照条件。预热实际
  仍通过引擎请求产生KV，并非Python缓存key；其多agent服务与本库本地账本
  不同。**defer**转移预测/预取：先证明本项目有相应稳定前缀、真实缓存事件、
  空闲资源与取消生命周期，不能只加无人消费的预测器。

- [Persistent Memory in Multi-Agent LLM Inference，2610.07782v1，2026-10-06](https://arxiv.org/html/2610.07782v1)：
  读§2–5及局限，区分token几何推算峰值与设备实测、trace reset、组件实际
  可达、共享状态与独立题目。其单系统负结果不能推出记忆普遍无用。
  **adapt**：本轮直接测真实`MemoryLedger.list`且核完整返回；未来QA必须
  用可发生有效跨会话复用的任务、探针与隔离，不能由数据库耗时推断质量。

2026-10-16复查[LMCache官方README](https://github.com/LMCache/LMCache)与
[Benchmarking](https://docs.lmcache.ai/getting_started/benchmarking.html)：
已有原生分层、引擎适配与可观测接口，后续优先复用；文档可访问不代表已安装
或本项目已接入。没有新增模型服务、付费或GPU任务。

## 对当前候选的具体影响

沿用MemGPT分层按需装配、LongMemEval保留原始value及检索/阅读分离的原则，
把已存在的状态筛选进一步落实到精确scope匹配后装配。它是普通系统优化，
不是上述论文算法的完整复刻，也不是语义摘要/向量压缩。

| 候选 | 本轮决定 | 依据及最小检验 |
|---|---|---|
| existing mixed-status路径中先匹配scope，再装配完整对象 | 实测候选 | 无schema/外部接口改变；完整packet及异常对照，六类21对计时 |
| 新建scope索引/副本缓存 | defer | 写入、迁移和失效额外复杂；先验证无迁移的按需装配收益 |
| SQL LIKE或json_each代替Python成员语义 | reject | 字符串/字典/list/null及错误边界不等价 |
| 文本hash字典标为KV缓存命中 | reject | 没有模型tensor消费者，不会自动省prefill |
| 引擎exact-prefix + 原生LMCache适配 | 下一真实KV阶段 | 缺已配置服务、模型、缓存身份及资源合同；单独验证质量/TTFT |

复杂度仍含全库O(N)元数据解码；优化只减少不匹配scope的content/source复制、
文档及依赖读取。没有以隐藏原文、删掉历史、放宽scope或更换评测口径取得收益。
