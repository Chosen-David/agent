# 研究与迁移边界（2026-10-19）

复用 [12篇既有阅读矩阵](../memory-storage-20261015/research.md)，不把旧精读
算作本轮新读10篇。涉及 LongMemEval、A-MEM、Mem0、MemGPT、Zep、PagedAttention、
SGLang、CacheBlend、KVFlow、LMCache、RAGCache、ObjectCache；各自方法/定位/局限
保留在原矩阵。本轮不声称复现这些论文或提升任务正确率。

## 当前核查

- [MemScope 2610.21170v1](https://arxiv.org/html/2610.21170v1)，阅读§3.1–4.4。
  原始轨迹、实际存储状态与源码联合定位局部修复；保持provider身份和存储兼容，
  对照从相同初始状态开始，保留回退及成功回归。采用的是局部、可回溯改动和对照
  验证方法，不是安装其Patch Agent。其GAIA/xBench/ALFWorld数据不能转成这里的收益。
  特别注意§4.4 history版本不总胜过无history，不能仅引用最优消融证明整套机制优越。
- [Python 3.12 heapq官方文档](https://docs.python.org/3.12/library/heapq.html)，
  nsmallest等价sorted(...,key=...)[:n]且面向小n。采用显式key避免比较字典载荷，
  起始行保留tie次序。该数据结构是成熟标准库复用，不包装成新算法。

直接打开arXiv官方HTML成功；另一搜索引擎未检出对应论文而返回同名内存工具，
未将这些无关结果作为依据。文章只作为方法启发，性能须本地完整检索测量。

## 定位与机制假设

真实入口 knowledge CLI → indexed_search → FTS/RRF → sections → lexical overlap
→ 两条excerpt → JSON。旧实现对每节分词一次，再对前两节重算是否匹配；
这不是正确性bug，而是可避免的重复工作。候选保留score和原片段，精确取2个最小key。
O(S log S)最坏排序改为O(S log 2)，节树和正文仍照常生成；不宣称总内存O(1)。
对真实短片段可能收益很小或无收益，必须逐场景保留负结果；不改预算和质量口径。

## 历史证据取舍

实际result_store查询 `knowledge indexed search section ranking latency` 扫描上限500、
返回3候选；首次扫描230目录，保存日志时新增本轮目录后扫描231，均partial=true，
包含旧record缺失错误。
advice-context-20261009、combined-integration-v5-20261007、math-random-score-20261009
不覆盖本基线完整indexed_search性能，均拒作新性能证据。私有完整查询日志已保存。
知识查询 `bounded top k exact heap selection` 命中学习/GPU相关卡，不适配本地精确
词法片段选择，拒作算法证明；不伪造required knowledge_refs。官方heapq为直接依据。
