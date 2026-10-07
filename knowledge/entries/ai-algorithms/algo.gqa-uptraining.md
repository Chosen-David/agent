# GQA：额外训练与质量/速度折中

## 问题触发

KV heads 共享；GQA uptraining；multi query quality；grouped-query

## 精确结论与证据身份

EMNLP 2023 的 T5 实验支持 mean-pooling 转换和额外训练后 GQA 的质量/速度折中；转换本身不保证等价。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- model: T5.1.1 XXL
- uptraining: 5% original pretraining steps
- timing: 8 TPUv4 chips greedy decoding

## Observation / 实验 / 源码定位

- §3 Table 1：MHA-XXL 平均 47.2、GQA-8 47.1；时间为 1.51 s 与 0.28 s，每 sample 每 TPUv4 chip。
- §3.3 Figures 4–5：mean pooling 优于 first/random；5% uptraining 有收益，10% 增量变小。

## 可算例子与任务映射

32 Q heads 改 8 KV heads 时，同 dtype/head_dim/长度的 KV 存储理论减少至 1/4；不是延迟自动减少到 1/4。

## 失败情形与不可推广范围

- 不能把不同任务指标的平均值看成一个标准精度；图/表时间标注须以方法与表为准。
- 5% 对应约 600 TPUv3 chip-days，不是无成本；直接替换 decoder-only 新模型需质量验证。

## 最小迁移验证

- 核对 Q heads/KV heads 分组与转换权重。
- 少量代表输入检查质量，再决定是否值得 uptraining；不盲重做已报道 pooling 全网格。

## 来源定位与尚未验证项

- [§3.1; Table 1; §3.3 Figures 4–5](https://aclanthology.org/2023.emnlp-main.298.pdf)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
