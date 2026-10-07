# 最大流：容量网络与二分图匹配

## 问题触发

二分图匹配；Dinic maxflow；residual graph

## 精确结论与证据身份

ACL mf_graph 是可复用残量网络入口；一般复杂度按 Dinic 最坏界 O(V²E)，特殊图的更好界需单独证明。

以下是已核查源码的实现入口；固定 commit，不代表已安装或已测性能。

## 前提与比较设置

- graph: directed capacity network
- capacity: nonnegative integer
- source_sink: distinct

## Observation / 实验 / 源码定位

- add_edge 保存正反边；flow 用 level graph 和阻塞流更新 residual capacity。
- flow 是增量修改残量状态；再次调用的结果不是自动从零重算。

## 可算例子与任务映射

二分图 source→左、左→右、右→sink 全容量 1，最大流等于最大匹配数；边权不自动进入该目标。

## 失败情形与不可推广范围

- 加权最小成本问题需要 min-cost flow；不能把最大 cardinality 当最大 weight。
- 容量溢出、状态复用和不当图建模会改变语义。

## 最小迁移验证

- 小二分图枚举匹配或检查 min-cut 容量作独立 oracle。
- 核对重复 flow 调用与 cap 类型上界。

## 固定实现与许可证

`atcoder/ac-library@864245a00b00dd008d1abfdc239618fdb7d139da`，许可证 CC0-1.0。入口：`atcoder::mf_graph<long long> g(n); g.add_edge(u,v,cap); g.flow(s,t)`。

- `atcoder/maxflow.hpp`

## 来源定位与尚未验证项

- [LICENSE](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/LICENSE)；查阅 2026-10-06。
- [atcoder/maxflow.hpp](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/maxflow.hpp)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
