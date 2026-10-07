# Segment tree：结合聚合与边界搜索

## 问题触发

区间聚合；segment tree monoid；非交换 运算

## 精确结论与证据身份

ACL segtree 支持满足结合律/单位元的区间聚合；set/prod 为 O(log n)，不要擅自要求交换律。

以下是已核查源码的实现入口；固定 commit，不代表已安装或已测性能。

## 前提与比较设置

- algebra: associative op with identity
- range: zero-based half-open
- operation: point set and range aggregate

## Observation / 实验 / 源码定位

- prod 用左右两个累积器保持顺序，适用于非交换 monoid。
- max_right/min_left 需符合文档的单调 predicate 且 f(e())=true。

## 可算例子与任务映射

字符串拼接是非交换 monoid，prod(0,3) 应为 abc，不得返回 cba。

## 失败情形与不可推广范围

- 无结合律的运算不可直接使用；区间更新需另选 lazy_segtree。
- 整数溢出、浮点结合律误差和 predicate 非单调可破坏结果。

## 最小迁移验证

- 检查独立 algebra 例子、空区间与非交换顺序。
- 边界搜索先核对 predicate 单调性。

## 固定实现与许可证

`atcoder/ac-library@864245a00b00dd008d1abfdc239618fdb7d139da`，许可证 CC0-1.0。入口：`atcoder::segtree<S,op,e> seg(values); seg.set(p,x); seg.prod(l,r)`。

- `atcoder/segtree.hpp`

## 来源定位与尚未验证项

- [LICENSE](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/LICENSE)；查阅 2026-10-06。
- [atcoder/segtree.hpp](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/segtree.hpp)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
