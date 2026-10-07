# Fenwick tree：点增量与区间和

## 问题触发

点更新 区间求和；Fenwick；prefix sum

## 精确结论与证据身份

优先复用 ACL 的 Fenwick 实现处理动态点增量/区间和；每操作 O(log n)、存储 O(n)，不是任意区间操作通用解。

以下是已核查源码的实现入口；固定 commit，不代表已安装或已测性能。

## 前提与比较设置

- operation: point add and range sum
- range: zero-based half-open
- concurrency: single writer

## Observation / 实验 / 源码定位

- add 沿 p += p&-p 上升，prefix sum 沿 r -= r&-r；sum(l,r) 是前缀差。
- 整数实现内部使用 unsigned；支持类型和溢出语义应核对。

## 可算例子与任务映射

数组 [2,1,3]，add(1,4) 后 sum(0,2)=7，半开区间不含下标 2。

## 失败情形与不可推广范围

- 不支持直接区间赋值/min；非可减聚合不能用前缀差。
- 教学库不提供并发安全/持久化或生产性能承诺。

## 最小迁移验证

- 核对类型范围、l=r、边界和负增量。
- 用独立朴素数组对照少量操作，再按目标规模测开销。

## 固定实现与许可证

`atcoder/ac-library@864245a00b00dd008d1abfdc239618fdb7d139da`，许可证 CC0-1.0。入口：`atcoder::fenwick_tree<long long> bit(n); bit.add(p,x); bit.sum(l,r)`。

- `atcoder/fenwicktree.hpp`

## 来源定位与尚未验证项

- [LICENSE](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/LICENSE)；查阅 2026-10-06。
- [atcoder/fenwicktree.hpp](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/fenwicktree.hpp)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
