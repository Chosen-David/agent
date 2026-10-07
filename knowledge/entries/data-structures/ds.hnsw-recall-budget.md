# HNSW：ef、召回与内存预算

## 问题触发

HNSW ef recall；近似近邻；ANN memory

## 精确结论与证据身份

HNSW 的 ef/M/ef_construction 是召回、查询/构建成本和内存的折中；参数不能只按教程默认值宣称最优。

以下是已核查源码的实现入口；固定 commit，不代表已安装或已测性能。

## 前提与比较设置

- operation: approximate vector nearest-neighbor search
- metric: l2 ip or cosine
- quality: approximate

## Observation / 实验 / 源码定位

- README 分开定义构建 M/ef_construction 与查询 ef；源码为多层图搜索。
- 并发 insert/query 组合限制与索引保存后的 ef 恢复行为要按固定版本核对。

## 可算例子与任务映射

k=10、返回 8 个真实 top-10，Recall@10=0.8；更快不能替代你的最低召回约束。

## 失败情形与不可推广范围

- 无所有数据分布上的 O(log n) 最坏搜索保证；分布变化可影响召回。
- 不支持把 ANN 结果作为 exact correctness oracle。

## 最小迁移验证

- 用精确检索测 Recall@k 与 p95 延迟；包含目标分布和内存。
- 至少一个较高 ef 对照，确认召回而不是仅速度。

## 固定实现与许可证

`nmslib/hnswlib@ca426729609b3221563047ceb269cc1213e0d376`，许可证 Apache-2.0。入口：`hnswlib.Index(space="l2",dim=d); init_index(...); add_items(...); set_ef(ef); knn_query(...,k=k)`。

- `hnswlib/hnswalg.h`
- `README.md`

## 来源定位与尚未验证项

- [LICENSE](https://github.com/nmslib/hnswlib/blob/ca426729609b3221563047ceb269cc1213e0d376/LICENSE)；查阅 2026-10-06。
- [hnswlib/hnswalg.h](https://github.com/nmslib/hnswlib/blob/ca426729609b3221563047ceb269cc1213e0d376/hnswlib/hnswalg.h)；查阅 2026-10-06。
- [README.md](https://github.com/nmslib/hnswlib/blob/ca426729609b3221563047ceb269cc1213e0d376/README.md)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
