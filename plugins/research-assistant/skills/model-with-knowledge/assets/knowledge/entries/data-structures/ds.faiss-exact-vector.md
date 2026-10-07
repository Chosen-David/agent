# Faiss IndexFlat：精确向量搜索强基线

## 问题触发

向量检索 exact baseline；Faiss IndexFlat；L2 inner product

## 精确结论与证据身份

需要精确召回或评估 ANN 时，先用 Faiss IndexFlat 建立强基线；精确扫描每 query 约 O(nd)，并考虑 batched BLAS 路径。

以下是已核查源码的实现入口；固定 commit，不代表已安装或已测性能。

## 前提与比较设置

- operation: dense vector nearest-neighbor search
- metric: L2 or inner product
- quality: exact

## Observation / 实验 / 源码定位

- IndexFlat 存完整向量；L2 与 IP 是不同 metric，L2 返回平方距离。

## 可算例子与任务映射

query=(1,0)，vectors=(1,0),(2,0)：IP 第二个更高，cosine 规范化后并列，说明 metric 不能混用。

## 失败情形与不可推广范围

- IP 不是自动 cosine；cosine 需要规范化。
- CPU/GPU API、传输与目标 build 要核对；没有无条件高性能保证。

## 最小迁移验证

- 核对 float32/layout、metric、归一化与 k>n 返回行为。
- 小样本直接计算距离，ANN 的 recall 对此基线比较。

## 固定实现与许可证

`facebookresearch/faiss@83ae8b0908312c1e40734a806a3cc435b64f9496`，许可证 MIT。入口：`faiss.IndexFlatL2(d); index.add(float32_vectors); index.search(queries,k)`。

- `faiss/IndexFlat.h`

## 来源定位与尚未验证项

- [LICENSE](https://github.com/facebookresearch/faiss/blob/83ae8b0908312c1e40734a806a3cc435b64f9496/LICENSE)；查阅 2026-10-06。
- [faiss/IndexFlat.h](https://github.com/facebookresearch/faiss/blob/83ae8b0908312c1e40734a806a3cc435b64f9496/faiss/IndexFlat.h)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
