# DSU：增量连通与不可删除边界

## 问题触发

增量连通性；union find；DSU path compression

## 精确结论与证据身份

ACL DSU 用按大小合并与路径压缩支持增量连通；均摊 O(α(n))，不能处理删除边或有向可达性。

以下是已核查源码的实现入口；固定 commit，不代表已安装或已测性能。

## 前提与比较设置

- operation: incremental undirected connectivity
- updates: insert-only
- concurrency: single writer

## Observation / 实验 / 源码定位

- parent_or_size 负值存 root 大小；leader 压缩路径，merge 合并较小树。

## 可算例子与任务映射

merge(0,1)、merge(1,2) 后 same(0,2)=true；删除 (1,2) 不在这个 API 的能力范围。

## 失败情形与不可推广范围

- 均摊不等于每操作常数；rollback 不能直接套有压缩实现。
- 动态图删除需不同结构/离线算法。

## 最小迁移验证

- 用 BFS 小图连通性作独立 oracle。
- 核对重复合并、自环和 size；需要删除时换方案。

## 固定实现与许可证

`atcoder/ac-library@864245a00b00dd008d1abfdc239618fdb7d139da`，许可证 CC0-1.0。入口：`atcoder::dsu uf(n); uf.merge(a,b); uf.same(a,b)`。

- `atcoder/dsu.hpp`

## 来源定位与尚未验证项

- [LICENSE](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/LICENSE)；查阅 2026-10-06。
- [atcoder/dsu.hpp](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/dsu.hpp)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
