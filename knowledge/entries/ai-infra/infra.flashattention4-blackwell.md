# FlashAttention-4：Blackwell 非矩阵瓶颈与过时基线

## 问题触发

Blackwell B200；shared memory softmax；CuTe DSL；FlashAttention-4

## 精确结论与证据身份

2026-03 预印本在 B200 上报告性能，但图注明确较新 cuDNN 已吸收部分技术、达到相近性能；复用时必须重新核对版本。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- hardware: B200
- dtype: BF16
- operator: attention forward
- baseline: cuDNN 9.13 and Triton in paper

## Observation / 实验 / 源码定位

- §5 设置总 token=32k，序列 1k–32k，hidden=2048；head dims 64、128 和 (192,128)。
- §5.1 Figure 4：相对 cuDNN 9.13 为 1.1–1.3×，相对 Triton 为 2.1–2.7×；图注说更新 cuDNN 性能可相近。

## 可算例子与任务映射

基线由 1 ms 更新到 0.8 ms，而候选仍 0.8 ms，旧 1.25× 优势就消失了。这是版本敏感性的假设例子。

## 失败情形与不可推广范围

- 预印本身份，未标为顶会已接受；不把峰值 1613 TFLOPs/s 当整模型速度。
- B200 条件不能直接迁移到 A100/H100；新 cuDNN 基线会改变收益。

## 最小迁移验证

- 读取目标硬件和当前 cuDNN/库版本。
- 先做数值/梯度和一个目标形状的库比较；单独检查确定性反向。

## 来源定位与尚未验证项

- [§2.2–3; §5.1; Figure 4 caption](https://arxiv.org/pdf/2603.05451)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
