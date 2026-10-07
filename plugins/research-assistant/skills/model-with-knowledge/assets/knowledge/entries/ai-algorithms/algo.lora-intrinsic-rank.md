# LoRA：低秩更新与合并边界

## 问题触发

低秩微调；LoRA rank；adapter merge；intrinsic rank

## 精确结论与证据身份

ICLR 2022 实验支持部分任务用低秩权重更新进行高效适配；低秩需求是任务相关的经验，不是所有模型更新的定理。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- method: frozen backbone plus low-rank weight update
- models: RoBERTa DeBERTa GPT-2 GPT-3 in paper
- metric: task quality and trainable parameters

## Observation / 实验 / 源码定位

- §5 Tables 2–4 比较多任务适配；§7 分析 rank 与更新子空间。
- 可合并 W+BA 后不加推理分支；未合并、多 adapter 切换时不是零开销。

## 可算例子与任务映射

d=k=4096、r=8 时低秩参数 r(d+k)=65,536，对照 dense 16,777,216，约 1/256；这只计算一个矩阵可训练参数。

## 失败情形与不可推广范围

- 冻结权重仍有存储与激活成本；rank 增大不保证单调改善。
- 原论文含引用的他人基线和不同设置，不能当严格同条件本机 A/B。

## 最小迁移验证

- 核对 target modules、rank/alpha、初始化与 merge 语义。
- 先选小规模 rank 对照与 held-out 质量，不重复全量秩扫描来证明普遍低秩。

## 来源定位与尚未验证项

- [§5 Tables 2–4; §7 rank ablations; Appendix](https://arxiv.org/pdf/2106.09685)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
