# FlashAttention：用 IO 分析选择精确注意力实现

## 问题触发

精确注意力；HBM IO；attention memory；FlashAttention

## 精确结论与证据身份

NeurIPS 2022 的实验支持分块与重计算减少注意力中间矩阵的 HBM 流量；不是把精确注意力算术复杂度改成线性。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- operator: dense exact attention
- hardware: NVIDIA GPU
- metric: attention IO and end-to-end training

## Observation / 实验 / 源码定位

- §3 的分块算法不在 HBM 保存完整 N×N 分数矩阵；§4 分别比较运行时间、内存和训练。
- §4.1 的端到端 GPT-2 训练与核算子加速分开报告，不能混用。

## 可算例子与任务映射

N=4096 时 N²=16,777,216；单头 FP16 分数矩阵约 32 MiB。此算术示例不包含 Q/K/V 或反向存储。

## 失败情形与不可推广范围

- 算术仍为 O(N²d)；线性的是额外中间存储。
- 短序列、mask、dtype 或实现版本变化后，旧收益不保证成立。

## 最小迁移验证

- 核对 mask/dropout/梯度语义及浮点容忍度。
- 先测代表性一个形状的算子和端到端占比，再决定是否扩展。

## 来源定位与尚未验证项

- [§3; §4.1–4.3; Figures 3–4](https://papers.nips.cc/paper_files/paper/2022/file/67d57c32e20fd0a7a302cb81d36e40d5-Paper-Conference.pdf)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
