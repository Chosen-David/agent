# FlashAttention-2：小 batch 下的并行划分

## 问题触发

occupancy；小 batch 长序列；warp partition；FlashAttention-2

## 精确结论与证据身份

ICLR 2024 的 A100 实验显示改善 block/warp 划分可提升效率；长序列、小 batch/少 heads 时应先检查并行度。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- hardware: A100
- operator: dense exact attention
- metric: kernel forward/backward throughput

## Observation / 实验 / 源码定位

- §3.2 将序列维度也并行；§3.3 减少 warp 间 shared-memory 通信。
- §4 报告 A100 的 50–73% 峰值 FLOPs 利用率；GPT 训练的最高 225 TFLOPs/s 是另一指标。

## 可算例子与任务映射

batch=1、heads=8 只给原划分 8 个 block；序列分块可增加可调度任务。这是结构分析，不是实测加速。

## 失败情形与不可推广范围

- 不能把 kernel 利用率当端到端模型加速。
- 不承诺 A100 结果适用于 Hopper/Blackwell；原子累加与确定性要求要单独核查。

## 最小迁移验证

- 核查 batch×heads 是否足够填满目标 GPU。
- 比较现有库和新实现的数值、确定性及目标形状延迟。

## 来源定位与尚未验证项

- [§3.2–3.3; §4; Figures 3–5](https://proceedings.iclr.cc/paper_files/paper/2024/file/98ed250b203d1ac6b24bbcf263e3d4a7-Paper-Conference.pdf)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
